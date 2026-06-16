# Deploying AgentOps

AgentOps is designed to be **100% free, self-hosted**. You can deploy it on anything — a $5 VPS, a Raspberry Pi, your laptop, or Kubernetes. No external API dependencies.

---

## Option 1: Docker Compose (Simplest)

Best for: single-server deployments, homelab, staging, small teams.

```bash
# 1. Clone and configure
git clone <your-repo> && cd agentops
cp .env.example .env
# Edit .env: set JWT_SECRET to a random string

# 2. Start everything
docker compose up -d --build

# 3. Pull the LLM models (first time only)
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull nomic-embed-text

# 4. Seed demo data
docker compose exec backend python -m app.seed
```

**Production adjustments:**
- Change `JWT_SECRET` to a strong random value
- Set `OLLAMA_LLM_MODEL` to a smaller model like `phi3:mini` if resource-constrained
- Add a reverse proxy (nginx, Caddy) for TLS/SSL
- Use Docker secrets or a vault for secrets instead of env vars

**Minimal resource mode** (runs on 1GB RAM VPS):

In `.env`:
```
OLLAMA_LLM_MODEL=phi3:mini
```

Pull the smaller model:
```bash
docker compose exec ollama ollama pull phi3:mini
```

---

## Option 2: Kubernetes (Helm)

Best for: production-grade deployments, auto-scaling, multi-team.

```bash
# Install via Helm
helm upgrade --install agentops ./charts/agentops \
  --set config.jwtSecret="<random-string>" \
  --set config.ollamaBaseUrl="http://ollama:11434"

# Or with a values file
helm upgrade --install agentops ./charts/agentops -f my-values.yaml
```

The chart includes: backend deployment, service, ingress, PostgreSQL (Bitnami), Redis (Bitnami).

**Hardware requirements per replica:**
| Component | CPU | RAM | Storage |
|---|---|---|---|
| Backend | 0.5 core | 512MB | — |
| PostgreSQL | 1 core | 2GB | 10GB+ |
| Ollama | 2+ cores | 8GB+ (4GB for phi3:mini) | 5-10GB for models |
| Redis | 0.3 core | 256MB | 1GB |

---

## Option 3: Manual (No Docker)

Best for: tight integration with existing infrastructure.

```bash
# Backend
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontends
cd admin-dashboard && npm install && npm run build
cd engineer-dashboard && npm install && npm run build

# Serve frontend static files with nginx, pointing API proxy to backend

# Ollama (separate process)
# Install from https://ollama.com, then:
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

---

## Optional: Self-Hosted Observability (LangFuse)

[LangFuse](https://langfuse.com) is the open-source alternative to LangSmith — MIT-licensed, self-hosted, provides traces, evaluations, dashboards.

### Enable in Docker Compose

Uncomment the `langfuse` and `langfuse-db` services in `docker-compose.yml`, then:

```bash
docker compose up -d

# Add the Python package
docker compose exec backend pip install langfuse

# Set environment variables (already in compose if uncommented):
# LANGFUSE_SECRET_KEY=<generate-random>
# LANGFUSE_PUBLIC_KEY=<generate-random>
# LANGFUSE_HOST=http://langfuse:3000
```

### Access LangFuse Dashboard

Open http://localhost:3000 — create your account and connect the public/secret keys to AgentOps via `.env`.

### After enabling

- Every agent call (triage, investigation, remediation) is automatically traced
- Traces show: LLM input/output, tokens, latency, cost ($0 since Ollama is free)
- You can add eval scores, feedback, and compare runs

---

## Optional: Guardrails

For input/output guardrails, add:

- **[Guardrails AI](https://www.guardrailsai.com/)** — Open source, adds structural/type/safety guards around LLM calls
- **[NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)** — Open source, topic/security guards, works with any LLM

Neither is pre-integrated — AgentOps' agents already use structured Pydantic output (JSON mode), which provides basic structural guarantees.

---

## Architecture Diagram for Production

```
                         Internet
                            |
                      [Reverse Proxy]
                       (nginx/Caddy)
                      /       |       \
                     /        |        \
            Admin UI     Engineer UI     API
           (:5173)        (:5174)       (:8000)
                                          |
                                    [Backend]
                                       /|\
                                      / | \
                                     /  |  \
                           [PostgreSQL] [Ollama] [Redis (optional)]
                            +pgvector    (LLM)      (cache)
```

## Backup & Recovery

```bash
# Database
docker compose exec postgres pg_dump -U agentops agentops > backup.sql

# Ollama models are stored in the ollama_data volume
# Backup: docker run --rm -v ollama_data:/data alpine tar czf - /data > ollama-models.tar.gz
```

## Monitoring the Free Stack

| What | How |
|---|---|
| LLM traces | LangFuse dashboard (optional, self-hosted) |
| Incident analytics | Admin Dashboard > Analytics (built-in) |
| Agent feedback | `POST /api/analytics/feedback` (stores in DB) |
| Server health | `GET /health`, container health checks |
| Logs | `docker compose logs -f backend` |
| Metrics | Prometheus + Grafana (add node-exporter) |
