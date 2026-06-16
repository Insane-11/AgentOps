# AgentOps

**AI-Powered Incident Response & Operations Agent**

AgentOps is a multi-surface platform that brings AI agent workflows to incident management. Built on the LangChain ecosystem -- LangChain, LangGraph, LangSmith, and LangServe.

## Architecture

```
Frontend Layer:    Admin Dashboard (React)   Engineer Dashboard (React)   On-Call App (React Native)
                            |                         |                          |
API Layer:              FastAPI REST + LangServe Agent Endpoints + WebSocket/SSE
                            |                         |                          |
Agent Layer:     Triage Agent -> Investigation Agent -> Remediation Agent (LangGraph State Machine)
                            |                         |                          |
Observability:              LangSmith (Tracing, Eval, Feedback Loops)
                            |                         |                          |
Data Layer:            PostgreSQL (Relational) + pgvector (Embeddings)
```

## Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# Run seed data
docker-compose exec backend python -m app.seed
```

## Access Points

| Surface | URL | Credentials |
|---|---|---|
| Admin Dashboard | http://localhost:5173 | admin@agentops.dev / admin123 |
| Engineer Dashboard | http://localhost:5174 | alice@agentops.dev / alice123 |
| API | http://localhost:8000 | -- |
| API Docs | http://localhost:8000/docs | -- |

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL
- **AI Agents**: LangChain, LangGraph, LangSmith, LangServe
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **Infrastructure**: Docker Compose

## Development Phases

See [phases.md](phases.md) for the complete phased development roadmap from skeleton to production.

## License

MIT
