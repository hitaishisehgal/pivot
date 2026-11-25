"""Reproducible UCI Portuguese dataset profile."""
import json
from pathlib import Path
from src.data.ingestion import load_dataset,with_targets

def run():
    source=load_dataset(); df=with_targets(source)
    numeric=df.select_dtypes(include="number")
    profile={"rows":len(source),"columns":len(source.columns),"column_names":source.columns.tolist(),
        "dtypes":{k:str(v) for k,v in source.dtypes.items()},"missing_values":{k:int(v) for k,v in source.isna().sum().items()},
        "g3_counts":{str(k):int(v) for k,v in df["G3"].value_counts().sort_index().items()},
        "performance_category_counts":{str(k):int(v) for k,v in df["performance_category"].value_counts().sort_index().items()},
        "numeric_summary":source.select_dtypes(include="number").describe().round(3).to_dict(),
        "derived_column":"performance_category"}
    path=Path("reports/experiments"); path.mkdir(parents=True,exist_ok=True)
    (path/"data_profile.json").write_text(json.dumps(profile,indent=2),encoding="utf-8")
    return profile

if __name__=="__main__":print(json.dumps(run(),indent=2))
