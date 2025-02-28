from mangum import Mangum
from .main import app  # Import your Flask app


# Create the Magnum handler for Flask
def lambda_handler(event, context):
    return magnum.handler(app, event, context)