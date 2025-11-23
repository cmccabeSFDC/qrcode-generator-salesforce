import os
from dotenv import load_dotenv

load_dotenv()

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "qr-code-generator-secret-key")

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
