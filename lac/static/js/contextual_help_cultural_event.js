function init_events_cultural_event(){
    $('textarea[name="description"]:eq(0)').on('click', function(){
        sub_contextual_help(this, '.description-help', this);
    }); //SHORT DESCRIPTION

    $('.ce-field-details').on('ed_init', function(e){
        var element = $(this);
        var element_parent = $($(this).parents('.form-group').first());
        e.ed.on('focus',function(){
        sub_contextual_help(element_parent, '.details-help', element);
    });
    }); //DETAILED DESCRIPTION

    $('.img-container').parents('div').first().on('change', function(){
        sub_contextual_help(this, '.image-help', '.img-container');
    }); //IMAGE

    var location_artists = $(".form-control.artists-container").parents('div').first();
    location_artists.on('click', function(){
        sub_contextual_help(this, '.artists-help', location_artists);
    }); //ARTISTS NAMES

    $('.tree-container').on('click', function(){
        sub_contextual_help(this, '.categories-help', '.tree-container');
    }); //CATEGORIES

    $('[id*=contact]').on('click', function(){
        sub_contextual_help(this, '.contact-help', $('[id*=contact]').parent("div").first());
    }); //CONTACTS

    $('input[name="dates"]').on('click', function(){
        sub_contextual_help(this, '.date-help', '.help-date-wdget');
    }); //DATES

    $(document).on('select2:opening', 'div.venue-block .venue-title', function(){
        sub_contextual_help($($(this).parents('.form-group').first().find('span.select2').first()),
                            '.venue-help', 'div.venue-block > div');
     }); //VENUE TITLE


    $(document).on('ed_init', 'div.venue-block textarea[name="description"]', function(e){
        var element = $(this);
        var element_parent = $($(this).parents('.form-group').first());
        e.ed.on('focus',function(){
        sub_contextual_help(element_parent, '.venue-description-help', element);
      });
    }); //DETAILED DESCRIPTION

    $('.address-well input[name="title"]').on('click', function(){
        var element = $(this);
        sub_contextual_help(element, '.address-title-help', element);
     }); //ADDRESS TITLE

    $('select[name="country"]').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.address-country-help', this);
    }); //ADDRESS COUNTRY

     $('select[name="zipcode"]').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.address-zipcode-help', this);
    });  //ADDRESS ZIPCODE

    $('select[name="city"]').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.address-city-help', this);
    });  //ADDRESS CITY

     $('select[name="department"]').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.address-department-help', this);
    });  //ADDRESS DEPARTMENT

    $('input[name="ticketing_url"]').on('click', function(){
        sub_contextual_help(this, '.ticketing-url-help', this);
    }); // TICKETING URL
}

$(document).ready(function(){
    init_contextual_help();
    init_events_cultural_event();
    $('form.deform').on('item_added item_reloaded', function(event){
        init_events_cultural_event();
         });
});
