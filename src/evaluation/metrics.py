import numpy as np
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score, accuracy_score,
    precision_score, recall_score, f1_score, balanced_accuracy_score, confusion_matrix,
    classification_report)

def regression_metrics(y, pred):
    pred = np.clip(np.asarray(pred).reshape(-1), 0, 20)
    return {"mae": float(mean_absolute_error(y, pred)), "rmse": float(np.sqrt(mean_squared_error(y, pred))),
            "r2": float(r2_score(y, pred))}

def classification_metrics(y, pred):
    labels = [0, 1, 2]
    return {"accuracy": float(accuracy_score(y, pred)),
            "precision_macro": float(precision_score(y, pred, labels=labels, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y, pred, labels=labels, average="macro", zero_division=0)),
            "macro_f1": float(f1_score(y, pred, labels=labels, average="macro", zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
            "confusion_matrix": confusion_matrix(y, pred, labels=labels).tolist(),
            "per_class": classification_report(y, pred, labels=labels, output_dict=True, zero_division=0)}
