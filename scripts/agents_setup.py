"""Create the 5 specialized RAG agents and orchestrator agent in Azure AI Foundry."""

import json
import os
import sys
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ORCHESTRATOR_NAME, SPECIALIST_SPECS  # noqa: E402

load_dotenv()

VECTOR_STORES_FILE = PROJECT_ROOT / "config" / "vector_stores.json"


def main() -> None:
    """Register all specialist RAG agents and the orchestrator agent in Foundry."""
    if not VECTOR_STORES_FILE.exists():
        raise FileNotFoundError(
            f"Run scripts/ingest.py first to generate {VECTOR_STORES_FILE}"
        )

    store_ids: dict[str, str] = json.loads(VECTOR_STORES_FILE.read_text())
    model = os.environ["MODEL_DEPLOYMENT_NAME"]

    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    for domain, spec in SPECIALIST_SPECS.items():
        vs_id = store_ids.get(domain)
        if not vs_id:
            raise KeyError(
                f"Missing vector store ID for domain '{domain}' in {VECTOR_STORES_FILE}"
            )

        agent = project.agents.create_version(
            agent_name=spec["agent_name"],
            definition=PromptAgentDefinition(
                model=model,
                instructions=spec["instructions"],
                tools=[FileSearchTool(vector_store_ids=[vs_id])],
            ),
            description=spec["description"],
        )
        print(f"Registered RAG agent '{agent.name}' (v{agent.version}) -> {vs_id}")

    specialist_catalog = "\n".join(
        f"- {spec['agent_name']}: {spec['description']}"
        for spec in SPECIALIST_SPECS.values()
    )
    orchestrator = project.agents.create_version(
        agent_name=ORCHESTRATOR_NAME,
        definition=PromptAgentDefinition(
            model=model,
            instructions=(
                "You are the Supply Chain Orchestrator. Given a user question, you either:\n"
                "1) Select which specialist agents to consult by returning ONLY a JSON array of "
                "agent names from this list:\n"
                f"{specialist_catalog}\n"
                "2) Or, when given specialist RAG responses, synthesize them into a single "
                "accurate, well-structured final answer."
            ),
        ),
        description="Routes supply-chain queries to specialist Foundry RAG agents and synthesizes answers.",
    )
    print(f"Registered orchestrator '{orchestrator.name}' (v{orchestrator.version})")


if __name__ == "__main__":
    main()

