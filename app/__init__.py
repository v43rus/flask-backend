from flask import Flask
import os
from flask_cors import CORS
from dotenv import load_dotenv

frontend_url = os.getenv("FRONTEND_ORIGIN", "*")  # fallback till * om inte definierad

def create_app():
    # Load environment variables from .env
    load_dotenv()

    app = Flask(__name__)

    from .main import main as main_bp

    app.register_blueprint(main_bp)

    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": frontend_url}})

    return app
