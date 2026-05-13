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
CREATE TABLE IF NOT EXISTS stocks (
    ticker  TEXT PRIMARY KEY,
    company TEXT,
    sector  TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS earnings (
    id SERIAL PRIMARY KEY,
    ticker TEXT REFERENCES stocks(ticker) ON DELETE CASCADE, -- foreign key to stocks table
    fiscal_quarter TEXT,   
    report_date DATE,
    eps_estimate NUMERIC(10,4),
    eps_actual NUMERIC(10,4),
    surprise_pct NUMERIC(8,4),
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, fiscal_quarter) -- prevent duplicate entries for the same quarter
);
CREATE INDEX IF NOT EXISTS idx_earnings_ticker ON earnings(ticker);
CREATE INDEX IF NOT EXISTS idx_earnings_report_date ON earnings(report_date);
"""

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()

# -- Stock management functions --
def upsert_stock(ticker: str, company: str, sector: str = "Unknown"):
    sql = """
        INSERT INTO stocks (ticker, company, sector)
        VALUES (%s, %s, %s)
        ON CONFLICT (ticker) DO UPDATE
            SET company = EXCLUDED.company, -- update company name if ticker already exists
                sector  = EXCLUDED.sector -- update sector if ticker already exists
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (ticker.upper(), company, sector))
        conn.commit()
 
def get_watchlist():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM stocks ORDER BY ticker")
            return cur.fetchall()
 
def delete_stock(ticker: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM stocks WHERE ticker = %s", (ticker.upper(),))
        conn.commit()

