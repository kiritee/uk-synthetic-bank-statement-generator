# Ensure root directory is in sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import json
import pandas as pd
from tqdm import tqdm
from scripts.helpers import call_gpt, call_gpt_async, generate_uuid, extract_json_block
from scripts.config import load_config


def create_prompt(n=5):
    return [{
        "role": "system",
        "content": "You are a financial persona generator for synthetic bank data modeling."
    }, {
        "role": "user",
        "content": f"""
Generate {n} ultra-realistic UK gig/temp economy personas with traits:
- name, location, age
- gig_types (e.g., Uber, Tuition, NHS shifts)
- income_style (structured, irregular, hidden)
- payment_channels (BACS, FPS, PayPal, cash)
- behaviors (e.g., overdraft, Klarna, gambling, informal income)
- complexity_level (basic, noisy_legit, ambiguous, high_risk, synthetic_fraud)
- income_regular (yes/no), income_stability (high/medium/low)
- income_true_last_3mo, income_lender_assess_6mo
- risk_level
- persona_description
- income_interpretation

Return as a JSON list of objects.
"""
    }]

def generate_personas():
    all_rows = []
    cfg= load_config()
    if cfg["batch_size"] > cfg["num_users"]:
        print(f"⚠️ Reducing batch_size ({cfg['batch_size']}) to num_users ({cfg['num_users']})")
        cfg["batch_size"] = cfg["num_users"]
    for i in tqdm(range(0, cfg["num_users"], cfg["batch_size"])):
        prompt = create_prompt(cfg["batch_size"])
        raw_result = call_gpt(prompt)
        clean_result = extract_json_block(raw_result)
        try:
            data = json.loads(clean_result)
        except Exception as e:
            print(f"❌ JSON Parse error:\n{clean_result}\nException: {e}")
            continue

        for idx, persona in enumerate(data):
            persona["user_id"] = generate_uuid("user", i + idx)
            all_rows.append(persona)

    df = pd.DataFrame(all_rows)
    output_path = os.path.abspath(cfg["output_dir"])
    os.makedirs(output_path, exist_ok=True)
    df.to_csv(os.path.join(output_path, "personas.csv"), index=False)
    print(f"✅ Personas saved to {os.path.join(output_path, 'personas.csv')}")


async def generate_personas_async():
    cfg= load_config()
    if cfg["batch_size"] > cfg["num_users"]:
        print(f"⚠️ Reducing batch_size ({cfg['batch_size']}) to num_users ({cfg['num_users']})")
        cfg["batch_size"] = cfg["num_users"]
    BATCH_SIZE = cfg["batch_size"]
    OUTPUT_DIR = os.path.abspath(cfg["output_dir"])
    NUM_USERS = cfg["num_users"]
    num_batches = (NUM_USERS + BATCH_SIZE - 1) // BATCH_SIZE
    prompts = [create_prompt(cfg["batch_size"]) for _ in range(num_batches)]
    results = await asyncio.gather(*[call_gpt_async(p) for p in prompts])

    all_rows = []
    for i, result in enumerate(results):
        if result.startswith("❌ Error"):
            print(result)
            continue
        try:
            parsed = json.loads(extract_json_block(result))
            for idx, persona in enumerate(parsed):
                persona["user_id"] = generate_uuid("user", i * BATCH_SIZE + idx)
                all_rows.append(persona)
        except Exception as e:
            print(f"❌ JSON Parse Error: {e}")
            continue

    df = pd.DataFrame(all_rows)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, "personas.csv"), index=False)
    print(f"✅ Personas saved to {os.path.join(OUTPUT_DIR, 'personas.csv')}")


def main():
    print("🔍 Generating personas...")
    # generate_personas()
    asyncio.run(generate_personas_async())
    print("✅ Persona generation complete.")

if __name__ == "__main__":
    main()
