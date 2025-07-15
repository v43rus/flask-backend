from flask import Blueprint, jsonify
from .service import (
    scrape_hackernews,
    get_tag_history_service,
    get_all_tags_with_counts,
)

hn_bp = Blueprint("hn", __name__)


@hn_bp.route("/api/scrape", methods=["GET"])
def scrape():
    try:
        posts = scrape_hackernews()
        return jsonify({"message": f"{len(posts)} posts scraped and saved."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hn_bp.route("/api/tags/history/<tag>", methods=["GET"])
def get_tag_history(tag):
    try:
        history = get_tag_history_service(tag)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hn_bp.route("/api/tags", methods=["GET"])
def list_tags():
    try:
        tags = get_all_tags_with_counts()
        return jsonify(tags)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
