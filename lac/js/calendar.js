require('jquery.calendario');

$(window).load(function(){
      var $wrapper = $( '#custom-inner' ),
        $calendar = $( '#calendar' );
      if($calendar.length>=1){
	      var cal = $calendar.calendario({
				      onDayClick : function( $el, $contentEl, dateProperties) {
				      	  $('html, body').animate({scrollTop : 0},800);
				      	  $('.selected-day').removeClass('selected-day');
				      	  $el.addClass('selected-day');
				      	  loading_progress();
				      	  var params = {day: parseInt(dateProperties.day),
				      	                month: dateProperties.month,
				      	                year: dateProperties.year,
				      	                op: 'find_cultural_event'};
				      	  var target = $($('.pontus-main').first());
				      	  var url = $calendar.data('url');
					     $.getJSON(url,params, function(data) {
					        if(data['body']){
					        	target.removeClass('home');
					            var result = data['body'];
	                            target.html(result);
	                            init_result_search()

					        }
					       finish_progress();
					     });

				      },
				      displayWeekAbbr : true,
				      weeks : [ 'Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi' ],
					  weekabbrs : [ 'Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam' ],
					  months : [ 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
					  monthabbrs : [ 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jui', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc' ],
	      		} ),
	      	$month = $( '#custom-month' ).html( cal.getMonthName() ),
	      	$year = $( '#custom-year' ).html( cal.getYear() );

	      	$( '#custom-next' ).on( 'click', function() {
	      			cal.gotoNextMonth( updateMonthYear );
	      		});
	      	$( '#custom-prev' ).on( 'click', function() {
	      		cal.gotoPreviousMonth( updateMonthYear );
	      		} );


	      function updateMonthYear() {
	      		$month.html( cal.getMonthName() );
	      		$year.html( cal.getYear() );
	      	}
      }

});

