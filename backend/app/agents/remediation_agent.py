from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.config import settings


class RemediationStep(BaseModel):
    order: int = Field(description="Step order number")
    action: str = Field(description="What to do")
    expected_duration: str = Field(description="Expected time to complete")
    rollback: str | None = Field(default=None, description="How to rollback if this step fails")
    automated: bool = Field(description="Can this step be automated or requires manual action")


class RemediationOutput(BaseModel):
    steps: list[RemediationStep] = Field(description="Ordered list of remediation steps")
    estimated_ttr: str = Field(description="Estimated time to resolve in minutes")
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, HIGH")
    verify_steps: list[str] = Field(description="Steps to verify the fix worked")


SYSTEM_PROMPT = """You are a senior Site Reliability Engineer creating a remediation plan.

Given the incident details and investigation findings, your job is to:
1. Create an ordered step-by-step remediation plan
2. Estimate time to resolve
3. Assess risk of each step
4. Provide rollback instructions for each step
5. List verification steps to confirm the fix

Be specific and practical. Prioritize speed-to-fix while minimizing blast radius.

You MUST respond with valid JSON only, matching this schema:
{"steps": [{"order": 1, "action": "...", "expected_duration": "...", "rollback": "...", "automated": true}], "estimated_ttr": "...", "risk_level": "LOW|MEDIUM|HIGH", "verify_steps": ["..."]}"""


def create_remediation_chain(llm: ChatOllama | None = None):
    if llm is None:
        llm = ChatOllama(
            model=settings.ollama_llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
            format="json",
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Title: {title}\nDescription: {description}\nService: {service_name}\nTriage Summary: {triage_summary}\nRoot Cause: {root_cause}\nAffected Systems: {affected_systems}"),
    ])

    chain = prompt | llm.with_structured_output(RemediationOutput)
    return chain
