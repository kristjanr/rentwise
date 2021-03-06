(function($) {
    $(function() {
         $('.jcarousel').jcarousel({
                wrap: 'circular'
            });

        $('.jcarousel-control-prev')
            .on('jcarouselcontrol:active', function() {
                $(this).removeClass('inactive');
            })
            .on('jcarouselcontrol:inactive', function() {
                $(this).addClass('inactive');
            })
            .jcarouselControl({
                target: '-=1'
            });

        $('.jcarousel-control-next')
            .on('jcarouselcontrol:active', function() {
                $(this).removeClass('inactive');
            })
            .on('jcarouselcontrol:inactive', function() {
                $(this).addClass('inactive');
            })
            .jcarouselControl({
                target: '+=1'
            });

        $('.jcarousel-pagination')
                .on('jcarouselpagination:active', 'a', function() {
                    $(this).addClass('active');
                })
                .on('jcarouselpagination:inactive', 'a', function() {
                    $(this).removeClass('active');
                })
                .on('click', function(e) {
                    e.preventDefault();
                })
                .jcarouselPagination({
                    item: function(page) {

                        return '<a href="#' + page + '">' + page + '</a>';
                    }
                });
    });
    var total_items = $('.jcarousel').find('li').length;
    if(total_items < 2)
    {
        $('.jcarousel-control-prev, .jcarousel-control-next, .jcarousel-pagination').hide();
    }
})(jQuery);
