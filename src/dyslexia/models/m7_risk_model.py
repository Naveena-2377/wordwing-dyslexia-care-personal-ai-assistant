"""Module 7: dyslexia-risk / severity scoring with gradient boosting.

Deliberately interpretable - a screening score that a teacher cannot interrogate
is a score no school will act on. SHAP values ship with every prediction.
"""
import numpy as np


class RiskScorer:
    def __init__(self, cfg: dict):
        from xgboost import XGBClassifier

        m = cfg["model"]
        self.model = XGBClassifier(
            n_estimators=m["n_estimators"], max_depth=m["max_depth"],
            learning_rate=m["learning_rate"], subsample=m["subsample"],
            eval_metric="logloss", tree_method="hist",
        )
        self.calibrator = None
        self.feature_names = cfg["features"]

    def fit(self, X, y, X_val=None, y_val=None):
        self.model.fit(X, y)
        if X_val is not None:
            from sklearn.calibration import CalibratedClassifierCV
            from sklearn.frozen import FrozenEstimator  # sklearn>=1.6

            self.calibrator = CalibratedClassifierCV(
                FrozenEstimator(self.model), method="isotonic").fit(X_val, y_val)
        return self

    def predict_proba(self, X) -> np.ndarray:
        est = self.calibrator or self.model
        return est.predict_proba(X)[:, 1]

    def band(self, score: float) -> str:
        """Screening output is a band, never a diagnosis."""
        if score < 0.33:
            return "low_indicator"
        if score < 0.66:
            return "monitor"
        return "refer_for_assessment"

    def explain(self, X):
        import shap

        return shap.TreeExplainer(self.model).shap_values(X)
