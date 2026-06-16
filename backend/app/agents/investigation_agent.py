from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


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
Respond with structured data only."""


def create_investigation_chain(llm: ChatOpenAI | None = None):
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Title: {title}\nDescription: {description}\nService: {service_name}\nTriage Summary: {triage_summary}"),
    ])

    chain = prompt | llm.with_structured_output(InvestigationOutput)
    return chain
