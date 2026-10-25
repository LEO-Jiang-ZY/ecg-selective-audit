# Calibration Is Not Enough — interactive lecture

An executable slide deck for *Calibration Is Not Enough: A Three-Level Audit of
Selective Prediction for Multi-Label ECG Classification* (MD6329 Deep Learning,
Nanyang Technological University).

The presentation is written as a Python script and built with
[lectrace](https://pypi.org/project/lectrace/), which replays the execution
state by state in the browser: every variable, every array shape, every
intermediate number in the talk is produced by the same code that produced the
paper's results.

## Live site

The site has two layers, both static:

| Path | What it is |
|---|---|
| `/` | project landing page — problem, method, four figures, seed table |
| `/lectrace/` | the executable deck |


```
https://<your-username>.github.io/<repo-name>/
```

Open `/lectrace/` full screen, then use the arrow keys to advance. There is
nothing to install and no runtime dependency — `site/` is pure static HTML,
CSS, JS and JSON.

## What the four execution states show

| State | Shows | Point it makes |
|---|---|---|
| 1 | one 12 × 1,000 record, per-lead z-scoring | the model sees morphology, not amplitude |
| 2 | layer-by-layer forward pass, 12×1000 → 5 | channel width never grows; pooling discards time |
| 3 | temperature scaling, entropy, threshold | a monotone map does not change the acceptance set |
| 4 | three-tier error budget | 6.9 points is the whole budget of any score |

Eighty steps in total; the speaker notes attached to each step are reproduced in
`SPEAKER_SCRIPT.md`.

## Repository layout

```
01_audit.py              the deck itself (single file, plain Python)
demo/                    frozen inputs: one ECG record, test logits
assets/                  figures reused inside the deck
site/                    published site root
  index.html             project landing page
  styles.css             one stylesheet, no framework
  assets/                five figures used by the landing page
  lectrace/              prebuilt deck (HTML + JS + trace JSON)
vercel.json              deploy config: output directory is site/
SPEAKER_SCRIPT.md        10-minute script with per-slide timing
DEPLOY_VERCEL.md         Vercel deployment (recommended)
DEPLOY_GITHUB_PAGES.md   GitHub Pages alternative
```

`_site/` is a local preview build and is git-ignored.

## Rebuilding the site

```bash
python -m pip install lectrace
cd lecture
lectrace run 01_audit.py          # check every step executes
lectrace build --output site/lectrace   # regenerate the deck
```

The deck reads only files in `demo/`, so it does not need the 1 GB PTB-XL
dataset, PyTorch, or a GPU to build. The numbers are frozen artefacts of the
experiments; the code around them is real and executable.

## Reproducing the underlying paper

The full experimental pipeline (cache → train → calibrate → evaluate → error
budget) lives in the parent project and is summarised in the paper's
reproduction checklist appendix.

## License

Code: MIT. Figures and text: the author's, for this course submission.
