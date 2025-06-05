import pandas as pd
import random
from datetime import datetime, timedelta
from scripts.helpers import call_gpt, cfg
from tqdm import tqdm
import os
import json

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def simulate_transactions(user, months=6):
    start_date = datetime.today() - timedelta(days=months*30)
    end_date = datetime.today()
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    all_txns = []
    for date in dates:
        n_txns = random.randint(1, 4)
        for _ in range(n_txns):
            base_prompt = f"""
You are generating realistic raw bank statement transactions for a UK gig worker with the following profile:
{json.dumps(user)}

Generate ONE messy Open Banking-style transaction entry in JSON with:
- timestamp (in ISO format)
- amount (positive or negative)
- transaction_type (CREDIT or DEBIT)
- currency (GBP)
- description_raw (as messy and real as possible)
- description_cleaned
- merchant
- is_income (True/False)
- risk_flag (e.g., "gambling", "unexplained inflow", "synthetic_loop", None)
- source_type (platform, agency, tuition, govt, refund, etc.)

Output a JSON dict.
"""
            response = call_gpt([{"role": "user", "content": base_prompt}], max_tokens=512)
            try:
                txn = json.loads(response.strip())
                txn["user_id"] = user["user_id"]
                all_txns.append(txn)
            except:
                continue
    return all_txns

def main():
    personas = pd.read_csv(f'{cfg["output_dir"]}/personas.csv')
    os.makedirs(f'{cfg["output_dir"]}/transactions', exist_ok=True)

    for _, user in tqdm(personas.iterrows(), total=personas.shape[0]):
        txns = simulate_transactions(user.to_dict(), months=cfg["months"])
        df = pd.DataFrame(txns)
        df.to_csv(f'{cfg["output_dir"]}/transactions/{user["user_id"]}.csv', index=False)

if __name__ == "__main__":
    main()
