from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, enable_pgvector
from app.api import auth, incidents, engineers, alerts, triage, workflow, embeddings, analytics, integrations, api_keys
from app.middleware.rate_limit import RateLimitMiddleware
from app.langserve_routes import add_agent_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await enable_pgvector()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(engineers.router)
app.include_router(alerts.router)
app.include_router(triage.router)
app.include_router(workflow.router)
app.include_router(embeddings.router)
app.include_router(analytics.router)
app.include_router(integrations.router)
app.include_router(api_keys.router)

add_agent_routes(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
