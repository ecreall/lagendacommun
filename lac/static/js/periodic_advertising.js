var settings_format = {
    'full_page':{
        float: 'none',
        width: '100%',
        height: '100%',
        margin: '0' 
    },
    'horizontal_half_page':{
        float: 'none',
        width: '100%',
        height: '50%',
        margin: '0' 
    },
    'vertical_half_page':{
        float: 'page',
        width: '50%',
        height: '100%',
        margin: '0' 
    },
    'vertical_quarter_page':{
        float: 'page',
        width: '25%',
        height: '100%',
        margin: '0' 
    },
    'horizontal_quarter_page':{
        float: 'none',
        width: '100%',
        height: '25%',
        margin: '0' 
    },
    'eighth_page':{
        float: 'none',
        width: '100%',
        height: '12.5%',
        margin: '0' 
    },
    'sixteenth_page':{
        float: 'none',
        width: '100%',
        height: '6.25%',
        margin: '0' 
    },
};

var settings_position = {
    'double_central': {
       'one_page': false,
       'page_1': true,
       'page_2': true
    },
    'front_cover': {
       'one_page': true,
       'page_1': true,
    },
    'page_2': {
       'one_page': false,
       'page_1': true
    },
    'page_3': {
       'one_page': false,
       'page_2': true
    },
    'back_cover': {
       'one_page': true,
       'page_1': true,
    },
};

function get_settings(format, position){
    var position_set = settings_position[position];
    if(!position_set){
      return {}
    };
    var format_set = settings_format[format];
    var format_set_page1 = $.extend({}, format_set);
    var format_set_page2 = $.extend({}, format_set);
    position_set['pages'] = {};
    if (position_set.page_1){
       if(format_set_page1.float && format_set_page1.float == 'page'){
         format_set_page1.float = 'none'    
       };
       position_set.pages['page_1'] = format_set_page1
    }

    if (position_set.page_2){
       if(format_set_page2.float && format_set_page2.float == 'page'){
         format_set_page2.float = 'right'    
       };
       position_set.pages['page_2'] = format_set_page2
    }

    return position_set
}

function get_periodic_preview(format, position){
    settings = get_settings(format, position)
    var position_1 = "";
    var position_2 = "";
    if(settings.page_1){
        position_1 = "<div class=\"position\""+
                      "style=\"width: ${page_1_width};"+
                              "float: ${page_1_float};"+
                              "height: ${page_1_height};"+
                              "margin-top: ${page_1_margin}\"></div>";
    };
    if(settings.page_2 && !settings.one_page ){
        position_2 = "<div class=\"position\""+
                      "style=\"width: ${page_2_width};"+
                              "float: ${page_2_float};"+
                              "height: ${page_2_height};"+
                              "margin-top: ${page_2_margin}\"></div>";
    }; 
    var prototype = "";
    if(settings.one_page){
        prototype = "<div class=\"periodic-preview one-page\">"+
                      "<div class=\"page page-1\">"+
                          position_1+
                      "</div></div>";
        if(position_1 != ""){
            prototype = prototype.replace('${page_1_width}', settings.pages.page_1.width)
                         .replace('${page_1_float}', settings.pages.page_1.float)
                         .replace('${page_1_height}', settings.pages.page_1.height)
                         .replace('${page_1_margin}', settings.pages.page_1.margin)
        }
    }else{
        prototype = "<div class=\"periodic-preview double-page\">"+
                      "<div class=\"page page-1\">"+
                          position_1+
                      "</div>"+
                      "<div class=\"page page-2\">"+
                          position_2+
                      "</div></div>";
        if(position_1 !== ""){
            prototype = prototype.replace('${page_1_width}', settings.pages.page_1.width)
                         .replace('${page_1_float}', settings.pages.page_1.float)
                         .replace('${page_1_height}', settings.pages.page_1.height)
                         .replace('${page_1_margin}', settings.pages.page_1.margin)
        }
        if(position_2 !== ""){
            prototype = prototype.replace('${page_2_width}', settings.pages.page_2.width)
                     .replace('${page_2_float}', settings.pages.page_2.float)
                     .replace('${page_2_height}', settings.pages.page_2.height)
                     .replace('${page_2_margin}', settings.pages.page_2.margin)
        }
    };
    return prototype

};

function synchronize_preview(){
      var form = $($(this).parents('form').first());
      var old_preview = $(form.find('.periodic-preview').first());
      if(old_preview.length>0){
        old_preview.remove();
      }
      var input_position = $(form.find('.periodic-position').first());
      var input_format = $(form.find('.periodic-format').first());
      var format_form_group = $(input_format.parents('.form-group').first());
      if (input_position.val() !=="" && input_format.val() !== ""){
          format_form_group.after(get_periodic_preview(input_format.val(), input_position.val()));
      }else{
          format_form_group.after(get_periodic_preview());        
      }
};

function add_preview(){
    var inputs = $('.periodic-position');
    for(var i=0; i<inputs.length; i++){
      var input_position = $(inputs[i]);
      var form = $(input_position.parents('form').first());
      var input_format = $(form.find('.periodic-format').first());
      var format_form_group = $(input_format.parents('.form-group').first());
      var position_form_group = $(input_position.parents('.form-group').first());
      format_form_group.css('width', '70%');
      position_form_group.css('width', '70%');
      if (input_position.val() !=="" && input_format.val() !== ""){
          format_form_group.after(get_periodic_preview(input_format.val(), input_position.val()));
      }else{
          format_form_group.after(get_periodic_preview());        
      }
    }
};

$(document).ready(function(){

  add_preview();

  $(".periodic-setting").on('change', synchronize_preview);
});
    