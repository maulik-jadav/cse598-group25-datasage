"""Poster figures, read straight from the result files so the poster cannot drift from the data.

    python docs/final/poster/make_figs.py docs/final/poster/figs      # needs matplotlib and segno

- fig_accuracy.png  right answers by approach: 200 standard unseen questions (95% ranges) and the hard split
- fig_parts.png     what each part of DataSage is worth (ablations on the same 200 questions)
- fig_models.png    accuracy against speed for every model tried as DataSage's planner (if the model study exists)
- qr_repo.png       QR code to the repository
Sources: eval/results/study_scale_ablations.json, eval/results/summary.csv, eval/results/study_models.json.
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import segno  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "eval" / "results"
out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "figs")
out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
GREY, TEAL, DARK = "#9C9A93", "#0F766E", "#14284B"

study = json.loads((RESULTS / "study_scale_ablations.json").read_text())
abl = study["ablations"]
rows = list(csv.DictReader(open(RESULTS / "summary.csv")))


def pooled(system: str, splits: list[str]):
    picked = [r for r in rows if r["system"] == system and r["dataset"] in splits]
    if len(picked) != len(splits):
        return None
    n = sum(int(r["tasks"]) for r in picked)
    return 100 * sum(round(float(r["analysis_accuracy"]) * int(r["tasks"])) for r in picked) / n


# Figure 2: right answers by approach, standard (200 questions, with 95% ranges) and hard (40 questions).
names = [("b0", "Stakeholder's script"), ("b1", "Fixed cleaning script"), ("b2", "One LLM call, no tools"),
         ("datasage-m3", "DataSage (Qwen3-30B)")]
hard = {k: pooled(k, ["sales-hard", "penguins-hard"]) for k, _ in names}
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=220)
ys = list(range(len(names)))[::-1]
for y, (key, label) in zip(ys, names):
    a = abl[key]
    acc, lo, hi = 100 * a["accuracy"], 100 * a["ci95"][0], 100 * a["ci95"][1]
    color = TEAL if key == "datasage-m3" else GREY
    ax.barh(y + 0.19, acc, 0.36, color=color)
    ax.errorbar(acc, y + 0.19, xerr=[[acc - lo], [hi - acc]], fmt="none", ecolor="#333", capsize=4, lw=1.2)
    ax.text(hi + 1.5, y + 0.19, f"{acc:.1f}%", va="center", fontsize=11, fontweight="bold" if key == "datasage-m3" else None)
    if hard[key] is not None:
        ax.barh(y - 0.19, hard[key], 0.36, color=color, alpha=0.45, hatch="//", edgecolor="white")
        ax.text(hard[key] + 1.5, y - 0.19, f"{hard[key]:.1f}% hard", va="center", fontsize=10, color="#444")
    else:
        ax.text(1.5, y - 0.19, "not run on the hard split", va="center", fontsize=10, color="#777")
ax.set_yticks(ys, [lab for _, lab in names])
ax.set_xlim(0, 112)
ax.set_xlabel("Right answers (%)")
ax.text(0, len(names) - 0.35, f"solid: {abl['datasage-m3']['n']} standard unseen questions (bars: 95% range)   "
        "hatched: 40 hard questions, 343 to 1,935 rows", fontsize=10, color="#444")
fig.tight_layout()
fig.savefig(out / "fig_accuracy.png")
plt.close(fig)

# Figure 3: what each part is worth.
parts = [("datasage-m3", "All parts on"), ("datasage-m3-nomerge", "No merge rule in prompt"),
         ("datasage-m3-novalidator", "No validator"), ("datasage-m3-nocoverage", "No coverage check"),
         ("datasage-m3-compact", "Short memory"), ("datasage-m3-reject", "No approvals (all refused)")]
fig, ax = plt.subplots(figsize=(10, 4.2), dpi=220)
ys = list(range(len(parts)))[::-1]
for y, (key, label) in zip(ys, parts):
    a = abl[key]
    acc, lo, hi = 100 * a["accuracy"], 100 * a["ci95"][0], 100 * a["ci95"][1]
    ax.barh(y, acc, 0.6, color=TEAL if key == "datasage-m3" else GREY)
    ax.errorbar(acc, y, xerr=[[acc - lo], [hi - acc]], fmt="none", ecolor="#333", capsize=4, lw=1.2)
    ax.text(hi + 1.5, y, f"{acc:.1f}%", va="center", fontsize=11)
ax.set_yticks(ys, [lab for _, lab in parts])
ax.set_xlim(0, 110)
ax.set_xlabel(f"Right answers on the same {abl['datasage-m3']['n']} questions (%)")
fig.tight_layout()
fig.savefig(out / "fig_parts.png")
plt.close(fig)

# Figure 4 (when the model study exists): every planner model, accuracy against median seconds.
models_path = RESULTS / "study_models.json"
if models_path.exists():
    data = json.loads(models_path.read_text())
    pts = []
    for short, m in data.get("models", {}).items():
        a = (m.get("agent") or {}).get("heldout_test") or {}
        if a.get("tasks") == 80 and a.get("seconds_median") and not short.endswith("-original"):
            pts.append((short, float(a["seconds_median"]), 100 * float(a["accuracy"])))
    if pts:
        fig, ax = plt.subplots(figsize=(10, 4.6), dpi=220)
        for name, sec, acc in pts:
            default = name == "qwen3-30b"
            ax.scatter(sec, acc, s=70 if default else 28, color=TEAL if default else GREY, zorder=3 if default else 2)
            if name in ("qwen3-30b", "qwen3-235b", "inkling-small", "llama4-scout", "llama4-maverick"):
                ax.annotate(name, (sec, acc), xytext=(5, 4), textcoords="offset points", fontsize=9,
                            color=TEAL if default else "#333", fontweight="bold" if default else None)
        ax.set_xscale("log")
        ax.set_xticks([15, 30, 60, 120, 240, 480], ["15", "30", "60", "120", "240", "480"])
        ax.minorticks_off()
        ax.set_xlabel("Median seconds per question (log scale, measured under shared load)")
        ax.set_ylabel("Right answers (%)")
        ax.set_ylim(0, 103)
        fig.tight_layout()
        fig.savefig(out / "fig_models.png")
        plt.close(fig)

segno.make("https://github.com/shrey-Bish/cse598-group25-datasage", error="m").save(out / "qr_repo.png", scale=12, border=2)
print("figures written to", out)
