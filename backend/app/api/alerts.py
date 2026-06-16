import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from langchain_ollama import ChatOllama
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.triage_agent import create_triage_chain
from app.config import settings
from app.database import get_db
from app.models.alert_event import AlertEvent
from app.models.incident import Incident
from app.models.organization import Organization
from app.models.service import Service
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

    try:
        service_name = "unknown"
        service_status = "unknown"
        if incident.service_id:
            svc_result = await db.execute(select(Service).where(Service.id == incident.service_id))
            svc = svc_result.scalar_one_or_none()
            if svc:
                service_name = svc.name
                service_status = svc.status

        llm = ChatOllama(
            model=settings.ollama_llm_model,
            base_url=settings.ollama_base_url,
            temperature=0,
            format="json",
        )
        chain = create_triage_chain(llm)
        triage_result = await chain.ainvoke({
            "title": incident.title,
            "description": incident.description or "",
            "service_name": service_name,
            "service_status": service_status,
        })

        stmt = (
            update(Incident)
            .where(Incident.id == incident.id)
            .values(
                severity=triage_result.severity.upper(),
                agent_summary=triage_result.summary,
                status="TRIAGED",
            )
        )
        await db.execute(stmt)
    except Exception as e:
        print(f"Triage agent failed (non-blocking): {e}")

    await db.commit()
    await db.refresh(alert)
    return alert
