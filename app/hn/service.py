import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from collections import Counter
from app.db import db_conn
from .tags import TECH_TAGS


def scrape_hackernews():
    url = "https://news.ycombinator.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select(".athing")
    posts = []

    for item in items:
        title_tag = item.select_one(".titleline > a")
        if not title_tag:
            continue

        post_id = item["id"]
        title = title_tag.get_text(strip=True)
        url = title_tag["href"]
        author = item.find_next_sibling("tr").select_one(".hnuser")
        points = item.find_next_sibling("tr").select_one(".score")

        posts.append(
            {
                "id": post_id,
                "title": title,
                "url": url,
                "author": author.text if author else None,
                "points": int(points.text.replace(" points", "")) if points else 0,
                "created_at": datetime.now().isoformat(),
            }
        )

    save_posts(posts)
    return posts


def save_daily_tag_statistics(tag_list):
    counter = Counter(tag_list)
    today = date.today()
    with db_conn() as conn:
        with conn.cursor() as cur:
            for tag, count in counter.items():
                cur.execute(
                    """
                INSERT INTO hn_tag_statistics (tag, date, count)
                VALUES (%s, %s, %s)
                ON CONFLICT (tag, date)
                DO UPDATE SET count = hn_tag_statistics.count + EXCLUDED.count
            """,
                    (tag, today, count),
                )
        conn.commit()


def get_tag_history_service(tag):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT date, count
            FROM hn_tag_statistics
            WHERE tag = %s
            ORDER BY date ASC
        """,
                (tag,),
            )
            history = cur.fetchall()
    
    # Create a dictionary of existing data for quick lookup
    existing_data = {row["date"]: row["count"] for row in history}
    
    # Generate all dates from July 15, 2025 to today
    start_date = date(2025, 7, 15)
    end_date = date.today()
    
    complete_history = []
    current_date = start_date
    
    while current_date <= end_date:
        count = existing_data.get(current_date, 0)  # Use 0 if no data exists
        complete_history.append({
            "date": current_date,
            "count": count
        })
        current_date += timedelta(days=1)
    
    return complete_history


def get_all_tags_with_counts(limit=50):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT tag, SUM(count) as total_count
            FROM hn_tag_statistics
            GROUP BY tag
            ORDER BY total_count DESC
            LIMIT %s
        """,
                (limit,),
            )
            tags = cur.fetchall()
    return [{"tag": row["tag"], "count": row["total_count"]} for row in tags]


def get_popular_tags_by_period(period: str, limit=50):
    today = date.today()

    periods = {
        "1d": timedelta(days=1),
        "3d": timedelta(days=3),
        "1w": timedelta(weeks=1),
        "2w": timedelta(weeks=2),
        "1m": timedelta(days=30),
    }

    if period not in periods:
        raise ValueError("Invalid period specified")

    from_date = today - periods[period]

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tag, SUM(count) as total_count
                FROM hn_tag_statistics
                WHERE date >= %s
                GROUP BY tag
                ORDER BY total_count DESC
                LIMIT %s;
            """, (from_date, limit))
            rows = cur.fetchall()

    return [{"tag": row["tag"], "count": row["total_count"]} for row in rows]


def get_popular_posts_by_period_and_tag(tag: str, period: str, page: int = 1, per_page: int = 12):
    today = date.today()

    periods = {
        "1d": timedelta(days=1),
        "3d": timedelta(days=3),
        "1w": timedelta(weeks=1),
        "2w": timedelta(weeks=2),
        "1m": timedelta(days=30),
    }

    if period not in periods:
        raise ValueError("Invalid period specified")

    from_date = today - periods[period]
    from_datetime = datetime.combine(from_date, datetime.min.time())
    offset = (page - 1) * per_page

    with db_conn() as conn:
        with conn.cursor() as cur:
            # Get total count for pagination info
            cur.execute("""
                SELECT COUNT(*) as count
                FROM hn_posts p 
                JOIN hn_tags t ON p.id = t.post_id
                WHERE t.tag = %s AND p.created_at >= %s;
            """, (tag.lower(), from_datetime.isoformat()))
            result = cur.fetchone()
            total_count = result['count'] if result else 0

            # Get paginated posts
            cur.execute("""
                SELECT p.id, p.title, p.url, p.author, p.points, p.created_at
                FROM hn_posts p
                JOIN hn_tags t ON p.id = t.post_id
                WHERE t.tag = %s AND p.created_at >= %s
                ORDER BY p.points DESC
                LIMIT %s OFFSET %s;
            """, (tag.lower(), from_datetime.isoformat(), per_page, offset))
            rows = cur.fetchall()

    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    return {
        "posts": [dict(row) for row in rows],
        "pagination": {
            "current_page": page,
            "per_page": per_page,
            "total_posts": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


def save_posts(posts):
    with db_conn() as conn:
        with conn.cursor() as cur:
            # Insert or update posts
            for post in posts:
                cur.execute(
                    """
                INSERT INTO hn_posts (id, title, url, author, points, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET points = hn_posts.points + EXCLUDED.points
            """,
                    (
                        post["id"],
                        post["title"],
                        post["url"],
                        post["author"],
                        post["points"],
                        post["created_at"],
                    ),
                )

            # Extract and insert tags
            all_tags = []
            for post in posts:
                tags = extract_tags(post["title"])
                all_tags.extend(tags)
                for tag in tags:
                    cur.execute(
                        """
                    INSERT INTO hn_tags (tag, post_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """,
                        (tag.lower(), post["id"]),
                    )
            # Save daily tag statistics
            save_daily_tag_statistics(all_tags)
        conn.commit()


def extract_tags(title):
    found = [tag for tag in TECH_TAGS if tag.lower() in title.lower()]
    return found
