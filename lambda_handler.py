from mangum import Mangum
from .main import app  # Import your Flask app

handler = Mangum(app)
