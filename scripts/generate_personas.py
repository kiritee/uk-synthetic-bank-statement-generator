import pandas as pd
from scripts.helpers import call_gpt, cfg, generate_uuid
from tqdm import tqdm

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

def main():
    all_rows = []
    for i in tqdm(range(0, cfg["num_users"], cfg["batch_size"])):
        prompt = create_prompt(cfg["batch_size"])
        result = call_gpt(prompt)
        try:
            data = eval(result.strip())
        except Exception:
            print("Parse error:", result)
            continue
        for idx, persona in enumerate(data):
            persona["user_id"] = generate_uuid("user", i + idx)
            all_rows.append(persona)
    df = pd.DataFrame(all_rows)
    df.to_csv(f'{cfg["output_dir"]}/personas.csv', index=False)

if __name__ == "__main__":
    main()
