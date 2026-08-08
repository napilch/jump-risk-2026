import os, time, requests, pandas as pd

KEY  = os.environ.get("POLYGON_KEY")
BASE = "https://api.polygon.io/v2/aggs/ticker"

def _one(ticker, start, end, mult=5, span="minute"):
    url = f"{BASE}/{ticker}/range/{mult}/{span}/{start}/{end}"
    r = requests.get(url, params={"adjusted":"true","sort":"asc",
                                  "limit":50000,"apiKey":KEY}, timeout=30)
    r.raise_for_status()
    js = r.json()
    if js.get("resultsCount", 0) == 0:
        return pd.DataFrame()
    return pd.DataFrame(js["results"])

def fetch(ticker, start="2026-04-01", end="2026-08-07"):
    """Fetch 5-min bars in monthly chunks to dodge the 50k row cap."""
    months = pd.date_range(start, end, freq="MS").union(
             pd.DatetimeIndex([start, end]))
    parts = []
    for a, b in zip(months[:-1], months[1:]):
        df = _one(ticker, a.strftime("%Y-%m-%d"), b.strftime("%Y-%m-%d"))
        if len(df): parts.append(df)
        time.sleep(13)
    if not parts:
        raise ValueError(f"no data for {ticker}")
    out = pd.concat(parts).drop_duplicates(subset="t").sort_values("t")
    out["t"] = pd.to_datetime(out["t"], unit="ms", utc=True
                 ).dt.tz_convert("America/New_York")
    return out.rename(columns={"t":"dt","o":"open","h":"high",
                               "l":"low","c":"close","v":"volume"}
                     ).reset_index(drop=True)

if __name__ == "__main__":
    if not KEY: raise SystemExit("POLYGON_KEY not set")
    for tkr in ["NVDA", "SMH"]:
        df = fetch(tkr)
        df.to_csv(f"data/{tkr}_5m.csv", index=False)
        print(f"OK {tkr:6s} rows={len(df):6d} "
              f"first={df.dt.iloc[0]} last={df.dt.iloc[-1]}")

TICKERS = ["NVDA","SMH","CRWV","IREN","CORZ","APLD","BE","RIOT","CLSK",
           "MSFT","JNJ","KO"]

def fetch_all():
    import os
    for t in TICKERS:
        path = f"data/{t}_5m.csv"
        if os.path.exists(path):
            print(f"skip {t}"); continue
        try:
            df = fetch(t)
            df.to_csv(path, index=False)
            print(f"OK {t:6s} rows={len(df):6d} last={df.dt.iloc[-1]}")
        except Exception as e:
            print(f"FAIL {t:6s} {type(e).__name__}: {e}")
