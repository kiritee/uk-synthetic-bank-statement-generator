# Ensure root directory is in sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import random
from datetime import datetime, timedelta
from scripts.helpers import call_gpt, extract_json_block
from scripts.config import load_config
from tqdm import tqdm
import json

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def create_prompt(user, months=6):
    return [{
        "role": "system",
        "content": "You are a bank statement transactions generator for synthetic bank data modeling."
    }, {
        "role": "user",
        "content": f"""
You are simulating a full {months}-month UK bank statement for a gig worker with the following profile:
{json.dumps(user, indent=2)}

Generate a JSON array of messy Open Banking-style transaction entries covering the last {months} months. Ensure:
- Realistic frequency
- Mix of CREDIT and DEBIT
- Messy, real-looking raw descriptions
- Diverse merchant names and source types
- Clear income vs non-income behavior

Each transaction must include:
- timestamp (ISO 8601)
- amount (positive or negative, GBP)
- transaction_type ("CREDIT" or "DEBIT")
- currency ("GBP")
- description_raw
- description_cleaned
- merchant
- is_income (True/False)
- risk_flag (e.g. "gambling", "unexplained inflow", "synthetic_loop", or null)
- source_type (e.g. "platform", "agency", "tuition", "govt", "refund", etc.)

Output ONLY a valid JSON array.
"""
    }]


def simulate_transactions(user, months=6):
    raw_response = call_gpt(create_prompt(user, months))
    cleaned_response = extract_json_block(raw_response)

    try:
        txns = json.loads(cleaned_response)
        for txn in txns:
            txn["user_id"] = user["user_id"]
        return txns
    except Exception as e:
        print("❌ JSON Parse Error:", e)
        print(cleaned_response)
        return []


def main():
    cfg = load_config()
    personas_path = os.path.join(cfg["output_dir"], "personas.csv")
    if not os.path.exists(personas_path):
        raise FileNotFoundError(f"❌ personas.csv not found at {personas_path}")

    personas = pd.read_csv(personas_path)

    if personas.empty:
        raise ValueError("❌ personas.csv is empty. Nothing to process.")


    os.makedirs(f'{cfg["output_dir"]}/transactions', exist_ok=True)

    for _, user in tqdm(personas.iterrows(), total=personas.shape[0]):
        txns = simulate_transactions(user.to_dict(), months=cfg["months"])
        df = pd.DataFrame(txns)
        df.to_csv(f'{cfg["output_dir"]}/transactions/{user["user_id"]}.csv', index=False)

if __name__ == "__main__":
    main()
