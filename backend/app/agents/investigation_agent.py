from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.config import settings


class InvestigationOutput(BaseModel):
    root_cause_hypothesis: str = Field(description="Likely root cause of the incident")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    affected_systems: list[str] = Field(description="List of affected systems or components")
    investigation_steps: list[str] = Field(description="Steps taken to reach this conclusion")
    logs_to_check: list[str] = Field(description="Specific logs, metrics, or dashboards to verify")


SYSTEM_PROMPT = """You are a senior Site Reliability Engineer investigating an incident.

Given the incident details and triage summary, your job is to:
1. Identify the most likely root cause
2. List all affected systems
3. Describe the investigation steps you took
4. Suggest specific logs, metrics, or dashboards to verify your hypothesis

Focus on practical, actionable investigation for a cloud-native stack
(APIs, databases, queues, caching layers, Kubernetes, etc.).

You MUST respond with valid JSON only, matching this schema:
{"root_cause_hypothesis": "...", "confidence": 0.0-1.0, "affected_systems": ["..."], "investigation_steps": ["..."], "logs_to_check": ["..."]}"""

RAG_CONTEXT_PROMPT = """
Here are similar past incidents that may be relevant:
{rag_context}
"""


def create_investigation_chain(llm: ChatOllama | None = None):
    if llm is None:
        llm = ChatOllama(
            model=settings.ollama_llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
            format="json",
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Title: {title}\nDescription: {description}\nService: {service_name}\nTriage Summary: {triage_summary}"),
        ("human", RAG_CONTEXT_PROMPT),
    ])

    chain = prompt | llm.with_structured_output(InvestigationOutput)
    return chain
