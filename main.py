from flask import Flask, render_template, request, jsonify
from pymongo.mongo_client import MongoClient
import pprint
import math
import time
import os
import re

FEET_PER_LATITUDE = 365000.0
FEET_PER_LONGITUDE = 288200.0
FEET_FROM_NODE_BOX_LENGTH = 250

RATIO_LATITUDE = FEET_PER_LATITUDE / FEET_FROM_NODE_BOX_LENGTH
RATIO_LONGITUDE = FEET_PER_LONGITUDE / FEET_FROM_NODE_BOX_LENGTH

LATITUDE_DISTANCE = FEET_FROM_NODE_BOX_LENGTH / FEET_PER_LATITUDE
LONGITUDE_DISTANCE = FEET_FROM_NODE_BOX_LENGTH / FEET_PER_LONGITUDE

crime_weight = 50
road_weight = 50
lighting_weight = 50
time_weight = 50

paths = []
# paths -> path -> node

crimeDistances = []

def transform(street_name):
    street_types = {
        'Terrace': 'TER',
        'Parkway': 'PKWY',
        'Boulevard': 'BLVD',
        'Trail': 'TRL',
        'PATH Trail': 'PATH TRL',
        'Street': 'ST',
        'Road': 'RD',
        'Drive': 'DR',
        'Avenue': 'AVE',
        'Circle': 'CIR'
    }
    
    for street_type, abbreviation in street_types.items():
        match = re.search(fr'\b{street_type}\b', street_name, re.IGNORECASE)
        if match:
            return street_name[:match.end()].replace(street_type, abbreviation).upper()

    return ""

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY="8f4a4162e34ef3412932c027",
)


uri = "mongodb+srv://leapingturtlefrog:9aMc5Ko52zSqwiYh@base.grpjw.mongodb.net/?retryWrites=true&w=majority&appName=Base"

client = MongoClient(uri)
db = client.maps2


@app.route("/map")
def map_view():
    return render_template("map.html")


@app.route("/process1", methods=["POST"])
def process1():
    data = request.get_json()
    crime_weight = data.get("crime")
    road_weight = data.get("roadQuality")
    lighting_weight = data.get("lighting")
    time_weight = data.get("time")

    print(f"crime: {crime_weight}, road quality: {road_weight}, lighting: {lighting_weight}, time: {time_weight}")
    
    return ""

@app.route("/clearPaths", methods=["POST"])
def clearPaths():
    paths = []
    
    return ""


@app.route("/process2", methods=["POST"])
def process2():

    start = time.perf_counter()


    
    data = request.get_json()
    
    # crimes
    seen_crimes = set()
    
    batches = [(node[1] - LATITUDE_DISTANCE, node[1] + LATITUDE_DISTANCE, node[0] - LONGITUDE_DISTANCE, node[0] + LONGITUDE_DISTANCE) for node in data["coordinates"] if data["coordinates"].index(node) % 10 == 0]

    crimes = db.crime2.find({"$or": [{"$and": [{"Latitude": {"$gt": lat_min}}, {"Latitude": {"$lt": lat_max}}, {"Longitude": {"$gt": long_min}}, {"Longitude": {"$lt": long_max}}]} for lat_min, lat_max, long_min, long_max in batches]})

    severity_map = {crime_severity["Crime"]: crime_severity["Severity"] for crime_severity in db.crime_severity.find()}

    for crime in crimes:
        severity = severity_map.get(crime.get("NIBRS Code Name"))
        info = (severity, crime.get('Latitude'), crime.get('Longitude'))
        seen_crimes.add(info)
    
    # streetlights
    batches = [(node[1] - LATITUDE_DISTANCE, node[1] + LATITUDE_DISTANCE, node[0] - LONGITUDE_DISTANCE, node[0] + LONGITUDE_DISTANCE) for node in data["coordinates"]]

    lighting_index = db.streetlights.count_documents({"$or": [{"$and": [{"latitude": {"$gt": lat_min}}, {"latitude": {"$lt": lat_max}}, {"longitude": {"$gt": long_min}}, {"longitude": {"$lt": long_max}}]} for lat_min, lat_max, long_min, long_max in batches]})
    
    # road quality

    street_list = set(data['streets'])
    parsed_streets = [transform(street) for street in street_list]
    qual_sum = 0

    for street in parsed_streets:
        if street != '':
            try:
                qual_sum += db.road_quality.find_one({'Street Name': street}).get('Surface Distress Index')
            except:
                pass
    
    road_index = qual_sum / len(street_list)

    crime_index = sum([crime[0] for crime in seen_crimes])

    time_index = data['duration']

    crime_final = crime_index * crime_weight / 100
    lighting_final = lighting_index * lighting_weight
    road_final = road_index * road_weight * 2
    time_final = time_index * time_weight * 2 / 100

    print(f'Crime Index: {crime_final}. Streetlight Index: {lighting_final}. Road Quality Index: {road_final}. Time Index: {time_final}.')
    
    end = time.perf_counter()
    
    print(f"Time to complete: {end - start}")

    return jsonify(round(crime_final + time_final - lighting_final - road_final))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)