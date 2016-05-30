function init_is_cultural_animator(){
    var is_cultural_animator_inputs = $("input[name='is_cultural_animator']");
    for(var i=0; i<is_cultural_animator_inputs.length;i++){
        var input = $(is_cultural_animator_inputs[i]);
        var structure_form = $($(input.parents('form').first()).find('.cultural-animator-structure').parents('.form-group').first());
        $(structure_form.find('a.deform-close-button')).css('display', 'none');
        if(input.prop('checked')){
            structure_form.css('display', 'block')
        }else{
            structure_form.css('display', 'none')
        }
    }
}

$(document).ready(function(){
    $('.ajax-form .control-form-button').on('click', function(event){
        var form = $($(this).parents('.ajax-form').find(".controled-form").first());
        var changepassword = $(form.find("input[name='changepassword']").first());
        if(!changepassword.prop('checked')){
            changepassword.prop('checked', true);
        }else{
            changepassword.prop('checked', false);
        }
    });
    
    init_is_cultural_animator();
    $("input[name='is_cultural_animator']").on('change', function(){
        var input = $(this);
        var structure_form = $($(input.parents('form').first()).find('.cultural-animator-structure').parents('.form-group').first());
        if(input.prop('checked')){
            $(structure_form.find('a.deform-seq-add')).click();
            $(structure_form.find('a.deform-close-button')).css('display', 'none');
            structure_form.slideDown();
        }else{
            structure_form.slideUp('fast');
            $(structure_form.find('a.deform-close-button')).click()
        }
    })
});
