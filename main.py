from flask import Flask, request
from service import WeatherService
from datetime import datetime
# creating a Flask app
app = Flask(__name__)

@app.route('/forecast/<city>', methods=['GET'])
def forecast(city: str):
    if request.method == 'GET':
        data = WeatherService().get_forecast(city)
        resp_data = {
            "alerts": data["alerts"],
            "current": {
                "condition": {
                    "icon": data["current"]["condition"]["icon"].strip("//"),
                    "text": data["current"]["condition"]["text"].strip()
                },
                "temp_c": round(data["current"]["temp_c"]),
                "temp_f": round(data["current"]["temp_f"])
            },
            "forecast": {"forecastday": []},
            "location": {
                "name": data["location"]["name"],
                "localtime": data["location"]["localtime"],
            }
        }
        current_time = data["location"]["localtime"]
        latest_hour_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M").replace(minute=0)
        for forecastday in data["forecast"]["forecastday"]:
            temp_dict = {
             "date": forecastday["date"],
             "day": {
                 "avgtemp_c": round(forecastday["day"]["avgtemp_c"]),
                 "avgtemp_f": round(forecastday["day"]["avgtemp_f"]),
                 "mintemp_c": round(forecastday["day"]["mintemp_c"]),
                 "mintemp_f": round(forecastday["day"]["mintemp_f"]),
                 "maxtemp_c": round(forecastday["day"]["maxtemp_c"]),
                 "maxtemp_f": round(forecastday["day"]["maxtemp_f"]),
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
                if latest_hour_time <= date:
                    temp_dict["hour"].append({
                        "temp_c": round(hour["temp_c"]),
                        "temp_f": round(hour["temp_f"]),
                        "condition": {
                            "icon": hour["condition"]["icon"].strip("//"),
                            "text": hour["condition"]["text"].strip()
                        },
                        "time": hour["time"]
                    })
            resp_data["forecast"]["forecastday"].append(temp_dict)

        return resp_data


@app.route('/search/<city>', methods=['GET'])
def search(city: str):
    if request.method == 'GET':
        return WeatherService().search_city(city)


# driver function
if __name__ == '__main__':
    app.run(debug=True)