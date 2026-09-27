"""Train the reading-risk scoring model on session-level features."""
import argparse
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

from ..common.config import load_config
from ..common.paths import ROOT as PROJ
from ..common.logging_utils import get_logger
from ..models.m7_risk_model import RiskScorer

log = get_logger(__name__)


def main(config: str):
    cfg = load_config(config)
    df = pd.read_csv(PROJ / cfg["data"]["features_csv"])
    feats = [c for c in cfg["features"] if c in df.columns]
    X, y = df[feats], df["label"]        # label: 1 = at-risk indicator, 0 = typical

    X_tr, X_tmp, y_tr, y_tmp = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42)
    X_va, X_te, y_va, y_te = train_test_split(
        X_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=42)

    scorer = RiskScorer({**cfg, "features": feats}).fit(X_tr, y_tr, X_va, y_va)
    proba = scorer.predict_proba(X_te)
    out_dir = PROJ / cfg["output"]["dir"]; out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(scorer, out_dir / "risk_model.joblib")
    (out_dir / "metrics.json").write_text(json.dumps({
        "roc_auc": roc_auc_score(y_te, proba),
        "report": classification_report(y_te, (proba > 0.5).astype(int),
                                        output_dict=True, zero_division=0),
        "features": feats,
    }, indent=2))
    log.info("risk model AUC %.3f", roc_auc_score(y_te, proba))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/m7_risk.yaml")
    main(ap.parse_args().config)
