# AI Reading Assistant for Dyslexic Children

A reading companion that **learns each child's personal error profile** from their
actual reading attempts and adapts to it — instead of applying the same static
accessibility settings to every child.

## The one-line pitch

Existing tools (Read&Write, Immersive Reader, Speechify) are *configuration*:
you toggle a font, a colour, a speed. This project is *learning*: a trained model
watches how this specific child reads, classifies the errors they actually make,
scores severity, and picks the next exercise accordingly.

## What is trained vs what is integrated

Be explicit about this in your report and demo — it is what separates this from an
API wrapper.

| | Component | Status |
| --- | --- | --- |
| **Trained** | M1 Handwriting reversal CNN | trained by you |
| **Trained** | M2 Reading error-type classifier (BiLSTM) | trained by you |
| **Trained** | M3 Sentence simplifier (T5 fine-tune) | fine-tuned by you |
| **Trained** | M4 Confusable-pair detector (CNN + speech fusion) | trained by you |
| **Trained** | M7 Risk / severity scorer (XGBoost) | trained by you |
| **Learned online** | M8 Adaptive coach (Thompson sampling) | learns per child |
| Integrated | OCR (EasyOCR/Tesseract) | existing |
| Integrated | ASR (Whisper) | existing |
| Integrated | TTS (Coqui/Azure) | existing |
| Integrated | LLM Q&A, image generation | existing |

## Quickstart

```bash
make setup                  # venv + deps + editable install
cp .env.example .env        # fill in keys
make data                   # download datasets (needs kaggle.json)
make prep                   # preprocessing for every module
make train                  # train all models
make eval                   # collect metrics into reports/metrics/summary.json
make api                    # http://localhost:8000/docs
```

## Repository layout

```
configs/      one YAML per trainable module — every hyperparameter lives here
data/         raw → interim → processed → synthetic (nothing committed)
docs/         features, architecture, datasets, pipeline, evaluation, ethics
notebooks/    exploration + the end-to-end demo notebook
src/dyslexia/
  common/     config, seeds, paths, alignment, audio + text utils
  data/       download + per-module preprocessing + synthetic error generator
  models/     model definitions only (no training loops)
  training/   one script per trainable module
  inference/  pipeline + predictor wrappers (what the API imports)
  services/   OCR, STT, TTS, LLM, image generation, readability guardrail
  api/        FastAPI app + routers
  evaluation/ metrics + report collection
frontend/     React app (accessibility rules in frontend/README.md)
deployment/   Dockerfiles, compose, nginx, k8s
```

## Documentation

1. [Features & scope](docs/01_features.md)
2. [Architecture](docs/02_architecture.md)
3. [Datasets](docs/03_datasets.md)
4. [**Pipeline: preprocessing → deployment**](docs/04_pipeline.md)
5. [Evaluation protocol](docs/05_evaluation.md)
6. [Deployment](docs/06_deployment.md)
7. [Ethics, consent & safety](docs/07_ethics_consent.md)

## Non-negotiables

- The system produces a **screening indicator**, never a diagnosis.
- Real child recordings are used for **testing only** — never as the bulk of training.
- No child audio leaves the device/server without explicit guardian consent.
