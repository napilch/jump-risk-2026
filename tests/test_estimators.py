import numpy as np, sys
sys.path.insert(0, "src")
from calib import z_stat
from logtest import MU1

def rv_bv(r):
    a = np.abs(r)
    return np.sum(r**2), (MU1**-2)*np.sum(a[:-1]*a[1:])

def test_bv_matches_rv_without_jumps():
    rng = np.random.default_rng(42)
    rv_s, bv_s = [], []
    for _ in range(3000):
        RV, BV = rv_bv(rng.normal(0, 0.01, 78))
        rv_s.append(RV)
        bv_s.append(BV)
    ratio = np.mean(bv_s)/np.mean(rv_s)
    assert 0.95 < ratio < 1.05

def test_bv_ignores_a_jump():
    rng = np.random.default_rng(7)
    base = rng.normal(0, 0.01, 78)
    RV0, BV0 = rv_bv(base)
    jumped = base.copy()
    jumped[40] = jumped[40] + 0.15
    RV1, BV1 = rv_bv(jumped)
    assert RV1 > 2*RV0
    assert BV1 < 1.5*BV0

def test_statistic_is_standard_normal_under_null():
    rng = np.random.default_rng(1)
    z = np.array([z_stat(rng.normal(0, 0.01, 78)) for _ in range(5000)])
    z = z[~np.isnan(z)]
    assert abs(np.mean(z)) < 0.25
    assert 0.7 < np.std(z) < 1.4

def test_power_against_jumps():
    rng = np.random.default_rng(3)
    hits = 0
    for _ in range(500):
        r = rng.normal(0, 0.01, 78)
        r[rng.integers(5, 70)] += 0.08
        if z_stat(r) > 2.84:
            hits += 1
    assert hits/500 > 0.5
