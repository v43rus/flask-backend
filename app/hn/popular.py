from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app.db import db_conn

popular_posts_bp = Blueprint("popular_posts", __name__)

RANGE_MAP = {
    "1d": timedelta(days=1),
    "3d": timedelta(days=3),
    "1w": timedelta(weeks=1),
    "2w": timedelta(weeks=2),
    "1m": timedelta(days=30),
}

@popular_posts_bp.route("/api/posts/popular", methods=["GET"])
def get_popular_posts():
    tag = request.args.get("tag")
    range_key = request.args.get("range")
    limit = request.args.get("limit", default=10, type=int)

    if not tag or not range_key:
        return jsonify({"error": "Both 'tag' and 'range' query parameters are required."}), 400

    if range_key not in RANGE_MAP:
        return jsonify({"error": f"Invalid range value '{range_key}'."}), 400

    start_date = datetime.now() - RANGE_MAP[range_key]

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.title, p.url, p.author, p.points, p.created_at
                FROM hn_posts p
                JOIN hn_tags t ON p.id = t.post_id
                WHERE t.tag = %s AND p.created_at >= %s
                ORDER BY p.points DESC
                LIMIT %s
            """, (tag.lower(), start_date, limit))
            rows = cur.fetchall()

    results = [
        {
            "id": row["id"],
            "title": row["title"],
            "url": row["url"],
            "author": row["author"],
            "points": row["points"],
            "created_at": row["created_at"].isoformat()
        }
        for row in rows
    ]

    return jsonify(results)
