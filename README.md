# 🏦 Synthetic Bank Data Generator (UK Gig Economy Edition)

This project generates ultra-realistic **Open Banking–style transaction data** for UK-based gig and temporary workers — complete with realistic personas, irregular income patterns, and messy transaction descriptions.

Built with:
- **GPT-powered persona + transaction simulation**
- **kirkomi_utils** for unified logging and LLM management
- **CLI orchestration** via `bankgen`

---

## 🚀 Features

- ✅ 1000+ synthetic UK gig-worker personas  
- ✅ GPT-4-family (via kirkomi_utils.llm) powered transaction text generation  
- ✅ Handles edge cases: gambling, refunds, synthetic loops, overdrafts  
- ✅ Produces clean, lender-usable CSVs  
- ✅ Fully async + cache-aware LLM calls  
- ✅ Modular logging with contextual tags (SmartLogger)

---

## 📁 Directory Structure

```
synthetic_bank_data/
├── data/
│   ├── personas.csv              ← Generated personas
│   └── transactions/             ← One CSV per user
├── scripts/
│   ├── config.yaml               ← Main configuration
│   ├── config.py                 ← load_config(), save_config()
│   ├── helpers.py                ← get_llm(), uuid, cost, etc.
│   ├── generate_personas.py      ← Persona generation (async)
│   ├── generate_transactions.py  ← Transaction generation (async)
├── promptlib/
│   ├── personas.py               ← full_persona_1_shot template
│   └── transactions.py           ← full_transaction_1_shot template
├── logs/
├── bankgen.py                    ← CLI entrypoint
├── requirements.txt
├── Dockerfile
├── Makefile
└── README.md
```

---

## ⚙️ Configuration

### 1. `scripts/config.yaml`
Project-level controls (types shown):

```yaml
num_users: 1
months: 6
batch_size: 10
tx_batch_size: 5
output_dir: data

# LLM configuration (optional)
provider: openai
model: gpt-4o-mini
temperature: 0.2
# max_tokens: 15000
provider_options:
  openai:
    request_timeout_s: 45
    max_retries: 0
    watchdog_timeout_s: 70
```

> Do **not** put your API key here — it lives in `.env`.

---

### 2. `.env`
LLM provider and credentials (used by `kirkomi_utils.llm`):

```bash
# .env
OPENAI_API_KEY=sk-...

LLM_PROVIDER=openai
LLM_MODEL=gpt-5
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=4096
OPENAI_REQUEST_TIMEOUT_S=60
OPENAI_ENABLE_FALLBACK=false
```

- `.env` values = defaults  
- `config.yaml` can override model/temperature/max_tokens  
- `OPENAI_API_KEY` is required

---

## 🧠 Architecture Overview

| Layer | Responsibility |
|-------|----------------|
| **kirkomi_utils.llm** | Unified LLMClient facade with caching, retries, async support |
| **kirkomi_utils.logging** | SmartLogger with colored console + file output, tags, timers |
| **scripts/helpers.py** | Bridges config + LLM + project logic (`get_llm()`, `estimate_cost_tokens`) |
| **scripts/generate_personas.py** | Generates gig-worker personas |
| **scripts/generate_transactions.py** | Generates Open Banking–style transactions |
| **bankgen.py** | CLI orchestrator with config validation, cost preview, and stage control |

---

## 🛠️ Setup (Local)

### Install dependencies
```bash
pip install -r requirements.txt
```

### Set up environment
```bash
export OPENAI_API_KEY="sk-..."
# or create a .env file
```

### Run the generator
```bash
python -m scripts.bankgen
```

### Or run specific stages
```bash
python -m scripts.bankgen --run personas
python -m scripts.bankgen --run transactions
```

---

## 🧩 CLI Usage

| Command | Description |
|----------|-------------|
| `bankgen -r personas` | Generate personas only |
| `bankgen -r transactions` | Generate transactions only |
| `bankgen --validate-config` | Validate `config.yaml` types and keys |
| `bankgen --dry-run` | Simulate execution |
| `bankgen --set-config num_users 250` | Update configuration value |
| *(no args)* | Run full pipeline (personas + transactions) |

During runs, the CLI:
- Estimates token + cost via `estimate_cost_tokens`
- Prompts for confirmation
- Logs progress with contextual tags (`[COST]`, `[LLM]`, `[TXN_GEN]`, etc.)

---

## 📊 Output Format

### Personas (`data/personas.csv`)
| Field | Description |
|--------|-------------|
| user_id | Unique identifier |
| name, location, age | Persona metadata |
| gig_types, payment_channels | Work/income context |
| income_regular, income_stability | Behavioral features |
| income_true_last_3mo, income_lender_assess_6mo | Computed income stats |
| risk_level | Risk tag |
| persona_description | Narrative summary |

### Transactions (`data/transactions/<user_id>.csv`)
| Field | Description |
|--------|-------------|
| timestamp | Transaction date/time |
| amount | Float, ± sign per type |
| transaction_type | CREDIT / DEBIT |
| description_raw | Messy Open Banking string |
| description_cleaned | Normalized description |
| merchant | Parsed merchant |
| is_income | Boolean |
| risk_flag | e.g. gambling, refund, synthetic_loop |
| source_type | Platform / agency / tuition / refund |

---

## 💡 Example Use Cases

- Train ML models for **income detection**  
- Develop **affordability/risk scoring** prototypes  
- Benchmark **Open Banking parsers**  
- Simulate **synthetic fraud behavior** for testing models

---

## 🧰 Logging

Uses `kirkomi_utils.logging.logger.log` — contextual, colorized, timestamped output.

Example:
```
[16:24:10] INFO  - [COST] Estimated token usage for personas: 40,960 tokens
[16:24:11] DEBUG - [LLM] Starting block: batch 3...
[16:24:12] INFO  - [LLM] Finished block in 0.70s
[16:24:18] INFO  - [TXN] ✅ Transactions written to /data/transactions
```

Change verbosity:
```python
from kirkomi_utils.logging.logger import log
import logging
log.set_levels(console_level=logging.DEBUG)
```

---

## 🧩 Running Programmatically

```python
from scripts.generate_personas import generate_personas_async
from scripts.generate_transactions import generate_transactions_async
import asyncio

asyncio.run(generate_personas_async())
asyncio.run(generate_transactions_async())
```

or use the shared LLM facade:
```python
from scripts.helpers import get_llm
llm = get_llm()
result = llm.chat([{"role":"user","content":"Generate 5 fintech personas"}])
print(result.content)
```

---

## 🐳 Docker + Makefile Usage

Build image:
```bash
make build
```

Run full pipeline:
```bash
make run
```

Run specific step:
```bash
make run-personas
make run-transactions
```

Validate config:
```bash
make validate
```

Dry run:
```bash
make dry
```

---

## 🧾 License & Credits

**Author:** Kiritee Konark Mishra  
Built for **ultra-realism and chaos-tolerant financial systems**

LLM integration and structured logging powered by **kirkomi_utils**  
© 2025 Kiritee Konark Mishra. All rights reserved.
