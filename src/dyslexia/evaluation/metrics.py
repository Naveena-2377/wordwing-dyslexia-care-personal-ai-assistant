"""Task-appropriate metrics. Accuracy alone hides the failure that matters:
missing a real error is worse than flagging a false one in a screening tool."""
from sklearn.metrics import (classification_report, confusion_matrix,
                             f1_score, roc_auc_score)


def error_classifier_report(y_true, y_pred, labels):
    return {
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "per_class": classification_report(y_true, y_pred, target_names=labels,
                                           output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def screening_report(y_true, y_score, recall_floor: float = 0.90):
    """Report precision at the threshold that guarantees a minimum recall."""
    import numpy as np
    from sklearn.metrics import precision_recall_curve

    prec, rec, thr = precision_recall_curve(y_true, y_score)
    idx = np.where(rec >= recall_floor)[0]
    chosen = idx[np.argmax(prec[idx])] if len(idx) else 0
    return {
        "roc_auc": roc_auc_score(y_true, y_score),
        "recall_floor": recall_floor,
        "precision_at_floor": float(prec[chosen]),
        "threshold": float(thr[min(chosen, len(thr) - 1)]),
    }


def simplification_report(sources, predictions, references):
    import sacrebleu
    import textstat

    return {
        "sari_proxy_bleu": sacrebleu.corpus_bleu(predictions, [references]).score,
        "mean_grade_before": sum(map(textstat.flesch_kincaid_grade, sources)) / len(sources),
        "mean_grade_after": sum(map(textstat.flesch_kincaid_grade, predictions)) / len(predictions),
    }
