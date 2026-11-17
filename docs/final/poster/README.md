# Poster

`Group25_Poster.pdf` is the print-ready poster: one page, 24 × 36 in portrait, as the course asks. Arsha checks
every number (task A3 in `docs/TEAM_HANDOFF.md`) and Shrey submits it on Canvas by Nov 23, 2:00 PM.

| File | What it is |
|---|---|
| `Group25_Poster.pdf` | The poster to submit |
| `poster.html` | Its source: one HTML page at 2304 × 3456 px (96 px per inch). Edit this, not the older Claude Design canvas |
| `figs/fig_accuracy.png` | Figure 3: right answers by approach, 200 standard questions (with 95% ranges) and 40 hard questions |
| `figs/fig_parts.png` | Figure 4: one part of DataSage turned off at a time, same 200 questions |
| `figs/app_shot.png` | Figure 2: the browser app, a risky fix waiting under its row |
| `figs/fig_models.png` | Accuracy against seconds for the 41 planner models (not on the poster; for the report or talk) |
| `figs/qr_repo.png` | QR code to this repository |
| `make_figs.py` | Makes every image above except the screenshot, straight from the result files |

Where each number comes from:

| On the poster | Source |
|---|---|
| 95.5% of 200 questions, the 95% range, the 4 runs, B0/B1/B2 on 200, ablations, the 36 of 39 misses | `eval/results/study_scale_ablations.json`, `docs/final/findings_scale_and_ablations.md` |
| Hard split (100% with the grouping fix and 90.0% before it, 80 of 80 over two seeds, 97.5%, 10.0%, 55.0%, 637 damaged cells, 1,750 errors) | `eval/results/summary.md` (`sales-hard`, `penguins-hard`), `eval/results/fix_groupby/` (with the fix), `docs/final/findings_hard.md` sections 3 and 10 |
| 41 models, rank 4, 93.8%, median 20 points | `eval/results/study_models.json`, `docs/final/findings_models.md` |
| Table 1 (the example input) | `baseline/examples/messy_sales.csv` and `examples/messy_sales_rules.json` |

## Changing it

Edit `poster.html`, then print it again with Chrome (macOS path shown):

```bash
cd docs/final/poster
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --virtual-time-budget=8000 --print-to-pdf=Group25_Poster.pdf "file://$PWD/poster.html"
pdfinfo Group25_Poster.pdf | grep "Page size"     # must say 1728 x 2592 pts (24 x 36 in)
```

If the results change, rebuild the figures (needs `pip install matplotlib segno`):

```bash
python make_figs.py figs
```
