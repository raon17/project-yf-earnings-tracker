import yfinance as yf
import pandas as pd
from datetime import date

from db import upsert_earnings, upsert_stock

def _quarter_label(dt) -> str:
    #   Convert a Timestamp to 'Q1 YYYY' format
    month = dt.month
    q = (month - 1) // 3 + 1
    return f"Q{q} {dt.year}"
 
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
        
        rows = []
        for ts, row in df.iterrows():
            est  = row.get("EPS Estimate")
            act  = row.get("Reported EPS")
            surp = row.get("Surprise(%)")
 
            rows.append({
                "ticker":         ticker,
                "report_date":    ts.date(),
                "eps_estimate":   None if pd.isna(est)  else float(est),
                "eps_actual":     None if pd.isna(act)  else float(act),
                "surprise_pct":   None if pd.isna(surp) else float(surp),
                "fiscal_quarter": _quarter_label(ts)
            })

            upsert_earnings(rows)
            return ticker, len(rows), ""
 
    except Exception as e:
        return ticker, 0, str(e)


if __name__ == "__main__":
    fetch_ticker("NVDA")