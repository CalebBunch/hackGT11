const mapboxApiKey = "pk.eyJ1IjoiY2J1bmNoIiwiYSI6ImNtMWxteW13NTBiaDUybHB6cWJ3Y3dnajUifQ.B_7JKx-8vsKrYnbifAwIgg";

mapboxgl.accessToken = mapboxApiKey;

let map;
let marker1;
let marker2;
let routeGroupIds = [];

function getUserInput() {
    const startDestination = document.getElementById("start-destination").value;
    const endDestination = document.getElementById("end-destination").value;
    return { startDestination, endDestination };
}

async function geocode(address) {
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(address)}.json?access_token=${mapboxApiKey}`;
    const response = await fetch(url);
    const data = await response.json();
    if (data.features && data.features.length > 0) {
        return {
            lng: data.features[0].geometry.coordinates[0],
            lat: data.features[0].geometry.coordinates[1],
        };
    }
    throw new Error("No results found");
}

async function handleEnterKey(event) {
    if (event.key === "Enter") {
        const { startDestination, endDestination } = getUserInput();
        
        try {
            const startCoords = await geocode(startDestination);
            const endCoords = await geocode(endDestination);

            // Update markers
            marker1.setLngLat([startCoords.lng, startCoords.lat]);
            marker2.setLngLat([endCoords.lng, endCoords.lat]);

            // Optionally update the input fields to show the coordinates
            document.getElementById("start-destination").value = `${startCoords.lng}, ${startCoords.lat}`;
            document.getElementById("end-destination").value = `${endCoords.lng}, ${endCoords.lat}`;

            // Request new routes
            await requestRoutes([startCoords.lng, startCoords.lat], [endCoords.lng, endCoords.lat]);
        } catch (error) {
            alert(error.message);
        }
    }
}

document.getElementById("start-destination").addEventListener("keydown", handleEnterKey);
document.getElementById("end-destination").addEventListener("keydown", handleEnterKey);

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
    let wayPoints = calculateWayPoints(origin, destination);
    let wayPointOne = wayPoints[0].join(",");
    let wayPointTwo = wayPoints[1].join(",");

    const url1 = `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`;
    const url2 = `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${wayPointOne};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`;
    const url3 = `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${wayPointTwo};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`;
    
    const urls = [url1, url2, url3];
    let all_routes = [];

    for (const url of urls) {
        try {
            const response = await fetch(url);
            const data = await response.json();

            if (data.routes) {
                all_routes.push(...data.routes);
            } else {
                console.error("No routes found");
            }
        } catch (error) {
            console.error("Error fetching routes:", error);
        }
    }

    drawRoutes(all_routes);
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
        
    }
    return waypoints
}


function drawRoutes(routes) {
    if (routeGroupIds.length === 3) {
        clearPreviousRoutes();
    }

    const colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"];

    routes.forEach((route, index) => {
        const routeGeoJSON = {
            type: "Feature",
            properties: {
                stroke: colors[index % colors.length], // Use the color based on index
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
                "line-color": routeGeoJSON.properties.stroke, // Correctly apply stroke color
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

