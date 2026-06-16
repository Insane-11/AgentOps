import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.auth import get_current_org
from app.config import settings
from app.integrations import (
    send_slack_alert, send_slack_acknowledgement,
    trigger_pagerduty_alert, acknowledge_pagerduty,
    create_github_issue,
    execute_remediation_webhook, detect_runbook_type,
)
from app.integrations.models import IntegrationConfig
from app.models.incident import Incident
from app.models.organization import Organization

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/config")
async def list_configs(
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    result = await db.execute(
        select(IntegrationConfig).where(
            IntegrationConfig.organization_id == org.id,
            IntegrationConfig.is_enabled == True,
        )
    )
    configs = result.scalars().all()
    return {
        "configs": [
            {
                "id": str(c.id),
                "provider": c.provider,
                "config_key": c.config_key,
                "is_enabled": c.is_enabled,
            }
            for c in configs
        ]
    }


class SetConfigRequest(BaseModel):
    provider: str
    config_key: str
    config_value: str


@router.post("/config")
async def set_config(
    req: SetConfigRequest,
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    stmt = select(IntegrationConfig).where(
        IntegrationConfig.organization_id == org.id,
        IntegrationConfig.provider == req.provider,
        IntegrationConfig.config_key == req.config_key,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        existing.config_value = req.config_value
    else:
        config = IntegrationConfig(
            organization_id=org.id,
            provider=req.provider,
            config_key=req.config_key,
            config_value=req.config_value,
        )
        db.add(config)
    await db.commit()
    return {"status": "saved"}


@router.post("/notify/{incident_id}")
async def notify_integrations(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    incident = await db.get(Incident, uuid.UUID(incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    results = {}

    slack_webhook = await _get_config(db, org.id, "slack", "webhook_url")
    if slack_webhook:
        results["slack"] = await send_slack_alert(
            slack_webhook, incident.title, incident.description or "",
            incident.severity, str(incident.id),
        )

    pd_key = await _get_config(db, org.id, "pagerduty", "routing_key")
    if pd_key:
        results["pagerduty"] = await trigger_pagerduty_alert(
            pd_key, incident.title, incident.description or "",
            incident.severity, str(incident.id),
        )

    gh_token = await _get_config(db, org.id, "github", "token")
    gh_repo = await _get_config(db, org.id, "github", "repo")
    if gh_token and gh_repo:
        results["github"] = await create_github_issue(
            gh_token, gh_repo, incident.title, incident.description or "",
            incident.severity, str(incident.id),
        )

    return {"incident_id": incident_id, "results": results}


@router.post("/remediate/{incident_id}")
async def execute_auto_remediation(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    incident = await db.get(Incident, uuid.UUID(incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    webhook_base = await _get_config(db, org.id, "remediation", "webhook_base_url")
    api_key = await _get_config(db, org.id, "remediation", "api_key")

    if not webhook_base or not api_key:
        raise HTTPException(status_code=400, detail="Auto-remediation not configured. Set webhook_base_url and api_key.")

    from app.agents.runbook_agent import create_runbook_chain
    from langchain_ollama import ChatOllama

    chain = create_runbook_chain(ChatOllama(
        model=settings.ollama_llm_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        format="json",
    ))
    plan = await chain.ainvoke({
        "title": incident.title,
        "root_cause": incident.agent_summary or "Unknown",
        "affected_systems": incident.service_name or "Unknown",
        "remediation_steps": "See agent_summary",
        "risk_level": incident.severity,
        "verify_steps": "Monitor after remediation",
    })

    step_results = []
    for step in plan.steps:
        action_type = detect_runbook_type(step.action)
        result = await execute_remediation_webhook(webhook_base, api_key, action_type, step.parameters)
        step_results.append({"step": step.action, "target": step.target, "result": result})

    return {"incident_id": incident_id, "plan": plan.model_dump(), "step_results": step_results}



async def _get_config(db: AsyncSession, org_id: uuid.UUID, provider: str, key: str) -> str | None:
    stmt = select(IntegrationConfig).where(
        IntegrationConfig.organization_id == org_id,
        IntegrationConfig.provider == provider,
        IntegrationConfig.config_key == key,
        IntegrationConfig.is_enabled == True,
    )
    result = (await db.execute(stmt)).scalar_one_or_none()
    return result.config_value if result else None
