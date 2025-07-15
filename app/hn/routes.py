from flask import Blueprint, jsonify
from .service import scrape_hackernews, get_tag_history_service, get_all_tags_with_counts

hn_bp = Blueprint("hn", __name__)

@hn_bp.route("/api/scrape", methods=["GET"])
def scrape():
    posts = scrape_hackernews()
    return jsonify({"message": f"{len(posts)} posts scraped and saved."})

@hn_bp.route("/api/tags/history/<tag>", methods=["GET"])
def get_tag_history(tag):
    history = get_tag_history_service(tag)
    return jsonify(history)

@hn_bp.route("/api/tags", methods=["GET"])
def list_tags():
    tags = get_all_tags_with_counts()
    return jsonify(tags)