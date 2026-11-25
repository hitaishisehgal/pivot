"""Reproducible baseline and multitask training. The held-out test is scored only after fitting."""
import argparse, json, os
from pathlib import Path
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_validate, cross_val_predict
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import FEATURES, MODES, GROUPS, TARGET, category
from src.preprocessing.pipeline import make_preprocessor, make_forest
from src.evaluation.metrics import regression_metrics, classification_metrics
from src.evaluation.calibration import fit_temperature, apply_temperature, calibration_metrics

def _class(y): return np.asarray([category(v) for v in y], dtype=int)

def train_forest(dev, test, feature_cols, mode, task, outdir):
    target = dev[TARGET].to_numpy() if task == "regression" else _class(dev[TARGET])
    test_y = test[TARGET].to_numpy() if task == "regression" else _class(test[TARGET])
    pipe = Pipeline([("prep", make_preprocessor(dev[feature_cols], scale_numeric=False)),
                     ("model", make_forest(task))])
    scoring = "neg_mean_absolute_error" if task == "regression" else "f1_macro"
    # Stratify regression folds on the coarse grade bands, never on continuous G3 values.
    cv_splits=list(_cv.split(dev[feature_cols], _class(dev[TARGET])))
    cv = cross_validate(pipe, dev[feature_cols], target, cv=cv_splits, scoring=scoring, n_jobs=1)
    temperature=1.0
    if task=="classification":
        oof=cross_val_predict(pipe,dev[feature_cols],target,cv=cv_splits,method="predict_proba",n_jobs=1)
        temperature=fit_temperature(np.log(np.clip(oof,1e-9,1)),target)
    pipe.fit(dev[feature_cols], target)
    if task=="regression":
        pred=pipe.predict(test[feature_cols]); metrics=regression_metrics(test_y,pred)
    else:
        raw=pipe.predict_proba(test[feature_cols]); calibrated=apply_temperature(raw,temperature)
        pred=pipe.named_steps["model"].classes_[calibrated.argmax(1)]
        metrics=classification_metrics(test_y,pred)
        metrics["calibration"]={"temperature":temperature,**calibration_metrics(test_y,calibrated)}
    cv_scores=-cv["test_score"] if task=="regression" else cv["test_score"]
    metrics["cv_mean"] = float(np.mean(cv_scores))
    metrics["cv_std"] = float(np.std(cv_scores, ddof=1))
    folder = Path(outdir)/"versions"/f"{mode}_rf_{task}"
    folder.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, folder/"pipeline.joblib")
    if task=="classification": (folder/"calibrator.json").write_text(json.dumps({"temperature":temperature},indent=2),encoding="utf-8")
    (folder/"metadata.json").write_text(json.dumps({"mode":mode,"task":task,"features":feature_cols,
        "test_metrics":metrics,"seed":42}, indent=2), encoding="utf-8")
    return metrics

def run(data_path="data/raw/student-por.csv", outdir="artifacts", ablation=False):
    global _cv
    df=load_dataset(data_path)
    dev,test,_cv=split_data(df)
    results={}
    if not ablation:
        for mode, cols in MODES.items():
            for task in ("regression","classification"):
                results[f"{mode}_rf_{task}"]=train_forest(dev,test,cols,mode,task,outdir)
    try:
        import tensorflow as tf
        tf.keras.utils.set_random_seed(42)
    except Exception as exc:
        results["dnn_status"]={"status":"blocked","error":f"{type(exc).__name__}: {exc}"}
        report=Path("reports/experiments"); report.mkdir(parents=True,exist_ok=True)
        (report/"training_results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
        print(json.dumps(results,indent=2))
        return results
    # DNN fit uses training-only preprocessing; reserve a deterministic validation slice in development.
    from src.models.multitask_dnn import build_multitask, fit_multitask, predict
    from sklearn.model_selection import train_test_split
    settings=[("A1",(32,),.2),("A2",(64,32),.2),("A3",(64,32),.35),("A4",(128,64,32),.2)]
    if not ablation:
        # Selected using development-only validation ablation, before final test scoring.
        selected={"full":"A1","early":"A2"}
        meta=Path(outdir)/"metadata"; meta.mkdir(parents=True,exist_ok=True)
        (meta/"dnn_selection.json").write_text(json.dumps(selected,indent=2),encoding="utf-8")
    for mode, cols in MODES.items():
        sub=dev
        prep=make_preprocessor(sub[cols], True)
        fit_idx,val_idx=train_test_split(np.arange(len(sub)),test_size=.2,random_state=42,
             stratify=_class(sub[TARGET]))
        xfit=prep.fit_transform(sub.iloc[fit_idx][cols]); xval=prep.transform(sub.iloc[val_idx][cols]); xtest=prep.transform(test[cols])
        yfit=sub.iloc[fit_idx][TARGET].to_numpy(float); yval=sub.iloc[val_idx][TARGET].to_numpy(float)
        mode_settings=settings if ablation else [s for s in settings if s[0]==selected[mode]]
        for arch,widths,drop in mode_settings:
            model=build_multitask(xfit.shape[1],widths,drop)
            hist=fit_multitask(model,xfit,yfit,_class(yfit),validation_split=0,epochs=200,batch_size=16,
                verbose=0) if False else model.fit(xfit,{"grade_scaled":yfit/20.,"category":_class(yfit)},
                validation_data=(xval,{"grade_scaled":yval/20.,"category":_class(yval)}),epochs=200,batch_size=16,verbose=0,
                callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss",patience=20,restore_best_weights=True),
                    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss",factor=.5,patience=8,min_lr=1e-5)])
            if ablation:
                # Architecture comparisons use development validation only; the final test remains untouched.
                pred,probs=predict(model,xval)
                result={"validation_regression":regression_metrics(yval,pred),
                    "validation_classification":classification_metrics(_class(yval),probs.argmax(1)),
                    "epochs":len(hist.history["loss"]),"architecture":list(widths),"dropout":drop}
            else:
                pred,probs=predict(model,xtest)
                val_probs=model(tf.convert_to_tensor(xval),training=False)["category"].numpy()
                temperature=fit_temperature(np.log(np.clip(val_probs,1e-9,1)),_class(yval))
                probs=apply_temperature(probs,temperature)
                result={"regression":regression_metrics(test[TARGET],pred),
                    "classification":{**classification_metrics(_class(test[TARGET]),probs.argmax(1)),
                        "calibration":{"temperature":temperature,**calibration_metrics(_class(test[TARGET]),probs)}},
                    "epochs":len(hist.history["loss"]),"architecture":list(widths),"dropout":drop}
            folder=Path(outdir)/"versions"/f"{mode}_dnn_{arch}"; folder.mkdir(parents=True,exist_ok=True)
            if not ablation:
                # Use a TensorFlow checkpoint so model persistence does not need Keras' h5py serializer.
                tf.train.Checkpoint(model=model).write(str(folder/"weights"))
                joblib.dump(prep,folder/"preprocessor.joblib")
                (folder/"architecture.json").write_text(json.dumps({"input_dim":int(xfit.shape[1]),
                    "widths":list(widths),"dropout":drop,"learning_rate":.001,
                    "loss_weights":{"grade_scaled":1.,"category":1.}},indent=2),encoding="utf-8")
                (folder/"calibrator.json").write_text(json.dumps({"temperature":temperature},indent=2),encoding="utf-8")
                np.savez(folder/"history.npz",**hist.history)
                (folder/"metadata.json").write_text(json.dumps({"mode":mode,"features":cols,"results":result},indent=2),encoding="utf-8")
            results[f"{mode}_dnn_{arch}"]=result
        if not ablation:
            # The base deployment alias is the A2 shared multi-task model.
            pass
    report=Path("reports/experiments"); report.mkdir(parents=True,exist_ok=True)
    name="ablation_results.json" if ablation else "training_results.json"
    (report/name).write_text(json.dumps(results,indent=2),encoding="utf-8")
    if not ablation:
        try:
            from src.training.mlflow_tracking import log_results
            results["mlflow_status"]={"status":"logged","runs":log_results(results)}
        except Exception as exc:
            results["mlflow_status"]={"status":"error","error":f"{type(exc).__name__}: {exc}"}
        (report/name).write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))
    return results

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--data",default="data/raw/student-por.csv")
    parser.add_argument("--artifacts",default="artifacts"); parser.add_argument("--ablation",action="store_true")
    args=parser.parse_args(); run(args.data,args.artifacts,args.ablation)
