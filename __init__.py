import os
from flask import Flask, render_template, request, jsonify

crime_weight = 50
road_weight = 50
lighting_weight = 50

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="8f4a4162e34ef3412932c027",
    )
    
    from pymongo.mongo_client import MongoClient

    uri = "mongodb+srv://leapingturtlefrog:9aMc5Ko52zSqwiYh@base.grpjw.mongodb.net/?retryWrites=true&w=majority&appName=Base"

    client = MongoClient(uri)
    db = client.maps1

    try:
        client.admin.command("ping")
        example = db.crime
        # print(example)
    except Exception as e:
        print(e)

    @app.route("/map")
    def map_view():
        return render_template("map.html") 
    
    @app.route("/debug")
    def debug():
        example_db_data = db.crime1.find_one({"Longitude": -84.408028})["NIBRS Code Name"]
        return render_template("debug.html", example_db_data=example_db_data)
    
    @app.route("/process1", methods=["POST"])
    def process1():
        data = request.get_json()
        crime_weight = data.get("crime")
        road_weight = data.get("roadQuality")
        lighting_weight = data.get("lighting")

        print(f"crime: {crime_weight}, road quality: {road_weight}, lighting: {lighting_weight}")

        result = {
            "crime": crime_weight,
            "roadQuality": road_weight,
            "lighting": lighting_weight
        }

        return jsonify(result=result)

    
    return app
