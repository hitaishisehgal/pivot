from pathlib import Path
import pandas as pd
from src.preprocessing.feature_schema import FEATURES, TARGET, category

EXPECTED = FEATURES + [TARGET]

def load_dataset(path="data/raw/student-por.csv"):
    path = Path(path)
    if not path.exists():
        # Original provided workspace location; no download or synthetic fallback.
        path = Path("data/student/student-por.csv")
    df = pd.read_csv(path, sep=";", quotechar='"')
    validate_dataset(df)
    return df

def validate_dataset(df):
    missing = sorted(set(EXPECTED) - set(df.columns))
    extra = sorted(set(df.columns) - set(EXPECTED))
    if missing or extra:
        raise ValueError(f"Dataset schema mismatch; missing={missing}, extra={extra}")
    if len(df) != 649:
        raise ValueError(f"Expected 649 official Portuguese records, got {len(df)}")
    if df[TARGET].isna().any() or not df[TARGET].between(0, 20).all():
        raise ValueError("G3 must be present and in [0, 20]")
    return True

def with_targets(df):
    result = df.copy()
    result["performance_category"] = result[TARGET].map(category).astype("int64")
    return result
