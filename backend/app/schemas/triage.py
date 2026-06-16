from pydantic import BaseModel


class TriageRequest(BaseModel):
    title: str
    description: str | None = None
    service_name: str = "unknown"
    service_status: str = "unknown"


class TriageResult(BaseModel):
    severity: str
    confidence: float
    summary: str
    suggested_action: str
    recommended_engineer_role: str | None = None
