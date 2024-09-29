from flask import Flask, render_template, request, jsonify
from pymongo.mongo_client import MongoClient
import pprint
import math
import time
import os

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

paths = []
# paths -> path -> node

crimeDistances = []

def create_app(test_config=None) -> Flask:
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


        seen_crimes = set()
        data = request.get_json()
    
        batches = [(node[1] - LATITUDE_DISTANCE, node[1] + LATITUDE_DISTANCE, node[0] - LONGITUDE_DISTANCE, node[0] + LONGITUDE_DISTANCE) for node in data["coordinates"] if data["coordinates"].index(node) % 10 == 0]

        crimes = db.crime2.find({"$or": [{"$and": [{"Latitude": {"$gt": lat_min}}, {"Latitude": {"$lt": lat_max}}, {"Longitude": {"$gt": long_min}}, {"Longitude": {"$lt": long_max}}]} for lat_min, lat_max, long_min, long_max in batches]})

        severity_map = {crime_severity["Crime"]: crime_severity["Severity"] for crime_severity in db.crime_severity.find()}

        for crime in crimes:
            severity = severity_map.get(crime.get("NIBRS Code Name"))
            info = (severity, crime.get('Latitude'), crime.get('Longitude'))
            seen_crimes.add(info)

        print(f'Crime Length: {len(seen_crimes)}')

        end = time.perf_counter()

        print(f"Time to complete: {end - start}")

        return ""

    
    return app
