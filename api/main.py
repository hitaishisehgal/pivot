from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from api.schemas import PredictionRequest, BatchRequest, ScenarioRequest, StudentProfileRequest
from api.services import predictor, mongo_collection

load_dotenv(os.getenv("PIVOT_ENV_FILE",".env"),override=False)
if not os.getenv("MONGODB_URI") and Path("atlas-credentials.env").exists():
    load_dotenv("atlas-credentials.env",override=False)

app=FastAPI(title="PIVOT API",version="1.0.0",description="Student performance research prototype")
logger=logging.getLogger(__name__)

@app.get("/health")
def health(): return {"status":"ok","api":"PIVOT","artifacts":predictor.root.exists()}

def predict(request):
    try: result=predictor.predict_one(request.mode,request.features,request.model)
    except (RuntimeError,ValueError,KeyError) as exc: raise HTTPException(422,str(exc)) from exc
    result["created_at"]=datetime.now(timezone.utc).isoformat()
    if request.student_id: result["student_id"]=request.student_id
    result["history_saved"]=False
    try:
        coll=mongo_collection("prediction_history")
        if coll is not None:
            result["record_id"]=str(coll.insert_one(dict(result)).inserted_id)
            result["history_saved"]=True
    except Exception as exc:
        # Prediction is the primary operation; history persistence is optional.
        logger.warning("Prediction succeeded, but MongoDB history persistence failed (%s)",type(exc).__name__)
    return result

@app.post("/predict")
def predict_route(request:PredictionRequest): return predict(request)

@app.post("/predict/batch")
def batch(request:BatchRequest):
    outputs=[]
    for i,record in enumerate(request.records):
        try:
            validated=PredictionRequest(mode=request.mode,model=request.model,features=record)
            outputs.append(predictor.predict_one(validated.mode,validated.features,validated.model))
        except Exception as exc: raise HTTPException(422,f"Record {i}: {exc}") from exc
    return {"mode":request.mode,"count":len(outputs),"predictions":outputs}

@app.post("/scenario")
def scenario(request:ScenarioRequest):
    features=dict(request.base.features)
    if set(request.changes)-set(features): raise HTTPException(422,"Changes may only update provided mode features")
    changed={**features,**request.changes}
    try:
        changed_request=PredictionRequest(mode=request.base.mode,model=request.base.model,features=changed)
        before=predictor.predict_one(request.base.mode,features,request.base.model)
        after=predictor.predict_one(changed_request.mode,changed_request.features,changed_request.model)
    except Exception as exc: raise HTTPException(422,str(exc)) from exc
    return {"baseline":before,"scenario":after,"grade_delta":after["grade"]-before["grade"],
            "interpretation":"Model scenario comparison only; not a causal estimate."}

@app.get("/students")
def students(limit:int=100):
    try:
        coll=mongo_collection("student_profiles")
        if coll is None: return {"students":[],"message":"MONGODB_URI is not configured"}
        items=list(coll.find({}, {"_id":0}).sort("last_seen",-1).limit(min(limit,500)))
        return {"students":items}
    except Exception as exc: raise HTTPException(503,f"MongoDB unavailable: {type(exc).__name__}") from exc

@app.post("/students")
def save_student(profile:StudentProfileRequest):
    try:
        coll=mongo_collection("student_profiles")
        if coll is None: raise HTTPException(503,"MONGODB_URI is not configured")
        now=datetime.now(timezone.utc).isoformat()
        coll.update_one({"student_id":profile.student_id},{"$set":{"cohort":profile.cohort,"last_seen":now},"$setOnInsert":{"created_at":now}},upsert=True)
        return {"student_id":profile.student_id,"cohort":profile.cohort,"last_seen":now}
    except HTTPException: raise
    except Exception as exc: raise HTTPException(503,f"MongoDB unavailable: {type(exc).__name__}") from exc

@app.get("/students/{student_id}")
def student_detail(student_id:str):
    try:
        profile=mongo_collection("student_profiles").find_one({"student_id":student_id},{"_id":0})
        if profile is None: raise HTTPException(404,"Student profile not found")
        profile["recent_predictions"]=list(mongo_collection("prediction_history").find({"student_id":student_id},{"_id":0}).sort("created_at",-1).limit(20))
        return profile
    except HTTPException: raise
    except Exception as exc: raise HTTPException(503,f"MongoDB unavailable: {type(exc).__name__}") from exc

@app.get("/students/{student_id}/history")
def student_history(student_id:str,limit:int=100):
    try:
        coll=mongo_collection("prediction_history")
        return {"student_id":student_id,"history":list(coll.find({"student_id":student_id},{"_id":0}).sort("created_at",-1).limit(min(limit,500)))}
    except Exception as exc: raise HTTPException(503,f"MongoDB unavailable: {type(exc).__name__}") from exc
