/**
 * MapIt
 *
 * @copyright	Copyright 2013, Dimitris Krestos
 * @license		Apache License, Version 2.0 (http://www.opensource.org/licenses/apache2.0.php)
 * @link			http://vdw.staytuned.gr
 * @version		v0.2.2
 */

/* Available options
 *
 * Map type: 	ROADMAP, SATELLITE, HYBRID, TERRAIN
 * Map styles: false, GRAYSCALE
 *
 */

	/* Sample html structure

	<div id='map_canvas'></div>

	*/

document.write('<script type="text/javascript" src="https://maps.google.com/maps/api/js?v=3.23" ></script>');
// document.write('<script type="text/javascript" src="https://github.com/ChadKillingsworth/geolocation-marker/releases/download/v2.0.4/geolocation-marker.js" ></script>');

var current_position = {
	latitude: 46.626695,
	longitude: 2.401473,
	content: 'Unknown location',
	zoom: 6
}

var activate_route = false;

function init_map(id, populate_func) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(get_init_position(id, populate_func),
    	                                     error_position(id, populate_func));
  } else {
    $(id).mapit($(id).data('options'));
    populate_func($(id))
  }
}

function get_init_position(id, populate_func){
	var func = function init_position(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                activate_route = true;
                current_position = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    content: 'Your location',
                    zoom: 10
                };
                $(id).mapit($(id).data('options'));
                populate_func($(id))
              };
	return func
}

function error_position(id, populate_func){
	$(id).mapit($(id).data('options'));
	populate_func($(id))
}


function create_markers(options, map){
    var infowindow = new google.maps.InfoWindow();
	var marker, i;
	var markers = {};
	var locations = {}
    $.each(options.locations, function( id, data ) {
		// Add Markers
		var position = new google.maps.LatLng(data.latitude, data.longitude);
		var location = data.latitude + '' + data.longitude;
		if (location in locations){
			var newLat = locations[location].position.lat()
			var newLng = locations[location].position.lng()
            if (locations[location].nb % 6 == 0){
            	newLat = position.lat()
            }else{
                newLng = newLng + (0.1 / 3000);
            }
            newLat = newLat + (0.1 / 3000);
            position = new google.maps.LatLng(newLat, newLng)
            locations[location] = {'position': position,
                                   'nb': locations[location].nb+1};
		}else{
		    locations[location] = {'position': position,
                                   'nb': 1};
		}
		marker = new google.maps.Marker({
			position: position,
			map: map,
			icon: new google.maps.MarkerImage(data.icon || options.marker.icon),
			title: data.title
		});

		// Create an array of the markers
		markers[id] = marker;
		// Init info for each marker
		google.maps.event.addListener(marker, 'click', (function(marker, id) {
			return function() {
				infowindow.setContent(data.content);
				infowindow.open(map, marker);
			}
		})(marker, id));

	});
    return markers
}


(function($, window, undefined) {
	"use strict";

	$.fn.mapit = function(options) {
		var defaults = {
			type: 'ROADMAP',
			styles: 'GRAYSCALE',
			marker: {
				latitude: current_position.latitude,
				longitude: current_position.longitude,
				icon: 'lacstatic/images/map/marker_red.png',
				title: 'France',
				content: current_position.content,
				open: false,
				center: true
			},
			zoom: current_position.zoom,
			scrollwheel: false,
			locations: {},
			origins: {},
			show_all: false
		};

		var options = $.extend(defaults, options);
		$(this).each(function() {
			var $this = $(this);

				// Init Map
				var directionsDisplay = new google.maps.DirectionsRenderer();

				var mapOptions = {
					scrollwheel: options.scrollwheel,
					scaleControl: false,
					center: options.marker.center ? new google.maps.LatLng(options.marker.latitude, options.marker.longitude) : new google.maps.LatLng(options.latitude, options.longitude),
					zoom: options.zoom,
					mapTypeId: eval('google.maps.MapTypeId.' + options.type)
				};
				var map = new google.maps.Map(document.getElementById($this.attr('id')), mapOptions);
				directionsDisplay.setMap(map);

				// Styles
				if (options.styles) {
					var GRAYSCALE_style = [{featureType:"all",elementType:"all",stylers:[{saturation: -100}]}];
					var MIDNIGHT_style	= [{featureType:'water',stylers:[{color:'#021019'}]},{featureType:'landscape',stylers:[{color:'#08304b'}]},{featureType:'poi',elementType:'geometry',stylers:[{color:'#0c4152'},{lightness:5}]},{featureType:'road.highway',elementType:'geometry.fill',stylers:[{color:'#000000'}]},{featureType:'road.highway',elementType:'geometry.stroke',stylers:[{color:'#0b434f'},{lightness:25}]},{featureType:'road.arterial',elementType:'geometry.fill',stylers:[{color:'#000000'}]},{featureType:'road.arterial',elementType:'geometry.stroke',stylers:[{color:'#0b3d51'},{lightness:16}]},{featureType:'road.local',elementType:'geometry',stylers:[{color:'#000000'}]},{elementType:'labels.text.fill',stylers:[{color:'#ffffff'}]},{elementType:'labels.text.stroke',stylers:[{color:'#000000'},{lightness:13}]},{featureType:'transit',stylers:[{color:'#146474'}]},{featureType:'administrative',elementType:'geometry.fill',stylers:[{color:'#000000'}]},{featureType:'administrative',elementType:'geometry.stroke',stylers:[{color:'#144b53'},{lightness:14},{weight:1.4}]}]
					var BLUE_style = [{featureType:'water',stylers:[{color:'#46bcec'},{visibility:'on'}]},{featureType:'landscape',stylers:[{color:'#f2f2f2'}]},{featureType:'road',stylers:[{saturation:-100},{lightness:45}]},{featureType:'road.highway',stylers:[{visibility:'simplified'}]},{featureType:'road.arterial',elementType:'labels.icon',stylers:[{visibility:'off'}]},{featureType:'administrative',elementType:'labels.text.fill',stylers:[{color:'#444444'}]},{featureType:'transit',stylers:[{visibility:'off'}]},{featureType:'poi',stylers:[{visibility:'off'}]}]
					var mapType = new google.maps.StyledMapType(eval(options.styles + '_style'), { name: options.styles });
					map.mapTypes.set(options.styles, mapType);
					map.setMapTypeId(options.styles);
				}
                if(activate_route){
					// Home Marker
					var home = new google.maps.Marker({
						map: map,
						position: new google.maps.LatLng(options.marker.latitude, options.marker.longitude),
						icon: new google.maps.MarkerImage(options.marker.icon),
						title: options.marker.title
					});

					// Add info on the home marker
					var info = new google.maps.InfoWindow({
						content: options.marker.content
					});

					// Open the info window immediately
					if (options.marker.open) {
						info.open(map, home);
					} else {
						google.maps.event.addListener(home, 'click', function() {
							info.open(map, home);
						});
					};
				}

				// Create Markers (locations)
				var markers = create_markers(options, map);
				var markers_array = $.map(markers, function(val, key) { return val; });
                var markerclusterer = new MarkerClusterer(map, markers_array, {minimumClusterSize: 5});
				// Directions
				var directionsService = new google.maps.DirectionsService();

				$this.on ('route', function(event, origin) {
					if(activate_route){
						var request = {
							origin: new google.maps.LatLng(options.marker.latitude, options.marker.longitude),
							destination: new google.maps.LatLng(options.locations[origin].latitude, options.locations[origin].longitude),
							travelMode: google.maps.TravelMode.DRIVING
						};
						directionsService.route(request, function(result, status) {
							if (status == google.maps.DirectionsStatus.OK) {
								directionsDisplay.setDirections(result);
							};
						});
						$this.trigger('route_displayed', {
							'origin': options.marker.latitude+","+options.marker.longitude,
							'destination': options.locations[origin].latitude+","+ options.locations[origin].longitude
						})
					}else{
                        $('.rout-map-btn').addClass('disabled');
					}
				});
                
                $this.on ('remove_route', function(event) {
                    directionsDisplay.setMap(null)
                    directionsDisplay.setMap(map)
                });

                $this.on ('update_locations', function(event, locations) {
                	$this.trigger('clear');
					$this.trigger('reset');
					markers = create_markers({'locations': locations}, map)
					markers_array = $.map(markers, function(val, key) { return val; });
					markerclusterer = new MarkerClusterer(map, markers_array, {minimumClusterSize: 5});
					options.locations = locations
					if (!options.show_all){
				       $this.trigger('hide_all');
				    }

				});

				// Hide Markers Once (helper)
				$this.on ('hide_all', function() {
					for (var id in options.locations){
						markers[id].setVisible(false);
					};
					markerclusterer.clearMarkers();
				});

                // Show Markers Per Category (helper)
				$this.on ('show_all', function(event) {
					$this.trigger('hide_all');
					$this.trigger('reset');

					// Set bounds
					var bounds = new google.maps.LatLngBounds();
					for (var id in options.locations){
						markers[id].setVisible(true);
						// Add markers to bounds
						bounds.extend(markers[id].position);
					};

					// Auto focus and center
					map.fitBounds(bounds);
				});

				// Show Markers Per Category (helper)
				$this.on ('show', function(event, category) {
					$this.trigger('hide_all');
					$this.trigger('reset');

					// Set bounds
					var bounds = new google.maps.LatLngBounds();
					for (var id in options.locations){
						if ($.inArray(category, options.locations[id].categories) >= 0) {
							markers[id].setVisible(true);
						};

						// Add markers to bounds
						bounds.extend(markers[id].position);
					};

					// Auto focus and center
					map.fitBounds(bounds);
				});

				// Hide Markers Per Category (helper)
				$this.on ('hide', function(event, category) {
					for (var id in options.locations){
						if ($.inArray(category, options.locations[id].categories) >= 0) {
							markers[id].setVisible(false);
						};
					};
				});

				// Clear Markers (helper)
				$this.on ('clear', function() {
					if (markers) {
						for(var id in markers){
							markers[id].setMap(null);
						};
					};
					markerclusterer.clearMarkers();
				});

				$this.on ('reset', function() {
					$this.trigger('remove_route');
					map.setCenter(new google.maps.LatLng(options.marker.latitude, options.marker.longitude), options.zoom);
				});

				// Hide all locations once
				if (!options.show_all){
				    $this.trigger('hide_all');
				}
		});
	};

	$(document).ready(function () { $('[data-toggle="mapit"]').mapit(); });

})(jQuery);