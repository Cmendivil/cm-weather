import logging
from calendar import weekday
from flask import Flask, request, jsonify
from flask_cors import CORS
from service import WeatherService
from datetime import datetime
from dotenv import load_dotenv
from os import environ as env
from functools import wraps
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from asgiref.wsgi import WsgiToAsgi
# Load .env file to environment
load_dotenv()

# Creating a Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000, https://cristianmendivil.com"])

# Set up Flask-RESTful API
api = Api(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Define response models
condition_fields = {
    'icon': fields.String(),
    'text': fields.String()
}

hour_fields = {
    'time': fields.String(),
    'temp': fields.Integer(),
    'condition': fields.Nested(condition_fields)
}

day_fields = {
    'date': fields.String(),
    'date_day': fields.String(),
    'day': fields.Nested({
        'avgtemp': fields.Integer(),
        'mintemp': fields.Integer(),
        'maxtemp': fields.Integer(),
        'condition': fields.Nested(condition_fields)
    }),
    'hour': fields.List(fields.Nested(hour_fields))
}

city_fields = {
    'name': fields.String(),
    'region': fields.String(),
    'country': fields.String(),
    'url': fields.String()
}

location_fields = {
    'name': fields.String(),
    'localtime': fields.String()
}

forecast_response_fields = {
    'current': fields.Nested(condition_fields),
    'temp': fields.Integer(),
    'forecast': fields.List(fields.Nested(day_fields)),
    'location': fields.Nested(location_fields)
}

error_fields = {
    'error': fields.String(),
    'details': fields.String()
}


class Forecast(Resource):
    def get(self, city: str, unit: str):
        """
        Returns the weather forecast for the specified city and temperature unit.
        """
        try:
            if unit.lower() not in ['c', 'f']:
                return {"error": "Invalid temperature unit", "details": unit}, 400

            data = WeatherService().get_forecast(city)
            if not data:
                return {"error": "City not found", "details": city}, 400

            resp_data = {
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
            current_time = data["location"]["localtime"]
            latest_hour_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M").replace(minute=0)

            for forecastday in data["forecast"]["forecastday"]:
                week_day = datetime.strptime(forecastday["date"], "%Y-%m-%d").date().strftime("%A")
                date_now = datetime.now()
                if week_day == date_now.date().strftime("%A"):
                    week_day = "Today"
                temp_dict = {
                    "date": forecastday["date"],
                    "week_day": week_day,
                    "day": {
                        "avgtemp": round(forecastday["day"]["avgtemp_{}".format(unit)]),
                        "mintemp": round(forecastday["day"]["mintemp_{}".format(unit)]),
                        "maxtemp": round(forecastday["day"]["maxtemp_{}".format(unit)]),
                        "condition": {
                            "icon": forecastday["day"]["condition"]["icon"].strip("//"),
                            "text": forecastday["day"]["condition"]["text"].strip()
                        }
                    },
                    "hour": []
                }

                for hour in forecastday["hour"]:
                    if latest_hour_time.date() != datetime.strptime(forecastday["date"], "%Y-%m-%d").date():
                        continue

                    date = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
                    time = date.strftime("%-I%p")
                    if time == date_now.time().strftime("%-I%p"):
                        time = "Now"
                    if latest_hour_time <= date:
                        temp_dict["hour"].append({
                            "temp": round(hour["temp_{}".format(unit)]),
                            "condition": {
                                "icon": hour["condition"]["icon"].strip("//"),
                                "text": hour["condition"]["text"].strip()
                            },
                            "time": time
                        })
                resp_data["forecast"].append(temp_dict)

            return marshal_with(forecast_response_fields)(resp_data)
        except Exception as err:
            return marshal_with(error_fields)({"error": "Unexpected error", "details": str(err)}), 500


class Search(Resource):
    def get(self, city: str):
        """
        Returns a list of cities matching the search term.
        """
        try:
            resp = WeatherService().search_city(city)
            output = []

            for city in resp:
                cityData = {}
                cityData["name"] = city["name"]
                cityData["region"] = city["region"]
                cityData["country"] = city["country"]
                cityData["url"] = city["url"]

                output.append(cityData)
            return marshal_with([city_fields])(output)
        except Exception as err:
            return marshal_with(error_fields)({"error": "Unexpected error", "details": str(err)}), 500


# Add routes to the API
api.add_resource(Forecast, '/forecast/<string:city>/<string:unit>')
api.add_resource(Search, '/search/<string:city>')


asgi_app = WsgiToAsgi(app)

# Driver function
if __name__ == '__main__':
    app.run(debug=True)
