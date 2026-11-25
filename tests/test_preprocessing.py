import pandas as pd
from src.preprocessing.pipeline import make_preprocessor
from src.preprocessing.feature_schema import MODES
from src.data.ingestion import load_dataset

def test_pipeline_handles_unknown_categories():
    df=load_dataset(); x=df[MODES["early"]].iloc[:5].copy()
    prep=make_preprocessor(x); prep.fit(x)
    new=x.iloc[:1].copy(); new.loc[new.index[0],"school"]="UNKNOWN"
    assert prep.transform(new).shape[0]==1

def test_early_schema_excludes_period_grades():
    assert "G1" not in MODES["early"] and "G2" not in MODES["early"]
