import uuid
from datetime import datetime

from pydantic import BaseModel


class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    service_id: str | None = None
    severity: str = "MEDIUM"


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    assigned_engineer_id: str | None = None


class IncidentRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    service_id: uuid.UUID | None
    title: str
    description: str | None
    severity: str
    status: str
    assigned_engineer_id: uuid.UUID | None
    agent_summary: str | None
    agent_trace_id: str | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
