function is_empty_node(element){
  var element_copy = element.clone();
  $(element_copy.find('button.clear-style, button.newparagraph-style')).remove();
  var html = element_copy.html();
  if(html=='&nbsp;' || 
       html==" " || 
       html=="" || 
       html=="<br>" || 
       html == "<br data-mce-bogus=\"1\">"){
        return true
    };
    return false

}

function remove_empty_node(body, elements){
  var parag = $(body.find(elements));
  for(var i=0; i < parag.length; i++){
    if(is_empty_node($(parag[i]))){
        $(parag[i]).remove()
    }
  }
};

node_to_remove = 'p, div.article-node'

function init_body(ed){
  ed.focus();
  var body = $(ed.getBody());
  $(body.find('.article-body')).hover(function(){$(this).addClass('on')},function(){$(this).removeClass('on')});
  $(body.find('.article-heading')).hover(function(){$(this).addClass('on')},function(){$(this).removeClass('on')})
  $(body.find('.lead-paragraph')).hover(function(){$(this).addClass('on')},function(){$(this).removeClass('on')});
  var clear_btn = "<button class=\"btn btn-xs btn-danger clear-style\">"+
                     "<span class=\"article-ico mce-i-removeformat\"></span> "+
                          lac_translate("Clear formatting")+"</button>";
  var newparagraph_btn = "<button class=\"btn btn-xs btn-primary newparagraph-style\">"+
                           "<span class=\"glyphicon glyphicon-plus-sign\"></span> "+
                               lac_translate("Insert a new paragraph")+"</button>";
  var article_nodes =  $(body.find('.article-node'));
  for(var i=0; i < article_nodes.length; i++){
    var node = $(article_nodes[i]);
    if($(node.find('.clear-style')).length == 0){
      node.prepend(clear_btn)
    };
    if($(node.find('.newparagraph-style')).length == 0){
      node.append(newparagraph_btn)
    }
  };
  $(body.find('.article-node button.clear-style')).unbind('click').bind('click', function(){
      var parent = $($(this).parents('.article-node').first());
      $(parent.find('button.clear-style, button.newparagraph-style')).remove();
      var html = parent.html();
      parent.replaceWith(html);
      remove_empty_node(body, node_to_remove);
      var last_p = $(body.find('p').last());
      ed.selection.select(last_p[0], true); // ed is the editor instance
      ed.selection.collapse(false);
      ed.fire('change');

  });
  $(body.find('.article-node button.newparagraph-style')).unbind('click').bind('click', function(){
      var parent = $($(this).parents('.article-node').first());
      parent.after("<p>"+lac_translate("Add the new text here")+"</p>");
      var new_p = $(parent.next());
      ed.selection.select(new_p[0], true);
      ed.selection.collapse(false);
      ed.fire('change');

  });

};

function add_style_article_node(ed, default_content, style_class){
      ed.focus();
      var node = $(ed.selection.getNode());
      var content = ed.selection.getContent();
      if (node.prop("tagName") != 'BODY'){
          content = node.prop('outerHTML');
      };
      if (content == ''){
          content = default_content;
      };
      var wraped_content = "<div class=\"article-node "+style_class+"\">"+content+"</div>";
      if (node.prop("tagName") == 'BODY'){
          ed.selection.setContent(wraped_content);
      }else{
          node.replaceWith(wraped_content);
      };
      var body = ed.getBody();
      remove_empty_node($(body), node_to_remove);
      var last_p = $($(body).find('p').last());
      ed.selection.select(last_p[0], true); // ed is the editor instance
      ed.selection.collapse(false);
      ed.fire('change');
};

function add_style_folder(ed, style_class){
      ed.focus();
      // Applying the specified format with the variable specified
      tinymce.activeEditor.formatter.register('folder_format', {inline : 'span', styles : {color : '%value'}});
      tinymce.activeEditor.formatter.apply('folder_format', {value : style_class.split(":")[1]});
      ed.fire('change');
};

function init_article_extension(ed, scripts){
    article_menu_style =  "background-image: linear-gradient(to bottom, #f0ad4e 0%, #eb9316 100%); background-repeat: repeat-x; border-color: #e38d13;";
    ed.on('init', function(e) {
          var menu_article_container = $($("i.article-menu").parents('div.mce-btn').first());
          menu_article_container.attr("style", article_menu_style);
          menu_article_container.hover(function(){
                  menu_article_container.css("background-image", "linear-gradient(to bottom, #eb9316 0%, #eb9316 100%)");
                }, function(){
                  menu_article_container.css("background-image", "linear-gradient(to bottom, #f0ad4e 0%, #eb9316 100%)");
            });
          var menu_article = $(menu_article_container.find('button').first());
          menu_article.prepend(lac_translate('Article style'));
          menu_article.attr("style", "color: white");
          $(ed.getBody()).find('button.clear-style, button.newparagraph-style').remove();
          init_body(ed);
          var head = $($(ed.getBody()).parents('html').first().find('head').first());
          for(var i=0; i<scripts.length; i++){
              head.append('<script src=\"'+scripts[i]+'\">');
          };
      });

    ed.on('change', function(e){
       init_body(ed);
       remove_empty_node($(ed.getBody()), 'div.article-node');
    });

};


function add_article_menu(ed, scripts){
    ed.addButton('styles_article', {
        title : lac_translate('Article style'),
        type: 'menubutton',
        icon: 'icon article-menu',
        menu: [
              {
                  text: lac_translate('Lead paragraph'),
                  onclick: function(){
                     add_style_article_node(ed, lac_translate('Lead paragraph'), 'lead-paragraph')
                  }
              },
              {
                  text: lac_translate('Article'),
                  onclick: function(){
                    add_style_article_node(ed, lac_translate('Article body'), 'article-body')
                  }
              },
              {
                  text: lac_translate('Heading'),
                  onclick: function(){
                    add_style_article_node(ed, lac_translate('Heading'), 'article-heading')
                  }
              }
          ]
    });
    init_article_extension(ed, scripts)
}


function init_style_folders_extension(ed){
    folders_menu_style =  "background-image: linear-gradient(to bottom, #337ab7 0px, #265a88 100%); background-repeat: repeat-x; border-color: gray;";
    ed.on('init', function(e) {
          var menu_article_container = $($("i.folders-menu").parents('div.mce-btn').first());
          menu_article_container.attr("style", folders_menu_style);
          menu_article_container.hover(function(){
                  menu_article_container.css("background-color", "#265a88");
                }, function(){
                  menu_article_container.css("background-image", "linear-gradient(to bottom, #337ab7 0px, #265a88 100%)");
            });
          var menu_article = $(menu_article_container.find('button').first());
          menu_article.prepend(lac_translate('Smart folders styles'));
          menu_article.attr("style", "color: white");
      });
};


var folder_styles = {};

function add_folders_menu(ed, folders){
    if(folders.length>0){
      var styles = {};
      var styles_folder = [];
       for(var i=0; i<folders.length; i++){
            folder_styles[folders[i].title] = folders[i].style;
            var style_function = function(){
              var sf = folder_styles[this._text];
              add_style_folder(ed, sf);
            };
            styles_folder = styles_folder.concat(
                {
                    text: folders[i].title,
                    onclick: style_function
                })
       }

      ed.addButton('styles_folders', {
          title : lac_translate('Smart folders styles'),
          type: 'menubutton',
          icon: 'icon folders-menu',
          menu: styles_folder
      });
      init_style_folders_extension(ed)
    }
}

function myFileBrowser(field_name, url, type, win) {

   // from http://andylangton.co.uk/blog/development/get-viewport-size-width-and-height-javascript
                var w = window,
                d = document,
                e = d.documentElement,
                g = d.getElementsByTagName('body')[0],
                x = w.innerWidth || e.clientWidth || g.clientWidth,
                y = w.innerHeight|| e.clientHeight|| g.clientHeight;
            var language = 'en';
            if (tinymce.settings.language == 'fr_FR'){
              language = 'fr';
            }
            var cmsURL = '@@filemanager_index?&field_name='+field_name+'&langCode='+language;

            if(type == 'image') {           
                cmsURL = cmsURL + "&type=images";
            }

            tinyMCE.activeEditor.windowManager.open({
                file : cmsURL,
                title : 'Filemanager',
                width : x * 0.8,
                height : y * 0.8,
                resizable : "yes",
                close_previous : "no"
            });
}