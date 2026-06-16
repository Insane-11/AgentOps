import httpx


async def create_github_issue(
    token: str,
    repo: str,
    title: str,
    description: str,
    severity: str,
    incident_id: str,
):
    if not token or not repo:
        return {"status": "skipped", "reason": "GitHub token or repo not configured"}

    body = f"""## Incident: {title}

**Severity:** {severity}
**Incident ID:** {incident_id}

### Description
{description or 'No description provided.'}

---
_Automatically created by AgentOps_
"""

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/repos/{repo}/issues",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                json={
                    "title": f"[{severity}] {title}",
                    "body": body,
                    "labels": ["incident", severity.lower()],
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return {"status": "created", "issue_url": data.get("html_url")}
    except Exception as e:
        return {"status": "error", "error": str(e)}
