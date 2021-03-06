from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic.edit import DeleteView
from django_tables2 import RequestConfig
from geopy.distance import distance

from app.models import Item, Image, Search, FoundItem
from app.tables import FoundItemTable, ItemTable
from app.varia import send_emails, send_item_published_email_to_owner
from rentwise.settings_default import LOGIN_URL_FACEBOOK
from .forms import ItemForm, SearchForm


def log_in_view(request):
    """
    Returns a redirect to facebook login page which will then after logging in
    redirects to the page in the next parameter.
    """
    return redirect(LOGIN_URL_FACEBOOK + '?next=' + request.GET.get('next', ''))


def home(request):
    """
    Landing Page View.
    Provides stats about user activity on the page.
    Handles search query.
    """
    published_items = Item.objects.filter(is_published=True).count()
    fb_profile_clicks = sum(item.renters.count() for item in Item.objects.all())
    context = dict(
        published_items=published_items,
        fb_profile_clicks=fb_profile_clicks,
    )
    context = search_items(context, request)
    return render(request, 'app/index.html', context)


def search_items(context, request):
    """
    Method to handle item search.
    Validates SearchForm from GET request, persists the search specifics and returns context with item table.
    """
    if request.method != 'GET':
        context['form'] = SearchForm()
        return render(request, 'app/index.html', context)

    form = SearchForm(request.GET)
    if not form.is_valid():
        return render(request, 'app/index.html', context)
    what = form.cleaned_data['what'].strip()
    place = form.cleaned_data['place']
    location = form.cleaned_data['location']
    category = form.cleaned_data['category']

    search = None
    if what or category or place or location:
        search_data = form.cleaned_data
        if request.user.is_authenticated():
            search_data['user'] = request.user
        search = Search(**search_data)
        search.save()
        context['searched'] = True

    # Cannot repopulate location field. Google places api js populates it based on the place field.
    form = SearchForm(data=dict(what=what, place=place, category=category))
    context['form'] = form

    # Search
    items = Item.objects.filter(is_published=True)
    if category:
        items = items.filter(categories=category)
    if what:
        # items = items.annotate(what=SearchVector('name', 'description'))
        items = items.filter(Q(name__icontains=what) | Q(description__icontains=what))

    # Create table from results
    table = None
    if items and search and search.location:
        found_items = []
        for item in items:
            found_item = FoundItem(item=item, search=search)
            found_item.distance = distance(item.location, location).miles
            found_item.save()
            found_items.append(found_item)
            table = FoundItemTable(found_items)
    elif items:
        table = ItemTable(items)

    if table:
        RequestConfig(request).configure(table)
        context['table'] = table
    return context


@method_decorator(login_required, name='dispatch')
class ItemAddView(FormView):
    """
    Checks for valid form in POST request, saves item and sends emails.
    """
    form_class = ItemForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'app/add_item.html', {'form': form})

    def post(self, request, *args, **kwargs):
        if len(Item.objects.filter(user=request.user)) > 500:
            return redirect('home')
        form = self.form_class(request.POST)

        if form.is_valid():
            item_data = {k: v for k, v in form.cleaned_data.items() if 'image' not in k}
            item_data['user'] = request.user
            categories = item_data.pop('categories')
            item = Item(**item_data)
            item.save()

            item.categories = categories
            item.save()

            images_data = {k: v for k, v in form.cleaned_data.items() if 'image' in k}
            for key in sorted(k for k, v in images_data.items() if v):
                url = images_data[key]
                image = Image(item=item, url=url)
                image.save()

            send_emails(request, item)
            response = redirect('view_item', item.id)
            response['Location'] += '?new=true'
            return response
        else:
            return render(request, 'app/add_item.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ItemDetailView(DetailView):
    """
    Shows unpublished item details to owner and staff Users.
    """
    template_name = 'app/item_details.html'
    model = Item

    def get(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = get_object_or_404(Item, id=item_id) if item_id else None
        if item.is_published or item.user == request.user or request.user.is_staff:
            return super().get(request, *args, **kwargs)
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['distance'] = self.request.GET.get('distance')
        if self.request.GET.get('new'):
            context['new'] = self.request.GET['new'] == 'true'
        return context


@method_decorator(login_required, name='dispatch')
class ItemDeleteView(DeleteView):
    """
    Allows only the owner or staff User to delete Item.
    """
    model = Item
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = get_object_or_404(Item, id=item_id) if item_id else None
        if item and (item.user == request.user or request.user.is_staff):
            return super().post(request, *args, **kwargs)
        return redirect('view_item', item.id)


@staff_member_required
def publish_item(request, *args, **kwargs):
    """
    Allows staff to publish item.
    """
    item_id = kwargs.get('pk')
    item = get_object_or_404(Item, id=item_id) if item_id else None
    if item and request.user.is_staff:
        item.is_published = True
        item.save()
        if not item.email_sent_to_user:
            send_item_published_email_to_owner(request, item)
            item.email_sent_to_user = True
            item.save()
    return redirect('view_item', item.id)


@staff_member_required
def unpublish_item(request, *args, **kwargs):
    """
    Allows staff to unpublish item.
    """
    item_id = kwargs.get('pk')
    item = get_object_or_404(Item, id=item_id) if item_id else None
    if item and request.user.is_staff:
        item.is_published = False
        item.save()
    return redirect('view_item', item.id)


def logout_view(request):
    """
    Logs out User and redirects to landing page.
    """
    logout(request)
    return redirect('home')


@login_required
def contact_owner(request, pk):
    """
    Adds the requesting User as a renter to the given item_id
    if the requestin User is not the owner of the Item and
    the user has not already been added.
    """
    if not pk:
        return redirect('home')
    item = get_object_or_404(Item, id=pk) if pk else None
    if not item.renters.filter(id=request.user.id) and request.user != item.user and not request.user.is_staff:
        item.renters.add(request.user)
        item.save()
    return redirect(item.user.profile.facebook_url)
