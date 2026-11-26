"""FastAPI service exposing the Foundry multi-agent supply-chain RAG app."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.orchestrator import ask_supply_chain

app = FastAPI(
    title="Supply-Chain Multi-Agent RAG API",
    description="Orchestrates specialized Azure AI Foundry RAG agents for supply-chain queries.",
    version="0.1.0",
)

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Supply-Chain Foundry AI</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 780px; margin: 40px auto; padding: 0 16px; }
    textarea { width: 100%; height: 80px; padding: 10px; font-size: 15px; box-sizing: border-box; }
    button { margin-top: 10px; padding: 10px 18px; font-size: 15px; cursor: pointer; }
    .meta { color: #555; font-size: 13px; margin-top: 16px; }
    pre { white-space: pre-wrap; background: #f6f8fa; padding: 14px; border-radius: 6px; }
  </style>
</head>
<body>
  <h2>Supply-Chain Multi-Agent RAG (Azure AI Foundry)</h2>
  <textarea id="q" placeholder="Ask about CNC machining, injection moulding, fabrication rules, should-costing, or RFQs..."></textarea>
  <button onclick="send()">Ask Agents</button>
  <div id="meta" class="meta"></div>
  <pre id="out" style="display:none"></pre>
  <script>
    async function send() {
      const q = document.getElementById('q').value.trim();
      if (!q) return;
      document.getElementById('meta').textContent = 'Consulting Foundry RAG agents...';
      document.getElementById('out').style.display = 'none';
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question: q})
      });
      const data = await res.json();
      document.getElementById('meta').textContent = 'Agents consulted: ' + (data.agents_consulted || []).join(', ');
      document.getElementById('out').textContent = data.answer || JSON.stringify(data, null, 2);
      document.getElementById('out').style.display = 'block';
    }
  </script>
</body>
</html>"""


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Supply-chain question to ask the agents.")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """Serve a simple web UI for querying the multi-agent supply-chain app."""
    return INDEX_HTML


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe for Azure Container Instances."""
    return {"status": "ok"}


@app.post("/ask")
def ask(req: QueryRequest) -> dict:
    """Run multi-agent RAG orchestration for a supply-chain question."""
    try:
        return ask_supply_chain(req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

