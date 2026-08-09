import numpy as np, sys
sys.path.insert(0,"src")
from scipy import stats
from logtest import MU1, THETA

def z_stat(r, min_bars=12):
    M = len(r)
    if M < min_bars: return np.nan
    a = np.abs(r)
    RV = np.sum(r**2)
    BV = (MU1**-2)*np.sum(a[:-1]*a[1:])
    TP = M*(MU1**-3)*(M/(M-2))*np.sum(a[2:]**(4/3)*a[1:-1]**(4/3)*a[:-2]**(4/3))
    if RV<=0 or BV<=0 or TP<=0: return np.nan
    return (np.log(RV)-np.log(BV))/np.sqrt(THETA*(1/M)*max(TP/BV**2,1.0))

def simulate(M, n=20000, sigma=0.30, seed=0):
    """Pure diffusion, NO jumps. Returns z-stats under the true null."""
    rng = np.random.default_rng(seed)
    sd = sigma/np.sqrt(252*M)
    return np.array([z_stat(rng.normal(0, sd, M)) for _ in range(n)])

if __name__ == "__main__":
    print(f"{'bars/day':>9s}{'nominal':>9s}{'actual':>9s}{'crit(1%)':>10s}")
    for M, label in [(78,'5min'),(39,'10min'),(26,'15min'),(13,'30min')]:
        z = simulate(M)
        z = z[~np.isnan(z)]
        actual = (1-stats.norm.cdf(z) < 0.01).mean()
        crit   = np.quantile(z, 0.99)
        print(f"{label:>9s}{'1.0%':>9s}{actual*100:8.1f}%{crit:10.2f}")
