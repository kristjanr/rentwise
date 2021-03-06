from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MinLengthValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.fields import LocationField


class Profile(models.Model):
    """
    Extends the User model through one to one relationship in order to keep the FB-specific data.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facebook_id = models.TextField(max_length=500)
    picture_url = models.TextField(max_length=500)

    @property
    def facebook_url(self):
        return 'https://www.facebook.com/%s/' % self.facebook_id

    def __str__(self):
        return self.user.__str__() + ' ' + self.facebook_url


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Assures that a Profile is created after a User is created.
    """
    if created:
        Profile.objects.create(user=instance)


class Category(models.Model):
    """
    Contains the categories the Item can have.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


positive_decimal = MinValueValidator(Decimal('0.01'))
min_1 = MinValueValidator(1)
max_500 = MaxValueValidator(500)
max_5000 = MaxValueValidator(5000)


class Item(models.Model):
    """
    Item model with all the necessary validators on the fields, which are used when adding an Item.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Owner', )
    renters = models.ManyToManyField(User, related_name='items')
    categories = models.ManyToManyField(Category, related_name='items', verbose_name='Categories', )
    name = models.TextField(max_length=100, validators=[MinLengthValidator(5)], verbose_name='Name', )
    description = models.TextField(max_length=5000, validators=[MinLengthValidator(20)], verbose_name='Description', )
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2,
                                        validators=[max_5000, positive_decimal], verbose_name='Price (£/day)', )
    minimum_rental_period = models.IntegerField(validators=[min_1, max_500], verbose_name='Min. days', )
    estimated_value = models.IntegerField(validators=[min_1], verbose_name='Value (£)', )
    place = models.CharField(max_length=250, verbose_name='Location', )
    location = LocationField(base_field='place')
    is_published = models.BooleanField(default=False, verbose_name='Is published', )
    created_at = models.DateTimeField(auto_now=True, verbose_name='Added on', )
    email_sent_to_user = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/item/%i/" % self.id


class Image(models.Model):
    """
    The Image model - every Item can have multiple Images.
    """
    item = models.ForeignKey('item', on_delete=models.CASCADE, )
    url = models.URLField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.url


class Search(models.Model):
    """
    Search model to record what searches have been done.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True,
                                 verbose_name='Filter by category', )
    what = models.CharField(max_length=250, blank=True, null=True)
    place = models.CharField(max_length=250, blank=True, null=True)
    location = LocationField(base_field='place', blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.what + ' ' + self.place


class FoundItem(models.Model):
    """
    This is needed to be able to sort and show the distance column at the search results table.
    """
    search = models.ForeignKey(Search, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    distance = models.FloatField(verbose_name='Distance (miles)', null=True)

    @property
    def name(self):
        return self.item.name
