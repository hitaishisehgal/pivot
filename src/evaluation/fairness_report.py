"""Generate transparent test-set subgroup summaries for saved RF artifacts."""
import json
from pathlib import Path
import joblib
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import MODES, TARGET, category
from src.evaluation.fairness import subgroup_report

def run():
    df=load_dataset(); _,test,_=split_data(df); out={}
    truth=test[TARGET].to_numpy(); classes=[category(v) for v in truth]
    for mode,cols in MODES.items():
        reg=joblib.load(Path("artifacts/versions")/f"{mode}_rf_regression"/"pipeline.joblib")
        cls=joblib.load(Path("artifacts/versions")/f"{mode}_rf_classification"/"pipeline.joblib")
        gp=reg.predict(test[cols]).clip(0,20); cp=cls.predict(test[cols])
        frame=test[cols].reset_index(drop=True)
        out[mode]=subgroup_report(frame,truth,gp,classes,cp).to_dict("records")
    p=Path("reports/experiments"); p.mkdir(parents=True,exist_ok=True)
    (p/"fairness.json").write_text(json.dumps(out,indent=2),encoding="utf-8"); return out

if __name__=="__main__": print(json.dumps(run(),indent=2))
