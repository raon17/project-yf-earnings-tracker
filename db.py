import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
 
load_dotenv()

def get_db_connection():    
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor
    )
    return conn

DDL = """
CREATE TABLE IF NOT EXISTS earnings (
    ticker  TEXT PRIMARY KEY,
    company TEXT,
    sector  TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW()
"""

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()