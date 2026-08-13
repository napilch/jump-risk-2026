import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, sys
sys.path.insert(0, "src")
from kelly import kelly_continuous, growth_rate
from leverage import estimate, path_after, run_levered

MU, SIG, R = 0.10, 0.20, 0.04
FSTAR = kelly_continuous(MU, SIG, R)

def fig_growth():
    fs = np.linspace(0, 3.2*FSTAR, 400)
    g = [growth_rate(f, MU, SIG, R)*100 for f in fs]
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.plot(fs, g, lw=1.8, color="tab:blue")
    ax.axhline(R*100, color="grey", ls=":", lw=1)
    ax.axvline(FSTAR, color="tab:green", ls="--", lw=1)
    ax.axvline(2*FSTAR, color="tab:red", ls="--", lw=1)
    ax.text(FSTAR, max(g), " f*", color="tab:green", fontsize=9, va="top")
    ax.text(2*FSTAR, max(g), " 2f*", color="tab:red", fontsize=9, va="top")
    ax.set_xlabel("leverage f")
    ax.set_ylabel("expected log growth rate (%)")
    ax.set_title("Growth returns to the risk-free rate at 2f*",
                 loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig("figures/fig4_growth.png", dpi=150)
    print("saved fig4")

TREATED = ["CORZ","RIOT","CLSK","BE","APLD","CRWV","IREN"]

def fig_ruin():
    fs = np.linspace(1, 10, 37)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    frac = []
    for f in fs:
        n = sum(run_levered(path_after(t), f, mmr=0.10)[1] for t in TREATED)
        frac.append(n/len(TREATED)*100)
    ax[0].plot(fs, frac, "o-", ms=3, color="tab:red")
    ax[0].axvline(4, color="black", ls="--", lw=1)
    ax[0].text(4, 50, " 4x", fontsize=9)
    ax[0].set_xlabel("leverage f")
    ax[0].set_ylabel("% of names force-liquidated")
    ax[0].set_title("Liquidation rate, July 2026 path", loc="left", fontsize=10)
    for t in TREATED:
        mu, sig, _ = estimate(t)
        ax[1].scatter(kelly_continuous(mu, sig, 0.04),
                      run_levered(path_after(t), 4, mmr=0.10)[0], s=28)
        ax[1].annotate(t, (kelly_continuous(mu, sig, 0.04),
                       run_levered(path_after(t), 4, mmr=0.10)[0]),
                       fontsize=7, xytext=(3,3), textcoords="offset points")
    ax[1].set_xlabel("Kelly leverage recommended pre-peak")
    ax[1].set_ylabel("equity remaining at 4x")
    ax[1].set_title("What Kelly recommended vs what survived",
                    loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig("figures/fig5_ruin.png", dpi=150)
    print("saved fig5")

from estimation_error import kelly_distribution

def fig_estimation():
    tf = FSTAR
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for d, c in [(54,"tab:red"), (252,"tab:orange"), (2520,"tab:blue")]:
        fh = kelly_distribution(MU, SIG, d)
        ax[0].hist(np.clip(fh, -8, 12), bins=90, alpha=.45,
                   density=True, color=c, label=f"{d} days")
    ax[0].axvline(tf, color="black", ls="--", lw=1)
    ax[0].axvline(2*tf, color="tab:red", ls=":", lw=1)
    ax[0].set_xlabel("estimated Kelly leverage")
    ax[0].set_ylabel("density")
    ax[0].set_title("Estimated f* on a true f* of 1.5", loc="left", fontsize=10)
    ax[0].legend(frameon=False, fontsize=8)
    days = np.array([54,126,252,504,1260,2520,5040])
    prob = [(kelly_distribution(MU,SIG,d) > 2*tf).mean()*100 for d in days]
    ax[1].semilogx(days, prob, "o-", ms=4, color="tab:red")
    ax[1].set_xlabel("days used to estimate mu")
    ax[1].set_ylabel("P(estimated f > 2f*)  %")
    ax[1].set_title("Overbetting risk barely decays", loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig("figures/fig6_estimation.png", dpi=150)
    print("saved fig6")
