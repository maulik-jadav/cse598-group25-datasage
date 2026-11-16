# Poster (draft)

`Group25_Poster.pdf` is the print-ready poster: one page, 24 × 36 in portrait, as the course asks. It is a
draft until Arsha's check (task A3 in `docs/TEAM_HANDOFF.md`); submit it on Canvas by Nov 23, 2:00 PM.

| File | What it is |
|---|---|
| `Group25_Poster.pdf` | The poster to submit |
| `poster.html` | Its source: one HTML page at 2304 × 3456 px (96 px per inch) |
| `figs/fig_accuracy.png`, `figs/fig_speed.png` | Figures 2 and 3 |
| `figs/qr_repo.png` | QR code to this repository |
| `make_figs.py` | Makes the three images from the numbers in `eval/results/summary.md` |

Every number comes from `eval/results/summary.md` (held-out seed 101, test seed 202). The example in
Tables 1 and 2 is the 30B demo run in `docs/final/demo/`.

## Changing it

Edit `poster.html`, then print it again with Chrome (macOS path shown):

```bash
cd docs/final/poster
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --virtual-time-budget=8000 --print-to-pdf=Group25_Poster.pdf "file://$PWD/poster.html"
pdfinfo Group25_Poster.pdf | grep "Page size"     # must say 1728 x 2592 pts (24 x 36 in)
```

If a number changes, update `make_figs.py` and run it (needs `pip install matplotlib segno`):

```bash
python make_figs.py figs
```
