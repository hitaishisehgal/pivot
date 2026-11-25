import os
import pytest

def test_database_is_optional_without_uri(monkeypatch):
    monkeypatch.delenv("MONGODB_URI",raising=False)
    from api.services import mongo_collection
    assert mongo_collection() is None

def test_isolated_atlas_roundtrip():
    if os.getenv("PIVOT_RUN_MONGO_TESTS")!="1" or not os.getenv("MONGODB_URI"):
        pytest.skip("Set PIVOT_RUN_MONGO_TESTS=1 with Atlas credentials to run the isolated integration check")
    from pymongo import MongoClient
    client=MongoClient(os.environ["MONGODB_URI"],serverSelectionTimeoutMS=8000)
    collection=client["pivot_test"]["integration_records"]
    record={"kind":"automated_test","value":"roundtrip"}
    result=collection.insert_one(record)
    try:
        found=collection.find_one({"_id":result.inserted_id})
        assert found["value"]=="roundtrip"
    finally:
        collection.delete_one({"_id":result.inserted_id})
        client.close()

def test_student_profile_prediction_history_api():
    if os.getenv("PIVOT_RUN_MONGO_TESTS")!="1" or not os.getenv("MONGODB_URI"):
        pytest.skip("Set PIVOT_RUN_MONGO_TESTS=1 with Atlas credentials for isolated API persistence checks")
    from uuid import uuid4
    from fastapi.testclient import TestClient
    from pymongo import MongoClient
    from api.main import app
    from src.data.ingestion import load_dataset
    from src.preprocessing.feature_schema import MODES
    student_id="test_"+uuid4().hex
    client=MongoClient(os.environ["MONGODB_URI"],serverSelectionTimeoutMS=8000)
    db=client[os.getenv("MONGODB_DATABASE","pivot_test")]
    api=TestClient(app)
    try:
        assert api.post("/students",json={"student_id":student_id,"cohort":"integration"}).status_code==200
        row=load_dataset().iloc[0].to_dict(); features={k:row[k] for k in MODES["early"]}
        pred=api.post("/predict",json={"mode":"early","model":"rf","student_id":student_id,"features":features})
        assert pred.status_code==200
        detail=api.get(f"/students/{student_id}")
        assert detail.status_code==200 and len(detail.json()["recent_predictions"])==1
        history=api.get(f"/students/{student_id}/history")
        assert history.status_code==200 and len(history.json()["history"])==1
    finally:
        db["student_profiles"].delete_one({"student_id":student_id})
        db["prediction_history"].delete_many({"student_id":student_id})
        client.close()
