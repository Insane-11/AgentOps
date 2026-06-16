from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.config import settings


class RunbookStep(BaseModel):
    action: str = Field(description="The action to perform (e.g., restart_service, scale_up, webhook)")
    target: str = Field(description="The target of the action (service name, deployment name, URL)")
    parameters: dict[str, str] = Field(default_factory=dict, description="Additional parameters for the action")


class RunbookPlan(BaseModel):
    steps: list[RunbookStep] = Field(description="Ordered list of runbook steps to execute")
    verification: str = Field(description="How to verify the remediation was successful")


SYSTEM_PROMPT = """You are a Runbook Automation Agent. Given an incident investigation result,
create an automated runbook plan that can be executed via webhooks.

Map each remediation step to an executable action type:
- restart_service: For service or pod restarts
- scale_up: For increasing replicas or capacity
- rollback: For reverting deployments
- clear_cache: For cache or CDN purges
- webhook: For custom API calls

For each step, specify the target and any parameters needed.
If an action cannot be automated, mark it as requiring manual intervention.

You MUST respond with valid JSON only, matching this schema:
{"steps": [{"action": "...", "target": "...", "parameters": {}}], "verification": "..."}"""


def create_runbook_chain(llm: ChatOllama | None = None):
    if llm is None:
        llm = ChatOllama(
            model=settings.ollama_llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.1,
            format="json",
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", """Title: {title}
Root Cause: {root_cause}
Affected Systems: {affected_systems}
Remediation Steps: {remediation_steps}
Risk Level: {risk_level}
Verification Steps: {verify_steps}"""),
    ])

    chain = prompt | llm.with_structured_output(RunbookPlan)
    return chain
