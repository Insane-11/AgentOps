from fastapi import FastAPI
from langserve import add_routes

from app.agents.triage_agent import create_triage_chain


def add_agent_routes(app: FastAPI) -> None:
    triage_chain = create_triage_chain()

    add_routes(
        app,
        triage_chain,
        path="/agents/triage",
        playground_type="chat",
        enabled_endpoints=["invoke", "batch", "stream"],
    )
