import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.incident import Incident
from app.models.organization import Organization
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate
from app.api.auth import get_current_org

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

OrgDep = Annotated[Organization, Depends(get_current_org)]


@router.get("", response_model=list[IncidentRead])
async def list_incidents(
    org: OrgDep,
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Incident).where(Incident.organization_id == org.id).order_by(Incident.created_at.desc())
    if status_filter:
        stmt = stmt.where(Incident.status == status_filter.upper())
    if severity:
        stmt = stmt.where(Incident.severity == severity.upper())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: uuid.UUID, org: OrgDep, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id, Incident.organization_id == org.id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(req: IncidentCreate, org: OrgDep, db: AsyncSession = Depends(get_db)):
    incident = Incident(
        organization_id=org.id,
        title=req.title,
        description=req.description,
        severity=req.severity.upper(),
        service_id=uuid.UUID(req.service_id) if req.service_id else None,
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.put("/{incident_id}", response_model=IncidentRead)
async def update_incident(incident_id: uuid.UUID, req: IncidentUpdate, org: OrgDep, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id, Incident.organization_id == org.id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_data = req.model_dump(exclude_unset=True)
    if not update_data:
        return incident

    stmt = update(Incident).where(Incident.id == incident_id).values(**update_data).returning(Incident)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()
