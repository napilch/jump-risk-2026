import numpy as np, pandas as pd, sys
sys.path.insert(0, "src")
import rv
from kelly import kelly_continuous

PEAK = pd.Timestamp("2026-06-22").date()

def daily_closes(ticker):
    """Daily close prices from the 5-min bars."""
    df = rv.load(ticker)
    return df.groupby("date").close.last()

def estimate(ticker, end=PEAK):
    """Annualised mu and sigma from log returns before `end`."""
    px = daily_closes(ticker)
    px = px[px.index < end]
    lr = np.diff(np.log(px.values))
    mu = lr.mean()*252 + 0.5*lr.var(ddof=1)*252
    sigma = lr.std(ddof=1)*np.sqrt(252)
    return mu, sigma, len(lr)

def path_after(ticker, start=PEAK):
    """Daily log returns from `start` onward."""
    px = daily_closes(ticker)
    px = px[px.index >= start]
    return np.diff(np.log(px.values))

def run_levered(returns, f, r=0.04, mmr=0.25):
    """Levered path with explicit assets and debt.
    Start: equity 1, assets f, debt f-1.
    Liquidate when equity/assets falls below mmr."""
    assets = float(f)
    debt = float(f) - 1.0
    for i, x in enumerate(returns):
        assets *= np.exp(x)
        debt *= np.exp(r/252)
        eq = assets - debt
        if eq <= 0:
            return 0.0, True, i
        if debt > 0 and eq/assets < mmr:
            return eq, True, i
    return assets - debt, False, -1
