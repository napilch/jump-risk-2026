import numpy as np, pandas as pd, sys
sys.path.insert(0,"src")
from logtest import bns_log

CRIT = {1: 2.84, 2: 3.04, 3: 3.28, 6: 3.82}

def jumps_corrected(ticker, step=1):
    d = bns_log(ticker, step, alpha=1.0)
    d["jump"] = (d.z > CRIT[step]).astype(int)
    return d

if __name__ == "__main__":
    groups = {"treated":["IREN","RIOT","CLSK","BE"],
              "control":["MSFT","JNJ","KO"]}
    print(f"{'group':9s}{'5min':>8s}{'10min':>8s}{'15min':>8s}{'30min':>8s}")
    for gname, tks in groups.items():
        rates = []
        for step in [1,2,3,6]:
            vals = []
            for t in tks:
                d = jumps_corrected(t, step)
                if len(d): vals.append(d.jump.mean())
            rates.append(np.mean(vals) if vals else float("nan"))
        print(f"{gname:9s}" + "".join(f"{r*100:7.1f}%" for r in rates))
