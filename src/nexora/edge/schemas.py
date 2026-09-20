import uuid
from pydantic import BaseModel, Field
from typing import Optional

class SessionRequest(BaseModel):
    scenario: str = 'normal'
    speed: int = Field(default=5)
    seed: int = Field(default=42, ge=0, le=1000000)

class FeedbackRequest(BaseModel):
    feedback_id: uuid.UUID
    action: str
    helpfulness: Optional[int] = Field(default=None, ge=1, le=5)
    note: str = Field(default='', max_length=500)

class ExperimentRequest(BaseModel):
    mode: str
    rounds: int = Field(default=1, ge=1, le=5)
