import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    title: str
    description: str | None = None
    source: str = "manual"
    severity: str = "MEDIUM"
    raw_payload: str | None = None


class AlertRead(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID | None
    title: str
    description: str | None
    source: str
    severity: str
    recorded_at: datetime

    model_config = {"from_attributes": True}
