

function update_rule_data(element){
  	var selection = $(element);
  	var data = $(selection.parents('.allocation-rule-bloc').first().find('.allocation-rule-data').first());
  	if(selection.is(':checked')){
  		data.slideDown( );
  	}else{
        data.slideUp('fast');
  	}

}

function init_selection_rules(){
  var selections = $('.allocation-rule-selection');
  for(var i=0; i<selections.length; i++){
  	var selection = $(selections[i]);
  	update_rule_data(selection)
  }

};


$(document).ready(function(){
	init_selection_rules();
	$('.allocation-rule-selection').on('change', function(){update_rule_data(this)})
})