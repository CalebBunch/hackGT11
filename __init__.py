import os
from flask import Flask, render_template, request, jsonify
import pprint
import math
import time

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
        
        # 33.774568 -84.39687

        nodes = [{
            "Latitude": 33.617926,
            "Longitude": -84.472797
        }]

        nodes2 = [{
            'Latitude': 33.774568,
            'Longitude': -84.39687
        }]
        
        nodes3 = [{
            'Latitude': 33.63993829,
            'Longitude': -84.45880295
        }]
        
        for node in nodes2:
            nodeLat = node.get("Latitude")
            nodeLong = node.get("Longitude")

            #print(nodeLat, nodeLong)

            print(LATITUDE_DISTANCE, LONGITUDE_DISTANCE)
            
            for crime in db.crime2.find({"Latitude": {"$gt": nodeLat - LATITUDE_DISTANCE}, "Latitude": {"$lt": nodeLat + LATITUDE_DISTANCE}, "Longitude": {"$gt": nodeLong - LONGITUDE_DISTANCE}, "Longitude": {"$lt": nodeLong + LONGITUDE_DISTANCE}}):
                info = (crime.get('NIBRS Code Name'), crime.get('Latitude'), crime.get('Longitude'))
                if info not in seen_crimes:
                    seen_crimes.add(info)
        
        print(len(seen_crimes))
        return render_template("debug.html", db_call_data=seen_crimes)
    
    @app.route("/debug1")
    def debug1():
        seen_crimes = set()
        
        # 33.774568 -84.39687
        
        steps = 10
        
        endLat = 33.8860
        endLong = -84.54291
        startLat = 33.63485
        startLong = -84.29435
        
        latStep = (endLat - startLat) / (steps - 1)
        longStep = (endLong - startLong) / (steps - 1)
        
        currLat = startLat
        currLong = startLong
        
        startTime = time.time()
        
        for i in range(steps):
            seen_crimes = set()
            
            for j in range(steps):
                seen_crimes = set()
                for crime in db.crime2.find({"$and": [{"Latitude": {"$gt": currLat - LATITUDE_DISTANCE}},{"Latitude": {"$lt": currLat + LATITUDE_DISTANCE}},{"Longitude": {"$gt": currLong - LONGITUDE_DISTANCE}},{"Longitude": {"$lt": currLong + LONGITUDE_DISTANCE}}]}):
                    #print(crime)
                    #seen_crimes.add(crime.get('_id'))
                    severity = db.crime_severity.find_one({"Crime": crime.get('NIBRS Code Name')}).get('Severity')
                    info = (severity, crime.get('Latitude'), crime.get('Longitude'))
                    if info not in seen_crimes:
                        seen_crimes.add(info)
                        
                #latString = "%.7s" % str(currLat)
                #longString = "%.7s" % str(currLong)
                
                #print(f'done lat:{latString}\t\tlong:{longString}\t\tcrimes:{len(seen_crimes)}')
                
                currLong += longStep
            currLong = startLong
            currLat += latStep
        
        print("COMPLETE")
        print("steps: ", steps**2)
        print("time: ", time.time()-startTime)
        
        return render_template("debug1.html", data="DONE")
    
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
        seen_crimes = set()
        seen_lights = set()
        data = request.get_json()
        i = 0
        for node in data['coordinates']:
            
            i += 1
            
            '''
            nodes = [{
                "Latitude": 33.617926,
                "Longitude": -84.472797
            }]
            
            nodeLat = 33.74584
            nodeLong = -84.42440
            '''
            
            nodeLat = node[1]
            nodeLong = node[0]

            print(nodeLat, nodeLong)

            # for crime in db.crime.find({"Latitude": {"$gt": nodeLat - LATITUDE_DISTANCE},
            #                             "Latitude": {"$lt": nodeLat + LATITUDE_DISTANCE},
            #                             "Longitude": {"$gt": nodeLong - LONGITUDE_DISTANCE},
            #                             "Longitude": {"$lt": nodeLong + LONGITUDE_DISTANCE}})

            for crime in db.crime2.find({"$and": [{"Latitude": {"$gt": nodeLat - LATITUDE_DISTANCE}},{"Latitude": {"$lt": nodeLat + LATITUDE_DISTANCE}},{"Longitude": {"$gt": nodeLong - LONGITUDE_DISTANCE}},{"Longitude": {"$lt": nodeLong + LONGITUDE_DISTANCE}}]}):
                #print(crime)
                #seen_crimes.add(crime.get('_id'))
                severity = db.crime_severity.find_one({"Crime": crime.get('NIBRS Code Name')}).get('Severity')
                info = (severity, crime.get('Latitude'), crime.get('Longitude'))
                if info not in seen_crimes:
                    seen_crimes.add(info)
            
            print(len(seen_crimes))
            print('Check')

        '''
            for light in db.streetlights.find({"latitude": {"$gt": nodeLat - LATITUDE_DISTANCE}, "latitude": {"$lt": nodeLat + LATITUDE_DISTANCE}, "longitude": {"$gt": nodeLong - LONGITUDE_DISTANCE}, "longitude": {"$lt": nodeLong + LONGITUDE_DISTANCE}}):
                info = (light.get('latitude'), light.get('longitude'))
                if info not in seen_lights:
                    seen_lights.add(info)'''
        
        #print(seen_crimes)
        #print(seen_lights)

        #crime_weight = sum([info[0] for info in seen_crimes])
        #light_weight = len(seen_lights)

        #print(f'Crime: {crime_weight}, Light: {light_weight}')
        print(f'Crime Length: {len(seen_crimes)}')
        return ""
    
    return app
