from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.inspection import permutation_importance

def mutual_information(x, y, task="regression", seed=42):
    fn=mutual_info_regression if task=="regression" else mutual_info_classif
    return fn(x,y,random_state=seed)

def permutation_scores(estimator, x, y, scoring="neg_mean_absolute_error", seed=42):
    return permutation_importance(estimator,x,y,scoring=scoring,n_repeats=5,random_state=seed,n_jobs=1)
