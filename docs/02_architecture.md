# Architecture

## The simple version

Think of it as a **reading tutor with three jobs**:

1. **Read to the child** — a page goes in, clear audio comes out with the current word lit up.
2. **Listen to the child** — the child reads aloud, and the system compares what they *said* against what was *written*, word by word.
3. **Decide what to practise next** — based on the pattern of mistakes it has seen so far.

Job 2 is where the ML lives. Everything else is plumbing around it.

## Data flow for one reading session

```
child reads aloud into mic
          │
          ▼
  [audio 16kHz mono]  ──────────►  Whisper ASR (word timestamps)
          │                              │
          │                              ▼
    target text  ──────────────►  Needleman-Wunsch word alignment
                                         │
                                         ▼
                              per-word feature vector
                   (edit distance, duration, ASR confidence,
                    confusable-letter count, word length, ...)
                                         │
                                         ▼
                          M2 BiLSTM error-type classifier
                                         │
                      ┌──────────────────┼──────────────────┐
                      ▼                  ▼                  ▼
               word-level labels   session features    error profile
               (UI highlighting)         │             (running tally)
                                         ▼                  │
                               M7 XGBoost risk score        │
                                         │                  │
                                         ▼                  ▼
                                  risk band          M8 Thompson sampling
                               (low/monitor/refer)   → next exercise
```

## Why a BiLSTM and not just a per-word classifier

Reading errors are not independent. A child who just stumbled is more likely to
stumble on the next word; an omission is often followed by a self-correction or a
repetition. A per-word model cannot see that context. The BiLSTM reads the whole
utterance in both directions, so the label for word 7 is informed by words 1–6 and
8–20. In practice this is worth several points of macro-F1 on the minority classes
(`reversal`, `repetition`) which are exactly the ones you care about.

## Module map

| Module | Input | Output | Model |
| --- | --- | --- | --- |
| M1 Handwriting CNN | 64×64 letter crop | normal / reversal / corrected | small CNN (or ResNet18) |
| M2 Error classifier | aligned word features | one of 8 error labels per word | BiLSTM |
| M3 Simplifier | complex sentence | simple sentence | T5-small fine-tune |
| M4 Confusion detector | M1 output + M2 reversals | per-pair confusion rate | fusion + running profile |
| M5 Integration services | page image / text / question | text, audio, answer, image | existing APIs |
| M6 Eye-tracking (optional) | ETDD70 fixation sequences | reading-behaviour features | research extension |
| M7 Risk scorer | session feature row | 0–1 score + band + SHAP | XGBoost + isotonic calibration |
| M8 Adaptive coach | error profile + history | next exercise | Thompson sampling |

## Service boundaries

- `models/` holds definitions only. No training loop, no file IO.
- `training/` holds one script per module. Nothing imports these at runtime.
- `inference/predictors.py` is the **only** thing the API imports. Swap a model
  implementation and the API does not change.
- `services/` wraps third-party APIs so a provider swap (Coqui → Azure) is a
  one-file change.

## Featurization must live in one place

`training/train_m2_error_clf.py::featurize` is imported by
`inference/predictors.py`. Do not reimplement it. Training/serving skew in a
hand-crafted feature pipeline is the single most common silent failure in
student ML projects — the model scores 0.91 offline and behaves randomly in the demo.
