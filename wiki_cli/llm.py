"""The only module that talks to the model.

It sends a list of chat messages to the local Ollama server and returns the
reply. Gemma doesn't read files or remember anything on its own; everything it
sees arrives through the messages built by the harness.
"""
import time
from dataclasses import dataclass

import requests

from . import config


class ModelUnavailable(Exception):
    """Raised with a user-facing explanation when the local model can't be used."""


@dataclass
class Reply:
    text: str
    seconds: float
    prompt_tokens: int
    output_tokens: int


def check_ready():
    """Confirm Ollama is running and the model is downloaded, or explain how to fix it."""
    try:
        resp = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3)
        resp.raise_for_status()
    except requests.RequestException:
        raise ModelUnavailable(
            f"Can't reach Ollama at {config.OLLAMA_HOST}.\n"
            "  Open the Ollama app (llama icon in the menu bar), then try again."
        )
    names = {m["name"] for m in resp.json().get("models", [])}
    if config.MODEL not in names:
        raise ModelUnavailable(
            f"Model '{config.MODEL}' isn't downloaded.\n"
            f"  While online, run: ollama pull {config.MODEL}"
        )


def chat(messages, temperature=0.7, schema=None, num_ctx=None):
    """Send messages ([{role, content}, ...]) to the local model and return a Reply.

    schema: optional JSON Schema. Ollama then forces the reply to be JSON matching it,
    which is how ingest gets reliable structured output from a small model.
    """
    check_ready()
    body = {
        "model": config.MODEL,
        "messages": messages,
        "stream": False,
        "think": False,  # Gemma 4 "thinking" is slow on an 8 GB M1 and not needed here
        "options": {"temperature": temperature, "num_ctx": num_ctx or config.NUM_CTX},
    }
    if schema:
        body["format"] = schema
    start = time.perf_counter()
    try:
        resp = requests.post(f"{config.OLLAMA_HOST}/api/chat", json=body, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.Timeout:
        raise ModelUnavailable(f"The model took longer than {config.REQUEST_TIMEOUT}s to answer.")
    except requests.RequestException as err:
        raise ModelUnavailable(f"The local model request failed: {err}")
    data = resp.json()
    if "message" not in data:
        raise ModelUnavailable(f"Unexpected reply from Ollama: {str(data)[:200]}")
    return Reply(
        text=data["message"]["content"].strip(),
        seconds=time.perf_counter() - start,
        prompt_tokens=data.get("prompt_eval_count", 0),
        output_tokens=data.get("eval_count", 0),
    )
