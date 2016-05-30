
var default_smart_folder_title = 'Title';


function get_preview_template(title){
    var folder_title = title;
    if (title == ""){
    	folder_title = default_smart_folder_title
    };
    return '<div class=\"color-preview\">'+
			'<button class=\"btn\" type=\"button\" id=\"preview-button\">'+
			folder_title+
			'</button>'+
            '<div class=\"folder-title\">'+
            '<div class=\"legend-folder\"></div> '+
            '<span>'+
            folder_title+
            '</span>'+
            '</div>'+
            '</div>'
};


function synchronize_style(event){
	var form = $($(this).parents('form').first());
	var preview_button = $(form.find('#preview-button').first());
    var preview_folder_title = $(form.find('.folder-title').first());
	var usual_color_input = $(form.find("input[name='usual_color']").first());
	var hover_color_input = $(form.find("input[name='hover_color']").first());
	var colors = {usual: {'font': font_default_val,
		                  'background-color': background_default_val},
                  hover: {'font': font_default_val,
                  	      'background-color': background_default_val}};

    var usual_color_value = usual_color_input.val();
    if (usual_color_value != ""){
        var usual_color_values = usual_color_value.split(',');
        colors.usual['font'] = usual_color_values[0];
        colors.usual['background-color'] = usual_color_values[1];
    };

    var hover_color_value = hover_color_input.val();
    if (hover_color_value != ""){
        var hover_color_values = hover_color_value.split(',');
        colors.hover['font'] = hover_color_values[0];
        colors.hover['background-color'] = hover_color_values[1];
    };
    preview_button.css('color', colors.usual['font']);
    preview_button.css('background-color', colors.usual['background-color']);
    preview_button.hover(
	    function() {
	        $(this).css('color', colors.hover['font']);
            $(this).css('background-color', colors.hover['background-color']);
	    },
	    function () {
	      $(this).css("color", colors.usual['font']);
          $(this).css("background-color", colors.usual['background-color']);
	    });
    preview_folder_title.css('color', colors.usual['background-color']);
    $(preview_folder_title.find('.legend-folder').first()).css('background-color', colors.usual['background-color']);

};


function add_preview(){
    var inputs = $('input.smartfolder-title-field');
    for(var i=0; i<inputs.length; i++){
    	var input = $(inputs[i]);
    	var form = $(input.parents('form').first());
    	if ($(form.find('.color-preview')).length == 0){
	        var usual_color_input = $(form.find("input[name='usual_color']").first());
	        usual_color_input.after(get_preview_template(input.val()))
	    }
    }
};

function init_classification_field(classification, to_refresh){
    var seq = $(classification.parents('.classifications-field').first());
    var classifications = $(seq.find('.classification-field'));
    var classification_value = classification.val();
    var options = classification.find('option');
    for(var i=0; i<options.length; i++){
        $(options[i]).attr("disabled", false);
    };
    var values = []
    for(var i=0; i<classifications.length; i++){
        var value = $(classifications[i]).val();
        if(value != "" && value != classification_value){
            classification.find('option[value='+value+']').attr('disabled', 'disabled');
        }
    };

    if(to_refresh){
        classification.select2({containerCssClass: 'form-control'});
        $($(classification.parents('.deform-seq-item').first()).find('.select2.select2-container').first()).css('width', '100%');
    }
}


function init_classifications_field(to_refresh){
    var classifications = $('.classification-field');
    for(var i=0; i<classifications.length; i++){
        var classification = $(classifications[i]);
        init_classification_field(classification, to_refresh)
    }
}


$(document).ready(function(){

	add_preview();

    $('input.smartfolder-title-field').on('keyup', function(){
        var title_input = $(this).val();
        var form = $($(this).parents('form').first());
	    var preview_button = $(form.find('#preview-button').first());
        var preview_folder_title = $(form.find('.folder-title span').first());
        if(title_input == ""){
            preview_button.html(default_smart_folder_title);
            preview_folder_title.html(default_smart_folder_title);
        }
        else{
            preview_button.html(title_input);
            preview_folder_title.html(title_input);
        }
    });

    $("input[name='usual_color'], input[name='hover_color']").on('change', synchronize_style);

    
    init_classifications_field(false);

    $('.classification-field').on('change', function(){
        init_classifications_field(true);
    });

   $('form.deform').on('item_added', function(event){
         var item_added = $(event.element);
         var parents = $(item_added.parents('.classifications-field'));
         if(parents.length>0){
            init_classifications_field(true);
            $(item_added.find('select.classification-field')).on('change', function(){
                 init_classifications_field(true);
             })
         }
    });

   $('form.deform').on('item_removed', function(event){
         var sequence = $(event.sequence);
         if(sequence.hasClass('classifications-field')){
            init_classifications_field(true)
         }
    });
});