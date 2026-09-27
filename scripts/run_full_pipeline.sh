#!/usr/bin/env bash
set -euo pipefail
python -m dyslexia.data.prepare_m1_handwriting
python -m dyslexia.data.prepare_m3_simplify
python -m dyslexia.data.synth_reading_errors
python -m dyslexia.data.prepare_m2_speech
python -m dyslexia.data.build_session_features
python -m dyslexia.training.train_m1_cnn        --config configs/m1_handwriting.yaml
python -m dyslexia.training.train_m2_error_clf  --config configs/m2_reading_error.yaml
python -m dyslexia.training.train_m3_simplifier --config configs/m3_simplifier.yaml
python -m dyslexia.training.train_m7_risk       --config configs/m7_risk.yaml
python -m dyslexia.evaluation.run_all
