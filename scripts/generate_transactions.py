# Ensure root directory is in sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import json
import pandas as pd
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import random
from datetime import datetime, timedelta
from scripts.helpers import call_gpt, call_gpt_async, count_tokens, extract_json_block
from scripts.config import load_config
from promptlib.transactions import full_transaction_1_shot

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def create_prompt(user, months=6):
    prompt = [
    #     {
    #     "role": "system",
    #     "content": "You are a bank statement transactions generator for synthetic bank data modeling."
    # }, 
    {
        "role": "user",
        "content": full_transaction_1_shot.format(months=months, persona=json.dumps(user, indent=2))
    }]
    # print("No of tokens in prompt:", count_tokens(prompt))
    return prompt


def simulate_transactions(user, months=6):
    """Simulate transactions for a user over a specified number of months."""

    response = call_gpt(create_prompt(user, months))

    try:
        txns = json.loads(response)
        for txn in txns:
            txn["user_id"] = user["user_id"]
        return txns
    except Exception as e:
        print("❌ JSON Parse Error:", e)
        print(response)
        return []

async def simulate_transactions_async(user, months=6):
    """Asynchronously simulate transactions for a user over a specified number of months."""
    
    response = await call_gpt_async(create_prompt(user, months))

    try:
        txns = json.loads(response)
        for txn in txns:
            txn["user_id"] = user["user_id"]
        return txns
    except Exception as e:
        print("❌ JSON Parse Error:", e)
        print(response)
        return []


def generate_transactions():
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


async def generate_transactions_async():
    cfg = load_config()
    personas_path = os.path.join(cfg["output_dir"], "personas.csv")
    if not os.path.exists(personas_path):
        raise FileNotFoundError(f"❌ personas.csv not found at {personas_path}")

    personas = pd.read_csv(personas_path)

    if personas.empty:
        raise ValueError("❌ personas.csv is empty. Nothing to process.")

    os.makedirs(f'{cfg["output_dir"]}/transactions', exist_ok=True)
    tasks = []
    for _, user in tqdm(personas.iterrows(), total=personas.shape[0]):
        tasks.append(simulate_transactions_async(user.to_dict(), months=cfg["months"]))
    
    txns_list = await asyncio.gather(*tasks)
    
    for txns, user in zip(txns_list, personas.iterrows()):
        df = pd.DataFrame(txns)
        df.to_csv(f'{cfg["output_dir"]}/transactions/{user[1]["user_id"]}.csv', index=False)

def main():
    print("🔍 Generating transactions...")
    # generate_transactions()
    asyncio.run(generate_transactions_async())
    print("✅ Transactions generation complete.")


if __name__ == "__main__":
    main()
