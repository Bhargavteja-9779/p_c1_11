"""Figures 1-4 (+ S1) from a results directory written by exp_final.py + exp_extra.py.
Usage: python scripts/make_figures.py RESULTS_DIR FIG_OUT_DIR"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

RD, FO = sys.argv[1], sys.argv[2]; os.makedirs(FO, exist_ok=True)
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
S = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.axisbelow": True, "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False})
R = pd.read_csv(f"{RD}/alarm_results.csv"); X = pd.read_csv(f"{RD}/extra/sa_theory_alarm_results.csv")
SW = pd.read_csv(f"{RD}/extra/delta_sweep_seed0.csv"); EC = pd.read_csv(f"{RD}/extra/event_counts_theory.csv")
AB = pd.read_csv(f"{RD}/extra/ablation_nohist_bootstrap_seed0.csv")
internal = [c for c in R.cohort.unique() if c.startswith("MIMIC")][0]
COH = [internal, "eICU", "VitalDB"]; LAB = {internal: "MIMIC-III (ICU, internal test)" if "test" in internal else "MIMIC-III (ICU, validation)",
                                            "eICU": "eICU (ICU, external)", "VitalDB": "VitalDB (operating room, external)"}
XT = X[X.method.str.startswith("SA-theory[train]")]
ALL = pd.concat([R, XT[R.columns.intersection(XT.columns)]], ignore_index=True)
NAMES = {"MAP": "Low-MAP alarm", "LR": "Logistic regression", "GBM": "Gradient boosting (GBM)", "GRU": "GRU", "FP": "First-passage",
         "SA-kappa[newGBM]": "State-aware, κ (primary)", "SA-delta[newGBM]": "State-aware, δ tuned", "SA-theory[train]": "State-aware, δ* theory"}
def save(fig, name):
    fig.savefig(f"{FO}/{name}.png", dpi=300, bbox_inches="tight"); fig.savefig(f"{FO}/{name}.pdf", bbox_inches="tight"); plt.close(fig)

# Figure 1: event mix and where the alarms go
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), sharey=True)
for ax, co in zip(axes, COH):
    e = EC[EC.cohort == co].iloc[0]; g = ALL[(ALL.cohort == co) & (ALL.burden_target == 1.0)]
    vals = [e.N_new / (e.N_new + e.N_rec), g[g.method == "GBM"].hours_share_A.mean(), g[g.method == "GBM"].alarm_share_A.mean(),
            g[g.method == "SA-theory[train]"].alarm_share_A.mean()]
    labs = ["Events that are\nnew-onset", "Monitored time\nwithout recent event", "GBM alarms in\nthat time", "State-aware alarms\nin that time"]
    cols = [S[1], INK2, S[0], S[2]]
    ax.barh(range(4), vals, color=cols, height=0.6)
    for i, v in enumerate(vals): ax.text(v + 0.02, i, f"{v:.0%}", va="center", color=INK, fontsize=7.5)
    ax.set_yticks(range(4)); ax.set_yticklabels(labs); ax.invert_yaxis(); ax.set_xlim(0, 1.05); ax.set_title(LAB[co], fontsize=8, color=INK)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0)); ax.grid(axis="y", visible=False)
fig.tight_layout(); save(fig, "Figure1_event_mix_alarm_allocation")

# Figure 2: new-onset vs recurrent sensitivity at 1 alarm/h (mean ± SD over seeds)
order = ["MAP", "FP", "LR", "GRU", "GBM", "SA-kappa[newGBM]", "SA-delta[newGBM]", "SA-theory[train]"]
fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.0), sharey=True)
for ax, co in zip(axes, COH):
    g = ALL[(ALL.cohort == co) & (ALL.burden_target == 1.0)]
    for i, m in enumerate(order):
        h = g[g.method == m]
        if not len(h): continue
        for j, (col, c, mk) in enumerate((("sensitivity_new", S[1], "o"), ("sensitivity_recurrent", S[0], "s"))):
            mu, sd = h[col].mean(), h[col].std() if len(h) > 1 else 0
            ax.errorbar(mu, i + (j - 0.5) * 0.28, xerr=sd, fmt=mk, ms=4.5, color=c, ecolor=c, elinewidth=1, capsize=0,
                        label=("New-onset events" if j == 0 else "Recurrent events") if (i == 0 and co == COH[0]) else None)
    mp = g[g.method == "MAP"].sensitivity_new.mean(); ax.axvline(mp, color=S[1], lw=0.8, ls=":")
    ax.set_yticks(range(len(order))); ax.set_yticklabels([NAMES[m] for m in order]); ax.invert_yaxis()
    ax.set_title(LAB[co], fontsize=8, color=INK); ax.set_xlabel("Events warned 5–15 min ahead")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0)); ax.grid(axis="y", visible=False)
fig.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.09)); fig.tight_layout(); save(fig, "Figure2_new_onset_vs_recurrent")

# Figure 3: theory — frontier traced by the state-A offset delta, with delta* and comparators
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6))
dtr = EC.delta_theory_train.iloc[0]
for ax, co in zip(axes, COH):
    s = SW[SW.cohort == co].sort_values("delta"); g = ALL[(ALL.cohort == co) & (ALL.burden_target == 1.0) & (ALL.seed == ALL.seed.min())]
    ax.plot(s.sensitivity_recurrent, s.sensitivity_new, color=INK2, lw=1.5, zorder=1)
    ax.scatter(s.sensitivity_recurrent, s.sensitivity_new, s=9, color=INK2, zorder=2)
    b = s.loc[s.J.idxmax()]; ax.scatter(b.sensitivity_recurrent, b.sensitivity_new, s=50, facecolor="none", edgecolor=INK, lw=1.2, zorder=3, label="Best δ (oracle)")
    t = g[g.method == "SA-theory[train]"].iloc[0]; ax.scatter(t.sensitivity_recurrent, t.sensitivity_new, s=40, color=S[2], marker="D", zorder=4, edgecolor=SURF, lw=1, label=f"δ* = log(Nrec/Nnew) = {dtr:.2f}")
    for m, c, mk, lb in (("GBM", S[0], "s", "GBM, pooled threshold"), ("MAP", S[1], "o", "Low-MAP alarm")):
        r = g[g.method == m].iloc[0]; ax.scatter(r.sensitivity_recurrent, r.sensitivity_new, s=36, color=c, marker=mk, zorder=4, edgecolor=SURF, lw=1, label=lb)
    ax.set_title(LAB[co], fontsize=8, color=INK); ax.set_xlabel("Recurrent events warned"); ax.set_ylabel("New-onset events warned" if co == COH[0] else "")
    for a in (ax.xaxis, ax.yaxis): a.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.07), fontsize=7)
fig.tight_layout(); save(fig, "Figure3_theory_frontier")

# Figure 4: mechanism ablation (GBM without >=60-min history features minus GBM), seed 0, patient bootstrap 95% CI
fig, ax = plt.subplots(figsize=(4.2, 2.4))
mets = [("sensitivity_new", "New-onset", S[1]), ("sensitivity_recurrent", "Recurrent", S[0]), ("sensitivity", "All events", INK2)]
for i, co in enumerate(COH):
    for j, (m, lb, c) in enumerate(mets):
        r = AB[(AB.cohort == co) & (AB.metric == m)].iloc[0]; y = i + (j - 1) * 0.25
        ax.errorbar(r.est * 100, y, xerr=[[(r.est - r.lo) * 100], [(r.hi - r.est) * 100]], fmt="o", ms=4.5, color=c, elinewidth=1, label=lb if i == 0 else None)
ax.axvline(0, color=INK, lw=0.8); ax.set_yticks(range(3)); ax.set_yticklabels([LAB[c].split(" (")[0] for c in COH]); ax.invert_yaxis()
ax.set_xlabel("Change when history features are removed (percentage points)"); ax.grid(axis="y", visible=False)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=7); fig.tight_layout(); save(fig, "Figure4_mechanism_ablation")

# Figure S1: burden curves for new-onset sensitivity
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4), sharey=True)
for ax, co in zip(axes, COH):
    for k, (m, c) in enumerate((("MAP", S[1]), ("GBM", S[0]), ("SA-kappa[newGBM]", S[6]), ("SA-theory[train]", S[2]))):
        g = ALL[(ALL.cohort == co) & (ALL.method == m)].groupby("burden_target").sensitivity_new.mean()
        ax.plot(g.index, g.values, marker="o", ms=4, lw=2, color=c, label=NAMES[m] if co == COH[0] else None)
    ax.set_xscale("log", base=2); ax.set_xticks([0.5, 1, 2]); ax.set_xticklabels(["0.5", "1", "2"]); ax.set_xlabel("Alarms per patient-hour")
    ax.set_title(LAB[co], fontsize=8, color=INK); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
axes[0].set_ylabel("New-onset events warned"); fig.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.06), fontsize=7)
fig.tight_layout(); save(fig, "FigureS1_burden_curves")
print("figures written to", FO)
