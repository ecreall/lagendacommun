
var director_id = '';


function init_edit_director(){
   var form_groups = $($('.directors-values').parents('.form-group'));
   form_groups.css('margin-bottom', '0px');
   form_groups.children('label').css('display', 'none');
   $('span.director-edit').on('click', render_edit_director_form)
};


function render_edit_director_form(event){
	$($(this).parents('.form-group').find('select').first()).select2("close");
	var form = $($(this).parents('form').first());
    var directors_values = $(form.find('.directors-values').first());
    var ids = $(directors_values.find('.director-data input[name="id"]'));
    var director_id = $(this).data('director_id');
    if(ids.length !== 0){
    	for(var i=0; i<ids.length; i++){
    		var input_id = $(ids[i]); 
	        if (input_id.val() === director_id){
	        	var director_form = $(input_id.parents('.deform-seq-item').first().find('.item-form-modal').first());
	        	director_form.modal('show');
	        	var title = $($(directors_values.find('.director-data').first()).find('input[name="title"]').first())
	            $(director_form.find('.modal-title').first()).html('<span>'+title.val()+' <span class="glyphicon glyphicon-pencil"></span></span>' );
	            event.stopPropagation() 
	          	break;
	        }
    	};
    };
};


function director_data_added(event){
   var element = $(event.element);
   var target = $(element.find('.director-data').first());
   if(element.parents('.directors-values').length != 0){
   	  var params = {op: 'get_artist_form',
                    artist_id: director_id};
   	  var url = $(location).attr('href').split($(location).attr('pathname'))[0]+'/@@creationculturelapi';
      $.getJSON(url,params, function(data) {
		    if(data['body']){
		        target.replaceWith($($(data['body']).find('.director-data').first()));
            $(target.find('input[name="id"]').first()).val(director_id);
		        try {
                  deform.processCallbacks();
	              }
	            catch(err) {};
		    }
	  });

   }
};


function unselect_director(e){
	var form = $($(e.target).parents('form').first());
    var directors_values = $(form.find('.directors-values').first());
    var ids = $(directors_values.find('.director-data input[name="id"]'));
    var director_id = e.params.data.id;
    if(ids.length !== 0){
    	for(var i=0; i<ids.length; i++){
    		var input_id = $(ids[i]); 
	        if (input_id.val() === director_id){
	        	$(input_id.parents('.deform-seq-item').find('.deform-close-button').first()).click();
	          	break;
	        }
    	};
    };
    $($(e.target).parents('.form-group').first().find('span.director-edit')).on('click', render_edit_director_form)
};


function select_director(e){
	var form = $($(e.target).parents('form').first());
    var directors_values = $(form.find('.directors-values').first());
    var ids = $(directors_values.find('.director-data input[name="id"]'));
    var exists = false;
    director_id = e.params.data.id;
    if(ids.length !== 0){
    	for(var i=0; i<ids.length; i++){
	        if ($(ids[i]).val() === director_id){
	          	exists = true;
	          	break;
	        }
    	};
    };
	if (! exists){
		form.unbind('item_added', director_data_added);
		form.bind('item_added', director_data_added);
	    $(directors_values.parents('.deform-seq').first().find('.deform-seq-add').first()).click();
	}
	$($(e.target).parents('.form-group').first().find('span.director-edit')).on('click', render_edit_director_form)
};



$(document).ready(function(){
  $('select.directors-container').on("select2:unselect", unselect_director);
  $('select.directors-container').on("select2:select", select_director);
  deform.addCallback(
         'init_edit_director',
         function() {
            init_edit_director()
           }
         )
});
