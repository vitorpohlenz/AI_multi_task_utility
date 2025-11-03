""" Auxiliary Functions module."""
import tiktoken
import json
import re
from pathlib import Path
from typing import Union

#region Functions
def load_prompt(prompt_file: str):
    """Load the prompt from the prompt file."""
    return prompt_file.read_text(encoding="utf-8")


def count_tokens(text: str, model: Union[str, None] = None) -> int:
    """
    Estimate tokens for a piece of text using tiktoken.
    """
    try:
        # Remove 'openai/' from the model name, eg. if it is Open Router model.
        enc = tiktoken.encoding_for_model(model.replace('openai/',''))
    except Exception:
        enc = tiktoken.get_encoding('cl100k_base')
    return len(enc.encode(text))


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
        # regex to find the first {..} block in the text
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                data = json.loads(match.group(0))
                return {"ok": True, "json": data, "error": None}
            except Exception as e2:
                return {"ok": False, "json": None, "error": f"json parse error: {e2}. original error: {e}", "text": text}
        return {"ok": False, "json": None, "error": str(e), "text": text}


def append_metrics(entry: dict, metrics_file: Path):
    # Read existing
    if metrics_file.exists():
        try:
            data = json.loads(metrics_file.read_text(encoding="utf-8"))
        except Exception:
            data = []
    else:
        data = []
    data.append(entry)
    metrics_file.write_text(json.dumps(data, indent=4), encoding="utf-8")

