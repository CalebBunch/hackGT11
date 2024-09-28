const mapboxApiKey = "pk.eyJ1IjoiY2J1bmNoIiwiYSI6ImNtMWxteW13NTBiaDUybHB6cWJ3Y3dnajUifQ.B_7JKx-8vsKrYnbifAwIgg";

mapboxgl.accessToken = mapboxApiKey;

let map;
let marker1;
let marker2;
let routeGroupIds = [];

function success(position) {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;

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

        // Get routes
        await requestRoutes([longitude, latitude], [lng, lat]);
    });
}

function error() {
    alert("Could not access geolocation!");
}

async function requestRoutes(origin, destination) {
    let wayPoints = calculateWayPoints(origin, destination)
    let wayPointOne = wayPoints[0].join(",");
    let wayPointTwo = wayPoints[1].join(",");

    const url1 = `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`;
    const url2 = `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${wayPointOne};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`;
    const url3 = `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${wayPointTwo};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`;
    const urls = [url1, url2, url3];

        try {
            const response = await fetch(url1);
            const data = await response.json();
        
            if (data.routes) {
                drawRoutes(data.routes);
            } else {
                console.error("No routes found");
            }
        } catch (error) {
            console.error("Error fetching routes:", error);
        }
        
        try {
            const response = await fetch(url2);
            const data = await response.json();
        
            if (data.routes) {
                drawRoutes(data.routes);
            } else {
                console.error("No routes found");
            }
        } catch (error) {
            console.error("Error fetching routes:", error);
        }

        try {
            const response = await fetch(url3);
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

function calculateWayPoints(origin, destination) {
    let waypoints = [];
    let [originLon, originLat] = origin
    let [destinationLon, destinationLat] = destination

    for (let i = 1; i <= 2; i++) {
        let fraction = i / 3;
        let wayPointLon = originLon + (fraction * (destinationLon - originLon));
        let wayPointLat = originLat + (fraction * (destinationLat - originLat));
        waypoints.push([wayPointLon, wayPointLat])
        
        // let marker = new mapboxgl.Marker({ color: "red" })
        //     .setLngLat([wayPointLon, wayPointLat])
        //     .addTo(map)
    }
    return waypoints
}

function drawRoutes(routes) {
    // const existingLayers = map.getStyle().layers.filter(layer => layer.id.startsWith("route"));
    // existingLayers.forEach(layer => map.removeLayer(layer.id));

    // const existingSources = map.getStyle().sources;
    // Object.keys(existingSources).forEach(sourceId => {
    //     if (sourceId.startsWith("route")) {
    //         map.removeSource(sourceId);
    //     }
    // });

    if (routeGroupIds.length == 3) {
        clearPreviousRoutes();
    }

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

        const routeId = `route${Date.now()}-${index}`;
        routeGroupIds.push(routeId);

        // Add the route to the map
        map.addSource(routeId, {
            type: "geojson",
            data: routeGeoJSON
        });

        map.addLayer({
            id: routeId,
            type: "line",
            source: routeId,
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

function clearPreviousRoutes() {
    routeGroupIds.forEach(routeId => {
        if (map.getLayer(routeId)) {
            map.removeLayer(routeId);
        }
        if (map.getSource(routeId)) {
            map.removeSource(routeId)
        }
    });
    routeGroupIds = [];
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(success, error);
} else {
    error();
}

