import pandas as pd, numpy as np, sys
sys.path.insert(0, "src")
import rv

TREATED = ["CRWV","IREN","CORZ","APLD","BE","RIOT","CLSK"]
CONTROL = ["MSFT","JNJ","KO"]
SECTOR  = ["NVDA","SMH"]

def build(alpha=0.01):
    """Panel of daily RV/BV/jump flags for all tickers."""
    rows = []
    for grp, tks in [("treated",TREATED),("control",CONTROL),("sector",SECTOR)]:
        for t in tks:
            try:
                d = rv.bns_test(t)
            except Exception as e:
                print(f"skip {t}: {e}"); continue
            d["ticker"] = t
            d["group"]  = grp
            d["is_jump"] = (d.p < alpha).astype(int)
            rows.append(d)
    p = pd.concat(rows, ignore_index=True)
    p["date"] = pd.to_datetime(p["date"])
    return p

if __name__ == "__main__":
    p = build()
    p.to_csv("data/panel.csv", index=False)
    print(f"panel: {len(p)} ticker-days, {p.ticker.nunique()} tickers\n")
    print(p.groupby("group").agg(
        days=("is_jump","size"),
        jump_days=("is_jump","sum"),
        jump_rate=("is_jump","mean"),
        mean_rv=("rv","mean")).round(4))
