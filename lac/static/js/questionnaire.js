
function set_questionnaire(id){
    $.cookie(id, 'true', {path: '/',  expires: 360*20});
}

function send_questionnaire(event){
  var form = $(this);
  var button = form.find('button').last();
  var email = form.find('input[name="email"]').last();
  var quest_id = form.find('input[name="id"]').last();
  var input_new_version = form.find('.questionnaire-new-version input[value="False"]');
  var explanation = form.find('textarea[name="explanation"]').last();
  $('.questionnaire-container .alert-danger').addClass('hide-bloc');
  if(input_new_version.prop('checked') && !explanation.val()){
    $('.questionnaire-container .alert-danger.alert-explanation').removeClass('hide-bloc');
  }else{
    if(!email.val()){
      $('.questionnaire-container .alert-danger.alert-email').removeClass('hide-bloc');
    }else{
    	var values = form.serialize()+'&'+button.val()+'='+button.val();
    	button.addClass('disabled')
      loading_progress();
    	$.post(window.location.href, values, function(data) {
          finish_progress();
          button.removeClass('disabled');
          form.addClass('hide-bloc')
          $('.questionnaire-container .alert-danger').addClass('hide-bloc');
          $('.questionnaire-btn').addClass('hide-bloc')
          $('.questionnaire-container .alert-success').removeClass('hide-bloc');
          set_questionnaire(quest_id.val())
          setTimeout(function(){form.parents('.modal').first().modal('hide')}, 2000); 
       });
    }
  }
  event.preventDefault();
}

function send_improve(event){
  var form = $(this);
  var button = form.find('button').last();
  var email = form.find('input[name="email"]').last();
  var improvement = form.find('textarea[name="improvement"]').last();
  var url_input = form.find('input[name="url"]').last();
  url_input.val(window.location.href)
  $('.improve-container .alert-danger').addClass('hide-bloc');
  if(!improvement.val()){
    $('.improve-container .alert-danger.improvement-alert').removeClass('hide-bloc');
  }else{
	  if(!email.val()){
	    $('.improve-container .alert-danger.email-alert').removeClass('hide-bloc');
	  }else{
	  	var values = form.serialize()+'&'+button.val()+'='+button.val();
	  	button.addClass('disabled')
	    loading_progress();
	  	$.post(window.location.href, values, function(data) {
	        finish_progress();
	        button.removeClass('disabled');
	        form.addClass('hide-bloc')
	        $('.improve-container .alert-danger').addClass('hide-bloc');
	        $('.improve-container .alert-success').removeClass('hide-bloc');
	        set_questionnaire()
	        setTimeout(function(){form.parents('.modal').first().modal('hide')}, 2000); 
	     });
    }
  }
	event.preventDefault();
}

$(document).ready(function(){
    $(document).on('submit','.questionnaire-container form', send_questionnaire);
    $(document).on('submit','.improve-container form', send_improve);
    setTimeout(function(){
      var btn = $('.questionnaire-btn');
      var id = btn.data('quest_id')
      if (!$.cookie(id) && ! $.cookie('questionnaire_closed')){
          $('.questionnaire-btn').click()
        }
      } , 10000);

    $(document).on('change', '.questionnaire-new-version', function(){
        var input = $(this).find('input[value="False"]');
        var explanation = $($(input.parents('form').first()).find('.explanation-version').first());
        if(input.prop('checked')){
            $(explanation.find('a.deform-close-button')).css('display', 'block');
            explanation.slideDown();
        }else{
            $(explanation.find('a.deform-close-button')).css('display', 'none');
            explanation.slideUp('fast');
        }
    })

    $(document).on('click', '.questionnaire-alert .close', function(){
       var date = new Date();
       date.setTime(date.getTime() + (60 * 60 * 1000));
       $.cookie('questionnaire_closed', 'true', {path: '/',  expires: date});
    })

    $(document).on('show.bs.modal', '.questionnaire-modal', function(){
        $('body').addClass('questionnaire-modal-open')
    })
    $(document).on('hidden.bs.modal', '.questionnaire-modal', function(){
        $('body').removeClass('questionnaire-modal-open')
    })
})