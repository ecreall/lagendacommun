function height_of(e){
  var height = $(e).height();
  if (height == null){
    return 0
  };
  return height
}

function map(f, l){
    var result = [];
    for(var i = 0; i<= l.length; i++){
        result.push(f(l[i]))
    };
    return result
}

function api_filter(f, l){
    var result = [];
    for(var i = 0; i<= l.length; i++){
        var element = l[i]; 
        if(f(element)){
            result.push(element)
        }
    };
    return result
}

function max(l){
  return l.sort().reverse()[0]
}

function min(l){
  return l.sort()[0]
}

function loading_progress(){
    $('img.lac-loading-indicator').removeClass('hide-bloc');
}

function finish_progress(){
    $('img.lac-loading-indicator').addClass('hide-bloc');
}

function collapse_current_collpsein(){
  var current_btn = $(this);
  var btns = $('.navbar-toggle.collapsed');
  for(var i = 0; i<= btns.length; i++){
      var btn = $(btns[i]);
      if (btn != current_btn){
        $(btn.data('target')).collapse('hide');
      }
  }

}

function set_visited(){
    $.cookie('visited', 'true', {path: '/',  expires: 1});
}

function disable_cookies_alert(){
  $('.navbar-cookies').css('display', 'none')
}

function accept_cookies(){  
    disable_cookies_alert();
    $.cookie('accept_cookies', 'true', {path: '/',  expires: 360*20});
}

function init_cookies_alert(){
  var accept_cookies = $.cookie('accept_cookies');
  if ( accept_cookies != undefined && Boolean(accept_cookies)){
    disable_cookies_alert()
  }
}

// function set_url_metaproperty(){
//   var target = $($('meta[property="og:url"]').first());
//   if (target.length>0){
//     var url_toshorten = target.attr('content');
//     var url = target.data('shortner_url');
//     var params = {'url': url_toshorten};
//     $.getJSON(url,params, function(data) {
//         if(data['short_url']){
//           target.attr('content', data['short_url']);
//         }
//      });
//   }
// }


function get_shortned_url(){
  var button = $(this);
  var url_toshorten = button.data('url');
  var url = button.data('shortner_url');
  var target = $(button.data('modal'));
  var params = {'url': url_toshorten};
  $.post(url,params, function(data) {
        if(data['short_url']){
          var shortned_link = data['short_url'];
          var link = $(target.find('.modal-body h4 a').first());
          link.attr('href', shortned_link).text(shortned_link);
          target.modal('show');
        }
     }, 'json');
}

//TODO to multiple result
function initscroll(){
  $('.results').infinitescroll('destroy');
  $('.results').infinitescroll({
    behavior: 'local',
    bufferPx: 0,
    binder: $('.result-scroll'),
    navSelector  : ".results .batch",
                   // selector for the paged navigation (it will be hidden)
    nextSelector : ".results .pager .next",
                   // selector for the NEXT link (to page 2)
    itemSelector : ".results .result-container",
                   // selector for all items you'll retrieve
    pathParse: function(path, next_page) {
       var new_path = path;
       var filter = $('#filter-'+$('.results').first().attr('id'));
       var data_get = '';
       if (filter.length>0){
            var form = $($(filter).find('form').first());
            var filter_container = $(form.parents('.filter-container'));
            var progress = filter_container.find('img.loading-indicator');
            var filter_btn = $(filter_container.find('.filter-btn').first());
            var data_get = $(form).serialize();
            data_get += '&'+'op=filter_result';
            var target = $($('.pontus-main .panel-body').first());
            var target_title = $($('.pontus-main .panel-heading').first());
            var url = filter_btn.data('url');
            var filter_source = filter_btn.data('filter_source');
            if (filter_source !== ''){
              data_get += '&'+'filter_source='+filter_source;
            }
            data_get += '&'+'filter_result=true';
            data_get += '&'+'scroll=true';
            data_get += '&'+ data_get;
      };
// ["http://0.0.0.0:6543/@@seemyideas?batch_num=", "&batch_size=1&action_uid=-4657697968224339750"]
// substanced Batch starts at 0, not 1
       var f = function(currPage) {
          var next_path = $($($('.results .result-container').parents('div').first()).find('.result-container').last()).data('nex_url')
          return next_path +'&'+ data_get;
       };
       return f;
    },
    loading: {
      finishedMsg: '<span class="label label-warning">'+ lac_translate("No more item.")+"</span>",
      img: window.location.protocol + "//" + window.location.host + "/lacstatic/images/loader.gif",
      msgText: "",
    }
  }, 
  function(arrayOfNewElems){
          init_cultural_event_schedules()
  });

};


function init_result_scroll(){
  var result_scrolls = $('.result-scroll');
  for(var i = 0; i<= result_scrolls.length; i++){
    var result_scroll = $(result_scrolls[i]);
    var overflow = result_scroll.data('overflow');
    var over = 150;
    if (overflow){
      over = 0;
    }
    var last_child = $(result_scroll.find('.result-item').last());
    if (last_child.length > 0){
        var top = last_child.offset().top - result_scroll.offset().top  + last_child.height() + over;
        if (top < 1600){
         result_scroll.height(top);
        }
    }else{
         result_scroll.height(100);
    }
 }
};

function activate_detail(event){
  var explanation = $($(this).parents('dd').find('.venue-detail').first());
  if($(this).hasClass('closed')){
    explanation.slideDown( );
    explanation.removeClass('hide-bloc');
    $(this).removeClass('closed');
    $(this).addClass('open');
    $(this).removeClass('glyphicon-info-sign');
    $(this).addClass('glyphicon-minus-sign');
  }else{
    explanation.slideUp( );
    explanation.addClass('hide-bloc');
    $(this).removeClass('open');
    $(this).addClass('closed');
    $(this).addClass('glyphicon-info-sign');
    $(this).removeClass('glyphicon-minus-sign');
  }
};


$.fn.isBound = function() {
    var data = $._data(this[0], "events");

    if (data === undefined || data.length === 0) {
        return false;
    }

    return data['mouseover'].length>=1 && data['mouseout'].length>=1;
};

function find_entities_by_artist(){
   var params = {artist: $(this).data('id'),
                 op: 'find_entities_by_artist'};
   var target = $($('.pontus-main').first());
   var url = $(this).data('url');
   $.getJSON(url,params, function(data) {
      if(data['body']){
        target.removeClass('home');
          var result = data['body'];
                  target.html(result);
                  init_result_search();
      }
   });
}

function normalize_footer(footer){
      var img = $(footer.find('img').first());
      if(img.length>0 && ! img.isBound()){
          img.hover(function(){
            var img = $(this);
            var footer = (img.parents('div.footer-picture').first());
            var message = $(footer.find('div.footer-message').first());
            var img_position = img.position();
            message.css('width', img.width()+'px');
            message.css('top', (img_position.top+img.height()-message.height()+5)+'px');
            var margin_left = parseInt(img.css('margin-left').split('px')[0])+5;
            message.css('left', (img_position.left+margin_left)+'px');
            message.css('display', 'block');
          }, function(){
            var footer = ($(this).parents('div.footer-picture').first());
            var message = $(footer.find('div.footer-message').first());
            message.css('display', 'none');
          });
      }
}

function normalize_footers(){
  var footers = $('div.footer-picture');
  for(var i = 0; i<= footers.length; i++){
       var footer = footers[i];
       normalize_footer($(footer));
  }
}


function init_result_search(){
    init_result_scroll();
    normalize_footers();
    init_cultural_event_schedules();
}


function resize_slick(){
  var schedules = $(this).find('.schedules-carousel.build');
  try{
      $(schedules).slick('setPosition');
  }catch(err){
      $(schedules).resize();
  }
  $(this).off('shown.bs.collapse', resize_slick);
}


function init_cultural_event_schedules(){
  try{
    $('.schedules-carousel.build:not(.slick-initialized)').slick({
          dots: false,
          slidesToShow: 2,
          slidesToScroll: 2,
          autoplay: false,
          responsive: [
              {
                breakpoint: 1024,
                settings: {
                  slidesToShow: 3,
                  slidesToScroll: 3,
                }
              },
              {
                breakpoint: 600,
                settings: {
                  slidesToShow: 2,
                  slidesToScroll: 2
                }
              },
              {
                breakpoint: 480,
                settings: {
                  slidesToShow: 1,
                  slidesToScroll: 1
                }
              }
              // You can unslick at a given breakpoint now by adding:
              // settings: "unslick"
              // instead of a settings object
           ]
         });
    $('.panel-collapse').off('shown.bs.collapse', resize_slick);
    $('.panel-collapse').on('shown.bs.collapse', resize_slick);
    }
  catch(err) {
  }
}


function init_home(){
  var folders = $('.home:not(.folder-bloc)').find('.smart-folder-well:not(.home-initialized)');
  var max_height = max(map(height_of, folders));
  folders.height(max_height);
  folders.addClass('home-initialized');
}

function more_content(elements, isvertical){
    try{
      elements.slick({
        vertical: isvertical,
        centerMode: true,
        dots: false,
        slidesToShow: 3,
        slidesToScroll: 3,
        autoplay: true,
        autoplaySpeed: 8000,
        infinite: true,
        responsive: [
            {
              breakpoint: 1024,
              settings: {
                slidesToShow: 3,
                slidesToScroll: 3,
                infinite: true,
                dots: false
              }
            },
            {
              breakpoint: 600,
              settings: {
                slidesToShow: 2,
                slidesToScroll: 2
              }
            },
            {
              breakpoint: 480,
              settings: {
                slidesToShow: 1,
                slidesToScroll: 1
              }
            }
            // You can unslick at a given breakpoint now by adding:
            // settings: "unslick"
            // instead of a settings object
         ]
       });
  }
  catch(err) {
  }

}

function home_carousel(){
 try{
      $('.home-carousel').slick({
        centerMode: true,
        dots: false,
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 8000,
        infinite: true,
        fade: true,
        cssEase: 'linear'
       });
  }
  catch(err) {
  }
}

function populate_map(form){
  var populate_func = function populate(map){
      var wrapper = $(form.parents('#wrapper').first());
      var button = form.find('button').last();
      var url = map.data('url');
      var values = form.serialize()+'&'+button.val()+'='+button.val();
      button.addClass('disabled')
      loading_progress();
      $.post(url, values, function(data) {
          if(data){
            map.trigger('update_locations', data)
            finish_progress();
            button.removeClass('disabled')
          }
       });
    }
  return populate_func
}

function update_locations(event){
  var form = $(this);
  var wrapper = $(form.parents('#wrapper').first());
  var menu_btn = $(wrapper.find('.map-form-menu').first());
  var map = $(wrapper.find('#map_canvas').first());
  var populate_func = populate_map($(this))
  menu_btn.trigger('click')
  if(!map.data('initialized')){
     init_map('#map_canvas', populate_func)
     map.data('initialized', true)
  }else{
      populate_func(map)
  }
  event.preventDefault();
}

function open_close_map_menu(event){
  var $this = $(this);
  var map_form = $($this.parents('.map-form').first());
  event.preventDefault();
  var target = $($this.data('target'));
  if($this.hasClass('active')){
      target.slideUp();
      $this.removeClass('active')
      map_form.removeClass('active')
  }else{
    target.slideDown();
    $this.addClass('active')
    map_form.addClass('active')
  }
}

function show_route_info(event, coordinates){
    var root_url = "https://www.google.com/maps/dir/"+coordinates.origin+"/"+coordinates.destination
    $('.route-info>a').attr('href', root_url)
    $('.route-info').removeClass("hide-bloc")
}

function close_route_info(){
  var $this = $(this);
  $($this.parents('.route-info').first()).addClass("hide-bloc")
}

function check_login(event){
  // event.currentTarget.action = event.currentTarget.action.replace('http://www', 'https://ssl').replace('http://', 'https://ssl.')
  // event.currentTarget.baseURI = event.currentTarget.baseURI.replace('http://www', 'https://ssl').replace('http://', 'https://ssl.')
  var form = $(this);
  var button = form.find('.login-form-submit').last();
  var checked = button.data('checked');
  if(!checked){
    var url = button.data('check_url');
    var values = form.serialize();
    button.addClass('disabled')
    loading_progress();
    $.post(url, values, function(data) {
        if(data.check){
          button.data('checked', true)
          $('.form-signin-alert').addClass('hide-bloc')
          button.trigger('click')
        }else{
          $('.form-signin-alert').removeClass('hide-bloc')
          button.data('checked', false)
          button.removeClass('disabled')
          finish_progress();
        }
     });
    event.preventDefault();
  }
}

function select2_ajax_search(select, val_in, val_out){
   var id = 'select2-'+$(select).attr('id')+'-results';
   var field = $($('#'+id).parents('.select2-container').first().find('.select2-search__field').first());
   if(!val_in && !val_out){
     val_in = val_out = field.val()
   }
   if(field.length != 0){
     field.val(val_in);
     field.trigger('keyup');
     field.val(val_out);
   }
}


$(document).ready(function(){
  set_visited();
  
  init_cookies_alert();
  $('.accept-cookies-btn').on('click', accept_cookies);

  $('.hidden-js').css('display', 'none');

  if (!window.matchMedia('(max-width: 991px)').matches) {
    $('li.menu-item').hover(function(){
        var submenu = $($(this).find('ul').first());
        submenu.show( "fast" );
        $(this).addClass('open');
        if ($(this).hasClass('submenu-item')){
          var width = $(this).width();
          submenu.css('left', width);
          submenu.css('top', '-3px');
           
        }
    }, function(){
        var submenu = $($(this).find('ul').first());
        submenu.hide( "fast" );
        $(this).removeClass('open');
    });
  }

  $( window ).resize(function(event){
    if(!$(event.target).hasClass('schedules-carousel')){
     init_result_search();
     }
  });

  //set_url_metaproperty();

  $('.shorten-url.btn').on('click', get_shortned_url);

  //init_result_scroll();

  $('.venue-detail-btn').on('click', activate_detail);
   
  $($('.search-item').parents('.panel-group').first()).find('.panel-collapse').on('shown.bs.collapse', function () {
      init_result_search();
  });

  $('.panel-collapse.collapse .results').attr('class', 'results-collapse');

  $('.panel-collapse').on('hidden.bs.collapse', function () {
      $(this).find('.result-collapse').attr('class', 'results-collapse');
      $('.results').attr('infinitescroll', null);
  });

  $('.panel-collapse').on('shown.bs.collapse', function () {
      $(this).find('.results-collapse').attr('class', 'results');
      init_result_search();
    });

  $('nav a nav-control').on('click', function(){
      $(".navbar-toggle").click();
  });


  //$('.artist-item-title').on('click', find_entities_by_artist);

  $(".ordered-folder-seq select").prop("disabled", true);
  $(".ordered-folder-seq").parents('form').on('submit', function(){
    $(".ordered-folder-seq select").prop("disabled", false);
  });

  $(".navbar-toggle.collapsed").on('click', collapse_current_collpsein);

  $('.menu-item.dropdown').on('hide.bs.dropdown', function () {
    var toggle = $($(this).find('span.dropdown-toggle-action').first());
    toggle.removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
  }).on('show.bs.dropdown', function () {
    var toggle = $($(this).find('span.dropdown-toggle-action').first());
    toggle.removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
  });

  $('.menu-item.dropdown').on('click', function(event){
    if (!$(event.target).hasClass('dropdown-toggle-action')){
        event.stopPropagation()
    }
  });

  $('.alert-block:not(.off)').hover(function(){
        var $this = $(this);
        var url = $this.data('url');
        var alert_content = $($this.find('.alerts-content').first());
        var target = $(alert_content.find('.content').first());
        alert_content.find('.loading-indicator').removeClass('hide-bloc')
        alert_content.removeClass('hide-bloc');
        $.getJSON(url,{}, function(data) {
          if(data['body']){
            target.html(data['body']);
            alert_content.find('.loading-indicator').addClass('hide-bloc')
          }
        });

    }, function(){
        var $this = $(this);
        $this.find('.alerts-content').addClass('hide-bloc')
    });


  initscroll();

  init_result_search();
  
  more_content($('.more-content-carousel.verticla'), true);
  more_content($('.more-content-carousel:not(.vertical)'), false);
  home_carousel();
  init_home();
  $('#collapse-map').on('shown.bs.collapse', function () {
    $('.geo-search-form form').trigger('submit')
  })
  $(document).on('submit','.geo-search-form form', update_locations);
  $(document).on('submit', '.form-signin-principal', check_login);
  $('.map-form-menu').on('click', open_close_map_menu);
 $('#map_canvas').on('route_displayed', show_route_info)
 $('.route-info .close').on('click', close_route_info)

  $(document).on('select2:open', '.select2-preload', function(event){
     select2_ajax_search(this, " ", "")
   });

});

