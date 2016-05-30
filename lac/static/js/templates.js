
var venue_create_message = lac_translate("msg_create_venue");

function venue_item_template(item){
   var markup = '<div class="option-container clearfix">'+
                  '<div clas="col-sm-12">' +
                     '<div class="clearfix">' +
                        '<div class="col-sm-2">' + item.text + '</div>';
    if (item.city) {
      markup += '<div class="col-sm-3"><strong>' + item.city + '</strong></div>';
      markup += '<div class="col-sm-6">'
    }else{
      markup += '<div class="col-sm-10">'
    }
   if (item.description) {
      markup += item.description;
    }
    else{
      markup +='<div class="create-message-container alert alert-warning"><span class="glyphicon glyphicon-warning-sign"></span> '+venue_create_message+'</div>';
    }
   markup += '</div></div></div></div>';
   return markup
};


var artist_create_message = lac_translate("msg_create_artist");

function artist_item_template(item){
   var markup = '<div class="option-container clearfix">'+
                  '<div clas="col-sm-12">' +
                     '<div class="clearfix">' +
                        '<div class="col-sm-5">' + item.text + '</div>'+
                        '<div class="col-sm-7">';
   if (item.description) {
      markup += item.description;
    }
    else{
      markup +='<div class="create-message-container alert alert-warning"><span class="glyphicon glyphicon-warning-sign"></span> '+artist_create_message+'</div>';
    }
   markup += '</div></div></div></div>';
   return markup
};

function formatArtist (artist) {
  if (!artist.id) { return artist.text; }
  return '<span>'+ artist.text + '<span data-artist_id ="'+artist.id+'" class="artist-edit glyphicon glyphicon-pencil"></span></span>'
};

function formatDirector (artist) {
  if (!artist.id) { return artist.text; }
  return '<span>'+ artist.text + ' <span data-director_id ="'+artist.id+'" class="director-edit glyphicon glyphicon-pencil"></span></span>'
    
};


function formatReview(item){
  var markup = '<div>';
  if (item.icon) {
      markup += '<span class="'+ item.icon +'"></span>';
  };
  markup += ' ' + item.text;
  markup += '</div>';
  return markup
};


function formatLabel(item){
  var markup = '<div>';
  if(item.img){
      markup += '<img height="15px" src=\"'+item.img+'\" class="img-label"> ';
  }
  markup += item.text+'</div>';
  return markup
};



try {
    select2_ajax_templates['venue_item_template'] = venue_item_template;
    select2_ajax_templates['artist_item_template'] = artist_item_template;
    select2_ajax_templates['formatArtist'] = formatArtist;
    select2_ajax_templates['formatDirector'] = formatDirector;
    select2_ajax_templates['formatReview'] = formatReview;
    select2_ajax_templates['formatLabel'] = formatLabel;
}
catch(err) {
}