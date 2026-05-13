import yfinance as yf
import pandas as pd
from datetime import date

from db import upsert_stock


def fetch_ticker(ticker: str):
    #   https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.html
    ticker = ticker.upper()
    try:
        t = yf.Ticker(ticker)
        
        info = t.info or {}
        company = info.get("longName") or info.get("shortName") or ticker
        sector  = info.get("sector", "Unknown")
        
        df = t.earnings_dates
        if df is None or df.empty:
            return ticker, 0, "No earnings data"
        
        df.columns = [i.strip() for i in df.columns]

        upsert_stock(ticker, company, sector)
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

if __name__ == "__main__":
    fetch_ticker("NVDA")