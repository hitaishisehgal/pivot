from fastapi.testclient import TestClient
from api.main import app
from api.schemas import PredictionRequest, StudentProfileRequest
from src.preprocessing.feature_schema import MODES
from src.data.ingestion import load_dataset

client=TestClient(app)

def test_health(): assert client.get("/health").status_code==200

def test_early_input_rejects_grades():
    row=load_dataset().iloc[0].to_dict()
    try: PredictionRequest(mode="early",features=row)
    except Exception: return
    assert False,"early requests must reject G1/G2/G3 extras"

def test_api_batch_requires_records(): assert client.post("/predict/batch",json={"mode":"early","records":[]}).status_code==422

def test_invalid_grade_range_rejected():
    row=load_dataset().iloc[0].to_dict(); row.update({k:row[k] for k in MODES["full"]}); row["G1"]=25
    assert client.post("/predict",json={"mode":"full","features":{k:row[k] for k in MODES["full"]}}).status_code==422

def test_batch_rejects_target_leakage():
    row=load_dataset().iloc[0].to_dict(); features={k:row[k] for k in MODES["early"]}; features["G3"]=row["G3"]
    assert client.post("/predict/batch",json={"mode":"early","records":[features]}).status_code==422

def test_student_ids_are_pseudonymous_tokens():
    assert StudentProfileRequest(student_id="learner_001").student_id=="learner_001"
    try: StudentProfileRequest(student_id="student name")
    except Exception: return
    assert False,"student IDs must use the restricted pseudonymous token format"
