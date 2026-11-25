from sklearn.model_selection import train_test_split, StratifiedKFold
from src.preprocessing.feature_schema import TARGET, category

def split_data(df, seed=42, test_size=.2, max_folds=5):
    y = df[TARGET].astype(float)
    strat = y.map(category)
    dev, test = train_test_split(df, test_size=test_size, random_state=seed, stratify=strat)
    counts = dev[TARGET].map(category).value_counts()
    folds = min(max_folds, int(counts.min()))
    if folds < 2:
        raise ValueError("Insufficient development class counts for stratified cross-validation")
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    return dev.reset_index(drop=True), test.reset_index(drop=True), cv
