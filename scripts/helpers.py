# helpers.py
from openai import OpenAI, AsyncOpenAI
import openai
import yaml
import os
import random
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from scripts.model_pricing import price_per_1k
from scripts.config import load_config
import asyncio

_api_key_loaded = False

# Load YAML config
def load_config():
    with open("scripts/config.yaml", "r") as f:
        return yaml.safe_load(f)

def save_config(cfg_obj):
    with open("scripts/config.yaml", "w") as f:
        yaml.dump(cfg_obj, f)

def mask_key(key):
    if not key or len(key) < 10:
        return "[MASKED]"
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(min=1, max=20))
def call_gpt(messages, model=None, temperature=None, max_tokens=None):

    if not _api_key_loaded:
        api_key = os.getenv("OPENAI_API_KEY") or cfg.get("openai_api_key")
        if api_key:
            _api_key_loaded = True
        else:
            raise RuntimeError("❌ OpenAI API key not found in .env or config.yaml")

    # Set key for OpenAI SDK
    openai.api_key = api_key

    # Log masked key origin
    if os.getenv("OPENAI_API_KEY"):
        print("🔐 Using API key from .env")
    else:
        print("⚠️ Using API key from config.yaml (not recommended)")
    print(f"🔐 OpenAI API key loaded: {mask_key(api_key)}")


    try:
        client = OpenAI()


        response = client.chat.completions.create(
            model=model or cfg["gpt_model"],
            messages=messages,
            temperature=temperature if temperature is not None else cfg["temperature"],
            max_tokens=max_tokens if max_tokens is not None else cfg["max_tokens"],
        )
        
        result = response.choices[0].message.content


        return result.strip()
    except Exception as e:
        print(f"❌ GPT call failed: {e}")
        raise

def extract_json_block(text):
    """Strip triple backticks and return a clean JSON string."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()
    return text.rstrip("```").strip()


@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(min=1, max=20))
def call_gpt(messages, model=None, temperature=None, max_tokens=None):
    global _api_key_loaded
    load_dotenv()
    cfg = load_config()

    api_key = os.getenv("OPENAI_API_KEY") or cfg.get("openai_api_key")
    if not api_key:
        raise RuntimeError("❌ OpenAI API key not found in .env or config.yaml")

    if not _api_key_loaded:
        print("🔐 Using API key from .env" if os.getenv("OPENAI_API_KEY") else "⚠️ Using API key from config.yaml (not recommended)")
        print(f"🔐 OpenAI API key loaded: {mask_key(api_key)}")
        _api_key_loaded = True

    openai.api_key = api_key

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model or cfg["gpt_model"],
            messages=messages,
            temperature=temperature if temperature is not None else cfg["temperature"],
            # max_tokens=max_tokens if max_tokens is not None else cfg["max_tokens"],
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT call failed: {e}")
        raise 


# async version of call_gpt
async def call_gpt_async(messages, model=None, temperature=None, max_tokens=None):
    global _api_key_loaded
    load_dotenv()
    cfg = load_config()

    api_key = os.getenv("OPENAI_API_KEY") or cfg.get("openai_api_key")
    if not api_key:
        raise RuntimeError("❌ OpenAI API key not found in .env or config.yaml")
    if not _api_key_loaded:
        print("🔐 Using API key from .env" if os.getenv("OPENAI_API_KEY") else "⚠️ Using API key from config.yaml (not recommended)")
        print(f"🔐 OpenAI API key loaded: {mask_key(api_key)}")
        _api_key_loaded = True

    openai.api_key = api_key

    try:
        client = AsyncOpenAI()
        response = await client.chat.completions.create(
            model=model or cfg["gpt_model"],
            messages=messages,
            temperature=temperature if temperature is not None else cfg["temperature"],
            # max_tokens=max_tokens if max_tokens is not None else cfg["max_tokens"],
        )

        return response.choices[0].message.content.strip()
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
    max_tokens = int(cfg.get("max_tokens", 4096))
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


