import httpx
from app.config import settings


async def send_slack_alert(webhook_url: str, title: str, description: str, severity: str, incident_id: str):
    if not webhook_url:
        return {"status": "skipped", "reason": "no webhook URL configured"}

    color = {"CRITICAL": "#DC2626", "HIGH": "#EA580C", "MEDIUM": "#CA8A04", "LOW": "#16A34A"}.get(severity, "#6B7280")

    payload = {
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": f"🚨 {title}", "emoji": True},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Severity:* {severity}\n{description or 'No description'}"},
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "View Incident", "emoji": True},
                                "url": f"{settings.app_url or 'http://localhost:5174'}/incidents/{incident_id}",
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Acknowledge", "emoji": True},
                                "value": f"ack:{incident_id}",
                                "style": "primary",
                            },
                        ],
                    },
                ],
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook_url, json=payload, timeout=10)
            resp.raise_for_status()
            return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def send_slack_acknowledgement(webhook_url: str, title: str, engineer_name: str):
    if not webhook_url:
        return {"status": "skipped"}

    payload = {
        "text": f"✅ *{title}* acknowledged by {engineer_name}"
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook_url, json=payload, timeout=10)
            resp.raise_for_status()
            return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
