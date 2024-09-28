import os
from flask import Flask, render_template, request, jsonify

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="8f4a4162e34ef3412932c027",
    )
    
    from pymongo.mongo_client import MongoClient

    uri = "mongodb+srv://leapingturtlefrog:9aMc5Ko52zSqwiYh@base.grpjw.mongodb.net/?retryWrites=true&w=majority&appName=Base"

    # Create a new client and connect to the server
    client = MongoClient(uri)
    db = client.maps1

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        #print("Pinged your deployment. You successfully connected to MongoDB!")
        example = db.crime
        #print(example)
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
        result = data['value']
        return jsonify(result=result)
    
    return app
