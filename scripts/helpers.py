import openai
import yaml
import os
import random
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from scripts.model_pricing import price_per_1k


# Load environment variables
load_dotenv()

# Load YAML config
def load_config():
    with open("scripts/config.yaml", "r") as f:
        return yaml.safe_load(f)

def save_config(cfg_obj):
    with open("scripts/config.yaml", "w") as f:
        yaml.dump(cfg_obj, f)

cfg = load_config()

# API key from .env OR config fallback
openai.api_key = os.getenv("OPENAI_API_KEY") or cfg.get("openai_api_key")

def mask_key(key):
    if not key or len(key) < 10:
        return "[MASKED]"
    return key[:4] + "*" * (len(key) - 8) + key[-4:]

if os.getenv("OPENAI_API_KEY"):
    print("🔐 Using API key from .env")
else:
    print("⚠️ Using API key from config.yaml (not recommended)")

masked_key = mask_key(openai.api_key)
print(f"🔐 OpenAI API key loaded: {masked_key}")

@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(min=1, max=20))
def call_gpt(messages, model=None, temperature=None, max_tokens=None):
    try:
        response = openai.ChatCompletion.create(
            model=model or cfg["gpt_model"],
            messages=messages,
            temperature=temperature if temperature is not None else cfg["temperature"],
            max_tokens=max_tokens if max_tokens is not None else cfg["max_tokens"],
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ GPT call failed: {e}")
        raise



def generate_uuid(prefix, i):
    return f"{prefix}_{str(i).zfill(5)}"


def estimate_cost_tokens(stage: str, cfg) -> tuple:
    """
    Estimate total tokens and approximate cost in USD based on usage.
    """
    gpt_model = cfg.get("gpt_model", "gpt-4")
    max_tokens = int(cfg.get("max_tokens", 1024))
    num_users = int(cfg["num_users"])
    months = int(cfg["months"])

    if stage == "personas":
        calls = (num_users / cfg["batch_size"])
        tokens = calls * max_tokens
    elif stage == "transactions":
        calls = num_users * months
        tokens = calls * max_tokens
    else:
        raise ValueError("Invalid stage for estimation")

    model_price = price_per_1k.get(gpt_model, price_per_1k["gpt-4"])
    cost_usd = (tokens / 1000) * model_price
    return int(tokens), round(cost_usd, 2)


