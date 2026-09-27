"""Thin loaders that wrap saved artefacts behind a stable interface.

The API never imports training code - it imports these.
"""
from pathlib import Path

from ..common.paths import MODELS
from ..training.train_m2_error_clf import featurize


class HandwritingPredictor:
    def __init__(self, weights: Path = MODELS / "m1_handwriting_cnn" / "best.pt"):
        import torch
        from ..models.m1_cnn import SmallCNN

        self.model = SmallCNN()
        self.model.load_state_dict(torch.load(weights, map_location="cpu"))
        self.model.eval()
        self.classes = ["normal", "reversal", "corrected"]

    def predict(self, image_array):
        import torch

        with torch.no_grad():
            x = torch.tensor(image_array, dtype=torch.float32)[None, None]
            probs = torch.softmax(self.model(x), -1)[0]
        return {c: float(p) for c, p in zip(self.classes, probs)}


class ErrorClassifierPredictor:
    def __init__(self, weights: Path = MODELS / "m2_reading_error" / "best.pt"):
        import torch
        from ..models.m2_error_classifier import BiLSTMErrorClassifier

        ckpt = torch.load(weights, map_location="cpu")
        self.labels = ckpt["labels"]
        self.model = BiLSTMErrorClassifier(ckpt["input_dim"], len(self.labels))
        self.model.load_state_dict(ckpt["state_dict"])
        self.model.eval()

    def predict(self, pairs, word_meta):
        import torch

        words = []
        for i, p in enumerate(pairs):
            meta = word_meta[i] if i < len(word_meta) else {}
            words.append({
                "target": p.target, "spoken": p.spoken,
                "word_duration": meta.get("end", 0) - meta.get("start", 0),
                "asr_prob": meta.get("prob", 0.0),
            })
        X = torch.tensor([[featurize(wd, self.labels) for wd in words]],
                         dtype=torch.float32)
        with torch.no_grad():
            pred = self.model(X).argmax(-1)[0].tolist()
        return [{"position": i, "target": w["target"], "spoken": w["spoken"],
                 "label": self.labels[k]} for i, (w, k) in enumerate(zip(words, pred))]


class RiskPredictor:
    def __init__(self, path: Path = MODELS / "m7_risk_score" / "risk_model.joblib"):
        import joblib

        self.scorer = joblib.load(path)

    def score(self, features: dict) -> float:
        import pandas as pd

        row = pd.DataFrame([{f: features.get(f, 0.0)
                             for f in self.scorer.feature_names}])
        return float(self.scorer.predict_proba(row)[0])

    def band(self, score: float) -> str:
        return self.scorer.band(score)
