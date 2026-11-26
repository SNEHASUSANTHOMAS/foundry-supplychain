"""Standalone connectivity smoke test for the Azure AI Foundry OpenAI endpoint."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

endpoint = "https://foundrysnehaws2.services.ai.azure.com/openai/v1"
deployment_name = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-5.6-luna")
api_key = os.environ.get("API_KEY")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key,
)

response = client.responses.create(
    model=deployment_name,
    input="What is the capital of France?",
)

print(f"answer: {response.output[0]}")

