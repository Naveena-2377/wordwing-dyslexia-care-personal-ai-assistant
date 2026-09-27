# Evaluation protocol

## Why accuracy is the wrong headline number

In a typical reading session ~85% of words are read correctly. A model that
predicts `correct` for every word scores 85% accuracy and detects nothing.
Report **macro-F1** so every error class counts equally, and always publish the
per-class table alongside it.

## Per-module metrics

| Module | Primary | Secondary | Baseline to beat |
| --- | --- | --- | --- |
| M1 handwriting | macro-F1 | per-class recall, confusion matrix | logistic regression on pixels |
| M2 error classifier | **macro-F1 on real recordings** | per-class recall, synthetic→real gap | rule-based edit distance |
| M3 simplifier | SARI (or BLEU proxy) | Flesch-Kincaid delta, manual meaning-preservation on 50 sentences | zero-shot T5 |
| M7 risk scorer | ROC-AUC | precision at 90% recall, calibration curve, SHAP | logistic regression on WPM |
| M8 coach | cumulative regret vs. random / round-robin | simulated over synthetic learners | random arm selection |
| System | end-to-end latency, task completion | | |

## The screening threshold is a design decision, not a default

`screening_report()` in `evaluation/metrics.py` reports precision at a chosen
recall floor (default 0.90). For a screening tool, **missing an at-risk child is
much worse than flagging a typical one** — the cost of a false positive is one
follow-up conversation; the cost of a false negative is years of unsupported
reading. Pick the threshold that guarantees high recall and report the precision
you paid for it. Say this explicitly in your report; it is the kind of reasoning
that separates a project from a demo.

## Ablations worth running (these make the paper)

1. Synthetic data only vs. synthetic + weak-labelled real — quantifies what real data buys.
2. BiLSTM vs. per-word random forest — quantifies what sequence context buys.
3. With vs. without duration + pause features — tests whether `slow_decoding` is learnable at all.
4. Adaptive coach vs. fixed curriculum, in simulation — quantifies personalisation.
5. EMNIST pretraining vs. from scratch for M1.

## Reporting rules

- Every number gets a train/val/test provenance label.
- Small test set → report confidence intervals (bootstrap, 1000 resamples).
- Split by speaker, and say so.
- Publish the synthetic→real performance gap. Hiding it is the fastest way to lose a reviewer's trust.
