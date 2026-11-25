"""Controlled feature-group comparisons using the shared seed-42 split."""
import json
from pathlib import Path
import numpy as np
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import FEATURES, MODES, GROUPS, TARGET, category
from src.preprocessing.pipeline import make_preprocessor, make_forest
from src.evaluation.metrics import regression_metrics, classification_metrics

def run():
    df=load_dataset(); dev,test,cv=split_data(df); results={}
    labels=lambda y:np.asarray([category(v) for v in y],dtype=int)
    for mode,eligible in MODES.items():
        for group,group_features in GROUPS.items():
            cols=[c for c in group_features if c in eligible]
            for task in ("regression","classification"):
                y=dev[TARGET].to_numpy(float) if task=="regression" else labels(dev[TARGET])
                yt=test[TARGET].to_numpy(float) if task=="regression" else labels(test[TARGET])
                estimator=Pipeline([("prep",make_preprocessor(dev[cols],False)),("model",make_forest(task))])
                splits=list(cv.split(dev[cols],labels(dev[TARGET])))
                scoring="neg_mean_absolute_error" if task=="regression" else "f1_macro"
                scores=cross_validate(estimator,dev[cols],y,cv=splits,scoring=scoring,n_jobs=1)["test_score"]
                estimator.fit(dev[cols],y); pred=estimator.predict(test[cols])
                m=regression_metrics(yt,pred) if task=="regression" else classification_metrics(yt,pred)
                vals=-scores if task=="regression" else scores
                m["cv_mean"]=float(np.mean(vals)); m["cv_std"]=float(np.std(vals,ddof=1))
                results[f"{mode}_{group}_{task}"]={"features":cols,"metrics":m}
    path=Path("reports/experiments"); path.mkdir(parents=True,exist_ok=True)
    (path/"feature_groups.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    return results

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
