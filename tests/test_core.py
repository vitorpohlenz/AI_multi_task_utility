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

# def test_run_query_returns_schema(monkeypatch):
#     # deterministic stub for call_model to avoid network in unit test
#     def fake_call_model(prompt, question, temperature=0.2):
#         return {
#             "raw_text": '{"answer": "Do X.", "confidence": 0.8, "actions": ["do X"], "metadata": {"source": "test"}}',
#             "parsed": {"ok": True, "json": {"answer": "Do X.", "confidence": 0.8, "actions": ["do X"], "metadata": {"source": "test"}}},
#             "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
#             "latency_ms": 10,
#             "estimated_cost_usd": 0.0009,
#             "response_obj": {}
#         }

#     # Monkeypatch the call_model function used by run_query
#     monkeypatch.setattr(rq, "call_model", fake_call_model)

#     out = rq.run_query("dummy question", save_metrics=False)
#     assert isinstance(out, dict)
#     assert "answer" in out
#     # confidence must be between 0 and 1
#     assert 0.0 <= out.get("confidence", 0) <= 1.0
#     assert isinstance(out.get("actions", []), list)

def test_count_tokens():
    # simple tests for count_tokens
    n = count_tokens("this is a short test with model", MODEL)
    assert n >= 1

    n = count_tokens("this is a short test without model")
    assert n >= 1