import awsgi
from main import app # Import your Flask app


# Create the Magnum handler for Flask
def lambda_handler(event, context):
    return awsgi.response(app, event, context)