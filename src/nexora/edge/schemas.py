import uuid
from pydantic import BaseModel, Field
from typing import Optional

class SessionRequest(BaseModel):
    # Creating a session is an explicit user action.  Requiring both values
    # prevents an accidental POST from silently creating an unexpected replay.
    scenario: str
    speed: int
    seed: int = Field(default=42, ge=0, le=1000000)

class FeedbackRequest(BaseModel):
    feedback_id: uuid.UUID
    action: str
    helpfulness: Optional[int] = Field(default=None, ge=1, le=5)
    note: str = Field(default='', max_length=500)

class ExperimentRequest(BaseModel):
    mode: str
    rounds: int = Field(default=1, ge=1, le=5)

class Observation(BaseModel):
    event_time_s: float
    source_type: str
    source_label: str
    signals: dict
    heart_rate_bpm: float
    posture_angle_deg: float

class Prediction(BaseModel):
    prediction_id: str
    abstained: bool
    reason: Optional[str] = None
    probabilities: Optional[list] = None
    predicted_class: Optional[int] = None
    model_id: Optional[str] = None
    model_hash: Optional[str] = None
    inference_ms: Optional[float] = None
    features: Optional[list] = None
    source: str

class Decision(BaseModel):
    result: str
    reason_codes: list
    source_type: str
    event_time_s: float
