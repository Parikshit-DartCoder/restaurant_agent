import os
import json
import re

from dotenv import load_dotenv
from openai import OpenAI

from utils.logger import get_logger

# ---------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------

load_dotenv()

logger = get_logger("LLM")


class LLMUnavailableError(Exception):
    pass


_client = None


# ---------------------------------------------------
# Create OpenAI / OpenRouter client
# ---------------------------------------------------

def _get_client():
    global _client

    if _client:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise LLMUnavailableError("OPENAI_API_KEY missing")

    logger.info("Initializing OpenAI client")

    _client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    return _client


# ---------------------------------------------------
# Basic chat call
# ---------------------------------------------------

def chat(messages, temperature=0):

    try:

        logger.info("LLM CALL START")

        response = _get_client().chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            temperature=temperature,
        )

        text = response.choices[0].message.content

        logger.info("LLM RESPONSE RECEIVED")

        return text

    except Exception as e:

        logger.error("LLM CALL FAILED")

        raise LLMUnavailableError(str(e))


# ---------------------------------------------------
# Extract JSON from model output
# ---------------------------------------------------

def _extract_json_block(text):

    text = text.strip()

    # direct JSON
    if text.startswith("{") or text.startswith("["):
        return text

    # search JSON inside text
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)

    if match:
        return match.group(1)

    raise ValueError("No JSON object found in model response")


# ---------------------------------------------------
# Chat expecting JSON
# ---------------------------------------------------

def chat_json(messages):

    logger.info("CHAT_JSON START")

    raw = chat(messages)

    logger.info("Raw LLM output captured")

    try:

        block = _extract_json_block(raw)

        data = json.loads(block)

        logger.info("JSON successfully parsed")

        return data

    except Exception:

        logger.warning("No JSON detected in model output")
        logger.warning("Model output: %s", raw)

        return None