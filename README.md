# AgentOps

**AI-Powered Incident Response Platform — 100% Free, Self-Hosted**

AgentOps is a multi-surface incident management platform powered by local AI agents. No paid APIs, no external dependencies — everything runs locally using Ollama and HuggingFace.

## Architecture

```
Frontend Layer:    Admin Dashboard (React)   Engineer Dashboard (React)   On-Call App (React Native)
                            |                         |                          |
API Layer:              FastAPI REST + LangServe Agent Endpoints + WebSocket/SSE
                            |                         |                          |
Agent Layer:     Triage Agent -> Investigation Agent -> Remediation Agent (LangGraph State Machine)
                            |                         |                          |
Free AI Stack:    Ollama (LLaMA 3.1) + HuggingFace Embeddings (all-MiniLM-L6-v2)
                            |                         |                          |
Data Layer:            PostgreSQL (Relational) + pgvector (Embeddings)
```

## Why It's Free

| Component | Before (Paid) | Now (Free) |
|---|---|---|
| LLM | OpenAI GPT-4o-mini ($) | Ollama + LLaMA 3.1 8B (local, free) |
| Embeddings | OpenAI text-embedding-3-small ($) | HuggingFace all-MiniLM-L6-v2 (local, free) |
| Observability | LangSmith cloud (freemium) | Local DB feedback (free) |
| Database | PostgreSQL + pgvector (free) | Same (free) |
| Frontend | React/Vite/RN (free) | Same (free) |
| Deployment | Docker/K8s (free) | Same (free) |

**Zero API keys required. Zero monthly costs. Run on a laptop.**

Also includes **LangFuse** as an optional self-hosted observability layer (open-source LangSmith alternative) — same tracing/eval/dashboards, but you own the data and there are no limits.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides on:
- Docker Compose (single server, $5 VPS)
- Kubernetes via Helm (production)
- Manual (no Docker)
- Enabling LangFuse observability
- Guardrails
- Backup & recovery

## Quick Start

```bash
# Pull the LLM model (first time only)
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull nomic-embed-text

# Start all services
docker compose up --build

# Run seed data (demo users + services)
docker compose exec backend python -m app.seed
```

## Access Points

| Surface | URL | Credentials |
|---|---|---|
| Admin Dashboard | http://localhost:5173 | admin@agentops.dev / admin123 |
| Engineer Dashboard | http://localhost:5174 | alice@agentops.dev / alice123 |
| API | http://localhost:8000 | -- |
| API Docs | http://localhost:8000/docs | -- |

## Tech Stack

- **AI (Free)**: Ollama (LLaMA 3.1 8B), HuggingFace (all-MiniLM-L6-v2), LangChain, LangGraph
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL + pgvector
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **Mobile**: React Native + Expo
- **Infrastructure**: Docker Compose, Helm (K8s)

## Development Phases

See [phases.md](phases.md) for the complete phased development roadmap.

## License

MIT
