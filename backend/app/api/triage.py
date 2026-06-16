import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from langchain_ollama import ChatOllama
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.triage_agent import create_triage_chain
from app.config import settings
from app.database import get_db
from app.models.incident import Incident
from app.models.organization import Organization
from app.models.service import Service
from app.schemas.incident import IncidentRead
from app.schemas.triage import TriageResult
from app.api.auth import get_current_org

router = APIRouter(prefix="/api/triage", tags=["triage"])

OrgDep = Annotated[Organization, Depends(get_current_org)]


def _get_triage_chain():
    llm = ChatOllama(
        model=settings.ollama_llm_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        format="json",
    )
    return create_triage_chain(llm)


@router.post("/run/{incident_id}", response_model=IncidentRead)
async def run_triage(incident_id: uuid.UUID, org: OrgDep, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id, Incident.organization_id == org.id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    service_name = "unknown"
    service_status = "unknown"
    if incident.service_id:
        svc_result = await db.execute(select(Service).where(Service.id == incident.service_id))
        svc = svc_result.scalar_one_or_none()
        if svc:
            service_name = svc.name
            service_status = svc.status

    chain = _get_triage_chain()
    triage_result: TriageResult = await chain.ainvoke({
        "title": incident.title,
        "description": incident.description or "",
        "service_name": service_name,
        "service_status": service_status,
    })

    stmt = (
        update(Incident)
        .where(Incident.id == incident_id)
        .values(
            severity=triage_result.severity.upper(),
            agent_summary=triage_result.summary,
            status="TRIAGED",
        )
        .returning(Incident)
    )
    updated = await db.execute(stmt)
    await db.commit()
    return updated.scalar_one()
