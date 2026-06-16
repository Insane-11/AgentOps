from fastapi import FastAPI
from langserve import add_routes

from app.agents.triage_agent import create_triage_chain
from app.config import settings


def add_agent_routes(app: FastAPI) -> None:
    if not settings.openai_api_key:
        print("WARNING: OPENAI_API_KEY not set. LangServe agent routes will not be available.")
        return

    triage_chain = create_triage_chain()

    add_routes(
        app,
        triage_chain,
        path="/agents/triage",
        playground_type="chat",
        enabled_endpoints=["invoke", "batch", "stream"],
    )
