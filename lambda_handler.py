from mangum import Mangum
from main import app, asgi_app  # Import your Flask app


# Create the Magnum handler for Flask
def lambda_handler(event, context):
    handler = Mangum(asgi_app)
    return handler(event, context)