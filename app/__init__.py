from flask import Flask
from dotenv import load_dotenv


def create_app():
    # Load environment variables from .env
    load_dotenv()

    app = Flask(__name__)

    from .main import main as main_bp

    app.register_blueprint(main_bp)

    return app
