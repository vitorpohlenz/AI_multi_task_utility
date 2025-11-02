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
MODEL = os.getenv("MODEL")

sys.path.append(str(SRC_ROOT))

# Import the module under test.
from functions import count_tokens

def test_count_tokens():
    # simple tests for count_tokens
    n = count_tokens("this is a short test with model", MODEL)
    assert n >= 1

    n = count_tokens("this is a short test without model")
    assert n >= 1