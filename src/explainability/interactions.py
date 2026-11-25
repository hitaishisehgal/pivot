"""Pairwise partial-dependence interaction probe for a fitted RF regressor."""
import numpy as np
import json
from sklearn.inspection import partial_dependence
from pathlib import Path
import joblib
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import MODES

def pairwise_probe(mode="full", max_features=12):
    df=load_dataset(); dev,_,_=split_data(df); cols=MODES[mode]
    pipe=joblib.load(Path("artifacts/versions")/f"{mode}_rf_regression"/"pipeline.joblib")
    numeric=[c for c in cols if c in ("G1","G2","studytime","failures","absences","age","traveltime")]
    rows=[]
    # sklearn expects numerical partial-dependence features as floats; several
    # ordinal columns arrive as integers in the source CSV.
    probe_data=dev[cols].copy()
    probe_data[numeric]=probe_data[numeric].astype(float)
    for i,a in enumerate(numeric):
        for b in numeric[i+1:]:
            pdp=partial_dependence(pipe,probe_data,[(cols.index(a),cols.index(b))],kind="average",grid_resolution=8)
            surface=np.asarray(pdp.average[0],dtype=float)
            residual=surface-surface.mean(axis=0,keepdims=True)-surface.mean(axis=1,keepdims=True)+surface.mean()
            rows.append({"features":[a,b],"pdp_interaction_rms":float(np.sqrt(np.mean(residual**2)))})
    return sorted(rows,key=lambda row:row["pdp_interaction_rms"],reverse=True)[:max_features]

if __name__=="__main__":
    result={mode:pairwise_probe(mode) for mode in ("full","early")}
    path=Path("reports/experiments"); path.mkdir(parents=True,exist_ok=True)
    (path/"interactions.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
