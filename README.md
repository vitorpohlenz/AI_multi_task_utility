# AI Multi-Task Text Utility

A small, modular AI helper designed for **customer-support automation** and **text query processing**.  
It takes a question, calls the OpenAI API, and returns a structured **JSON response** with:

- **Answer**
- **Confidence score**
- **Recommended actions**
- **Notes**

And also saves:
- **Per-run metrics** (latency, tokens, estimated cost, etc)

This project demonstrates **prompt engineering**, **metrics logging**, and **structured output generation** — key foundations for production-grade AI assistants.


## Repository Structure
```
AI_multi_task_utility/
│
├── src/
│ ├── functions.py # Auxiliary functions as `load_prompt`
│ ├── run_query.py # Main script / module entrypoint
| └── safety.py # Moderation + PII redaction helpers
│
├── prompts/
│ └── main_prompt.md # Instruction-based prompt template
│
├── metrics/
│ └── metrics.json # Logged metrics (tokens, cost, latency, timestamp)
│
├── reports/
│ └── PI_report_en.md # 1–2 page project summary and analysis
│
├── tests/
│ └── test_core.py # Unit tests using `pytest`
│
├── .env.example # Environment variable template
├── README.md # This file
└── requirements.txt # Python dependencies
```

## Configuring the setup for this project:

### Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configure environment variables
Create a `.env` file in the project root folder, following the `.env.example` file

## How to run this project:

With the virtual environment activated run the file `src/run_query.py` passing your question with `--question` as arg.
Example:
```bash
python src/run_query.py --question "How I create a new account?"
```

Output:
```json
{
    "answer": "To create a new account, go to the sign‑up page, enter your email and password, confirm the terms, and click \"Register\"; then verify your email address via the link sent to your inbox.", 
    "confidence": 0.95, 
    "actions": ["visit sign‑up page", "enter email and password", "accept terms", "click Register", "check email for verification link"], 
    "notes": "If the user is on mobile, direct them to the app store or mobile site."}
```

## Running Tests
With the virtual environment activated call `pytest -s tests/`
Ex:
```bash
python -m pytest -s tests/
```

# Quick Reference
| Task | Command |
|---|---|
| Run query | `python -m src.run_query --question "Your question"` |
| Run tests | `python -m pytest -s tests/` |
| Metrics file | metrics/metrics.json |
| Install dependencies |  `pip install -r requirements.txt` |

# Extra

## Prompt Engineering Technique

This project uses an instruction-based + few-shot prompt template stored in prompts/main_prompt.md.
The prompt enforces JSON schema compliance and includes examples to improve reliability and minimize post-processing.

Technique summary:

- Instruction-based prompting → Guarantees structured fields (answer, confidence, actions)
- Few-shot examples → Improve consistency across customer-support queries
- Temperature control (low) → Prioritizes determinism over creativity

## Known Limitations

- Uses static cost estimates — does not dynamically fetch API pricing updates.
- Latency measurement includes network + API processing only (not disk write time).
- Limited safety detection; moderation is basic (no advanced adversarial filtering).
- Currently designed for single-question runs (not batched inputs).
- Does not include automatic retries on API timeouts.