import os
from openai import OpenAI
from openai.types.responses import Response
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

def get_response(
    client: OpenAI,
    model: str,
    user_input: str,
    tools: list[dict] = [],
    systeminformation: str | None = None,
    text_format: type[BaseModel] | None = None,
):  
    messages = []

    if systeminformation:
        messages.append({"role": "system", "content": systeminformation})

    messages.append({"role": "user", "content": user_input})

    if text_format:
        response = client.responses.parse(
            model=model,
            input=messages,
            tools=tools,
            text_format=text_format,
        )

        return response

    response = client.responses.create(
        model=model,
        input=messages,
        tools=tools,
    )

    return response

def _get_items_by_type(response: Response, type_: str) -> list:
    return [
        item
        for item in response.output
        if item.type == type_
    ]

def _get_first_item_by_type(response: Response, type_: str):
    return next(
        (
            item
            for item in response.output
            if item.type == type_
        ),
        None
    )

def get_text(response: Response) -> str:
    return response.output_text

def has_tool_calls(response: Response) -> bool:
    return any(
        item.type == "function_call"
        for item in response.output
    )

def get_tool_calls(response: Response) -> list:
    return _get_items_by_type(response, "function_call")

def get_reasoning(response: Response) -> list:
    return _get_items_by_type(response, "reasoning")

def get_usage(response: Response):
    return response.usage

# tools = [
#     {
#         "type": "function",
#         "name": "search_documents",
#         "description": "Search documents in the local document database.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "query": {
#                     "type": "string",
#                     "description": "The search query",
#                 },
#             },
#             "required": ["query"],
#             "additionalProperties": False,
#         },
#     }
# ]