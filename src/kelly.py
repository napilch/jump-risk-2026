import numpy as np

def kelly_discrete(p, b):
    """Optimal fraction for a bet paying b-to-1 with win prob p."""
    return (p*b - (1-p)) / b

def kelly_continuous(mu, sigma, r=0.0):
    """Optimal leverage for drift mu, vol sigma, risk-free r."""
    return (mu - r) / sigma**2

def growth_rate(f, mu, sigma, r=0.0):
    """Expected log growth rate at leverage f."""
    return r + f*(mu - r) - 0.5*(f**2)*(sigma**2)
