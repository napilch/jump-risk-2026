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
