# AgentOps — Development Phases

## Phase 0: Project Scaffolding & Infrastructure (Skeleton)
**Goal:** Runnable shell with DB, auth, and deployment config.

### Backend Tasks
- [ ] Initialize Python project: `pyproject.toml`, `requirements.txt`
- [ ] FastAPI app entry (`main.py`) with CORS, health check
- [ ] PostgreSQL connection via SQLAlchemy async + Alembic migrations
- [ ] JWT auth: `/api/auth/login`, `get_current_user` dependency, admin + engineer roles
- [ ] Docker Compose: postgres + backend + frontends
- [ ] `.env.example`, `.gitignore`, `langsmith.yaml`

### Frontend Tasks
- [ ] Scaffold `admin-dashboard` with Vite + React + TS + Tailwind
- [ ] Scaffold `engineer-dashboard` with same stack
- [ ] Shared API client, auth context (token storage, protected routes)

### What's Deployable
- `docker-compose up` starts everything
- Auth flow works (login -> JWT -> protected routes)
- DB migrations run on startup

---

## Phase 1: Core Data Model & CRUD APIs
**Goal:** Full data layer without AI -- manual incident management like a traditional app.

### Backend Tasks
- [ ] SQLAlchemy models: `Organization`, `Engineer`, `Incident`, `AlertEvent`, `Service`
- [ ] Alembic migration for all tables
- [ ] CRUD endpoints: `GET/POST/PUT /incidents`, `GET/POST /engineers`, `POST /alerts`
- [ ] Seed script with demo data (org, 3 engineers, sample services)
- [ ] Engineer on-call status (toggle, rotation endpoint)

### Frontend Tasks
- [ ] Admin Dashboard: organization overview, engineer list with on-call status, services table
- [ ] Engineer Dashboard: incident queue (list with severity badges), incident detail page
- [ ] Alert ingestion form / mock alert button for demo

### What's Deployable
- Full CRUD for all entities
- Two React dashboards talking to the same API
- On-call rotation visible in UI

---

## Phase 2: LangChain Agent -- Triage Agent
**Goal:** First AI agent that classifies incoming alerts.

### Backend Tasks
- [ ] `agents/triage_agent.py`: LangChain chain using ChatOpenAI
  - Input: alert title, description, service name
  - Output: severity (CRITICAL/HIGH/MEDIUM/LOW), suggested engineer, initial summary
- [ ] `langserve_routes.py`: Mount triage agent at `/agents/triage`
- [ ] Wire `POST /alerts` to auto-trigger triage agent -> update incident
- [ ] LangSmith tracing: project name, tags, metadata

### Frontend Tasks
- [ ] Engineer Dashboard: show agent's triage decision on incident detail page
- [ ] Agent trace viewer component (basic JSON display with severity badge)

### LangSmith Integration
- [ ] All agent invocations traced
- [ ] View traces in LangSmith dashboard

### What's Deployable
- Alerts auto-classified by LLM
- Trace visible in LangSmith

---

## Phase 3: LangGraph State Machine -- Incident Workflow
**Goal:** Multi-step agent with state transitions.

### Backend Tasks
- [ ] `agents/incident_graph.py`: LangGraph StateGraph
  - States: `FIRED -> TRIAGED -> INVESTIGATING -> REMEDIATING -> RESOLVED`
  - Nodes: `triage_node`, `investigate_node`, `remediate_node`, `resolve_node`
  - Conditional edges: severity thresholds, human-in-the-loop gates
- [ ] `agents/investigation_agent.py`: Analyzes alert context, past incidents
- [ ] `agents/remediation_agent.py`: Suggests runbook steps
- [ ] Wire `POST /incidents/{id}/run-workflow` to execute graph
- [ ] WebSocket endpoint for real-time workflow progress (SSE)
- [ ] LangGraph `StreamMode` for step-by-step streaming

### Frontend Tasks
- [ ] Engineer Dashboard: real-time workflow visualization (node-by-node)
- [ ] Agent decision tree component (expandable, shows reasoning)
- [ ] Approve/Reject button for human-in-the-loop gates

### LangSmith Integration
- [ ] Per-node tracing within graph
- [ ] Run comparison (compare past runs for quality)

### What's Deployable
- Full incident lifecycle driven by LangGraph
- Real-time streaming of agent decisions
- Human approval gates

---

## Phase 4: RAG -- Past Incident Retrieval
**Goal:** Agents reference historical incidents for better decisions.

### Backend Tasks
- [ ] pgvector setup in PostgreSQL
- [ ] Embeddings table for past incident summaries
- [ ] `POST /incidents/{id}/embed`: generate + store embedding
- [ ] `investigation_agent.py` updated: retrieve top-3 similar past incidents via vector search
- [ ] Context window management in prompts

### Frontend Tasks
- [ ] Incident detail: show "Similar Past Incidents" panel
- [ ] Admin Dashboard: embedding health (coverage stats)

### LangSmith Integration
- [ ] RAG retrieval traces (retrieved docs, relevance scores)
- [ ] Feedback collection (thumbs up/down on retrieved results for fine-tuning)

### What's Deployable
- Agents remember past incidents
- Similarity search improves investigation quality

---

## Phase 5: On-Call Mobile App
**Goal:** React Native mobile app for on-call engineers.

### Tasks
- [ ] `oncall-app/` scaffold with React Native + Expo
- [ ] Auth: JWT login, token persistence
- [ ] Screens: Alert List, Incident Detail, Acknowledge/Escalate actions
- [ ] Push notifications (FCM/APNs via Expo Push)
- [ ] WebSocket client for live alert updates

### What's Deployable
- Mobile app connects to same backend
- Real-time alerting on phone

---

## Phase 6: Admin Analytics & LangSmith Dashboard Integration
**Goal:** Deep observability into agent performance.

### Backend Tasks
- [ ] Analytics endpoints: `GET /api/analytics/agent-accuracy`, `GET /api/analytics/cost-per-incident`
- [ ] LangSmith dataset creation for evaluation
- [ ] Automated eval runs on historical incidents
- [ ] Feedback loop: collect engineer corrections -> store as LangSmith examples -> improve prompts

### Frontend Tasks
- [ ] Admin Dashboard: agent accuracy over time, cost tracking, latency charts
- [ ] Comparison view: before/after agent improvements

### What's Deployable
- Full observability into AI performance
- Data-driven iteration cycle

---

## Phase 7: External Integrations & Auto-Remediation
**Goal:** Agents can act -- not just suggest.

### Tasks
- [ ] Slack integration: send alerts, receive acknowledgements via slash commands
- [ ] PagerDuty webhook integration for alert ingestion
- [ ] GitHub/GitLab integration: auto-create issues from incidents
- [ ] Auto-remediation via webhooks (restart service via Kubernetes API, rollback deploy)
- [ ] Runbook execution agent (executes curl/API calls instead of just suggesting)

### What's Deployable
- Agents that close the loop (detect -> diagnose -> fix)

---

## Phase 8: Multi-Tenant SaaS & Productionization
**Goal:** Production-ready multi-tenant deployment.

### Tasks
- [ ] Organization isolation in DB (row-level security)
- [ ] Rate limiting, pagination, caching
- [ ] API key management for webhook integrations
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Load testing with locust
- [ ] Documentation site
- [ ] Helm chart for Kubernetes deployment

---

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
|  |          |  | Endpoints|  |                    |    |
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
| 6     | Prompt tuning | --   | Eval datasets, feedback | -- |
| 7     | Tool-using agents | -- | Tool traces | -- |
| 8     | Production hardening | -- | Monitoring | Rate limiting |

**Guiding Principle:** Each phase is additive. No phase rewrites code from a previous phase -- it only extends. This lets you stop at any phase and have a working, deployable system.
