import json
import uuid
from typing import Any, AsyncGenerator, TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import select

from app.agents.triage_agent import create_triage_chain
from app.agents.investigation_agent import create_investigation_chain
from app.agents.remediation_agent import create_remediation_chain
from app.models.incident import Incident
from app.models.incident_embedding import IncidentEmbedding
from app.config import settings
from app.observability import get_trace_callbacks, is_langfuse_available


class AgentWorkflowState(TypedDict):
    incident_id: str
    title: str
    description: str
    service_name: str
    service_status: str

    severity: str
    triage_summary: str
    triage_confidence: float
    suggested_action: str
    recommended_engineer_role: str | None

    root_cause_hypothesis: str
    investigation_confidence: float
    affected_systems: list[str]
    investigation_steps: list[str]
    logs_to_check: list[str]
    rag_context: str

    remediation_steps: list[dict]
    estimated_ttr: str
    risk_level: str
    verify_steps: list[str]

    current_node: str
    errors: list[str]


def create_default_state(incident_id: str, title: str, description: str, service_name: str = "unknown", service_status: str = "unknown") -> AgentWorkflowState:
    return {
        "incident_id": incident_id,
        "title": title,
        "description": description,
        "service_name": service_name,
        "service_status": service_status,
        "severity": "UNKNOWN",
        "triage_summary": "",
        "triage_confidence": 0.0,
        "suggested_action": "",
        "recommended_engineer_role": None,
        "root_cause_hypothesis": "",
        "investigation_confidence": 0.0,
        "affected_systems": [],
        "investigation_steps": [],
        "logs_to_check": [],
        "rag_context": "",
        "remediation_steps": [],
        "estimated_ttr": "",
        "risk_level": "",
        "verify_steps": [],
        "current_node": START,
        "errors": [],
    }


def _get_llm():
    return ChatOllama(
        model=settings.ollama_llm_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        format="json",
    )


async def triage_node(state: AgentWorkflowState) -> AgentWorkflowState:
    state["current_node"] = "triage_node"
    try:
        chain = create_triage_chain(_get_llm())
        result = await chain.ainvoke({
            "title": state["title"],
            "description": state["description"],
            "service_name": state["service_name"],
            "service_status": state["service_status"],
        })
        state["severity"] = result.severity.upper()
        state["triage_summary"] = result.summary
        state["triage_confidence"] = result.confidence
        state["suggested_action"] = result.suggested_action
        state["recommended_engineer_role"] = result.recommended_engineer_role
    except Exception as e:
        state["errors"].append(f"triage_node: {e}")
    return state


async def investigate_node(state: AgentWorkflowState) -> AgentWorkflowState:
    state["current_node"] = "investigate_node"
    try:
        from app.database import async_session_factory as _sf

        rag_context = ""
        async with _sf() as session:
            stmt = select(IncidentEmbedding).where(
                IncidentEmbedding.incident_id == uuid.UUID(state["incident_id"])
            )
            result = await session.execute(stmt)
            source_embeddings = result.scalars().all()
            if source_embeddings:
                query_vector = source_embeddings[0].embedding
                similar_stmt = (
                    select(Incident, IncidentEmbedding)
                    .join(IncidentEmbedding, IncidentEmbedding.incident_id == Incident.id)
                    .where(IncidentEmbedding.id != source_embeddings[0].id)
                    .order_by(IncidentEmbedding.embedding.cosine_distance(query_vector))
                    .limit(3)
                )
                similar_result = await session.execute(similar_stmt)
                seen = set()
                context_parts = []
                for row in similar_result:
                    inc, emb = row
                    if inc.id in seen:
                        continue
                    seen.add(inc.id)
                    context_parts.append(
                        f"--- Past Incident: {inc.title} (Severity: {inc.severity}, Status: {inc.status}) ---\n{emb.text_chunk}"
                    )
                if context_parts:
                    rag_context = "\n\n".join(context_parts)

        state["rag_context"] = rag_context
        chain = create_investigation_chain(_get_llm())
        result = await chain.ainvoke({
            "title": state["title"],
            "description": state["description"],
            "service_name": state["service_name"],
            "triage_summary": state["triage_summary"],
            "rag_context": rag_context or "No relevant past incidents found.",
        })
        state["root_cause_hypothesis"] = result.root_cause_hypothesis
        state["investigation_confidence"] = result.confidence
        state["affected_systems"] = result.affected_systems
        state["investigation_steps"] = result.investigation_steps
        state["logs_to_check"] = result.logs_to_check
    except Exception as e:
        state["errors"].append(f"investigate_node: {e}")
    return state


async def remediate_node(state: AgentWorkflowState) -> AgentWorkflowState:
    state["current_node"] = "remediate_node"
    try:
        chain = create_remediation_chain(_get_llm())
        result = await chain.ainvoke({
            "title": state["title"],
            "description": state["description"],
            "service_name": state["service_name"],
            "triage_summary": state["triage_summary"],
            "root_cause": state["root_cause_hypothesis"],
            "affected_systems": ", ".join(state["affected_systems"]),
        })
        state["remediation_steps"] = [s.model_dump() for s in result.steps]
        state["estimated_ttr"] = result.estimated_ttr
        state["risk_level"] = result.risk_level
        state["verify_steps"] = result.verify_steps
    except Exception as e:
        state["errors"].append(f"remediate_node: {e}")
    return state


def should_continue(state: AgentWorkflowState) -> str:
    if state.get("errors"):
        return END
    return "investigate_node"


def build_incident_graph():
    builder = StateGraph(AgentWorkflowState)

    builder.add_node("triage_node", triage_node)
    builder.add_node("investigate_node", investigate_node)
    builder.add_node("remediate_node", remediate_node)

    builder.add_edge(START, "triage_node")
    builder.add_conditional_edges("triage_node", should_continue)
    builder.add_edge("investigate_node", "remediate_node")
    builder.add_edge("remediate_node", END)

    checkpointer = MemorySaver()

    graph = builder.compile(checkpointer=checkpointer)
    return graph


async def stream_incident_workflow(incident_id: str, title: str, description: str, service_name: str = "unknown", service_status: str = "unknown") -> AsyncGenerator[str, None]:
    graph = build_incident_graph()
    initial_state = create_default_state(incident_id, title, description, service_name, service_status)

    config = {"configurable": {"thread_id": incident_id}}
    if is_langfuse_available():
        config["callbacks"] = get_trace_callbacks()
    final_state = None

    async for event in graph.astream_events(initial_state, config, version="v2"):
        kind = event.get("event")
        node = event.get("name", "")
        if kind == "on_chain_start" and node in ("triage_node", "investigate_node", "remediate_node"):
            yield json.dumps({"type": "node_start", "node": node}) + "\n"
        elif kind == "on_chain_end" and node in ("triage_node", "investigate_node", "remediate_node"):
            data = event.get("data", {}).get("output", {})
            final_state = data
            yield json.dumps({"type": "node_complete", "node": node, "state": data}) + "\n"

    if final_state:
        yield json.dumps({"type": "workflow_complete", "state": final_state}) + "\n"
