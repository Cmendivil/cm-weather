import requests
import os
import logging
from dotenv import load_dotenv

# load .env file to environment
load_dotenv()

logging.basicConfig(level=logging.INFO)

class WeatherService:
    api_key = os.getenv("WEATHER_API_KEY")
    url = "http://api.weatherapi.com/v1/{}?key="+api_key+"&q={}"
    def get_forecast(self, city: str) -> object:
        try:
            param = city + "&days=7&aqi=no&alerts=yes"
            url = (self.url.format("forecast.json", param))
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise http_err
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
            raise conn_err
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
            raise timeout_err
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An error occurred: {req_err}")
            raise req_err
        except Exception as err:
            logging.error(f"An unexpected error occurred: {err}")
            raise err

    def search_city(self, city: str) -> object:
        try:
            response = requests.get(self.url.format("search.json", city))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise http_err
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
            raise conn_err
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
            raise timeout_err
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An error occurred: {req_err}")
            raise req_err
        except Exception as err:
            logging.error(f"An unexpected error occurred: {err}")
            raise err

