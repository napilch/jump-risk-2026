import numpy as np, pandas as pd, sys
sys.path.insert(0,"src")
import rv
from scipy import stats

def bns_at(ticker, step=1, min_bars=12, alpha=0.01):
    """BNS test after sub-sampling every `step`-th 5-min bar."""
    df = rv.load(ticker)
    mu1 = np.sqrt(2/np.pi); theta = (np.pi**2)/4 + np.pi - 5
    out = []
    for d, g in df.groupby("date"):
        g = g.sort_values("dt").iloc[::step]
        r = np.diff(np.log(g.close.values)); M = len(r)
        if M < min_bars: continue
        a = np.abs(r)
        RV = np.sum(r**2)
        BV = (mu1**-2)*np.sum(a[:-1]*a[1:])
        QP = (mu1**-4)*M/(M-3)*np.sum(a[3:]*a[2:-1]*a[1:-2]*a[:-3])
        if RV <= 0 or BV <= 0: continue
        RJ = (RV-BV)/RV
        z  = RJ/np.sqrt(theta*max(QP/BV**2,1.0)/M)
        out.append({"date":d,"z":z,"jump":int(1-stats.norm.cdf(z) < alpha)})
    return pd.DataFrame(out, columns=["date","z","jump"])

if __name__ == "__main__":
    groups = {"treated":["IREN","RIOT","CLSK","BE"],
              "control":["MSFT","JNJ","KO"]}
    print(f"{'group':9s}{'5min':>8s}{'10min':>8s}{'15min':>8s}{'30min':>8s}")
    for gname, tks in groups.items():
        rates = []
        for step in [1,2,3,6]:
            vals = []
            for t in tks:
                d = bns_at(t, step)
                if len(d): vals.append(d.jump.mean())
            rates.append(np.mean(vals) if vals else float("nan"))
        print(f"{gname:9s}" + "".join(f"{r*100:7.1f}%" for r in rates))
