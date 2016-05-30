function init_events_cinema_session(){
    $('.venue-title').parents('div').first().on('click', function(){
        sub_contextual_help(this, '.cinema-help');
        });
    $('textarea[name="schedules"]').parent('div').first().on('click', function(){
        sub_contextual_help(this, '.schedules-help');
    });
}

$(document).ready(function(){
    init_contextual_help();
    init_events_cinema_session();
    $('form.deform').on('item_added item_reloaded', function(event){
        init_events_cinema_session();
         });
});