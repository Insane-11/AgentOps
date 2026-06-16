import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.auth import get_current_org
from app.models.organization import Organization

router = APIRouter(prefix="/api/api-keys", tags=["api-keys"])


class ApiKeyRecord(BaseModel):
    id: str
    name: str
    key_prefix: str
    is_active: bool
    created_at: str


import uuid as _uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(8), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@router.get("/")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.organization_id == org.id)
    )
    keys = result.scalars().all()
    return {
        "keys": [
            {
                "id": str(k.id),
                "name": k.name,
                "key_prefix": k.key_prefix,
                "is_active": k.is_active,
                "created_at": k.created_at.isoformat(),
            }
            for k in keys
        ]
    }


class CreateApiKeyRequest(BaseModel):
    name: str


@router.post("/")
async def create_api_key(
    req: CreateApiKeyRequest,
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    raw_key = f"ao_{secrets.token_hex(24)}"
    key_hash = secrets.token_hex(32)
    key_prefix = raw_key[:8]

    api_key = ApiKey(
        organization_id=org.id,
        name=req.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
    )
    db.add(api_key)
    await db.commit()

    return {
        "id": str(api_key.id),
        "name": req.name,
        "key": raw_key,
        "key_prefix": key_prefix,
    }


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    api_key = await db.get(ApiKey, uuid.UUID(key_id))
    if not api_key or api_key.organization_id != org.id:
        raise HTTPException(status_code=404, detail="API key not found")
    await db.delete(api_key)
    await db.commit()
    return {"status": "deleted"}
