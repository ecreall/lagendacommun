
function selected_venues_btn_template(){
  return ('<span class="input-group-btn">' +
          '<button title=\"' + lac_translate('venue_history_msg_btn') + '\" type="button" class="btn btn-default history-activator venue-history-activator">' +
          '<input type="hidden" name="venue_history" value="false"></input> <i class="state-icon glyphicon glyphicon-unchecked"></i>'+
          ' <span class="glyphicon glyphicon-time">' +
         '</span></button></span>')
}


function contact_is_empty(schema){
  function filter_op(contact){
    for(var node in schema){
        var node_input = $(contact).find("input[name='"+node+"']").first();
        if($(node_input).val() != schema[node]){
              return false
        }
    }
    return true
    }

  return filter_op
}


function set_contact(contact, data){
  for(var node in data){
      var node_input = $(contact).find("input[name='"+node+"']").first();
      if(node_input.length>0){
          $(node_input).val(data[node])
      }
  }
}


function add_contacts(id, form, url){
  var params = {'id': id, 'op': 'get_venue_contacts'}
  $.getJSON(url,params, function(data) {
    if(data){
        var contacts = $(form.find('.deform-seq-item-container>.contact-well'));
        var contacts_to_replace = api_filter(contact_is_empty(data['schema']), contacts);
        if(contacts_to_replace.length>0){
           var contact = contacts_to_replace[0];
           set_contact(contact, data['data'])
        }

    }
  })
}

function get_venue_addresses(element, value, url){
    var btn = element;
    var modal = value;
    var target = $($(element).parents('.venue-block').first());
    var target_form = $(target.parents('form').first());
    var params = {};
    var op = 'venue_synchronizing';
    if(target.hasClass('cinema-block')){
      op = 'cinema_venue_synchronizing';
    };
    params['op'] = op;
    params['id'] = value;
    if($(element).parents('.add-venues-mode').length>=1){
      params['add_mode'] = true;
    };
    $.getJSON(url,params, function(data) {
        if(data['body']){
            var form = data['body'];
            var form_groups = $($(form).find('fieldset').first()).children('.form-group, .ajax-form');
            var mapping_start = $(target.find("input[name='__start__']").first());
            var new_venue_id = $($(form).find('fieldset').first()).children("input[name='id']");
            var new_venue_origin_oid = $($(form).find('fieldset').first()).children("input[name='origin_oid']");
            var venue_id = $(target.find("input[name='id']").first());
            var venue_origin_oid = $(target.find("input[name='origin_oid']").first());
            var target_form_groups = target.children('.form-group, .ajax-form');
            $(target_form_groups).remove();
            mapping_start.after(form_groups);
            if (new_venue_id.length>=1){
              if(venue_id.length>=1){venue_id.remove()};
              mapping_start.after(new_venue_id);
            }
            if (new_venue_origin_oid.length>=1){
              if(venue_origin_oid.length>=1){venue_origin_oid.remove()};
              mapping_start.after(new_venue_origin_oid);
            }
             target.show();
             try {
                  deform.processCallbacks();
              }
              catch(err) {};
              add_contacts(new_venue_id.val(), target_form, url)
              target.find('.venue-title').on('change', init_venue_title);
              target.find('.address-entry').on('change', init_addresses_field);
              var event = jQuery.Event( "item_reloaded" );
              target_form.trigger( event );
        }else{
            $(target.find("input[name='id']").first()).val('');
            $(target.find("input[name='origin_oid']").first()).val('');
        }
    });
};



function init_venue_title(){
        var find_url = $(this).data('url');
        var urlsplit = find_url.split("?");
        var url = urlsplit[0];
        var value = $(this).val();
        get_venue_addresses($(this), value, url);
};


function adapt_schedule_price(element){
   var item_price = $($($(element).parents('.schedule-well').first()).find('.item-price'));
   if($(element).attr('value') == 'Free admission') {
     if (!item_price.hasClass('hide-bloc')) {
         item_price.addClass('hide-bloc');
      };
   }else{
     if (item_price.hasClass('hide-bloc')) {
         item_price.removeClass('hide-bloc');
      }
   }
};


function init_schedule_price(elements){
   $(elements.find("input[type='radio']")).change(function() {
      if (this.checked){
         adapt_schedule_price(this)
      }
   });

   var ticket_type_inputs = $(elements.find("input[type='radio']:checked"));
   for (i=0; i<ticket_type_inputs.length; i++){
         var ticket_type_input = ticket_type_inputs[i];
         adapt_schedule_price(ticket_type_input)
   };

};

function ini_keywords_deletion(sequence){
     var min_len = parseInt($(sequence.find('.deform-insert-before').first()).attr('min_len'));
     var items = $(sequence.find('a.btn.deform-close-button'));
     items.css('display', 'none');
     if(items.length > min_len){
         var item = $(sequence.find('a.btn.deform-close-button').last());
         item.css('display', 'inline-block');
     }
};


function init_keyword_values(sequence){
     var level = parseInt($(sequence.find('.deform-insert-before').first()).attr('now_len'))-1;
     var level_data = $(sequence.find(".keyword-data span[data-level=\'"+level+"']").first());
     var values = level_data.data('values').split(',');
     var can_create = parseInt(level_data.data('can-create'));
     var select_field = $($(sequence.find('.deform-seq-item').last()).find('select.form-control').first());
     if (can_create == 0){
        select_field.select2({containerCssClass: 'form-control'})
     };
     $(sequence.find('.select2.select2-container')).css('width', '152px');
     for (i=0; i<values.length; i++){
        select_field.append("<option value=\""+values[i]+"\">"+values[i]+"</option>");
     };
};


function add_keyword(btn){
     var sequence = $($(btn).parents('.deform-seq').first());
     var add_item = deform.appendSequenceItem(btn);
     $(sequence.find('.select2.select2-container')).css('width', '152px');
     init_keyword_values(sequence);
     ini_keywords_deletion(sequence);
     return add_item
};

function remove_keyword(btn){
     var sequence = $($(btn).parents('.deform-seq').first());
     deform.removeSequenceItem(btn);
     ini_keywords_deletion(sequence);
};

$(document).ready(function(){

   $('.venue-title').on('change', init_venue_title);

   $(document).on('select2-started', '.venue-title', function(){
     var select2_parent = $($(this).parents('div.form-group').first());
     var selection =  $(select2_parent.find('.select2 > .selection').first())
     selection.addClass('input-group')
     selection.append(selected_venues_btn_template())
   });

   $(document).on('click', '.history-activator', function(){
      var val = $($(this).find('input').first()).val();
      if(val == 'true'){
       $($(this).find('input').first()).val('false');
      }else{
       $($(this).find('input').first()).val('true');
      }
   });
   $(document).on('click', '.venue-history-activator', function(){
      var $this = $(this)
      var select = $($this.parents('div.form-group').first().find('select'));
      select.select2('open')
      select2_ajax_search(select)
      var icon = $($this.find('i.state-icon').first());
      if(icon.hasClass('glyphicon-unchecked')){
        icon.removeClass('glyphicon-unchecked');
        icon.addClass('glyphicon-check')
        $this.addClass('active');
        $this.addClass('btn-warning');
        $this.removeClass('btn-default');
        
      }else{
        icon.removeClass('glyphicon-check');
        icon.addClass('glyphicon-unchecked');
        $this.removeClass('active')
        $this.removeClass('btn-warning');
        $this.addClass('btn-default');
      }
   });

   $('.ce-field-description').on('change', function(){
        var form = $($(this).parents('form').first());
        var description = $(form.find('.ce-field-description').first());
        var description_val = description.val();
        if (description_val != ""){
            var details_editor = null;
            for (editorId in tinyMCE.editors) {
                var orig_element = $(tinyMCE.get(editorId).getElement());
                if (orig_element.hasClass('ce-field-details')) {
                  details_editor = tinyMCE.get(editorId)
                }
              };
            if (details_editor != null &&
                details_editor.getContent() == ""){
              details_editor.setContent('<p>' + description_val + '</p>')
            }
        }
   });


   init_schedule_price($('.schedule-ticket-type'));

   $('form.deform').on('item_added', function(event){
         var item_added = $(event.element);
         item_added.find('.venue-title').on('change', init_venue_title);
         init_schedule_price($(item_added.find('.schedule-ticket-type')));
         var dates = $(item_added.find('.schedule-dates').first());
         if (dates.length>0){
             init_date_ical(dates)
         }
      });

});