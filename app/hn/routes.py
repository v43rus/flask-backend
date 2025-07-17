from flask import Blueprint, jsonify, request
from .service import (
    scrape_hackernews,
    get_tag_history_service,
    get_all_tags_with_counts,
    get_popular_tags_by_period,
    get_popular_posts_by_period_and_tag,
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


@hn_bp.route("/api/tags/popular/<period>", methods=["GET"])
def get_popular_tags(period):
    if not period:
        # Default to 1 week if no period is specified
        period = "1w"
    try:
        tags = get_popular_tags_by_period(period)
        return jsonify(tags)
    except ValueError:
        return jsonify({"error": "Invalid period. Valid options: 1d, 3d, 1w, 2w, 1m"}), 400
    

@hn_bp.route("/api/posts/top/<tag>/<period>", methods=["GET"])
def get_popular_posts(tag, period):
    if not period:
        # Default to 1 week if no period is specified
        period = "1w"
    
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 12
    
    try:
        result = get_popular_posts_by_period_and_tag(tag, period, page, per_page)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
