
function raz_schedules(){
	var form = $($($(this).parents('.panel-body').first()).find('form').first());
	form.find('.venue-block .form-group>textarea').val('')
}

$(document).ready(function(){
      $('.clear-cinema').on('click', raz_schedules);
});