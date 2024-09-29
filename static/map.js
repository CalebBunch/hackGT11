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

    const urls = [
        `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`,
        `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${wayPointOne};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`,
        `https://api.mapbox.com/directions/v5/mapbox/walking/${origin.join(",")};${wayPointTwo};${destination.join(",")}?geometries=geojson&alternatives=true&access_token=${mapboxApiKey}&steps=true&overview=full`
    ];

    let weights = [];
    let all_routes = [];

    await $.ajax({
        url: "/clearPaths",
        type: "POST",
        contentType: "application/json",
        data: ""
    });
    
    let cnt = 0;
    for (const url of urls) {
        try {
            const response = await fetch(url);
            const data = await response.json();

            if (data.routes) {
                tempData = data.routes[0].legs[0].steps;
                
                doneList = [];
                
                for(let i = 0; i < tempData.length; i++) {
                    doneList.push(tempData[i].name);
                }

                const geoData = {
                    "distance": data.routes[0].distance,
                    "duration": data.routes[0].duration,
                    "coordinates": data.routes[0].geometry.coordinates,
                    "streets": doneList
                };
                
                const processResponse = await $.ajax({
                    url: "/process2",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify(geoData),
                    success: function(response) {
                        cnt += 1;

                        try {
                            const parsedResponse = JSON.parse(response);
                            weights.push([geoData['distance'], geoData['duration'], parsedResponse]);
                            all_routes.push(...data.routes);

                        } catch (error) {
                            console.error("Error parsing JSON:", error);
                        }

                        if (cnt === 3) {
                        
                            weights.sort((a, b) => a[2] - b[2]);

                            const combined = all_routes.map((route, index) => ({
                                route: route,
                                weight: weights[index][2]
                            }));

                            combined.sort((a, b) => a.weight - b.weight);

                            const sortedRoutes = combined.map(item => item.route);
                        
                            renderRoutes();
                        
                            let i = 0;
                            document.querySelectorAll(".route-label").forEach(label => {
                                if (weights[i]) {
                                    const [distance, duration, rating] = weights[i];
                                    label.textContent = `Distance: ${distance.toFixed(2)} m - Time: ${duration.toFixed(2)} s - Overall Rating: ${rating}`;
                                    i++;
                                }
                            });
                          
                            drawRoutes(sortedRoutes);

                        }  
                    },
                });

            } else {
                console.error("No routes found");
            }
        } catch (error) {
            console.error("Error fetching routes:", error);
        }
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

    }
    return waypoints
}


function drawRoutes(routes) {
    if (routeGroupIds.length === 3) {
        clearPreviousRoutes();
    }

    const colors = ["#FF0000", "#FF6600", "#00FF00"];

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


function renderRoutes() {
    const routesDiv = document.getElementsByClassName("routes");
    routesDiv[0].style.display = "block"; 
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(success, error);
} else {
    error();
}

