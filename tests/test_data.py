import json
from pathlib import Path
from src.data.ingestion import load_dataset, validate_dataset
from src.preprocessing.feature_schema import FEATURES, category

def test_official_data_schema_and_size():
    df=load_dataset(); assert len(df)==649; assert len(FEATURES)==32; assert validate_dataset(df)

def test_grade_boundaries():
    assert [category(x) for x in [0,9,10,13,14,20]]==[0,0,1,1,2,2]
def test_research_notebooks_are_valid_json():
    paths=sorted(Path("notebooks").glob("*.ipynb"))
    assert len(paths)==4
    for path in paths:
        notebook=json.loads(path.read_text(encoding="utf-8"))
        assert notebook["nbformat"]==4 and notebook["cells"]
