#!/usr/bin/env bash
set -euo pipefail
# Requires: pip install kaggle  AND  ~/.kaggle/kaggle.json  (Kaggle > Account > API token)
echo "==> Kaggle datasets"
python -m dyslexia.data.download
echo
echo "==> Manual downloads still needed:"
echo "  Children's Speech (Zenodo 200495)  -> data/raw/m2_children_speech"
echo "  ETDD70 eye-tracking (Zenodo 13332134) -> data/raw/m6_etdd70"
