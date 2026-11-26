# `scripts/` — Setup, Ingestion & Smoke Tests

One-time provisioning and diagnostic scripts run from the project root:

- `ingest.py`: Uploads PDFs from `data/` into Azure AI Foundry Vector Stores and writes `config/vector_stores.json`.
- `agents_setup.py`: Registers the 5 specialist RAG agents and `supply-chain-orchestrator` in Azure AI Foundry.
- `test_llm.py`: Quick standalone smoke test to verify Foundry OpenAI endpoint connectivity.

