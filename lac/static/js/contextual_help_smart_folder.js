function init_events_smart_folder(){
    $('select[name="authors"]').parents('div').first().on('select2:opening', function(){
        sub_contextual_help(this, '.author-filter-help');
    }); // AUTHORS

    $('select[name="artists_ids"]').parents('div').first().on('select2:opening', function(){
        sub_contextual_help(this, '.artist-filter-help');
    }); //ARTISTS

    $('.item-text_to_search').on('click', function(){
        sub_contextual_help(this, '.text-filter-help');
    }); //TEXT

    $('.tree-container').on('click', function(){
        sub_contextual_help(this, '.categories-help');
    }); //CATEGORIES

    $('.item-created_after').add('.item-created_before').hover(function(){
        var dates_p = $('[value="created_date:mapping"]').parents('div').first();
        sub_contextual_help(dates_p, '.after-before-dates-help');
    },
    function(){}); // DATES CREATED BEFORE AND AFTER

    $('select[name="sources"]').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.source-help');
    }); // SOURCES

    $('.classifications-field').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.classification-help');
    }); //CLASSIFICATION

    $('input[name="add_as_a_block"]').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.add-as-a-block-help');
    }); //ADD AS A BLOCK

    $('.icon-input').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.icon-help');
    }); //ICON

    $('.color-picker').hover(function(){
        sub_contextual_help(this, '.colors-help');
    },
    function(){}
    ); //COLORS
}

$(document).ready(function(){
    init_contextual_help();
    init_events_smart_folder();
    $('form.deform').on('item_added item_reloaded', function(event){
        init_events_smart_folder();
         });
});
