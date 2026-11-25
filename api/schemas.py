from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.preprocessing.feature_schema import FEATURES

RANGES={"age":(15,22),"Medu":(0,4),"Fedu":(0,4),"traveltime":(1,4),
    "studytime":(1,4),"failures":(0,4),"famrel":(1,5),"freetime":(1,5),
    "goout":(1,5),"Dalc":(1,5),"Walc":(1,5),"health":(1,5),
    "absences":(0,93),"G1":(0,20),"G2":(0,20)}

class PredictionRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    mode: Literal["full","early"]="full"
    model: Literal["rf","dnn"]="rf"
    student_id: str | None = Field(default=None,min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_.-]+$")
    features: dict[str,Any]
    @model_validator(mode="after")
    def check_features(self):
        required=set(FEATURES)
        if self.mode=="early": required-={"G1","G2"}
        missing=required-set(self.features)
        extra=set(self.features)-required
        if missing or extra: raise ValueError(f"Feature mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
        if self.mode=="early" and ({"G1","G2"}&set(self.features)): raise ValueError("Early mode must not receive G1/G2")
        for key,(lo,hi) in RANGES.items():
            if key in required:
                try: value=float(self.features[key])
                except (ValueError,TypeError) as exc: raise ValueError(f"{key} must be numeric") from exc
                if not lo<=value<=hi: raise ValueError(f"{key} must be in [{lo},{hi}]")
        return self

class BatchRequest(BaseModel):
    mode: Literal["full","early"]="full"
    model: Literal["rf","dnn"]="rf"
    records: list[dict[str,Any]]=Field(min_length=1,max_length=500)

class ScenarioRequest(BaseModel):
    base: PredictionRequest
    changes: dict[str,Any]

class StudentProfileRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    student_id: str=Field(min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_.-]+$")
    cohort: str | None=Field(default=None,max_length=100)
