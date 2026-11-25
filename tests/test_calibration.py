import numpy as np
from src.evaluation.calibration import fit_temperature, apply_temperature, calibration_metrics

def test_temperature_scaling_normalizes_probabilities():
    p=np.array([[.8,.1,.1],[.1,.7,.2],[.2,.2,.6]])
    t=fit_temperature(np.log(p),[0,1,2]); q=apply_temperature(p,t)
    assert t>0 and np.allclose(q.sum(axis=1),1)
    assert calibration_metrics([0,1,2],q)["brier_score"]>=0
