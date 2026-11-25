"""Development-only MI and permutation importance diagnostics; no final-test selection."""
import json
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import MODES,TARGET,category
from src.preprocessing.pipeline import make_preprocessor,make_forest
from src.evaluation.feature_analysis import mutual_information,permutation_scores

def run():
    df=load_dataset(); dev,_,_=split_data(df); report={}
    for mode,cols in MODES.items():
        a,b=train_test_split(np.arange(len(dev)),test_size=.2,random_state=42,stratify=[category(v) for v in dev[TARGET]])
        train=dev.iloc[a]; valid=dev.iloc[b]; report[mode]={}
        for task in ("regression","classification"):
            y=train[TARGET].to_numpy(float) if task=="regression" else np.asarray([category(v) for v in train[TARGET]])
            yv=valid[TARGET].to_numpy(float) if task=="regression" else np.asarray([category(v) for v in valid[TARGET]])
            pipeline=Pipeline([("prep",make_preprocessor(train[cols],False)),("model",make_forest(task))])
            pipeline.fit(train[cols],y)
            z=pipeline.named_steps["prep"].transform(train[cols]); names=pipeline.named_steps["prep"].get_feature_names_out()
            mi=mutual_information(z,y,task)
            scoring="neg_mean_absolute_error" if task=="regression" else "f1_macro"
            perm=permutation_scores(pipeline,valid[cols],yv,scoring=scoring)
            report[mode][task]={
                "mutual_information_top20":[{"feature":str(names[i]),"score":float(mi[i])} for i in np.argsort(mi)[::-1][:20]],
                "permutation_top20":[{"feature":cols[i],"score_mean":float(perm.importances_mean[i]),"score_std":float(perm.importances_std[i])} for i in np.argsort(perm.importances_mean)[::-1][:20]],
                "validation_rows":len(valid),"note":"Importance ranks are development-only associations; they were not used to select features for final models."}
    path=Path("reports/experiments"); path.mkdir(parents=True,exist_ok=True)
    (path/"feature_selection.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report

if __name__=="__main__":print(json.dumps(run(),indent=2))
