import uuid
from datetime import datetime

import httpx


async def trigger_pagerduty_alert(
    routing_key: str,
    title: str,
    description: str,
    severity: str,
    incident_id: str,
    source: str = "agentops",
):
    if not routing_key:
        return {"status": "skipped", "reason": "no PagerDuty routing key"}

    pd_severity = severity.lower() if severity.lower() in ("critical", "error", "warning", "info") else "warning"

    payload = {
        "routing_key": routing_key,
        "event_action": "trigger",
        "dedup_key": f"agentops-{incident_id}",
        "payload": {
            "summary": title[:120],
            "source": source,
            "severity": pd_severity,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "custom_details": {
                "incident_id": incident_id,
                "description": description or "",
            },
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            return {"status": "triggered", "dedup_key": f"agentops-{incident_id}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def acknowledge_pagerduty(routing_key: str, incident_id: str):
    if not routing_key:
        return {"status": "skipped"}

    payload = {
        "routing_key": routing_key,
        "event_action": "acknowledge",
        "dedup_key": f"agentops-{incident_id}",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            return {"status": "acknowledged"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
