"""Tree SHAP summaries for fitted Random Forest pipelines."""
import json
from pathlib import Path
import joblib
import numpy as np
import shap
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import MODES

def explain(mode="full", task="regression", limit=100):
    df=load_dataset(); dev,_,_=split_data(df); cols=MODES[mode]
    pipeline=joblib.load(Path("artifacts/versions")/f"{mode}_rf_{task}"/"pipeline.joblib")
    prep=pipeline.named_steps["prep"]; model=pipeline.named_steps["model"]
    x=prep.transform(dev[cols].iloc[:limit]); names=prep.get_feature_names_out().tolist()
    values=shap.TreeExplainer(model)(x)
    arr=np.asarray(values.values)
    if arr.ndim==3: arr=np.mean(np.abs(arr),axis=(0,2))
    else: arr=np.mean(np.abs(arr),axis=0)
    ranking=sorted([{"feature":n,"mean_abs_shap":float(v)} for n,v in zip(names,arr)],key=lambda z:z["mean_abs_shap"],reverse=True)
    out={"mode":mode,"task":task,"background_rows":min(limit,len(dev)),"top_features":ranking[:30],
         "caution":"Associational attribution; correlated features and the small source cohort can destabilize rankings."}
    path=Path("reports/experiments"); path.mkdir(parents=True,exist_ok=True)
    (path/f"shap_{mode}_{task}.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    return out
