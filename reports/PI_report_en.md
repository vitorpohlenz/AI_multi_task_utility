# Project Implementation Report — Multi-Task Text Utility

**Author:** Vitor Pohlenz  
**Date:** November 2025  
**Language:** English  
**Repository:** https://github.com/vitorpohlenz/AI_multi_task_utility  

---

## Architecture Overview

The **Multi-Task Text Utility** is a modular Python application that acts as an intelligent helper for customer-support automation.  
Its main goal is to accept a **user question** and return a **structured JSON** with an `answer`, `confidence score`, `recommended actions`, and detailed **usage metrics**.

### Core Components

| Module | Purpose |
|---------|----------|
| `src/run_query.py` | Main entry point. Handles input parsing, prompt creation, API call, JSON formatting, and metrics logging. |
| `src/safety.py` | Performs content moderation and optional PII redaction before the prompt is sent to the model. |
| `src/functions.py` | Auxiliary functions to be consumed in `run_query.py` such as loading the prompt and check is the output is a valid JSON. |
| `prompts/main_prompt.md` | Defines the instruction-based + few-shot prompt template, ensuring consistent and valid JSON outputs. |
| `metrics/metrics.json` | Logs run-time statistics for monitoring cost and performance. |
| `tests/test_core.py` | Provides automated tests for exemple for JSON schema compliance and token counting. |

### Flow Summary

1. **User Input:** Question passed via Command Line Interface(CLI) argument.  
2. **Moderation Step:** Input validated for unsafe or disallowed content and also removing Personal Identifiable Information (PII).  
3. **Prompt Construction:** Instruction + few-shot examples embedded from `main_prompt.md`.  
4. **Model Call:** Request sent to the OpenAI API (model configurable via environment variable).  
5. **Post-processing:** JSON string parsed, validated, and logged.  
6. **Metrics Logging:** Metrics logs such as token counts, latency, cost, etc stored in `metrics/metrics.json`.  

This design balances simplicity and traceability, creating a foundation suitable for larger AI pipelines or API endpoints.

---

## Prompt Technique(s) Used and Rationale

Prompt engineering strategy:

**Instruction-Based Prompting**  
   - Clear task specification (“Respond in JSON with fields: answer, confidence, actions”).  
   - Reduces post-processing complexity and schema errors.
   - Include especific instruction: Say "I don't know" when unsure.

**Few-Shot Examples**  
   - Demonstrates expected format and tone through 2–3 representative examples.  
   - Increases reliability and helps the model adhere to concise, structured outputs.

**Temperature Control (0.2–0.4)**  
   - Keeps responses deterministic and concise, avoiding overly creative completions.

This approach ensures reproducibility, consistency, and schema compliance — essential qualities for downstream integration with support dashboards or analytics tools.

---

## Metrics Summary and Sample Results

The system automatically logs the following **metrics per query**:

| Metric | Description |
|---------|-------------|
| `tokens_prompt` | Number of tokens in the prompt (used to estimate cost). |
| `tokens_completion` | Tokens generated in the model output. |
| `total_tokens` | Combined total of prompt + completion tokens. |
| `latency_ms` | Total elapsed time for model completion. |
| `estimated_cost_usd` | Calculated based on OpenAI token pricing. |

### Example Metrics Log Entry

```json
{
  "timestamp": "2025-11-02T17:23:14Z",
  "tokens_prompt": 185,
  "tokens_completion": 85,
  "total_tokens": 270,
  "latency_ms": 1043,
  "estimated_cost_usd": 0.00092
}
```

## Challenges Encountered

**JSON Parsing Robustness**  
   - Some early responses returned text outside JSON brackets.  
   - Solved by enforcing strict JSON schema validation and re-prompting if invalid.

**Latency Variation**  
   - Observed inconsistent latency due to network or model queue delays.  
   - Mitigated by adding time measurement at API call level.

**Moderation and Safety Handling**  
   - Basic moderation implemented; advanced adversarial input detection remains a future improvement area.
   - Failed to find a way to call `client.moderations.create` when using [Open Router models](https://openrouter.ai/models)

---

## Potential Improvements

| Area | Improvement |
|-------|--------------|
| **Scalability** | Convert the script to a **FastAPI** or **Flask** service for real-time integration with front-end systems. |
| **Monitoring** | Integrate with **Prometheus** or **OpenTelemetry** for detailed metrics visualization. |
| **Safety** |Use `https://openrouter.ai/models` with [Open Router models](https://openrouter.ai/models). Extend moderation with pattern-based filters and allow user-configurable policies. |
| **RAG Integration** | Combine with a document retriever to answer domain-specific knowledge base queries. |
| **Testing** | Add schema validation tests using `jsonschema` for stricter response validation. |

---

## Conclusion

The Multi-Task Text Utility demonstrates a **production-ready blueprint** for structured AI responses, cost monitoring, and reliable JSON handling.  
It applies prompt engineering techniques that balance interpretability, safety, and operational efficiency.  
While still a lightweight prototype, it could attend the expectations.

---

