"""LIME local explanation for a saved RF pipeline."""
from pathlib import Path
import json
import joblib
from lime.lime_tabular import LimeTabularExplainer
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import MODES

def explain(mode="full", row=0, limit=300):
    df=load_dataset(); dev,_,_=split_data(df); cols=MODES[mode]
    pipe=joblib.load(Path("artifacts/versions")/f"{mode}_rf_classification"/"pipeline.joblib")
    prep=pipe.named_steps["prep"]; x=prep.transform(dev[cols].iloc[:limit]); names=prep.get_feature_names_out()
    exp=LimeTabularExplainer(x,feature_names=names,class_names=["At Risk","Satisfactory","Strong"],
        mode="classification",discretize_continuous=True,random_state=42)
    instance=prep.transform(dev[cols].iloc[[row]])[0]
    items=exp.explain_instance(instance,pipe.named_steps["model"].predict_proba,num_features=12).as_list()
    out={"mode":mode,"row":row,"explanation":[{"rule":name,"weight":float(weight)} for name,weight in items],
         "caution":"Local perturbation explanation; not causal and may be unstable under correlated inputs."}
    path=Path("reports/experiments"); path.mkdir(parents=True,exist_ok=True)
    (path/f"lime_{mode}_row{row}.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    return items
