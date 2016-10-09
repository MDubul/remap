var venueMap;
function init() {

  var locations = [
        ['Client Location', cli_lat, cli_lon],
        ['Your Location', vol_lat, vol_lon],
      ];

      var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 10,
        center: new google.maps.LatLng(cli_lat, cli_lon),
        mapTypeId: google.maps.MapTypeId.ROADMAP
      });

      var infowindow = new google.maps.InfoWindow();

      var marker, i;

      for (i = 0; i < locations.length; i++) {

          marker = new google.maps.Marker({
          position: new google.maps.LatLng(locations[i][1], locations[i][2]),
          map: map,
          icon: '/static/img/GoogleMapsMarkers/darkgreen_MarkerC.png'
        });
        if (i == 1) {
          marker.icon = '/static/img/GoogleMapsMarkers/red_MarkerV.png'
        }

        google.maps.event.addListener(marker, 'click', (function(marker, i) {
          return function() {
            infowindow.setContent(locations[i][0]);
            infowindow.open(map, marker);
          }
        })(marker, i));
  }
}

function loadScript() {
  
  var script = document.createElement('script');
  script.src ='http://maps.googleapis.com/maps/api/js?key=AIzaSyD7atNIGYo_Xd9zE_dntd_xvY3TBvOLVjE&callback=init';

  document.body.appendChild(script);
}


window.onload = loadScript;
