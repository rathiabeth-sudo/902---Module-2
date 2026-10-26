"""Classification and regression metrics (NumPy / scikit-learn only)."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, mean_absolute_error,
                             mean_squared_error, precision_recall_fscore_support, r2_score, roc_auc_score)


def reg_metrics(y, yhat) -> dict:
    return {"MAE": float(mean_absolute_error(y, yhat)), "RMSE": float(np.sqrt(mean_squared_error(y, yhat))),
            "R2": float(r2_score(y, yhat)), "n": int(len(y))}


def expected_calibration_error(probs: np.ndarray, y: np.ndarray, n_bins: int = 10) -> float:
    conf = probs.max(1)
    pred = probs.argmax(1)
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            ece += m.mean() * abs((pred[m] == y[m]).mean() - conf[m].mean())
    return float(ece)


def classification_metrics(y: np.ndarray, probs: np.ndarray, names: list[str]) -> dict:
    pred = probs.argmax(1)
    k = len(names)
    prec, rec, f1, sup = precision_recall_fscore_support(y, pred, labels=list(range(k)), zero_division=0)
    out = {
        "n": int(len(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "macro_precision": float(prec.mean()),
        "macro_recall": float(rec.mean()),
        "macro_f1": float(f1_score(y, pred, average="macro", labels=list(range(k)), zero_division=0)),
        "weighted_f1": float(f1_score(y, pred, average="weighted", labels=list(range(k)), zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "ece": expected_calibration_error(probs, y),
        "confusion_matrix": confusion_matrix(y, pred, labels=list(range(k))).tolist(),
        "per_class": {names[i]: {"precision": float(prec[i]), "recall": float(rec[i]), "f1": float(f1[i]),
                                 "support": int(sup[i])} for i in range(k)},
    }
    try:
        if len(np.unique(y)) == k:
            out["roc_auc_ovr_macro"] = float(roc_auc_score(y, probs, multi_class="ovr", average="macro"))
    except ValueError:
        pass
    return out
