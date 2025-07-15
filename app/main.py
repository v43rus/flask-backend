from flask import Blueprint, jsonify
from .hn.routes import hn_bp
from .hn.popular import popular_posts_bp

main = Blueprint("main", __name__)
main.register_blueprint(hn_bp)
main.register_blueprint(popular_posts_bp)


@main.route("/")
def index():
    return jsonify({"message": "Backend is running!"})
