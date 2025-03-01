import logging
from calendar import weekday
from flask import Flask, request, jsonify
from flask_cors import CORS
from service import WeatherService
from datetime import datetime
from dotenv import load_dotenv
from os import environ as env
from functools import wraps
from flask_restx import Api, Resource, fields

# Load .env file to environment
load_dotenv()

# Creating a Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000, https://cristianmendivil.com"])

# Set up Flask-RESTX API
api = Api(app, version="1.0", title="Weather API", description="A simple Weather API with documentation", doc="/redoc")

# Setup logging
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
app.logger.addHandler(handler)


@app.route("/swagger.json")
def swagger_json():
    return api.__schema__


# Define response models
condition_model = api.model('Condition', {
    'icon': fields.String(description='URL of the weather icon'),
    'text': fields.String(description='Weather condition text')
})

hour_model = api.model('HourForecast', {
    'time': fields.String(description='Time of forecast'),
    'temp': fields.Integer(description='Hourly temperature'),
    'condition': fields.Nested(condition_model)
})

day_model = api.model('DayForecast', {
    'date': fields.String(description='Date of forecast'),
    'date_day': fields.String(description='Day of the week'),
    'day': fields.Nested(api.model('Day', {
        'avgtemp': fields.Integer(description='Average temperature for the day'),
        'mintemp': fields.Integer(description='Minimum temperature for the day'),
        'maxtemp': fields.Integer(description='Maximum temperature for the day'),
        'condition': fields.Nested(condition_model)
    })),
    'hour': fields.List(fields.Nested(hour_model))
})

city_model = api.model("City", {
    'name': fields.String(description='City name'),
    'region': fields.String(description='City region'),
    'country': fields.String(description='City country'),
    'url': fields.String(description='City url name')
})

location_model = api.model('Location', {
    'name': fields.String(description='City name'),
    'localtime': fields.String(description='Local time of the city')
})

forecast_response_model = api.model('ForecastResponse', {
    'current': fields.Nested(condition_model),
    'temp': fields.Integer(description='Current temperature'),
    'forecast': fields.List(fields.Nested(day_model)),
    'location': fields.Nested(location_model)
})

error_model = api.model('ErrorResponse', {
    'error': fields.String(description='Error message'),
    'details': fields.String(description='Additional details')
})


@api.route('/forecast/<string:city>/<string:unit>')
@api.doc(description="Get the weather forecast for a city in the given unit (C or F)")
@api.response(200, 'Success', forecast_response_model)
@api.response(400, 'Invalid Request', error_model)
@api.response(500, 'Internal Server Error', error_model)
class Forecast(Resource):
    def get(self, city: str, unit: str):
        """
        /forecast/<city>/<unit>
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

            return resp_data
        except Exception as err:
            return {"error": "Unexpected error", "details": str(err)}, 500


@api.route('/search/<string:city>')
@api.doc(description="Search for a city based on the given name")
@api.response(200, 'Success', [city_model])
@api.response(500, 'Internal Server Error', error_model)
class Search(Resource):
    def get(self, city: str):
        """
        /search/<city>
        Returns a list of cities matching the search term.
        """
        try:
            print("In Search")
            resp = WeatherService().search_city(city)
            output = []

            for city in resp:
                cityData = {}
                cityData["name"] = city["name"]
                cityData["region"] = city["region"]
                cityData["country"] = city["country"]
                cityData["url"] = city["url"]

                output.append(cityData)
            return output
        except Exception as err:
            return {"error": "Unexpected error", "details": str(err)}, 500


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response


