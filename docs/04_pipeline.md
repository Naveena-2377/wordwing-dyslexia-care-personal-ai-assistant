# Pipeline: preprocessing → deployment

Twelve steps. Each has a definition of done. Do not start a step before the
previous one's check passes — every skipped check costs a full retraining cycle
later.

---

## Phase 1 — Data (steps 1–4)

### Step 1. Environment + repo

```bash
make setup
cp .env.example .env
pytest                       # the alignment tests should pass on a clean clone
```

**Done when:** `pytest` is green and `python -c "import dyslexia"` works.

### Step 2. Download and audit

```bash
make data
jupyter notebook notebooks/00_data_audit.ipynb
```

Record, per dataset: sample count, class balance, image dimensions, audio duration
and sample rate, corrupt-file count.

**Done when:** `docs/03_datasets.md` has real numbers filled in, not estimates.
Do not train anything before this.

### Step 3. Preprocessing

**M1 handwriting** (`prepare_m1_handwriting.py`):
grayscale → Otsu binarise → crop to ink bounding box → pad to square → resize 64×64
→ normalise → stratified 70/15/15 split → `m1_data.npz`

> Crop-then-pad matters. Raw datasets have wildly different letter sizes; without
> it the CNN learns "big ink = class A" instead of learning letter shape.

> **Never horizontally flip as augmentation here.** A flipped `b` *is* a `d`. You
> would be generating mislabelled data for the exact class you are trying to detect.

**M2 speech** (`prepare_m2_speech.py`):
resample 16 kHz mono → trim silence → loudness normalise → Whisper transcribe with
word timestamps → Needleman-Wunsch align against target text → one row per target
word with operation + timing + confidence.

**M3 text** (`prepare_m3_simplify.py`):
filter noisy pairs → tokenise to max 96 tokens → mask pad tokens with -100 → save.

**Synthetic** (`synth_reading_errors.py`): generate 20k corrupted utterances across
three severity profiles.

```bash
make prep
```

**Done when:** every processed artefact exists and
`notebooks/01`/`02` show the preprocessing output looks right to your eye. Look at
20 random preprocessed images and 5 alignments manually. This catches 80% of bugs.

### Step 4. Feature engineering

`build_session_features.py` rolls per-word records into one row per session:
WPM, accuracy, per-error-type rates, mean word duration, pause statistics,
long-word error rate, mean ASR confidence.

**Done when:** `session_features.csv` exists and its columns match `configs/m7_risk.yaml`.

---

## Phase 2 — Modelling (steps 5–8)

### Step 5. Baselines first

Before any neural network, record the dumb baseline:

| Module | Baseline | Purpose |
| --- | --- | --- |
| M1 | logistic regression on raw pixels | if the CNN cannot beat this, something is broken |
| M2 | rule-based: edit distance thresholds + `is_reversal_error` | this is a surprisingly strong baseline — beat it or drop the BiLSTM |
| M3 | untuned T5-small, zero-shot | shows what fine-tuning actually bought |
| M7 | logistic regression on WPM alone | proves the model is not just reading speed |

**Done when:** four baseline numbers are written into `reports/metrics/baselines.json`.
These go straight into your paper's results table.

### Step 6. Train M1 (handwriting CNN)

```bash
python -m dyslexia.training.train_m1_cnn --config configs/m1_handwriting.yaml
```

Two-stage: pretrain on EMNIST letters (learn letter shape), fine-tune on the
dyslexia set (learn reversal). Class-weighted cross-entropy, cosine LR, early
stopping on validation accuracy.

**Done when:** test macro-F1 > 0.85 and the confusion matrix shows `reversal`
recall is not the sacrificial class.

### Step 7. Train M2 (error classifier) — the core model

```bash
python -m dyslexia.training.train_m2_error_clf --config configs/m2_reading_error.yaml
```

Train on synthetic + weak-labelled NNCES. Validate on held-out NNCES speakers.
**Report the final number on real pilot recordings only.**

Expect a gap between synthetic and real performance — that gap is a finding, not a
failure. Report it and discuss it.

**Done when:** macro-F1 on real data beats the rule-based baseline from step 5.

### Step 8. Train M3 and M7

```bash
python -m dyslexia.training.train_m3_simplifier --config configs/m3_simplifier.yaml
python -m dyslexia.training.train_m7_risk       --config configs/m7_risk.yaml
```

M3: 3 epochs of T5-small on WikiLarge is enough; more overfits and the outputs get
repetitive. M7: XGBoost with isotonic calibration, because an uncalibrated
"0.8 risk" means nothing to a teacher.

**Done when:** M3 mean Flesch-Kincaid drops by ≥2 grade levels with no meaning loss
on a 50-sentence manual check, and M7 ROC-AUC beats the WPM-only baseline.

---

## Phase 3 — Integration (steps 9–10)

### Step 9. Wire the inference pipeline

`inference/pipeline.py` chains: ASR → align → M2 → session features → M7 → M8.

```bash
jupyter notebook notebooks/05_end_to_end_demo.ipynb
```

**Done when:** one audio file + target text produces a complete `SessionResult`
in under 10 seconds on CPU. If Whisper-small is too slow, drop to `base`.

### Step 10. API + frontend

```bash
make api        # http://localhost:8000/docs
```

Endpoints: `/read/ocr`, `/read/speak`, `/read/syllables`, `/simplify`,
`/session/analyze`, `/coach/next/{id}`, `/coach/feedback`.

Build the five frontend pages in the order listed in `frontend/README.md`.
Apply `dyslexia-theme.css` before writing a single component — retrofitting
accessibility is far more work than starting with it.

**Done when:** a person who has never seen the project can upload a page, hear it
read, read it back, and see their errors highlighted — without you touching a terminal.

---

## Phase 4 — Evaluation & deployment (steps 11–12)

### Step 11. Evaluate properly

```bash
make eval
```

See `docs/05_evaluation.md`. The headline metric is **macro-F1 on real recordings**,
not overall accuracy — overall accuracy is dominated by the `correct` class and
will read 0.9+ even for a useless model.

**Done when:** `reports/metrics/summary.json` holds every module's numbers and you
can defend each one.

### Step 12. Deploy

```bash
docker compose -f deployment/docker/docker-compose.yml up --build
```

Model weights are mounted, not baked into the image. See `docs/06_deployment.md`.

**Done when:** the stack runs from a clean clone on a machine that is not yours.
Test this before demo day, not on demo day.

---

## Timeline (a realistic one)

| Weeks | Steps | Output |
| --- | --- | --- |
| 1 | 1–2 | repo running, data audited |
| 2–3 | 3–4 | preprocessing done, features built |
| 4 | 5 | baselines recorded |
| 5–6 | 6–7 | M1 + M2 trained |
| 7 | 8 | M3 + M7 trained |
| 8–9 | 9–10 | pipeline + API + frontend |
| 10 | 11–12 | evaluation, deployment, demo video |
