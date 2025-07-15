from flask import Blueprint, jsonify
from .service import scrape_hackernews
from .db import save_posts

hn_bp = Blueprint("hn", __name__)

@hn_bp.route("/api/scrape", methods=["GET"])
def scrape():
    posts = scrape_hackernews()
    save_posts(posts)
    return jsonify({"message": f"{len(posts)} posts scraped and saved."})
