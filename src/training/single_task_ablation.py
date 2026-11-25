"""Compare independent single-task heads with the shared multi-task model on development validation only."""
import json
from pathlib import Path
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from src.data.ingestion import load_dataset
from src.data.splitting import split_data
from src.preprocessing.feature_schema import MODES,TARGET,category
from src.preprocessing.pipeline import make_preprocessor
from src.models.multitask_dnn import build_single_task
from src.evaluation.metrics import regression_metrics,classification_metrics

def run():
    tf.keras.utils.set_random_seed(42); df=load_dataset(); dev,_,_=split_data(df); results={}
    selected={"full":((32,),.2),"early":((64,32),.2)}
    for mode,cols in MODES.items():
        prep=make_preprocessor(dev[cols],True)
        a,b=train_test_split(np.arange(len(dev)),test_size=.2,random_state=42,stratify=[category(v) for v in dev[TARGET]])
        xfit=prep.fit_transform(dev.iloc[a][cols]); xval=prep.transform(dev.iloc[b][cols])
        yfit=dev.iloc[a][TARGET].to_numpy(float); yval=dev.iloc[b][TARGET].to_numpy(float)
        for task in ("regression","classification"):
            model=build_single_task(xfit.shape[1],task,*selected[mode])
            ytrain=yfit/20. if task=="regression" else np.asarray([category(v) for v in yfit])
            yvalid=yval/20. if task=="regression" else np.asarray([category(v) for v in yval])
            hist=model.fit(xfit,ytrain,validation_data=(xval,yvalid),epochs=200,batch_size=16,verbose=0,
                callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss",patience=20,restore_best_weights=True),
                    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss",factor=.5,patience=8,min_lr=1e-5)])
            raw=model(tf.convert_to_tensor(xval),training=False).numpy()
            if task=="regression": result=regression_metrics(yval,raw.reshape(-1)*20)
            else: result=classification_metrics(yvalid,raw.argmax(1))
            results[f"{mode}_{task}"]={"validation":result,"epochs":len(hist.history["loss"]),"architecture":list(selected[mode][0])}
    p=Path("reports/experiments"); p.mkdir(parents=True,exist_ok=True)
    (p/"single_task_results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    return results

if __name__=="__main__":print(json.dumps(run(),indent=2))
