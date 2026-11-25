import numpy as np
from src.evaluation.metrics import regression_metrics, classification_metrics

def test_regression_metrics_clip_bounds():
    got=regression_metrics([1,19],[0,23]); assert got["mae"]==1.0

def test_class_metrics_have_three_classes():
    got=classification_metrics([0,1,2],[0,1,1]); assert len(got["confusion_matrix"])==3
