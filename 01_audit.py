"""Calibration Is Not Enough — a 10-minute execution walkthrough.

Run as a plain script:      python 01_audit.py
Open the interactive viewer: lectrace serve 01_audit.py
Build a static site:         lectrace build --output _site

Presenter notes live in note() calls; press N in the viewer to reveal them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import yaml
from scipy.special import expit

from lectrace import image, note, text

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
RUN = PROJECT / "result" / "runs" / "seed_42"
sys.path.insert(0, str(PROJECT / "code" / "src"))

CLASSES = ["NORM", "MI", "STTC", "CD", "HYP"]
TEMPERATURE = 1.1868
THRESHOLD = 0.4264
TARGET_COVERAGE = 0.80


class Array:
    """Compact viewer representation for arrays that would otherwise flood the panel."""

    def __init__(self, value):
        self.value = np.asarray(value)

    def __lectrace__(self):
        v = self.value
        return {
            "shape": v.shape,
            "dtype": str(v.dtype),
            "min": round(float(v.min()), 3),
            "max": round(float(v.max()), 3),
            "mean": round(float(v.mean()), 3),
        }


def main() -> None:
    title()
    text(
        "> An AI-ECG model used for triage must decide **which records to issue and which to defer**. "
        "Papers report AUROC and ECE, and ECE is usually read as evidence of trustworthiness. "
        "This project tests that reading on PTB-XL with a frozen protocol."
    )
    text(
        "| quantity | before | after |\n"
        "|---|---|---|\n"
        "| test ECE (15 bins) | 0.0238 | **0.0068** |\n"
        "| AURC (entropy score) | 0.1900 | **0.1914** |\n"
        "| accepted any-label error @ 80% coverage | 30.98% | **31.23%** |"
    )
    text(
        "Calibration improves by a factor of 3.5 and the frontier does not move. "
        "The same direction holds in all three seeds we trained (+0.18, +0.37, +0.46 points). "
        "The next four states show where that error actually lives."
    )
    note(
        "Minutes 0-2. Frame the clinical decision, not the metric: the model is a triage layer, "
        "so the quantity that matters is the error rate among records it chose to issue. "
        "Then show the three-row table and let the dissociation land before explaining it."
    )

    state_1_input()
    logits = state_2_forward()
    state_3_score(logits)
    state_4_budget()
    closing()


def title() -> None:
    text("# Calibration Is Not Enough")
    text("**A three-level audit of selective prediction for multi-label ECG classification**")
    text("Zhengyu · MD6329 Deep Learning · NTU")


def state_1_input() -> None:
    text("## State 1 — what the network actually receives")
    raw = Array(np.load(ROOT / "demo" / "ecg_sample.npy"))
    text("One held-out record (ECG ID 63): 12 leads × 1,000 samples at 100 Hz, i.e. 10 seconds.")
    lead_mean = raw.value.mean(axis=1, keepdims=True)
    lead_std = raw.value.std(axis=1, keepdims=True)
    normalised = Array((raw.value - lead_mean) / (lead_std + 1e-6))
    batch = torch.from_numpy(normalised.value).unsqueeze(0)
    text("Each lead is z-scored on its own, then a batch dimension is added.")
    note(
        "What changes: millivolts become lead-relative units. Why it matters: the network never sees "
        "absolute amplitude, only morphology — which is why the same model transfers across devices "
        "with different gain settings. Press N to see this note during the talk."
    )


def state_2_forward() -> None:
    text("## State 2 — the forward pass, layer by layer")
    model = load_model()  # @stepover
    x = torch.from_numpy(
        np.load(ROOT / "demo" / "ecg_sample.npy")
    ).unsqueeze(0)
    text("Three residual blocks, each halving the sequence length while keeping 32 channels.")
    with torch.no_grad():
        h = model.stem(x)
        h = model.encoder[0](h)
        h = model.encoder[1](h)
        h = model.encoder[2](h)
        pooled = model.pool(h).squeeze(-1)
        logits = model.head(pooled)
        probs = torch.sigmoid(logits)
    text("Global average pooling collapses time; the linear head emits one logit per superclass.")
    note(
        "This is the 'how the neural program works' state. Point at the shape column: 12x1000 -> 32x500 "
        "-> 32x500 -> 32x250 -> 32x125 -> 32 -> 5. The encoder never changes channel width, so all 52k "
        "parameters are spent on temporal filters, not on a deep feature hierarchy."
    )
    return logits


def state_3_score(logits) -> None:
    text("## State 3 — from logits to an abstention score")
    text("The five logits from State 2 are rescaled, then turned into a single uncertainty number.")
    calibrated = logits / TEMPERATURE
    p = torch.sigmoid(calibrated)
    label_entropy = -(p * torch.log(p) + (1 - p) * torch.log(1 - p))
    score = label_entropy.mean()
    decision = "accept" if float(score) <= THRESHOLD else "defer"
    text(
        "Temperature scaling divides every logit by **T = 1.1868**, fitted on fold 9. "
        "The record-level score is the mean binary entropy over the five labels."
    )
    text(f"Score **{float(score):.4f}** against threshold **{THRESHOLD}** → **{decision}**.")
    note(
        "Make the invariance concrete: T changes the number, not the ordering, because it is the same "
        "positive scalar for every record. The threshold absorbs the rescaling. That is why ECE can fall "
        "by 71% while the accepted set stays essentially the same."
    )


def state_4_budget() -> None:
    text("## State 4 — how much could any score buy?")
    data = np.load(ROOT / "demo" / "test_logits.npz")
    y = data["labels"]
    p = expit(data["logits"])
    correct = np.all((p > 0.5) == (y > 0.5), axis=1).astype(float)
    confidence = np.maximum(p, 1 - p).mean(axis=1)
    k = int(TARGET_COVERAGE * len(y))
    oracle_order = np.argsort(-correct)
    model_order = np.argsort(-confidence)
    risk_oracle = 1 - correct[oracle_order][:k].mean()
    risk_model = 1 - correct[model_order][:k].mean()
    budget = risk_model - risk_oracle
    text(
        f"On {len(y)} held-out records at 80% coverage: perfect ordering would reach "
        f"**{100 * risk_oracle:.1f}%** error, the model reaches **{100 * risk_model:.1f}%**."
    )
    text(
        f"The entire budget available to any abstention score is **{100 * budget:.1f} percentage points**. "
        "Post-hoc scores recover 1.1 of them; a learned head adds 0.4 more, within noise. "
        "The rest needs a scorer that reads the model's internals, not its probabilities."
    )
    image(str(ROOT / "assets" / "fig4.png"), width=620)
    note(
        "This is the pivot of the talk. Without a budget, a 1-point improvement looks like progress. "
        "With it we can be precise about what is exhausted: post-hoc scores recover 0.17 of the 6.5 points, "
        "ensembling adds the same 0.17, and a learned head another 0.40 - so that family is nearly spent, "
        "while about 5.7 points remain open to a scorer that reads features. The 23.6 points of oracle "
        "error are a different quantity entirely: they sit in model discrimination and label ambiguity, "
        "and no ranking can remove them."
    )


def closing() -> None:
    text("## What this means clinically")
    text(
        "| decision unit | label coverage | label error | fully auto-issued |\n"
        "|---|---|---|---|\n"
        "| record-level | 79.6% | 9.90% | 79.6% |\n"
        "| label-level | 76.4% | **5.61%** | **39.8%** |"
    )
    text(
        "Changing the **decision unit** moves the operating point far more than changing the score. "
        "A ward that can review individual labels gets a different system from one that can only "
        "accept or reject whole records — and no calibration metric reveals that difference."
    )
    text(
        "**Report the frontier, the error target, and the granularity — not a single coverage point "
        "next to an ECE.**"
    )
    note(
        "Close on the clinical interpretation, not the numbers: 5.6% label error sounds better than 9.9%, "
        "but only 40% of records can then be issued untouched. Whether that trade is good depends on the "
        "review workflow, which is a hospital decision, not a modelling one."
    )


def load_model():
    cfg = yaml.safe_load((RUN / "config.yaml").read_text(encoding="utf-8"))
    from ptbxl.model import build_model

    model = build_model(cfg["model"], num_classes=len(CLASSES))
    state = torch.load(RUN / "best.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(state["model"])
    model.eval()
    return model


if __name__ == "__main__":
    main()
