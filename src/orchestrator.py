"""Multi-agent orchestration runtime using Azure AI Foundry agents."""

import json
import os
from functools import lru_cache

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from src.config import ORCHESTRATOR_NAME, VALID_AGENTS

load_dotenv()


@lru_cache(maxsize=1)
def _get_openai_client():
    """Return a cached Foundry OpenAI-compatible client."""
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    return project.get_openai_client()


def _invoke_agent(agent_name: str, prompt: str) -> str:
    """Invoke a named Foundry agent via Responses API with agent_reference."""
    oai = _get_openai_client()
    response = oai.responses.create(
        input=prompt,
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": agent_name,
            }
        },
    )
    return response.output_text or ""


def _route_question(question: str) -> list[str]:
    """Ask the orchestrator agent which specialist RAG agents should answer."""
    routing_prompt = (
        "Select 1 to 3 specialist agent names needed to answer the user's question. "
        "Respond ONLY with a JSON array of agent names, e.g. [\"should-cost-agent\", \"procurement-rfq-agent\"].\n\n"
        f"Question: {question}"
    )
    raw = _invoke_agent(ORCHESTRATOR_NAME, routing_prompt).strip()
    try:
        start, end = raw.find("["), raw.rfind("]")
        parsed = json.loads(raw[start : end + 1]) if start != -1 and end != -1 else []
        selected = [name for name in parsed if name in VALID_AGENTS]
        if selected:
            return selected
    except json.JSONDecodeError:
        pass
    return ["should-cost-agent", "fabrication-rules-agent"]


def ask_supply_chain(question: str) -> dict:
    """Route a question to specialist Foundry RAG agents and synthesize the final answer."""
    selected_agents = _route_question(question)

    specialist_outputs: dict[str, str] = {}
    for agent_name in selected_agents:
        specialist_outputs[agent_name] = _invoke_agent(agent_name, question)

    context_blocks = "\n\n".join(
        f"### {name}\n{text}" for name, text in specialist_outputs.items()
    )
    synthesis_prompt = (
        f"User Question: {question}\n\n"
        f"Specialist RAG Findings:\n{context_blocks}\n\n"
        "Synthesize a clear, concise, well-structured final answer grounded in the specialist findings above."
    )
    final_answer = _invoke_agent(ORCHESTRATOR_NAME, synthesis_prompt)

    return {
        "question": question,
        "agents_consulted": selected_agents,
        "specialist_responses": specialist_outputs,
        "answer": final_answer,
    }

