const mapboxApiKey = "pk.eyJ1IjoiY2J1bmNoIiwiYSI6ImNtMWxteW13NTBiaDUybHB6cWJ3Y3dnajUifQ.B_7JKx-8vsKrYnbifAwIgg";

mapboxgl.accessToken = mapboxApiKey;

function success(position) {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;

    const map = new mapboxgl.Map({
        container: "map",
        style: "mapbox://styles/mapbox/streets-v11",
        center: [longitude, latitude],
        zoom: 9
    });
}

function error() {
    alert('Could not access geolocation!');
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(success, error);
} else {
    error();
}
