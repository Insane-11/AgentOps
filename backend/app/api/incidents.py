import uuid
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.incident import Incident
from app.models.organization import Organization
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate
from app.api.auth import get_current_org
from app.api.pagination import PaginationParams

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

OrgDep = Annotated[Organization, Depends(get_current_org)]


@router.get("")
async def list_incidents(
    org: OrgDep,
    pagination: PaginationParams = Depends(),
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    base = select(Incident).where(Incident.organization_id == org.id)
    if status_filter:
        base = base.where(Incident.status == status_filter.upper())
    if severity:
        base = base.where(Incident.severity == severity.upper())

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    stmt = base.order_by(Incident.created_at.desc()).offset(pagination.offset).limit(pagination.per_page)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return {
        "items": [IncidentRead.model_validate(i).model_dump() for i in items],
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": ceil(total / pagination.per_page) if pagination.per_page else 0,
    }


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
