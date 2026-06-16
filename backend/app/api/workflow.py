import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.agents.incident_graph import stream_incident_workflow
from app.config import settings
from app.database import get_db
from app.models.incident import Incident
from app.models.organization import Organization
from app.models.service import Service
from app.api.auth import get_current_org

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

OrgDep = Annotated[Organization, Depends(get_current_org)]


@router.post("/run/{incident_id}")
async def run_workflow(incident_id: uuid.UUID, org: OrgDep, db: AsyncSession = Depends(get_db)):
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

    result = await db.execute(
        select(Incident).where(Incident.id == incident_id, Incident.organization_id == org.id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    await db.execute(
        update(Incident).where(Incident.id == incident_id).values(status="INVESTIGATING")
    )
    await db.commit()

    service_name = "unknown"
    service_status = "unknown"
    if incident.service_id:
        svc_result = await db.execute(select(Service).where(Service.id == incident.service_id))
        svc = svc_result.scalar_one_or_none()
        if svc:
            service_name = svc.name
            service_status = svc.status

    async def event_generator():
        async for event_str in stream_incident_workflow(
            incident_id=str(incident_id),
            title=incident.title,
            description=incident.description or "",
            service_name=service_name,
            service_status=service_status,
        ):
            yield {"event": "message", "data": event_str}

        from app.database import async_session_factory
        async with async_session_factory() as s:
            updated = await s.execute(
                select(Incident).where(Incident.id == incident_id)
            )
            inc = updated.scalar_one_or_none()
            if inc:
                yield {"event": "result", "data": json.dumps({
                    "id": str(inc.id),
                    "title": inc.title,
                    "status": inc.status,
                    "severity": inc.severity,
                    "agent_summary": inc.agent_summary,
                })}

    return EventSourceResponse(event_generator())
