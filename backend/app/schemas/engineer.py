import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class EngineerCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "engineer"
    phone: str | None = None


class EngineerUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    is_on_call: bool | None = None
    is_active: bool | None = None
    phone: str | None = None


class EngineerRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    email: str
    role: str
    is_on_call: bool
    is_active: bool
    phone: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
