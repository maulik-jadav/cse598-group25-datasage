"""Poster figures from eval/results/summary.md numbers (held-out seed 101, test seed 202)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import segno

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})

# Figure 2: answer accuracy per split.
splits = ["sales\nheld-out", "penguins\nheld-out", "sales\ntest", "penguins\ntest"]
systems = {
    "B0 stakeholder script": [0, 5, 10, 0],
    "B1 fixed cleaning script": [40, 30, 55, 35],
    "B2 single LLM call": [85, 35, 45, 50],
    "DataSage (Qwen3-30B)": [100, 85, 100, 85],
}
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=220)
w = 0.2
for i, (name, vals) in enumerate(systems.items()):
    xs = [j + (i - 1.5) * w for j in range(len(splits))]
    bars = ax.bar(xs, vals, w, label=name)
    for x, v in zip(xs, vals):
        ax.text(x, v + 1.5, f"{v}", ha="center", va="bottom", fontsize=10)
ax.axhline(90, ls="--", lw=1, color="gray")
ax.text(-0.45, 91.5, "goal 90%", color="gray", fontsize=10, ha="left")
ax.set_xticks(range(len(splits)), splits)
ax.set_ylabel("Answer correct (%)")
ax.set_ylim(0, 112)
ax.legend(ncol=2, fontsize=10.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.2))
fig.tight_layout()
fig.savefig(out / "fig_accuracy.png")

# Figure 3: accuracy vs seconds per question (held-out, mean of the two datasets).
pts = [
    ("B2 single LLM call", 28.75, 60.0),
    ("235B", 216.3, 62.5),
    ("235B + exclusion rule", 153.6, 87.5),
    ("30B", 14.45, 67.5),
    ("30B + exclusion rule", 14.15, 85.0),
    ("30B final (+ coverage check)", 17.6, 92.5),
]
fig, ax = plt.subplots(figsize=(10, 4.4), dpi=220)
for name, s, acc in pts:
    ax.scatter(s, acc, s=60, zorder=3)
    dx, ha = (1.12, "left")
    dy = -4.0 if name == "235B + exclusion rule" else 1.2
    ax.annotate(name, (s, acc), xytext=(s * dx, acc + dy), fontsize=10.5, ha=ha)
ax.set_xscale("log")
ax.axvline(60, ls="--", lw=1, color="gray")
ax.axhline(90, ls="--", lw=1, color="gray")
ax.text(62, 52, "60 s goal", color="gray", fontsize=10)
ax.text(10.5, 91, "90% goal", color="gray", fontsize=10)
ax.set_xlim(10, 400)
ax.set_ylim(50, 100)
ax.set_xlabel("Median seconds per question (log scale)")
ax.set_ylabel("Answer correct (%)")
fig.tight_layout()
fig.savefig(out / "fig_speed.png")

segno.make("https://github.com/shrey-Bish/cse598-group25-datasage", error="m").save(
    out / "qr_repo.png", scale=12, border=2)
print("ok")
