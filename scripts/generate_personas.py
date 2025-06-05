# Ensure root directory is in sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Ensure root directory is in sys.path

import asyncio
import json
import pandas as pd
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from scripts.helpers import call_gpt, call_gpt_async, generate_uuid
from scripts.config import load_config


def create_prompt(n=5):
    """Create a prompt for generating financial personas."""
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
    """Generate financial personas and save to CSV."""

    # Load configuration
    all_rows = []
    cfg= load_config()

    NUM_USERS = cfg["num_users"]
    if not isinstance(NUM_USERS, int) or NUM_USERS <= 0:
        print("❌ num_users must be a positive integer. Please check your config.")
        return

    BATCH_SIZE = cfg["batch_size"]
    if not isinstance(BATCH_SIZE, int) or BATCH_SIZE <= 0:
        print("❌ batch_size must be a positive integer. Please check your config.")
        return

    # Check and adjust batch size if necessary
    if BATCH_SIZE > NUM_USERS:
        print(f"⚠️ Reducing batch_size ({BATCH_SIZE}) to num_users ({NUM_USERS})")
        BATCH_SIZE = NUM_USERS

    # Generate personas in batches
    print(f"Generating {NUM_USERS} personas in batches of {BATCH_SIZE}...")

    for i in tqdm(range(0, NUM_USERS, BATCH_SIZE)): # tqdm for progress bar
        prompt = create_prompt(BATCH_SIZE)
        result = call_gpt(prompt)
        try:
            # Extract JSON block from the response
            data = json.loads(result) 
        except Exception as e:
            print(f"❌ JSON Parse error:\n{result}\nException: {e}")
            continue

        # Generate user IDs for each personaand append to all_rows
        for idx, persona in enumerate(data):
            persona["user_id"] = generate_uuid("user", i + idx)
            all_rows.append(persona)

    # Create DataFrame for all rowas and save to CSV
    if not all_rows:
        print("❌ No personas generated. Please check your configuration and try again.")
        return
    print(f"✅ Generated {len(all_rows)} personas.")
    print("Saving personas to CSV...")
    df = pd.DataFrame(all_rows)
    output_path = os.path.abspath(cfg["output_dir"])
    os.makedirs(output_path, exist_ok=True)
    df.to_csv(os.path.join(output_path, "personas.csv"), index=False)
    print(f"✅ Personas saved to {os.path.join(output_path, 'personas.csv')}")



async def generate_personas_async():
    """Asynchronously generate financial personas and save to CSV."""

    print("🔍 Generating personas asynchronously...")

    # Load configuration and prepare for async generation

    # Load configuration
    all_rows = []
    cfg= load_config()

    NUM_USERS = cfg["num_users"]
    if not isinstance(NUM_USERS, int) or NUM_USERS <= 0:
        print("❌ num_users must be a positive integer. Please check your config.")
        return

    BATCH_SIZE = cfg["batch_size"]
    if not isinstance(BATCH_SIZE, int) or BATCH_SIZE <= 0:
        print("❌ batch_size must be a positive integer. Please check your config.")
        return

    # Check and adjust batch size if necessary
    if BATCH_SIZE > NUM_USERS:
        print(f"⚠️ Reducing batch_size ({BATCH_SIZE}) to num_users ({NUM_USERS})")
        BATCH_SIZE = NUM_USERS

    # Generate personas in batches
    print(f"Generating {NUM_USERS} personas in batches of {BATCH_SIZE}...")

    num_batches = (NUM_USERS + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Total batches to process: {num_batches}")

    # Create prompts for each batch
    prompts = [create_prompt(BATCH_SIZE) for _ in range(num_batches)]

    # Generate personas asynchronously
    print("Calling GPT asynchronously...")

    # Use tqdm_asyncio for progress bar with async calls
    results = await tqdm_asyncio.gather(*[call_gpt_async(p) for p in prompts], desc="Generating Persona Batch", total=num_batches)

    print("Processing results...")
    all_rows = []
    for i, result in enumerate(results):
        # Check for errors in the result
        if result.startswith("❌ Error"):
            print(result)
            continue
        try:
            parsed = json.loads(result)
            for idx, persona in enumerate(parsed):
                # Generate user IDs for each persona
                if "user_id" in persona:
                    print(f"⚠️ Warning: 'user_id' already exists in persona {i * BATCH_SIZE + idx}. Overwriting.")
                if "user_id" not in persona:
                    print(f"🔍 Generating user_id for persona {i * BATCH_SIZE + idx}")
                persona["user_id"] = generate_uuid("user", i * BATCH_SIZE + idx)
                all_rows.append(persona)
        except json.JSONDecodeError as json_err:
            print(f"❌ JSON Decode Error: {json_err}")
            continue
        except Exception as e:
            print(f"❌ JSON Parse Error: {e}")
            continue

    if not all_rows:
        print("❌ No personas generated. Please check your configuration and try again.")
        return
    print(f"✅ Generated {len(all_rows)} personas.")
    print("Saving personas to CSV...")
    df = pd.DataFrame(all_rows)

    OUTPUT_DIR = os.path.abspath(cfg["output_dir"])
    if not os.path.exists(OUTPUT_DIR):
        print(f"⚠️ Output directory {OUTPUT_DIR} does not exist. Creating it.")
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
