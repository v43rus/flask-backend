from flask import Blueprint, jsonify
from .hn.routes import hn_bp

main = Blueprint("main", __name__)
main.register_blueprint(hn_bp)


@main.route("/")
def index():
    return jsonify({"message": "Backend is running!"})
