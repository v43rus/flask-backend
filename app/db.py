import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


@contextmanager
def db_conn():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
