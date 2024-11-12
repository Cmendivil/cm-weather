import requests
import os
from dotenv import load_dotenv

# load .env file to environment
load_dotenv()

class WeatherService:
    api_key = os.getenv("WEATHER_API_KEY")
    url = "http://api.weatherapi.com/v1/{}?key="+api_key+"&q={}"
    def get_forecast(self, city: str) -> object:
        param = city + "&days=7&aqi=no&alerts=yes"
        url = (self.url.format("forecast.json", param))
        return requests.get(url).json()

    def search_city(self, city: str) -> object:
        return requests.get(self.url.format("search.json", city)).json()
