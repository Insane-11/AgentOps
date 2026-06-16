import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert_event import AlertEvent
from app.models.incident import Incident
from app.models.organization import Organization
from app.schemas.alert import AlertCreate, AlertRead
from app.api.auth import get_current_org

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

OrgDep = Annotated[Organization, Depends(get_current_org)]


@router.get("", response_model=list[AlertRead])
async def list_alerts(org: OrgDep, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AlertEvent)
        .join(Incident, AlertEvent.incident_id == Incident.id, isouter=True)
        .where(Incident.organization_id == org.id)
        .order_by(AlertEvent.recorded_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(req: AlertCreate, org: OrgDep, db: AsyncSession = Depends(get_db)):
    incident = Incident(
        organization_id=org.id,
        title=req.title,
        description=req.description,
        severity=req.severity.upper(),
    )
    db.add(incident)
    await db.flush()

    alert = AlertEvent(
        incident_id=incident.id,
        title=req.title,
        description=req.description,
        source=req.source,
        severity=req.severity.upper(),
        raw_payload=req.raw_payload,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert
