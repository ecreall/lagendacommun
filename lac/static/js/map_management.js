
function submit_coordinates(element, location){
    var url = $(element).data('url');
    var data_get = {
        coordinates: location.lat()+','+location.lng(),
        address_id: $(element).data('address_title'),
        context_id: $(element).data('context_oid'),
        op: $(element).data('sync_operation')
    };
    $.get(url, data_get, function(data){});
};


function maploader(element){
    var map;
    var marker;
    var coordinatesmap = $($(element).find('#coordinatesmap'));
    var use_coordinates = coordinatesmap.length==1;
    var map_element = $(element).find('#map').first();
    var no_map_element = $(element).find('#nomap').first();
    var addressmap =  $(element).find('#addressmap').first();
    var address = addressmap.val();

   function mapload() {
        if(use_coordinates){
            coordinates = coordinatesmap.val();
            var latitude = parseFloat(coordinates.split(',')[0]);
            var longitude = parseFloat(coordinates.split(',')[1]);
            var latlng = new google.maps.LatLng(latitude, longitude);
        }
        else{
            var latlng = new google.maps.LatLng(34, 0);
        }

        map = new google.maps.Map(
                map_element[0], {
                  center: latlng,
                  zoom: 16,
                  mapTypeId: google.maps.MapTypeId.ROADMAP
                });

        if(use_coordinates){
            var marqueur = new google.maps.Marker({
                position: latlng,
                map: map
            });
        google.maps.event.addListener(marqueur, "click", function() {
                window.open('http://maps.google.fr/maps?f=q&hl=fr&q= ' + address);
        });
        } else {
            findAddressLocation(addressmap.val());
        }

    }

    //
    function addAddressToMap(result, status) {
        /* addAddressToMap() is called when the geocoder returns an
         * answer. It adds a marker to the map
         * showing the nicely formatted version of the address.
         */
        if (status != google.maps.GeocoderStatus.OK) {
            no_map_element.css('display', 'block');
            map_element.css('display', 'none');
        } else {
            no_map_element.css('display', 'none');
            map_element.css('display', 'block');
            map.fitBounds(result[0].geometry.viewport);
            var marker_title = result[0].formatted_address + "\nDétails, itinéraire et impression : cliquez sur la puce";
            if (marker) {
                marker.setPosition(result[0].geometry.location);
                marker.setTitle(marker_title);
            } else {
                marker = new google.maps.Marker({
                  position: result[0].geometry.location,
                  title: marker_title,
                  map: map
                });
            }
            google.maps.event.addListener(marker, "click", function() {
                window.open('http://maps.google.fr/maps?f=q&hl=fr&q= ' + address);
            });

            if(!use_coordinates){
                submit_coordinates(element, result[0].geometry.location);
            }
        }
    }

    // findLocation() is used to enter the sample addresses into the form.
    function findAddressLocation(address) {
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({address: address}, addAddressToMap);
    }

    mapload();
}


$(document).ready(function(){
    var map_containers = $('.map-container');
    for(var i = 0; i<map_containers.length; i++){
        maploader(map_containers[i])
    };
});