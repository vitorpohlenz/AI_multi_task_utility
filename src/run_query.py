#!/usr/bin/env python3
"""Run Query: minimal runnable app that queries OpenAI and returns a stable JSON output.

Usage:
  python src/run_query.py --question "How do I reset my password?"

The script will print JSON to stdout and also append a metrics entry to metrics/metrics.json.
"""
import sys
sys.dont_write_bytecode = True # Preventing cache

import os
import time
from datetime import datetime
import json
import argparse
from pathlib import Path
import openai
import dotenv
import tiktoken
import pandas as pd

# Environment variables
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")

# Pricing defaults (per 1Million tokens) — replace with your current prices
PRICE_PER_1M_PROMPT=float(os.getenv("PRICE_PER_1M_PROMPT", 0.2)) # $0.20 per 1 million tokens default for gpt-4o-mini
PRICE_PER_1M_COMPLETION=float(os.getenv("PRICE_PER_1M_COMPLETION", 0.8)) # $0.80 per 1 million tokens default for gpt-4o-mini

# Paths for files and directories
ROOT = Path(__file__).resolve().parents[1]
PROMPT_FILE = ROOT / "prompts" / "main_prompt.md"
METRICS_FILE = ROOT / "metrics" / "metrics.json"
METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Initialize the OpenAI client
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=BASE_URL
    )

#region Functions
def load_prompt():
    """Load the prompt from the prompt file."""
    return PROMPT_FILE.read_text(encoding="utf-8")


def count_tokens(text: str, model: str) -> int:
    """Estimate tokens for a piece of text.
    Use tiktoken if available, otherwise fall back to a simple word-based heuristic.
    """

    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("utf-8")
    return len(enc.encode(text))


def call_model(client: openai.OpenAI, prompt: str, question: str, temperature: float = 0.2):
    """Call the OpenAI ChatCompletion API and return parsed JSON plus raw response and usage.
    """
    # combine prompt + user question into messages for chat model
    system_prompt = prompt
    user_prompt = f"User question: {question}\n\nRespond using the JSON schema from the system prompt."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # For models that support `openai.ChatCompletion.create` or `openai.ChatCompletion.acreate`.
    start = time.time()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
        max_tokens=512,
    )
    end = time.time()

    latency_ms = int((end - start) * 1000)

    # Extract text
    text = resp.choices[0].message.content.strip()

    # usage may not be present for all clients
    tokens_prompt = resp.usage.prompt_tokens
    tokens_completion = resp.usage.completion_tokens
    total_tokens = resp.usage.total_tokens

    # If usage not provided, estimate using our token counter
    if tokens_prompt is None or tokens_completion is None:
        # approximate counting: tokens in system + user + response
        tokens_prompt = count_tokens(system_prompt + "\n" + user_prompt, MODEL)
        tokens_completion = count_tokens(text, MODEL)
        total_tokens = tokens_prompt + tokens_completion

    # estimate cost
    estimated_cost_usd = tokens_prompt*(PRICE_PER_1M_PROMPT/1e6) + tokens_completion*(PRICE_PER_1M_COMPLETION/1e6)

    return {
        "raw_text": text,
        "parsed": safe_parse_json(text),
        "usage": {"prompt_tokens": tokens_prompt, "completion_tokens": tokens_completion, "total_tokens": total_tokens},
        "latency_ms": latency_ms,
        "estimated_cost_usd": estimated_cost_usd,
        "response_obj": resp,
    }

def safe_parse_json(text: str):
    """Try to parse the assistant's text as JSON. If it fails, attempt to find JSON substring.
    Returns a dict with keys: ok (bool), json (object or None), error (str or None), text (original)
    """
    try:
        data = json.loads(text)
        return {"ok": True, "json": data, "error": None}
    except Exception as e:
        # attempt to extract first {...} block
        import re

        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                data = json.loads(m.group(0))
                return {"ok": True, "json": data, "error": None}
            except Exception as e2:
                return {"ok": False, "json": None, "error": f"json parse error: {e2}. original error: {e}", "text": text}
        return {"ok": False, "json": None, "error": str(e), "text": text}


def append_metrics(entry: dict):
    # Read existing
    if METRICS_FILE.exists():
        try:
            data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = []
    else:
        data = []
    data.append(entry)
    METRICS_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")


def run_query(client: openai.OpenAI, question: str, save_metrics: bool = True):
    prompt = load_prompt()
    result = call_model(client, prompt, question)

    timestamp = f"{datetime.now().isoformat()}"
    metrics_entry = {
        "timestamp": timestamp,
        "question": question,
        "tokens_prompt": int(result["usage"]["prompt_tokens"]),
        "tokens_completion": int(result["usage"]["completion_tokens"]),
        "total_tokens": int(result["usage"]["total_tokens"]),
        "latency_ms": int(result["latency_ms"]),
        "estimated_cost_usd": float(result["estimated_cost_usd"]),
        "ok_parse": bool(result["parsed"]["ok"]),
    }
    if save_metrics:
        append_metrics(metrics_entry)

    # Output contract JSON
    # If parse ok, print parsed json. Otherwise return a fallback structured JSON explaining parse failed
    if result["parsed"]["ok"]:
        out = result["parsed"]["json"]
    else:
        # safety fallback: produce a best-effort JSON
        out = {
            "answer": "I'm sorry — I couldn't produce a properly formatted JSON answer. Please try again or contact an admin.",
            "confidence": 0.0,
            "actions": ["ask user to rephrase", "escalate parsing error"],
            "metadata": {"notes": "parse_error", "raw_output": result["raw_text"]},
        }

    # Print canonical JSON to stdout
    print(json.dumps(out, ensure_ascii=False))

    # Also return for programmatic use
    return out

#endregion

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", "-q", required=True, help="User question text")
    parser.add_argument("--no-metrics", action="store_true", help="Do not save metrics")
    args = parser.parse_args()
    run_query(client=client, question=args.question, save_metrics=not args.no_metrics)