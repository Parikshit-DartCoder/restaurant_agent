import json
import os
import re
from typing import Any, Dict, List

from openai import OpenAI


class LLMUnavailableError(RuntimeError):
    pass


_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        base_url = os.getenv("OPENAI_BASE_URL", "").strip()

        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url

        _client = OpenAI(**kwargs)
    return _client


def chat(messages: List[Dict[str, str]], temperature: float = 0) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    try:
        response = _get_client().chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        raise LLMUnavailableError(str(e)) from e


def _extract_json_block(text: str) -> str:
    text = (text or "").strip()

    if text.startswith("{") and text.endswith("}"):
        return text

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        return match.group(0)

    raise ValueError("No JSON object found in model response")


def chat_json(messages: List[Dict[str, str]], temperature: float = 0) -> Dict[str, Any]:
    raw = chat(messages, temperature=temperature)
    block = _extract_json_block(raw)
    return json.loads(block)