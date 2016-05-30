// var contextual_help_mapping = {'dates': 'date-help', 'venue': 'venue-help', 'address-title':'address-title-help'};
function contextual_help_template(help){
    return ('<div class="contextual-help-item alert alert-warning alert-dismissible" style="margin-top:10px">' +
    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
    '<span class="glyphicon glyphicon-info-sign pull-right"></span>' +
     help +
    '</div>');
 }

function init_contextual_help(){
    var helps = $('.contextual-help');
    for(var i=0; i<helps.length; i++){
        var help = $(helps[i]);
        if (!window.matchMedia('(max-width: 991px)').matches) {
            help.data('top', help.offset().top);
        }
        if($('.principal-help').length == 0){
            help.addClass('hide-bloc');
        }
    }
}

function sub_contextual_help(element, help_class, insertion_node){
        if (insertion_node === null){
            insertion_node = element;
        }
        var help = $(help_class);
        $('.contextual-help').addClass('hide-bloc');
        if(help.length>0){
            var helps = $('.contextual-help-item');
            var help_parent = $(help.parents('.contextual-help.alert').first());
            helps.addClass('hide-bloc');
            if (!window.matchMedia('(max-width: 991px)').matches) {
                help_parent.removeClass('hide-bloc');
                var position = $(element).offset().top;
                help_parent.offset({top: position});
                help.removeClass('hide-bloc');
            }
            else{
                $(insertion_node).first().after(contextual_help_template(help.html()));
            }

        }
}
