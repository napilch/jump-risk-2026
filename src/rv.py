import numpy as np, pandas as pd, glob, os

def load(ticker):
    df = pd.read_csv(f"data/{ticker}_5m.csv", parse_dates=["dt"])
    df["dt"] = pd.to_datetime(df["dt"], utc=True).dt.tz_convert("America/New_York")
    # regular trading hours only: 09:30-16:00
    df = df.set_index("dt").between_time("09:30", "16:00").reset_index()
    df["date"] = df.dt.dt.date
    return df

def daily_rv(ticker, min_bars=50):
    """Realized variance and bipower variation per day."""
    df = load(ticker)
    out = []
    for d, g in df.groupby("date"):
        g = g.sort_values("dt")
        r = np.diff(np.log(g.close.values))      # 5-min log returns
        if len(r) < min_bars: continue
        rv = np.sum(r**2)
        mu1 = np.sqrt(2/np.pi)
        bv = (mu1**-2) * np.sum(np.abs(r[:-1]) * np.abs(r[1:]))
        out.append({"date": d, "n": len(r), "rv": rv, "bv": bv,
                    "jump": max(rv - bv, 0.0)})
    return pd.DataFrame(out)

if __name__ == "__main__":
    for t in ["NVDA","SMH","IREN","MSFT"]:
        d = daily_rv(t)
        print(f"{t:6s} days={len(d):4d}  "
              f"ann.vol={np.sqrt(d.rv.mean()*252)*100:5.1f}%  "
              f"jump share={d.jump.sum()/d.rv.sum()*100:4.1f}%")
