function init_events_interview(){
    $('textarea[name="article"]').on('ed_init', function(e){
        var element = $(this);
        var element_parent = $($(this).parents('.form-group').first());
        e.ed.on('focus',function(){
        sub_contextual_help(element_parent, '.article-help', element);
    });
    });
}

$(document).ready(function(){
    init_contextual_help();
    init_events_interview();
    $('form.deform').on('item_added item_reloaded', function(event){
        init_events_interview();
         });
});
