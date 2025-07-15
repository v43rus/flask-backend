import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
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

        post_id = item['id']
        title = title_tag.get_text(strip=True)
        url = title_tag['href']
        author = item.find_next_sibling("tr").select_one(".hnuser")
        points = item.find_next_sibling("tr").select_one(".score")

        posts.append({
            "id": post_id,
            "title": title,
            "url": url,
            "author": author.text if author else None,
            "points": int(points.text.replace(" points", "")) if points else 0,
            "created_at": datetime.now().isoformat()
        })

    save_posts(posts)
    return posts


def save_daily_tag_statistics(tag_list):
    counter = Counter(tag_list)
    today = date.today()
    with db_conn() as conn:
      with conn.cursor() as cur:
        for tag, count in counter.items():
            cur.execute("""
                INSERT INTO hn_tag_statistics (tag, date, count)
                VALUES (%s, %s, %s)
                ON CONFLICT (tag, date)
                DO UPDATE SET count = hn_tag_statistics.count + EXCLUDED.count
            """, (tag, today, count))
      conn.commit()


def get_tag_history_service(tag):
    with db_conn() as conn:
      with conn.cursor() as cur:
        cur.execute("""
            SELECT date, count
            FROM hn_tag_statistics
            WHERE tag = %s
            ORDER BY date ASC
        """, (tag,))
        history = cur.fetchall()
    return [{"date": row["date"], "count": row["count"]} for row in history]


def get_all_tags_with_counts(limit=50):
    with db_conn() as conn:
      with conn.cursor() as cur:
        cur.execute("""
            SELECT tag, SUM(count) as total_count
            FROM hn_tag_statistics
            GROUP BY tag
            ORDER BY total_count DESC
            LIMIT %s
        """, (limit,))
        tags = cur.fetchall()
    return [{"tag": row["tag"], "count": row["total_count"]} for row in tags]


def save_posts(posts):
    with db_conn() as conn:
      with conn.cursor() as cur:
        # Insert or update posts
        for post in posts:
            cur.execute("""
                INSERT INTO hn_posts (id, title, url, author, points, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET points = hn_posts.points + EXCLUDED.points
            """, (
                post["id"],
                post["title"],
                post["url"],
                post["author"],
                post["points"],
                post["created_at"]
            ))

        # Extract and insert tags
        all_tags = []
        for post in posts:
            tags = extract_tags(post["title"])
            all_tags.extend(tags)
            for tag in tags:
                cur.execute("""
                    INSERT INTO hn_tags (tag, post_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (tag.lower(), post["id"]))
        # Save daily tag statistics
        save_daily_tag_statistics(all_tags)
      conn.commit()


def extract_tags(title):
    found = [tag for tag in TECH_TAGS if tag.lower() in title.lower()]
    return found