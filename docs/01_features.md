# Features & scope

## Decision: what ships, what gets cut

Ten features sound impressive on a slide and sink a student timeline. Scope is
split into three tiers. Build tier 1 completely before touching tier 2.

### Tier 1 — the core (must work end to end)

| # | Feature | Powered by |
| --- | --- | --- |
| F1 | **Read-aloud with word-synced highlighting** — upload a page or type text, hear it read, current word highlighted | OCR + TTS with timestamps |
| F2 | **Read-aloud *back* analysis** — the child reads, the system records and returns which words went wrong and how | ASR + alignment + **M2 classifier** |
| F3 | **Dyslexia-friendly rendering** — OpenDyslexic/Lexend, spacing, cream background, 65-char lines | CSS only, zero ML |
| F4 | **Sentence simplifier** — complex textbook sentence → short simple sentence, with a readability guardrail | **M3 T5 fine-tune** |
| F5 | **Error profile dashboard** — WPM, accuracy, error mix, trend over sessions | aggregation of F2 |

### Tier 2 — the differentiators (what makes it novel)

| # | Feature | Powered by |
| --- | --- | --- |
| F6 | **Confusable-letter detector** — child writes/traces a letter, system detects b/d, p/q confusion | **M1 CNN + M4 fusion** |
| F7 | **Adaptive reading coach** — picks the next exercise from the child's live error profile | **M8 bandit** |
| F8 | **Risk / severity banding** — low indicator / monitor / refer for assessment, with SHAP explanation | **M7 XGBoost** |
| F9 | **Syllable coach** — struggling word gets broken into El-e-phant and pronounced slowly | TTS + syllabifier |

### Tier 3 — nice to have (only if time remains)

| # | Feature |
| --- | --- |
| F10 | Voice Q&A ("what does photosynthesis mean?") — Whisper + LLM + TTS |
| F11 | Visual concept generator — concept → illustration, heavily cached |
| F12 | Personalised learning path — auto-generated weekly exercise plan |
| F13 | Eye-tracking research extension (ETDD70) — for the paper, not the demo |

## What deliberately does NOT get built

- **Custom ASR from scratch.** Whisper is better than anything you can train in a semester.
- **Custom TTS.** Same reason.
- **Full deep RL for the coach.** A bandit gets 90% of the value at 5% of the effort and does not need thousands of episodes to stop being random.
- **Diagnosis.** Legally and ethically out of scope. Screening band only.

## The error taxonomy (this is your label set — freeze it early)

| Label | What it looks like | Why it matters |
| --- | --- | --- |
| `correct` | word read as written, at normal pace | baseline |
| `substitution` | different word entirely ("house" → "home") | guessing from context |
| `omission` | word skipped, usually a function word | classic dyslexia marker |
| `insertion` | extra word added | |
| `reversal` | confusable letter swap ("dog" → "bog") | the signature symptom |
| `slow_decoding` | correct but took >1.2s | fluency deficit, invisible to accuracy metrics |
| `repetition` | word or syllable repeated | decoding struggle |
| `mispronunciation` | phonetically close but wrong ("phone" → "pone") | phoneme mapping deficit |

Everything downstream — the risk score, the dashboard, the coach — is built on
these eight labels. Change them later and you retrain everything.
