import numpy as np, sys
sys.path.insert(0, "src")
from kelly import kelly_continuous, growth_rate

def mu_standard_error(sigma, years):
    """SE of the drift estimate. Does not shrink with finer sampling."""
    return sigma / np.sqrt(years)

def kelly_distribution(mu, sigma, days, r=0.04, n=20000, seed=0):
    """Kelly leverage you would estimate from `days` of data."""
    rng = np.random.default_rng(seed)
    se = mu_standard_error(sigma, days/252)
    mu_hat = rng.normal(mu, se, n)
    return (mu_hat - r) / sigma**2
