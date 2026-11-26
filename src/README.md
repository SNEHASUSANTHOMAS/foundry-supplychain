# `src/` — Core Application Runtime

Contains the production FastAPI service and multi-agent orchestration logic:

- `config.py`: Agent definitions (`SPECIALIST_SPECS`, `ORCHESTRATOR_NAME`, `VALID_AGENTS`) shared between setup and runtime.
- `orchestrator.py`: Routes incoming supply-chain questions to 1–3 specialist Foundry RAG agents and synthesizes their responses.
- `app.py`: FastAPI server exposing `/`, `/health`, and `/ask`.

