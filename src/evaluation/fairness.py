"""Descriptive subgroup metrics; small groups are suppressed from interpretation."""
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, recall_score

def subgroup_report(frame, grade_truth, grade_prediction, class_truth, class_prediction,
                    sensitive=("sex","school","address"), minimum_n=10):
    grade_truth=np.asarray(grade_truth); grade_prediction=np.asarray(grade_prediction)
    class_truth=np.asarray(class_truth); class_prediction=np.asarray(class_prediction)
    rows=[]
    for col in sensitive:
        if col not in frame: continue
        for value, idx in frame.groupby(col).groups.items():
            idx=list(idx)
            if len(idx)<minimum_n: continue
            rows.append({"feature":col,"group":str(value),"n":len(idx),
                         "mae":float(mean_absolute_error(grade_truth[idx],grade_prediction[idx])),
                         "recall_macro":float(recall_score(class_truth[idx],class_prediction[idx],average="macro",zero_division=0))})
    return pd.DataFrame(rows)
