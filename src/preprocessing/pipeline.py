"""Fold-fitted preprocessing factories; no target or held-out rows are transformed as inputs."""
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

def make_preprocessor(frame, scale_numeric=True):
    nums = frame.select_dtypes(include="number").columns.tolist()
    cats = [c for c in frame.columns if c not in nums]
    nsteps = [("impute", SimpleImputer(strategy="median"))]
    if scale_numeric: nsteps.append(("scale", StandardScaler()))
    csteps = [("impute", SimpleImputer(strategy="most_frequent")),
              ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]
    return ColumnTransformer([("num", Pipeline(nsteps), nums), ("cat", Pipeline(csteps), cats)],
                             verbose_feature_names_out=False)

def make_forest(kind, seed=42):
    if kind == "regression":
        return RandomForestRegressor(n_estimators=400, min_samples_leaf=2, max_features=.8,
                                     random_state=seed, n_jobs=-1)
    if kind == "classification":
        return RandomForestClassifier(n_estimators=400, min_samples_leaf=2, max_features=.8,
                                      class_weight="balanced", random_state=seed, n_jobs=-1)
    raise ValueError(kind)
