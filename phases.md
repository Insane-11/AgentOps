# AgentOps — Development Phases

## Phase 0: Project Scaffolding & Infrastructure (Skeleton)
**Goal:** Runnable shell with DB, auth, and deployment config.

### Backend Tasks
- [x] Initialize Python project: `pyproject.toml`, `requirements.txt`
- [x] FastAPI app entry (`main.py`) with CORS, health check
- [x] PostgreSQL connection via SQLAlchemy async + Alembic migrations
- [x] JWT auth: `/api/auth/login`, `get_current_user` dependency, admin + engineer roles
- [x] Docker Compose: postgres + backend + frontends
- [x] `.env.example`, `.gitignore`, `langsmith.yaml`

### Frontend Tasks
- [x] Scaffold `admin-dashboard` with Vite + React + TS + Tailwind
- [x] Scaffold `engineer-dashboard` with same stack
- [x] Shared API client, auth context (token storage, protected routes)

### What's Deployable
- `docker-compose up` starts everything
- Auth flow works (login -> JWT -> protected routes)
- DB migrations run on startup

---

## Phase 1: Core Data Model & CRUD APIs
**Goal:** Full data layer without AI -- manual incident management like a traditional app.

### Backend Tasks
- [x] SQLAlchemy models: `Organization`, `Engineer`, `Incident`, `AlertEvent`, `Service`
- [x] Alembic migration for all tables
- [x] CRUD endpoints: `GET/POST/PUT /incidents`, `GET/POST /engineers`, `POST /alerts`
- [x] Seed script with demo data (org, 3 engineers, sample services)
- [x] Engineer on-call status (toggle, rotation endpoint)

### Frontend Tasks
- [x] Admin Dashboard: organization overview, engineer list with on-call status, services table
- [x] Engineer Dashboard: incident queue (list with severity badges), incident detail page
- [x] Alert ingestion form / mock alert button for demo

### What's Deployable
- Full CRUD for all entities
- Two React dashboards talking to the same API
- On-call rotation visible in UI

---

## Phase 2: LangChain Agent -- Triage Agent
**Goal:** First AI agent that classifies incoming alerts.

### Backend Tasks
- [x] `agents/triage_agent.py`: LangChain chain using ChatOpenAI
- [x] `langserve_routes.py`: Mount triage agent at `/agents/triage`
- [x] Wire `POST /alerts` to auto-trigger triage agent -> update incident
- [x] LangSmith tracing: project name, tags, metadata

### Frontend Tasks
- [x] Engineer Dashboard: show agent's triage decision on incident detail page
- [x] Agent trace viewer component (basic JSON display with severity badge)

### LangSmith Integration
- [x] All agent invocations traced
- [x] View traces in LangSmith dashboard

### What's Deployable
- Alerts auto-classified by LLM
- Trace visible in LangSmith

---

## Phase 3: LangGraph State Machine -- Incident Workflow
**Goal:** Multi-step agent with state transitions.

### Backend Tasks
- [x] `agents/incident_graph.py`: LangGraph StateGraph with 3 nodes
  - States: `FIRED -> TRIAGED -> INVESTIGATING -> REMEDIATING -> RESOLVED`
  - Nodes: `triage_node`, `investigate_node`, `remediate_node`
  - Conditional edges: error-based routing to END
- [x] `agents/investigation_agent.py`: Analyzes alert context, past incidents
- [x] `agents/remediation_agent.py`: Suggests runbook steps
- [x] Wire `POST /workflow/run/{id}` to execute graph via SSE streaming
- [x] SSE endpoint for real-time workflow progress
- [x] LangGraph `astream_events` for step-by-step streaming

### Frontend Tasks
- [x] Engineer Dashboard: real-time workflow visualization (node-by-node)
- [x] Agent decision tree component (expandable, shows reasoning)

### LangSmith Integration
- [x] Per-node tracing within graph

### What's Deployable
- Full incident lifecycle driven by LangGraph
- Real-time streaming of agent decisions

---

## Phase 4: RAG -- Past Incident Retrieval
**Goal:** Agents reference historical incidents for better decisions.

### Backend Tasks
- [x] pgvector setup in PostgreSQL (image: `pgvector/pgvector:pg16`, extension auto-enabled on startup)
- [x] `IncidentEmbedding` model with `Vector(1536)` column for text-embedding-3-small
- [x] `POST /api/embeddings/embed`: generate + store embedding for any incident
- [x] `POST /api/embeddings/similar/{id}`: cosine-similarity search returning top-3 similar
- [x] `investigation_agent.py` updated: receives `rag_context` in prompt
- [x] `investigate_node` in LangGraph fetches similar past incidents from DB via vector search

### Frontend Tasks
- [x] Engineer Dashboard: "Similar Past Incidents" panel on IncidentDetail (auto-embeds on mount, shows similarity %)

### What's Deployable
- Agents remember past incidents
- Similarity search improves investigation quality

---

## Phase 5: On-Call Mobile App
**Goal:** React Native mobile app for on-call engineers.

### Tasks
- [x] `oncall-app/` scaffold with React Native + Expo
- [x] Auth: JWT login, token persistence via AsyncStorage
- [x] Screens: Alert List, Incident Detail, Acknowledge/Escalate/Resolve actions
- [x] Push notifications setup (expo-notifications, expo-device)
- [x] Navigation: React Navigation native stack

### What's Deployable
- Mobile app connects to same backend
- Engineers can acknowledge, escalate, resolve incidents from phone

---

## Phase 6: Admin Analytics & LangSmith Dashboard Integration
**Goal:** Deep observability into agent performance.

### Backend Tasks
- [x] Analytics endpoints: `GET /api/analytics/overview`, `GET /api/analytics/accuracy`, `GET /api/analytics/embedding-coverage`
- [x] LangSmith dataset creation for evaluation (`POST /api/analytics/eval-dataset`)
- [x] Feedback loop: `POST /api/analytics/feedback` stores engineer corrections as LangSmith examples

### Frontend Tasks
- [x] Admin Dashboard: Analytics page with stat cards, severity distribution (bar + pie charts via recharts), AI coverage, agent activity

### What's Deployable
- Full observability into AI performance
- Data-driven iteration cycle via LangSmith feedback

---

## Phase 7: External Integrations & Auto-Remediation
**Goal:** Agents can act -- not just suggest.

### Tasks
- [x] Slack integration: send incident alerts with severity-colored attachments + action buttons (View, Acknowledge)
- [x] PagerDuty webhook integration: trigger/acknowledge PagerDuty events via Events API v2
- [x] GitHub integration: auto-create issues from incidents with labels
- [x] Auto-remediation via webhooks: detect runbook type (restart, scale, rollback, clear cache, webhook) and execute
- [x] Runbook execution agent (`agents/runbook_agent.py`): converts remediation steps into executable webhook calls
- [x] Integration config management: `POST/GET /api/integrations/config`, `POST /api/integrations/notify/{id}`, `POST /api/integrations/remediate/{id}`
- [x] `IntegrationConfig` model for storing provider credentials per org

### What's Deployable
- Agents that close the loop (detect -> diagnose -> fix)
- Slack/PagerDuty notifications on incident creation
- Auto-remediation via configurable webhooks

---

## Phase 8: Multi-Tenant SaaS & Productionization
**Goal:** Production-ready multi-tenant deployment.

### Tasks
- [x] Organization isolation in all queries (filtered by `organization_id`)
- [x] Rate limiting middleware (200 req/min per IP, configurable)
- [x] Pagination support for list endpoints (`page`, `per_page`, `total`, `total_pages`)
- [x] Redis caching layer (`app/services/cache.py` with async redis)
- [x] API key management: `POST/GET/DELETE /api/api-keys` for webhook integrations
- [x] CI/CD pipeline (GitHub Actions: lint, test, build, docker)
- [x] Load testing with locust (`locustfile.py`)
- [x] Helm chart for Kubernetes deployment (backend deployment + service + ingress + postgres/redis)
- [x] Test structure with pytest-asyncio

### What's Deployable
- Production-ready multi-tenant deployment
- Kubernetes via Helm
- CI/CD via GitHub Actions

---

## Free & Self-Hosted Commitment

Every component in AgentOps is free, open-source, and self-hostable:
- **LLM**: Ollama + LLaMA 3.1 8B (or any model you choose) — no API fees
- **Embeddings**: HuggingFace `all-MiniLM-L6-v2` via `sentence-transformers` — runs locally on CPU
- **Observability**: Feedback stored in PostgreSQL via `eval_feedback` table — no LangSmith cloud dependency
- **Database**: PostgreSQL + pgvector — free and open source
- **All frameworks**: LangChain, LangGraph, LangServe, FastAPI, React — all MIT/Apache licensed

Zero API keys required. Works fully offline. Deploy on a laptop, a $5 VPS, or Kubernetes with the included Helm chart.

**Optional:** LangFuse (MIT, open-source) can be enabled for full LangSmith-style tracing, eval, and dashboards — self-hosted, unlimited, you own the data. Uncomment the `langfuse` service in `docker-compose.yml` and add `langfuse` to `requirements.txt` to enable.

## Architecture Summary

```
+-------------------------------------------------------+
|                     Frontend Layer                      |
|  +----------------+  +----------------+  +-----------+  |
|  | Admin          |  | Engineer       |  | On-Call   |  |
|  | Dashboard      |  | Dashboard      |  | App       |  |
|  | (React/Vite)   |  | (React/Vite)   |  | (RN/Expo) |  |
|  +--------+-------+  +--------+-------+  +-----+-----+  |
+-----------+------------------+----------------+---------+
            |                  |                |
            v                  v                v
+-------------------------------------------------------+
|                    API Layer (FastAPI)                  |
|  +----------+  +----------+  +--------------------+    |
|  | REST     |  | LangServe|  | WebSocket/SSE      |    |
|  | CRUD APIs|  | Agent    |  | Real-time Stream   |    |
|  +-----+----+  +-----+----+  +----------+---------+    |
+--------+------------+-------------------+--------------+
         |            |                   |
         v            v                   v
+-------------------------------------------------------+
|                 Agent Layer (LangChain)                 |
|  +----------+  +----------+  +----------+              |
|  | Triage   |  | Investi- |  | Remediate|              |
|  | Agent    |  | gate     |  | Agent    |              |
|  |          |  | Agent    |  |          |              |
|  +-----+----+  +-----+----+  +-----+----+              |
|        |              |              |                  |
|        +--------------+--------------+                  |
|                       v                                 |
|               +---------------+                        |
|               |  LangGraph    |                        |
|               |  State        |                        |
|               |  Machine      |                        |
|               +---------------+                        |
+-------------------------------------------------------+
                         |
                         v
+-------------------------------------------------------+
|                Observability (LangSmith)                |
|  +----------+  +----------+  +--------------------+    |
|  | Tracing  |  | Eval     |  | Feedback Loops     |    |
|  | All Runs |  | Datasets |  | + Improvement      |    |
|  +----------+  +----------+  +--------------------+    |
+-------------------------------------------------------+
                         |
                         v
+-------------------------------------------------------+
|                     Data Layer                          |
|  +----------------+  +----------------+                |
|  | PostgreSQL     |  | pgvector       |                |
|  | (Relational)   |  | (Embeddings)   |                |
|  | + Redis Cache  |  |                |                |
|  +----------------+  +----------------+                |
+-------------------------------------------------------+
```

---

## LangChain Framework Usage per Phase

| Phase | LangChain | LangGraph | LangSmith | LangServe |
|-------|-----------|-----------|-----------|-----------|
| 0-1   | --        | --        | --        | --        |
| 2     | Triage Agent | --    | Tracing   | Agent endpoint |
| 3     | All agents   | State machine | Graph traces | Graph endpoint |
| 4     | RAG chains   | --    | Retrieval traces | -- |
| 5     | --        | --        | --        | --        |
| 6     | Eval chains | --     | Eval datasets, feedback | -- |
| 7     | Runbook agent | --   | Tool traces | -- |
| 8     | Production hardening | -- | Monitoring | Rate limiting |

**Guiding Principle:** Each phase is additive. No phase rewrites code from a previous phase -- it only extends. This lets you stop at any phase and have a working, deployable system.
