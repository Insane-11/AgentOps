import httpx

REMEDIATION_WEBHOOKS = {
    "restart_service": {
        "method": "POST",
        "path_template": "/api/v1/namespaces/{namespace}/pods/{pod_name}/restart",
    },
    "scale_up": {
        "method": "PATCH",
        "path_template": "/api/v1/namespaces/{namespace}/deployments/{deployment}/scale",
    },
    "rollback": {
        "method": "POST",
        "path_template": "/api/v1/namespaces/{namespace}/deployments/{deployment}/rollback",
    },
    "clear_cache": {
        "method": "POST",
        "path_template": "/api/v1/cache/{cache_name}/clear",
    },
    "webhook": {
        "method": "POST",
        "path_template": "",
    },
}


def detect_runbook_type(action: str) -> str:
    action_lower = action.lower()
    if "restart" in action_lower or "reboot" in action_lower:
        return "restart_service"
    if "scale" in action_lower or "replica" in action_lower:
        return "scale_up"
    if "rollback" in action_lower or "revert" in action_lower:
        return "rollback"
    if "cache" in action_lower or "flush" in action_lower:
        return "clear_cache"
    return "webhook"


async def execute_remediation_webhook(
    webhook_base_url: str,
    api_key: str,
    action_type: str,
    params: dict | None = None,
):
    if not webhook_base_url:
        return {"status": "skipped", "reason": "no webhook base URL configured"}

    runbook = REMEDIATION_WEBHOOKS.get(action_type, REMEDIATION_WEBHOOKS["webhook"])
    params = params or {}

    path = runbook["path_template"]
    for key, value in params.items():
        path = path.replace(f"{{{key}}}", str(value))

    url = f"{webhook_base_url.rstrip('/')}{path}"
    method = runbook["method"]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method,
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=params,
                timeout=30,
            )
            resp.raise_for_status()
            return {"status": "executed", "action": action_type, "response_code": resp.status_code}
    except Exception as e:
        return {"status": "error", "action": action_type, "error": str(e)}
