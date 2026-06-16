from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.config import settings


class TriageOutput(BaseModel):
    severity: str = Field(description="Severity level: CRITICAL, HIGH, MEDIUM, or LOW")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    summary: str = Field(description="One-paragraph summary of the incident and its impact")
    suggested_action: str = Field(description="Immediate recommended action to take")
    recommended_engineer_role: str | None = Field(
        default=None,
        description="Suggested engineer speciality (senior, backend, infra, etc.)"
    )


SYSTEM_PROMPT = """You are a senior Site Reliability Engineer triaging an incoming incident alert.

Your job is to:
1. Assess the severity based on the title, description, and affected service
2. Write a concise summary of what's happening and the potential impact
3. Recommend an immediate action
4. Suggest what kind of engineer should handle this

Severity guidelines:
- CRITICAL: Customer-facing outage, data loss, security breach, payment system down
- HIGH: Partial service degradation, feature unavailability, performance regression affecting many users
- MEDIUM: Minor degradation, single-user issue, cosmetic bug, non-critical alert
- LOW: Informational, noise, already resolved, no user impact

You MUST respond with valid JSON only, matching this schema:
{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "confidence": 0.0-1.0, "summary": "...", "suggested_action": "...", "recommended_engineer_role": "..."}"""


def create_triage_chain(llm: ChatOllama | None = None):
    if llm is None:
        llm = ChatOllama(
            model=settings.ollama_llm_model,
            base_url=settings.ollama_base_url,
            temperature=0,
            format="json",
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Title: {title}\nDescription: {description}\nService: {service_name}\nService Status: {service_status}"),
    ])

    chain = prompt | llm.with_structured_output(TriageOutput)
    return chain
