import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flasgger import Swagger
from service import WeatherService
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://cristianmendivil.com"])
api = Api(app)

# Configure Swagger
swagger = Swagger(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Define response models for Flask-RESTful
condition_fields = {
    'icon': fields.String,
    'text': fields.String
}

hour_fields = {
    'time': fields.String,
    'temp': fields.Integer,
    'condition': fields.Nested(condition_fields)
}

day_fields = {
    'date': fields.String,
    'date_day': fields.String,
    'day': fields.Nested({
        'avgtemp': fields.Integer,
        'mintemp': fields.Integer,
        'maxtemp': fields.Integer,
        'condition': fields.Nested(condition_fields)
    }),
    'hour': fields.List(fields.Nested(hour_fields))
}

city_fields = {
    'name': fields.String,
    'region': fields.String,
    'country': fields.String,
    'url': fields.String
}

location_fields = {
    'name': fields.String,
    'localtime': fields.String
}

forecast_response_fields = {
    'current': fields.Nested(condition_fields),
    'temp': fields.Integer,
    'forecast': fields.List(fields.Nested(day_fields)),
    'location': fields.Nested(location_fields)
}

error_fields = {
    'error': fields.String,
    'details': fields.String
}


class Forecast(Resource):
    """
    Weather Forecast API
    ---
    parameters:
      - name: city
        in: path
        type: string
        required: true
        description: Name of the city to fetch weather for.
      - name: unit
        in: path
        type: string
        required: true
        description: Temperature unit ('C' or 'F').
    responses:
      200:
        description: Weather forecast retrieved successfully.
      400:
        description: Invalid request or city not found.
      500:
        description: Internal server error.
    """
    @marshal_with(forecast_response_fields)
    def get(self, city: str, unit: str):
        try:
            if unit.lower() not in ['c', 'f']:
                return {"error": "Invalid temperature unit", "details": unit}, 400

            data = WeatherService().get_forecast(city)
            if not data:
                return {"error": "City not found", "details": city}, 400

            return {
                "current": {
                    "condition": {
                        "icon": data["current"]["condition"]["icon"].strip("//"),
                        "text": data["current"]["condition"]["text"].strip()
                    },
                    "temp": round(data["current"]["temp_{}".format(unit)]),
                },
                "forecast": [],
                "location": {
                    "name": data["location"]["name"],
                    "localtime": data["location"]["localtime"],
                }
            }
        except Exception as err:
            return {"error": "Unexpected error", "details": str(err)}, 500


class Search(Resource):
    """
    City Search API
    ---
    parameters:
      - name: city
        in: path
        type: string
        required: true
        description: Name of the city to search.
    responses:
      200:
        description: List of matching cities.
      500:
        description: Internal server error.
    """
    @marshal_with(city_fields)
    def get(self, city: str):
        try:
            return WeatherService().search_city(city)
        except Exception as err:
            return {"error": "Unexpected error", "details": str(err)}, 500


# Register API endpoints
api.add_resource(Forecast, '/forecast/<string:city>/<string:unit>')
api.add_resource(Search, '/search/<string:city>')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
