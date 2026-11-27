# Supply-Chain Multi-Agent RAG (Azure AI Foundry)

A multi-agent Retrieval-Augmented Generation (RAG) service built on **Azure AI Foundry** and **FastAPI**. An orchestrator agent (`supply-chain-orchestrator`) routes incoming supply-chain questions to 1–3 specialized RAG agents backed by Foundry Vector Stores, then synthesizes their findings into a single grounded response.

## Specialist Agents

| Agent Name | Vector Store Domain | Focus |
| --- | --- | --- |
| `cnc-machining-agent` | `cnc_machining` | Milling, tolerances, tooling, and engineering guidelines |
| `injection-moulding-agent` | `injection_moulding` | Thermoplastics, mold design, cycle time, and quality |
| `fabrication-rules-agent` | `fabrication_rules` | Metal fabrication, welding standards, packaging, and compliance |
| `should-cost-agent` | `should_cost` | Should-costing formulas, cost heuristics, and market trends |
| `procurement-rfq-agent` | `procurement_rfq` | RFQ templates, supplier quoting, and procurement clauses |

---

## Project Structure

```text
foundry_supplychain/
├── .github/
│   └── workflows/
│       └── deploy-aci.yml        # GitHub Actions CI/CD: build image, push to ACR, deploy to Azure Container Instances
├── config/                       # Generated provisioning & runtime configuration
│   ├── README.md                 # Details on generated config files
│   └── vector_stores.json        # Domain -> Azure AI Foundry Vector Store ID mapping
├── data/                         # Raw supply-chain PDFs (gitignored; excluded from Docker image)
│   └── README.md                 # Domain filename prefixes and ingestion mapping
├── scripts/                      # One-time setup, data ingestion, and smoke-test scripts
│   ├── __init__.py
│   ├── README.md                 # Usage notes for setup and diagnostic scripts
│   ├── ingest.py                 # Uploads PDFs from data/ to Foundry Vector Stores -> config/vector_stores.json
│   ├── agents_setup.py           # Registers the 5 specialist RAG agents + orchestrator in Foundry
│   └── test_llm.py               # Standalone connectivity smoke test for the Foundry OpenAI endpoint
├── src/                          # Core application runtime (packaged into the Docker image)
│   ├── __init__.py
│   ├── README.md                 # Overview of runtime modules
│   ├── config.py                 # Shared agent specs and orchestrator constants
│   ├── orchestrator.py           # Question routing, specialist invocation, and answer synthesis
│   └── app.py                    # FastAPI app serving the web UI (/), /health, and POST /ask
├── .dockerignore                 # Excludes .venv, .env, data/, and .git from Docker build context
├── .env                          # Local secrets/config (gitignored; never commit)
├── .env.example                  # Template of required environment variables
├── .gitignore                    # Git ignore rules
├── .python-version               # Pins Python 3.12 for uv
├── Dockerfile                    # Production container image running uvicorn src.app:app
├── pyproject.toml                # Project dependencies and metadata
├── uv.lock                       # Locked dependency tree for reproducible installs
└── README.md                     # This guide
```

---

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** package manager
- An **Azure AI Foundry** project with a deployed model (e.g., `gpt-5.6-luna`)
- Azure authentication via either:
  - `az login` (for local development with `DefaultAzureCredential`), or
  - Service Principal credentials (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`)

---

## Quick Start (Local)

### 1. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Azure AI Foundry values:

```bash
cp .env.example .env
```

Required variables:
- `PROJECT_ENDPOINT` — Azure AI Foundry project endpoint
- `MODEL_DEPLOYMENT_NAME` — Model deployment name in Foundry
- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET` — Required when not using `az login` (e.g., inside Docker or CI)

### 2. Install Dependencies

```bash
uv sync
```

### 3. (One-Time Setup) Ingest PDFs & Register Agents

> Skip this step if `config/vector_stores.json` and the Foundry agents are already provisioned in your target Azure AI Foundry project.

```bash
# 1. Upload PDFs from data/ into Azure AI Foundry Vector Stores
uv run python -m scripts.ingest

# 2. Register the 5 specialist RAG agents and the orchestrator in Foundry
uv run python -m scripts.agents_setup
```

Optional connectivity smoke test:

```bash
uv run python -m scripts.test_llm
```

### 4. Run the FastAPI Server

```bash
uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser to use the interactive UI, or query the API directly:

```bash
# Health check
curl http://localhost:8000/health

# Ask a supply-chain question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What tolerances apply to CNC milling of aluminum parts?"}'
```

Interactive OpenAPI docs are available at **http://localhost:8000/docs**.

---

## Run with Docker

Build and run the container locally using your `.env` file:

```bash
docker build -t supply-chain-agent .
docker run --rm -p 8000:8000 --env-file .env supply-chain-agent
```

Then visit **http://localhost:8000** or check **http://localhost:8000/health**.

---

## Deployment (Azure Container Instances)

Pushing to `main` (or triggering **workflow_dispatch**) runs `.github/workflows/deploy-aci.yml`, which:
1. Logs into Azure and Azure Container Registry (`acrsupplychainsneha`)
2. Builds and pushes the Docker image tagged with `${{ github.sha }}`
3. Deploys the container to Azure Container Instances (`aci-supply-chain-agent` in `uksouth`, port `8000`)

Ensure the following GitHub repository secrets are configured:
- `AZURE_CREDENTIALS`
- `PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_SECRET`

### Live Endpoints (ACI)

- **Web UI:** `http://supply-chain-sneha.uksouth.azurecontainer.io:8000`
- **API Docs (Swagger):** `http://supply-chain-sneha.uksouth.azurecontainer.io:8000/docs`
- **Health Check:** `http://supply-chain-sneha.uksouth.azurecontainer.io:8000/health`

```bash
# Verify live container health
curl http://supply-chain-sneha.uksouth.azurecontainer.io:8000/health

# Check container status or logs via Azure CLI
az container show --resource-group RG_Foundry2 --name aci-supply-chain-agent \
  --query "{state:instanceView.state, fqdn:ipAddress.fqdn}" -o json
az container logs --resource-group RG_Foundry2 --name aci-supply-chain-agent
```

