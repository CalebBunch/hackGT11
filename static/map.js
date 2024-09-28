const mapboxApiKey = "pk.eyJ1IjoiY2J1bmNoIiwiYSI6ImNtMWxteW13NTBiaDUybHB6cWJ3Y3dnajUifQ.B_7JKx-8vsKrYnbifAwIgg";

mapboxgl.accessToken = mapboxApiKey;

let map;
let marker1;
let marker2;

function success(position) {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;

    document.getElementById("start-destination").value = `${longitude}, ${latitude}`;
    
    const bounds = [
        [-84.69846451717459, 33.53149303065644], // Southwest coordinates
        [-84.12587550388955, 33.94151145206728] // Northeast coordinates
    ];

    map = new mapboxgl.Map({
        container: "map",
        style: "mapbox://styles/mapbox/dark-v11",
        center: [longitude, latitude],
        zoom: 11,
        maxBounds: bounds
    });

    marker1 = new mapboxgl.Marker()
        .setLngLat([longitude, latitude])
        .addTo(map);

    marker2 = new mapboxgl.Marker({ color: "black" })
        .setLngLat([0, 0])
        .addTo(map);

    map.on("click", async (e) => {
        const { lng, lat } = e.lngLat;
        marker2.setLngLat([lng, lat]);

        document.getElementById("end-destination").value = `${lng}, ${lat}`;

        await requestRoutes([longitude, latitude], [lng, lat]);
    });
}


function error() {
    alert("Could not access geolocation!");
}

async function requestRoutes(origin, destination) {
    const url = `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.routes) {
            drawRoutes(data.routes);
        } else {
            console.error("No routes found");
        }
    } catch (error) {
        console.error("Error fetching routes:", error);
    }
}

function drawRoutes(routes) {
    const existingLayers = map.getStyle().layers.filter(layer => layer.id.startsWith("route"));
    existingLayers.forEach(layer => map.removeLayer(layer.id));

    const existingSources = map.getStyle().sources;
    Object.keys(existingSources).forEach(sourceId => {
        if (sourceId.startsWith("route")) {
            map.removeSource(sourceId);
        }
    });

    const colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"];

    routes.forEach((route, index) => {
        const routeGeoJSON = {
            type: "Feature",
            properties: {
                stroke: colors[index % colors.length],
                "stroke-width": 4,
                "stroke-opacity": 0.8
            },
            geometry: route.geometry
        };

        // Add the route to the map
        map.addSource(`route${index}`, {
            type: "geojson",
            data: routeGeoJSON
        });

        map.addLayer({
            id: `route${index}`,
            type: "line",
            source: `route${index}`,
            layout: {
                "line-cap": "round",
                "line-join": "round"
            },
            paint: {
                "line-color": routeGeoJSON.properties.stroke,
                "line-width": routeGeoJSON.properties["stroke-width"],
                "line-opacity": routeGeoJSON.properties["stroke-opacity"]
            }
        });
    });
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(success, error);
} else {
    error();
}

