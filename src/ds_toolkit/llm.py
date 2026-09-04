import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# models_openai = ["gpt-5.4-mini", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"]
# models_ollama = ["qwen3:4b", "qwen3:8b", "qwen3:14b", "qwen3:30b",]

def get_client(provider: str) -> OpenAI:

    if provider == "openai":
        return OpenAI()

    if provider == "ollama":
        return OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

    raise ValueError(f"Unknown provider: {provider}")

tools = [
    {
        "type": "function",
        "name": "search_documents",
        "description": "Search documents in the local document database.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    }
]

def get_response(
    client: OpenAI,
    model: str,
    user_input: str,
    tools: list[dict] | None = None,
    systeminformation: str | None = None,
    response_model: type[BaseModel] | None = None,
):
    messages = []

    if systeminformation:
        messages.append({"role": "system", "content": systeminformation})

    messages.append({"role": "user", "content": user_input})

    if response_model:
        response = client.responses.parse(
            model=model,
            input=messages,
            tools=tools
            text_format=response_model,
        )

        return response

    response = client.responses.create(
        model=model,
        input=messages,
        tools=tools
    )

    return response