import os
from flask import Flask, render_template, request, jsonify
import pprint
import math

FEET_PER_LATITUDE = 365000.0
FEET_PER_LONGITUDE = 288200.0
FEET_FROM_NODE_BOX_LENGTH = 5000

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
    
    from pymongo.mongo_client import MongoClient

    uri = "mongodb+srv://leapingturtlefrog:9aMc5Ko52zSqwiYh@base.grpjw.mongodb.net/?retryWrites=true&w=majority&appName=Base"

    client = MongoClient(uri)
    db = client.maps2

    try:
        client.admin.command("ping")
    except Exception as e:
        print(e)

    @app.route("/map")
    def map_view():
        return render_template("map.html") 
    
    @app.route("/debug")
    def debug():
        seen_crimes = set()
        
        nodes = [{
            "Latitude": 33.617926,
            "Longitude": -84.472797
        }]
        
        for node in nodes:
            nodeLat = node.get("Latitude")
            nodeLong = node.get("Longitude")
            
            for crime in db.crime.find({"Latitude": {"$gt": nodeLat - LATITUDE_DISTANCE}, "Latitude": {"$lt": nodeLat + LATITUDE_DISTANCE}, "Longitude": {"$gt": nodeLong - LONGITUDE_DISTANCE}, "Longitude": {"$lt": nodeLong + LONGITUDE_DISTANCE}}):
                info = (crime.get('NIBRS Code Name'), crime.get('Latitude'), crime.get('Longitude'))
                if info not in seen_crimes:
                    seen_crimes.add(info)
        
        return render_template("debug.html", db_call_data=seen_crimes)
    
    @app.route("/process1", methods=["POST"])
    def process1():
        data = request.get_json()
        crime_weight = data.get("crime")
        road_weight = data.get("roadQuality")
        lighting_weight = data.get("lighting")

        print(f"crime: {crime_weight}, road quality: {road_weight}, lighting: {lighting_weight}")
        
        return ""
    
    @app.route("/clearPaths", methods=["POST"])
    def clearPaths():
        paths = []
        
        return ""
    
    @app.route("/process2", methods=["POST"])
    def process2():
        data = request.get_json()
        paths.append(data)
        print("path appended")
        
        pprint.pprint(paths)
        
        #print("\n\n-----\n\n")
        
        return ""
    
    return app
