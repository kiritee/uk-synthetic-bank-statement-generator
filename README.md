# Synthetic Bank Data Generator (UK Gig Economy Edition)

This project generates ultra-realistic Open Banking-style bank transaction data for UK-based gig and temporary workers. It simulates complex financial behavior with LLM-powered persona and transaction generation.

---

## 🔧 Features

- ✅ 1000+ realistic UK gig worker personas
- ✅ GPT-4 powered messy transaction descriptions
- ✅ Edge cases: gambling, refunds, synthetic loops, bounced payments
- ✅ Output includes:
  - `description_raw`
  - `description_cleaned`
  - `merchant`
  - `is_income`
  - `risk_flag` (e.g., gambling, synthetic_loop)
  - `source_type` (e.g., platform, agency, tuition, govt, refund)

---

## 📁 Directory Structure

synthetic_bank_data/
├── data/                  
│   ├── personas.csv             ← All user profiles
│   └── transactions/            ← One CSV per user
├── scripts/
│   ├── config.yaml              ← Main configuration
│   ├── generate_personas.py     ← Persona creation via GPT
│   ├── generate_transactions.py ← Transaction generation via GPT
│   ├── helpers.py               ← OpenAI + utility functions
├── bankgen.py                   ← CLI entrypoint
├── logs/                        ← CLI logs
├── requirements.txt             
├── Dockerfile
├── Makefile

---

## 🚀 Setup (Local)

1. Install dependencies:
   pip install -r requirements.txt

2. Add your OpenAI API key:
   - Set it in `scripts/config.yaml`
   - OR export it via environment:
     export OPENAI_API_KEY="sk-..."

3. Run generation:
   python bankgen.py

Or use CLI:
   bankgen -r personas
   bankgen -r transactions
   bankgen set-config num_users 250

---

## 🐳 Docker + Makefile Usage

Build the image:
   make build

Run full pipeline:
   make run

Run specific step:
   make run-personas
   make run-transactions

Dry-run:
   make dry

Validate config:
   make validate

Update config:
   make config KEY=num_users VALUE=500

---

## ⚙️ CLI Options

bankgen -r personas         # Run only personas
bankgen -r transactions     # Run only transactions
bankgen set-config months 6 # Update config
bankgen --validate-config   # Validate config.yaml
bankgen --dry-run           # Show planned execution

---

## ✅ Output Fields

Each transaction:
- timestamp
- amount
- transaction_type (CREDIT/DEBIT)
- description_raw (messy Open Banking style)
- description_cleaned
- merchant
- is_income
- risk_flag
- source_type

Each persona:
- name, location, age
- gig_types, payment_channels
- complexity_level
- income_regular, income_stability
- income_true_last_3mo
- income_lender_assess_6mo
- risk_level
- persona_description
- income_interpretation

---

## 📌 Example Use Cases

- Train ML models for income detection
- Build affordability checks for lenders
- Simulate fraud/risk scoring models
- Benchmark Open Banking parsers

---

## ✨ Coming Soon

- Docker Compose with volume mounts
- S3 output writer
- CI validation via GitHub Actions

---

## 📬 Author

Kiritee Konark Mishra

Built for ultra-realism and chaos-tolerant financial system
