import numpy as np
from src.models.multitask_dnn import build_multitask, predict

def test_multitask_model_outputs_bounded_grade_and_three_probabilities():
    model=build_multitask(5)
    grade,prob=predict(model,np.zeros((4,5),dtype=np.float32))
    assert grade.shape==(4,) and ((grade>=0)&(grade<=20)).all()
    assert prob.shape==(4,3) and np.allclose(prob.sum(axis=1),1,atol=1e-5)
