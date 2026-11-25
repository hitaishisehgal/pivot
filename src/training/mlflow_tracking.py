"""Local MLflow experiment logging (SQLite tracking; file artifact store)."""
import os
import mlflow

def log_results(results):
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI","sqlite:///mlflow.db"))
    mlflow.set_experiment("PIVOT")
    logged=0
    def metrics(value,prefix=""):
        found={}
        if isinstance(value,dict):
            for key,item in value.items(): found.update(metrics(item,f"{prefix}_{key}" if prefix else key))
        elif isinstance(value,(int,float)) and not isinstance(value,bool): found[prefix[:250]]=float(value)
        return found
    for name,record in results.items():
        if not isinstance(record,dict): continue
        with mlflow.start_run(run_name=name):
            mlflow.log_param("model_key",name)
            for key,value in record.items():
                if key in ("epochs","dropout"): mlflow.log_param(key,value)
                elif key=="architecture": mlflow.log_param(key,"-".join(map(str,value)))
            for key,value in metrics(record).items(): mlflow.log_metric(key,value)
            logged+=1
    return logged
