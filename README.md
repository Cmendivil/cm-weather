# CM-WEATHER

## Prerequisites  
* Python  
* API key from <https://www.weatherapi.com>

## Installation
Run the following commands to create a virtual environment and install required libraries.  
```sh 
python -m venv venv
```  
```sh 
source venv/bin/activate
```  
```sh 
pip install -r requirements.txt
```

## Run locally
Create a `.env` file. Save API key(from <https://www.weatherapi.com>) into `.env` file using `WEATHER_API_KEY` as variable name.  
Create a token and save it to `AUTH_TOKEN` in `.env`. You can use the following command to generate a token.  
```sh
openssl rand -hex 32 
```
Run the following command to run app locally.  
```sh 
python main.py
```  
