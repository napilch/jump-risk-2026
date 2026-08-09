import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd, sys
sys.path.insert(0,"src")
from corrected import jumps_corrected

TREATED = ["IREN","RIOT","CLSK","BE"]
CONTROL = ["MSFT","JNJ","KO"]
PEAK    = pd.Timestamp("2026-06-22")

def fig_timeline():
    fig, axes = plt.subplots(2,1, figsize=(11,7), sharex=True)
    for ax, tks, name in [(axes[0],TREATED,"AI infrastructure (SA holdings)"),
                          (axes[1],CONTROL,"Control (non-AI large cap)")]:
        for t in tks:
            d = jumps_corrected(t)
            d["date"] = pd.to_datetime(d.date)
            ax.plot(d.date, np.sqrt(d.rv*252)*100, lw=1, alpha=.75, label=t)
            j = d[d.jump==1]
            ax.scatter(j.date, np.sqrt(j.rv*252)*100, s=22, zorder=5,
                       facecolors="none", edgecolors="black", lw=.8)
        ax.axvline(PEAK, color="red", ls="--", lw=1)
        ax.set_title(name, fontsize=10, loc="left")
        ax.set_ylabel("annualised vol (%)")
        ax.legend(fontsize=7, ncol=4, frameon=False)
    axes[1].set_xlabel("")
    fig.suptitle("Realised volatility, circles mark significant jump days",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig("figures/fig1_timeline.png", dpi=150)
    print("saved fig1")

def fig_robustness():
    labels = ["5min","10min","15min","30min"]
    steps  = [1,2,3,6]
    fig, ax = plt.subplots(figsize=(7,4.5))
    for tks, name, c in [(TREATED,"treated","tab:red"),
                         (CONTROL,"control","tab:blue")]:
        rates = [np.mean([jumps_corrected(t,s).jump.mean() for t in tks])*100
                 for s in steps]
        ax.plot(labels, rates, "o-", color=c, label=name)
    ax.axhline(2.5, color="grey", ls=":", lw=1)
    ax.text(0, 2.7, "simulated false-positive rate", fontsize=8, color="grey")
    ax.set_ylabel("jump days (%)"); ax.set_ylim(0, None)
    ax.legend(frameon=False)
    ax.set_title("Jump frequency by sampling interval", fontsize=11, loc="left")
    fig.tight_layout(); fig.savefig("figures/fig2_robustness.png", dpi=150)
    print("saved fig2")

def fig_size():
    labels = ["5min","10min","15min","30min"]
    actual = [2.5, 3.5, 3.9, 5.9]
    crit   = [2.84, 3.04, 3.28, 3.82]
    fig, ax = plt.subplots(figsize=(7,4.5))
    ax.bar(labels, actual, color="tab:orange", label="actual size")
    ax.axhline(1.0, color="black", ls="--", lw=1, label="nominal 1%")
    for i,(a,c) in enumerate(zip(actual,crit)):
        ax.text(i, a+.12, f"crit={c}", ha="center", fontsize=8)
    ax.set_ylabel("rejection rate under no-jump null (%)")
    ax.legend(frameon=False)
    ax.set_title("BNS test is oversized in finite samples", fontsize=11, loc="left")
    fig.tight_layout(); fig.savefig("figures/fig3_size.png", dpi=150)
    print("saved fig3")

if __name__ == "__main__":
    fig_timeline(); fig_robustness(); fig_size()
