
var artist_id = '';


function init_edit_artist(){
   var form_groups = $($('.artists-values').parents('.form-group'));
   form_groups.css('margin-bottom', '0px');
   form_groups.children('label').css('display', 'none');
   $('span.artist-edit').on('click', render_edit_artist_form)
};


function render_edit_artist_form(event){
	$($(this).parents('.form-group').find('select').first()).select2("close");
	var form = $($(this).parents('form').first());
    var artists_values = $(form.find('.artists-values').first());
    var ids = $(artists_values.find('.artist-data input[name="id"]'));
    var artist_id = $(this).data('artist_id');
    if(ids.length !== 0){
    	for(var i=0; i<ids.length; i++){
    		var input_id = $(ids[i]); 
	        if (input_id.val() === artist_id){
	        	var artist_form = $(input_id.parents('.deform-seq-item').first().find('.item-form-modal').first());
	        	artist_form.modal('show');
	        	var title = $($(artists_values.find('.artist-data').first()).find('input[name="title"]').first())
	            $(artist_form.find('.modal-title').first()).html('<span>'+title.val()+' <span class="glyphicon glyphicon-pencil"></span></span>' );
	            event.stopPropagation() 
	          	break;
	        }
    	};
    };
};


function artist_data_added(event){
   var element = $(event.element);
   var target = $(element.find('.artist-data').first());
   if(element.parents('.artists-values').length != 0){
   	  var params = {op: 'get_artist_form',
                    artist_id: artist_id};
   	  var url = $(location).attr('href').split($(location).attr('pathname'))[0]+'/@@creationculturelapi';
      $.getJSON(url,params, function(data) {
		    if(data['body']){
		        target.replaceWith($($(data['body']).find('.artist-data').first()));
            $(target.find('input[name="id"]').first()).val(artist_id);
		        try {
                  deform.processCallbacks();
	              }
	            catch(err) {};
		    }
	  });

   }
};


function unselect_artist(e){
	var form = $($(e.target).parents('form').first());
    var artists_values = $(form.find('.artists-values').first());
    var ids = $(artists_values.find('.artist-data input[name="id"]'));
    var artist_id = e.params.data.id;
    if(ids.length !== 0){
    	for(var i=0; i<ids.length; i++){
    		var input_id = $(ids[i]); 
	        if (input_id.val() === artist_id){
	        	$(input_id.parents('.deform-seq-item').find('.deform-close-button').first()).click();
	          	break;
	        }
    	};
    };
    $($(e.target).parents('.form-group').first().find('span.artist-edit')).on('click', render_edit_artist_form)
};


function select_artist(e){
	var form = $($(e.target).parents('form').first());
    var artists_values = $(form.find('.artists-values').first());
    var ids = $(artists_values.find('.artist-data input[name="id"]'));
    var exists = false;
    artist_id = e.params.data.id;
    if(ids.length !== 0){
    	for(var i=0; i<ids.length; i++){
	        if ($(ids[i]).val() === artist_id){
	          	exists = true;
	          	break;
	        }
    	};
    };
	if (! exists){
		form.unbind('item_added', artist_data_added);
		form.bind('item_added', artist_data_added);
	    $(artists_values.parents('.deform-seq').first().find('.deform-seq-add').first()).click();
	}
	$($(e.target).parents('.form-group').first().find('span.artist-edit')).on('click', render_edit_artist_form)
};



$(document).ready(function(){
  $('select.artists-container').on("select2:unselect", unselect_artist);
  $('select.artists-container').on("select2:select", select_artist);
  deform.addCallback(
         'init_edit_artist',
         function() {
            init_edit_artist()
           }
         )
});
