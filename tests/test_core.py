"""Pytest tests for the core functionality.
Run with: pytest -q
"""
import sys
sys.dont_write_bytecode = True # Preventing cache
import json
import os
import types
import dotenv
from pathlib import Path

dotenv.load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
PROMPT_FILE = ROOT / "prompts" / "main_prompt.md"
MODEL = os.getenv("MODEL")

sys.path.append(str(SRC_ROOT))

# Import the module under test.
from functions import count_tokens, safe_parse_json, load_prompt

def test_count_tokens():
    # simple tests for count_tokens
    n = count_tokens("this is a short test with model", MODEL)
    assert n >= 1

    n = count_tokens("this is a short test without model")
    assert n >= 1

def test_safe_parse_json():
    # simple tests for safe_parse_json
    data = safe_parse_json('{"answer": "Do X.", "confidence": 0.8, "actions": ["do X"], "metadata": {"source": "test"}}')
    assert data['ok']

    data = safe_parse_json("this is not a valid json")
    assert not data['ok']

def test_load_prompt():
    # simple tests for load_prompt
    prompt = load_prompt(PROMPT_FILE)
    assert (len(prompt) > 0) and isinstance(prompt, str)