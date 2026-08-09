import numpy as np, pandas as pd, sys
sys.path.insert(0,"src")
import rv
from scipy import stats

MU1   = np.sqrt(2/np.pi)
THETA = (np.pi**2)/4 + np.pi - 5

def bns_log(ticker, step=1, min_bars=12, alpha=0.01):
    df = rv.load(ticker)
    out = []
    for d, g in df.groupby("date"):
        g = g.sort_values("dt").iloc[::step]
        r = np.diff(np.log(g.close.values))
        M = len(r)
        if M < min_bars: continue
        a = np.abs(r)
        RV = np.sum(r**2)
        BV = (MU1**-2)*np.sum(a[:-1]*a[1:])
        TP = M*(MU1**-3)*(M/(M-2))*np.sum(a[2:]**(4/3)*a[1:-1]**(4/3)*a[:-2]**(4/3))
        if RV <= 0 or BV <= 0 or TP <= 0: continue
        z = (np.log(RV)-np.log(BV))/np.sqrt(THETA*(1/M)*max(TP/BV**2,1.0))
        out.append({"date":d,"rv":RV,"bv":BV,"z":z,
                    "jump":int(1-stats.norm.cdf(z) < alpha)})
    return pd.DataFrame(out, columns=["date","rv","bv","z","jump"])

if __name__ == "__main__":
    groups = {"treated":["IREN","RIOT","CLSK","BE"],
              "control":["MSFT","JNJ","KO"]}
    print(f"{'group':9s}{'5min':>8s}{'10min':>8s}{'15min':>8s}{'30min':>8s}")
    for gname, tks in groups.items():
        rates = []
        for step in [1,2,3,6]:
            vals = []
            for t in tks:
                d = bns_log(t, step)
                if len(d): vals.append(d.jump.mean())
            rates.append(np.mean(vals) if vals else float("nan"))
        print(f"{gname:9s}" + "".join(f"{r*100:7.1f}%" for r in rates))
