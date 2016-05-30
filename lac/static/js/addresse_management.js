
function be_update_form(form){
      var select_field = $($(form).find('.address-department-entry').first());
      var departement =  $(select_field.parents('.form-group').first());
      var label = departement.find('.control-label').first();
      label.removeClass('required');
      departement.addClass('hide-bloc');
      if(select_field.val() != null && select_field.val() != ''){
        var event = jQuery.Event("change");
        event.dt_update = true;
        select_field.val("").trigger(event);
      }
}

function fr_update_form(form){
      var departement =  $($($(form).find('.address-department-entry').first()).parents('.form-group').first());
      var label = departement.find('.control-label').first();
      label.addClass('required')
      departement.removeClass('hide-bloc')
}

var update_address_form_ops = {
    'be': be_update_form,
    'belgique': be_update_form,
    'fr': fr_update_form,
    'france': fr_update_form,
}


function get_fields_address(element, value, url){
    var modal = value;
    var target = $($(element).parents('.address-well').first());
    var params = get_context_data('#'+$(element).attr('id'));
    params['op'] = 'cities_synchronizing';
    params[$(element).attr('name')] = value;
    $.getJSON(url,params, function(data) {
        if(data){
          for (key in data){
              var select_field = $(target.find("select[name=\'"+key+"\']").first());
              if($(select_field.find("option[value=\""+data[key]+"\"]")).length == 0){
                  select_field.append("<option value=\""+data[key]+"\">"+data[key]+"</option>");
              };
              select_field.data('item_added', true);
              select_field.select2('val', data[key])
          }
        }
    });
};


function init_addresses_field(event){
    if (!event.dt_update){
      var select_tag = $(event.target);
      if(select_tag.data('item_added') == undefined || !select_tag.data('item_added')){
          var find_url = $(this).data('url');
          var urlsplit = find_url.split("?");
          var url = urlsplit[0];
          var value = $(this).val();
          get_fields_address($(this), value, url);
        }else{
          select_tag.data('item_added', false);
        }
    }
};

function update_form_element(element){
  var $this = $(element);
  var value = $this.val().toLowerCase();
  if (value in update_address_form_ops){
    var update_op = update_address_form_ops[value];
    var form = $($this.parents('.address-well').first());
    update_op(form);
  }
}


function update_form(event){
  update_form_element(this)
}


function init_addresses_form(){
  var countries = $('.address-country-entry');
  for(var i=0; i<countries.length; i++){
    var country = $(countries[i])
    update_form_element(country)
  }
}


$(document).ready(function(){

   $(document).on('change', '.address-entry', init_addresses_field);

   $(document).on('change', '.address-country-entry', update_form);
   
   init_addresses_form();

});