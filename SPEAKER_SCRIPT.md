# 10-Minute Presentation Script

**Format:** lectrace execution walkthrough (`lectrace serve 01_audit.py`)
**Total:** 10:00 · **States:** 4 · **Speaker notes:** press `N` in the viewer

> Timing is cumulative. `[→]` marks the key press to advance to the next step.
> Bold sentences are the ones to land slowly.

---

## 0:00 – 2:30 · Opening (no state yet)

**[Slide: title]**

> Good morning. I'm Zhengyu. This project started from a practical question about deploying ECG models, and ended with a result I did not expect.

**[→ three-row table]**

> Consider an AI system reading twelve-lead ECGs in a hospital. It is not replacing the cardiologist — it is a triage filter. For every record it decides: sign this one off, or send it to a human. In that role, the number that matters is not AUROC. It is: **among the records the model chose to sign, how often is it wrong?**
>
> The literature usually reports two things: discrimination, and a calibration metric like ECE. And there is an implicit inference — if the probabilities are well calibrated, then confidence can be trusted to decide when to abstain.
>
> I tested that inference. Here is the result on PTB-XL. Temperature scaling cuts ECE by a factor of 3.5 — from 0.0238 to 0.0068. And the accepted error at 80% coverage goes from 30.98% to 31.23%. AURC from 0.1900 to 0.1914.
>
> **Calibration improved substantially, and the triage behaviour did not change at all.**

**[→ sentence about four states]**

> So the rest of this talk is not "here is a better model". It is an audit: where does that error actually live, and how much of it is recoverable? Four execution states, each a few lines of the actual code.

---

## 2:30 – 3:45 · State 1 — the input tensor

**[→ State 1]**

> State one: what the network actually receives. This is one held-out record, ECG ID 63 — twelve leads, one thousand samples at 100 hertz, so ten seconds.
>
> The only preprocessing is per-lead z-scoring. **[→]** Each lead is normalised against its own mean and standard deviation.
>
> **This matters clinically and technically.** Clinically, the model never sees absolute millivolts — only morphology — which is part of why it transfers across devices with different gain. Technically, it means the input is a 12-by-1000 array where every lead has been put on the same scale, and the batch dimension makes it 1-12-1000.

---

## 3:45 – 6:00 · State 2 — the forward pass

**[→ State 2]**

> State two is the one the assignment calls "how the neural program works". Watch the shape column.
>
> The stem is a convolution with stride two: twelve channels to thirty-two, and the sequence halves to five hundred. **[→]** Then three residual blocks. Block one keeps the length; blocks two and three each halve it — 500, 250, 125.
>
> **[→]** Global average pooling collapses time entirely, giving a 32-dimensional vector. **[→]** And the linear head turns that into five logits, one per diagnostic superclass.
>
> Two observations. First, **the encoder never changes channel width** — it stays at 32 the whole way. All 52,000 parameters are spent on temporal filters, not on a deep feature hierarchy. That is a deliberate choice: this model is an instrument, not a competitor.
>
> Second, look at where the information is destroyed. Pooling averages over the entire ten seconds. If a diagnostic feature is brief — a single premature beat, say — averaging dilutes it. **That is the architectural origin of the errors we will see later.**

---

## 6:00 – 7:30 · State 3 — from logits to an abstention score

**[→ State 3]**

> State three: how the model decides to abstain. The five logits are divided by the temperature, 1.1868, fitted on fold nine. Then we take the binary entropy of each label and average.
>
> **[→]** For this record the score is just under the threshold, so it would be accepted. The model predicts MI, the true label is MI — a correct accept.
>
> Here is the point of this state. **Temperature scaling multiplies every logit by the same constant.** It changes the number, not the ordering. The threshold absorbs the rescaling. So the set of accepted records barely moves — which is exactly the 30.98 to 31.23 result from the opening.
>
> Calibration is not useless. It gives you probabilities you can threshold at a clinically meaningful value. **It just cannot tell you which records are safe.**

---

## 7:30 – 9:15 · State 4 — the budget

**[→ State 4]**

> State four is the part I would keep if I could keep only one slide.
>
> Instead of comparing a fourth score, I asked: how much room is there at all? So I computed three orderings on the same 2,198 test records. One sorts records by their **true** correctness — a perfect oracle, impossible in practice, but it gives a ceiling. One uses the model's actual confidence.
>
> **[→]** At 80% coverage, the oracle would still make 23.1% errors. The model makes 30.0%. **So the entire budget available to any scoring function — any entropy, any learned head, anything — is 6.9 points.**
>
> Switching from entropy to max-prob recovers 1.1 of those points. A learned correctness head, using the model's internal features, recovers another 0.4 — and that is within noise. **[→ image]**
>
> **The blue band in this figure is the ranking error. It is invisible. The orange band is what no score can fix.** Which means: for the last two years of selective-prediction papers, including my own first attempt, the score layer was never the bottleneck.

---

## 9:15 – 10:00 · Closing

**[→ closing table]**

> So what does move the operating point? The decision unit.
>
> Record-level abstention: sign the whole record or defer it. Label-level: accept the confident labels, defer only the uncertain ones. At a comparable label coverage, label error drops from 9.9% to 5.6%. **But only 40% of records can then be issued untouched, and every record still has about one label waiting for a human.**
>
> Whether that trade is good is a ward decision, not a modelling one. A system that routes individual labels to a reader gets a different deal from one that can only accept or reject whole records.
>
> **[→ final sentence]**
>
> **Report the frontier, the error target, and the granularity — not a single coverage point next to an ECE.** Thank you.

---

## Q&A preparation

| Likely question | Answer |
|---|---|
| Why such a small model? | Deliberate. 51k parameters makes the audit cheap enough to rerun per ablation, and the capacity check shows 16M is worse, so capacity is not the constraint. |
| Isn't 80% coverage arbitrary? | Yes — that is the argument. Section 5.8 reports risk-controlled coverage at four error targets instead of a single point. |
| Why not conformal prediction? | It needs exchangeability, and the device shift (TVD 0.326) violates it. Conformal is in future work with per-class variants. |
| Is the 0.4-point head gain real? | Direction is consistent on both folds, magnitude is 0.4 SE. I report it as suggestive, not established. It needs multiple seeds. |
| Why is HYP so bad? | AUPRC 0.492 at 11.9% prevalence. It is the weakest class and the most likely trigger of any-label errors. Fixing it needs loss reweighting, not threshold tuning. |
| Could a better model break the 6.9-point ceiling? | Yes — that is exactly what the ceiling says. It is a property of 61% exact-match accuracy, not of the task. Better discrimination moves the oracle up. |

---

## Delivery notes

1. **Do not read the code.** Point at the shape column and the variable panel; the code is evidence, not content.
2. **Pause after the 0.0238 → 0.0068 line.** The audience needs a beat to register that the second number did not move.
3. **State 4 is the pivot.** If you are running long, cut State 1 to 45 seconds and protect State 4.
4. **Never say "our model achieves".** Say "this model lets us measure". The contribution is the measurement.
5. Have `figures/fig1.png` ready as a backup slide if someone asks about the reliability diagram.
