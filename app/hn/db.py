import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)

def save_posts(posts):
    conn = get_db_connection()
    with conn.cursor() as cur:
        for post in posts:
            cur.execute("""
                INSERT INTO posts (id, title, url, author, points, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (post["id"], post["title"], post["url"], post["author"], post["points"], post["created_at"]))
    conn.commit()
    conn.close()
