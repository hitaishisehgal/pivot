import json, os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from src.preprocessing.feature_schema import MODES

class Predictor:
    def __init__(self, root=None): self.root=Path(root or os.getenv("PIVOT_ARTIFACT_DIR","artifacts"))
    def predict_one(self, mode, features, model_type="rf"):
        cols=MODES[mode]
        x=pd.DataFrame([{c:features[c] for c in cols}],columns=cols)
        if model_type=="dnn":
            from src.models.multitask_dnn import build_multitask, predict as predict_dnn
            selection_path=self.root/"metadata"/"dnn_selection.json"
            selection=json.loads(selection_path.read_text(encoding="utf-8")) if selection_path.exists() else {"full":"A2","early":"A2"}
            arch=selection[mode]
            folder=self.root/"versions"/f"{mode}_dnn_{arch}"
            if not (folder/"architecture.json").exists(): raise RuntimeError(f"{mode} DNN artifacts are missing")
            meta=json.loads((folder/"architecture.json").read_text(encoding="utf-8"))
            prep=joblib.load(folder/"preprocessor.joblib"); z=prep.transform(x)
            model=build_multitask(meta["input_dim"],tuple(meta["widths"]),meta["dropout"],meta["learning_rate"],meta["loss_weights"])
            import tensorflow as tf
            tf.train.Checkpoint(model=model).restore(str(folder/"weights")).expect_partial()
            grade,probs=predict_dnn(model,z)
            grade=float(grade[0]); probs=probs[0]
            cal=json.loads((folder/"calibrator.json").read_text(encoding="utf-8"))
            from src.evaluation.calibration import apply_temperature
            probs=apply_temperature(np.asarray([probs]),cal["temperature"])[0]
            cat=int(np.argmax(probs)); grade_cat=0 if grade<=9 else 1 if grade<=13 else 2
            return {"mode":mode,"grade":grade,"class_id":cat,"class_name":["At Risk","Satisfactory","Strong"][cat],
              "probabilities":[float(v) for v in probs],"disagreement":cat!=grade_cat,"grade_implied_class":grade_cat,
              "model":"multitask_dnn","model_version":mode+"_dnn_"+arch}
        regp=self.root/"versions"/f"{mode}_rf_regression"/"pipeline.joblib"
        clsp=self.root/"versions"/f"{mode}_rf_classification"/"pipeline.joblib"
        if not regp.exists() or not clsp.exists(): raise RuntimeError("Trained Random Forest artifacts are missing; run python -m src.training.train")
        reg,cls=joblib.load(regp),joblib.load(clsp)
        grade=float(np.clip(reg.predict(x)[0],0,20)); probs=cls.predict_proba(x)[0]
        labels=cls.named_steps["model"].classes_.tolist()
        calpath=self.root/"versions"/f"{mode}_rf_classification"/"calibrator.json"
        if calpath.exists():
            from src.evaluation.calibration import apply_temperature
            probs=apply_temperature(np.asarray([probs]),json.loads(calpath.read_text(encoding="utf-8"))["temperature"])[0]
        full=[float(probs[labels.index(i)]) if i in labels else 0. for i in range(3)]
        cat=int(np.argmax(full)); grade_cat=0 if grade<=9 else 1 if grade<=13 else 2
        return {"mode":mode,"grade":grade,"class_id":cat,"class_name":["At Risk","Satisfactory","Strong"][cat],
          "probabilities":full,"disagreement":cat!=grade_cat,"grade_implied_class":grade_cat,
          "model":"random_forest","model_version":mode+"_rf_v1"}

predictor=Predictor()

def mongo_collection(name="predictions"):
    uri=os.getenv("MONGODB_URI")
    if not uri: return None
    from pymongo import MongoClient
    client=MongoClient(uri,serverSelectionTimeoutMS=2500)
    client.admin.command("ping")
    return client[os.getenv("MONGODB_DATABASE","pivot")][name]
