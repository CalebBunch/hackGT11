import os
from flask import Flask, render_template

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="8f4a4162e34ef3412932c027",
    )

    @app.route("/map")
    def map_view():
        return render_template("map.html") 

    return app
