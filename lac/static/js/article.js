

function normalize_articles(){
	var articles = $('.article-content');
	for(var i=0; i<= articles.length; i++){
		var article = $(articles[i]);
		var article_image = $(article.find('div.article-picture').first());
		if(article_image.length>0){
			var first_article = $(article.find('div.article-node.article-body').first());
			if(first_article.length>0){
				article_image.insertBefore(first_article);
				setTimeout(function() {
                   normalize_footers();
                 }, 50);
				normalize_footers()
			};
	    }
	}
}


$(document).ready(function(){
  normalize_articles();
});