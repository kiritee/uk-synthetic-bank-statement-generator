# helpers.py
from openai import OpenAI, AsyncOpenAI
import openai
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from scripts.model_pricing import price_per_1k
from scripts.config import load_config, save_config
import asyncio

# _api_key_loaded is used to ensure the API key is loaded only once across multiple calls to call_gpt or call_gpt_async
_api_key_loaded = False
openai.api_key = None  # Initialize the OpenAI API key to None

# Mask the OpenAI API key for logging purposes e.g. "sk-1234...5678" -> "sk-****5678"
def mask_key(key):
    if not key or len(key) < 10:
        return "[MASKED]"
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


# function to set the OpenAI API key from environment variables or config file ensuring it is loaded only once
def set_openai_api_key():
    """Set the OpenAI API key from environment variables or config file."""

    # Track if the API key has already been loaded
    global _api_key_loaded 


    # Only load the API key if it hasn't been loaded yet
    if not _api_key_loaded: 
        # Load environment variables from .env file and configuration from config.yaml
        load_dotenv() 
        cfg = load_config() 
        
        global openai
        # Get the API key from environment variables or config file 
        # If the API key is not found, raise an error
        # If the API key is found, set it in the OpenAI client
        # and mark it as loaded to avoid reloading in future calls
        api_key = os.getenv("OPENAI_API_KEY") or cfg.get("openai_api_key") 
        if not api_key:
            raise RuntimeError("❌ OpenAI API key not found in .env or config.yaml")
        openai.api_key = api_key
        _api_key_loaded = True
        print("🔐 OpenAI API key loaded successfully."
              f" Key: {mask_key(api_key)}")
    else:
        print("🔐 OpenAI API key already loaded, skipping reloading.")
    return openai.api_key


# clean up the JSON block by removing triple backticks and any leading/trailing whitespace
def extract_json_block(text):
    """Strip triple backticks and return a clean JSON string."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()
    return text.rstrip("```").strip()


# function to call GPT synchronously with retry logic
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(min=1, max=20)) # retry up to 5 times with exponential backoff
def call_gpt(messages, model=None, temperature=None, max_tokens=None):
    """Call the GPT model with retry logic."""
    cfg = load_config()
    set_openai_api_key()  # Ensure API key is set before making the call
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model or cfg["gpt_model"],
            messages=messages,
            temperature=temperature if temperature is not None else cfg["temperature"],
            # max_tokens=max_tokens if max_tokens is not None else cfg["max_tokens"],
        )
        result = response.choices[0].message.content.strip()
        return extract_json_block(result)  # Clean up the JSON block before returning
    except Exception as e:
        print(f"❌ GPT call failed: {e}")
        raise


# function to call GPT asynchronously with retry logic
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(min=1, max=20))  # retry up to 5 times with exponential backoff
async def call_gpt_async(messages, model=None, temperature=None, max_tokens=None):
    """Asynchronously call the GPT model with retry logic."""
    cfg = load_config()
    set_openai_api_key()  # Ensure API key is set before making the call
    try:
        client = AsyncOpenAI()
        response = await client.chat.completions.create(
            model=model or cfg["gpt_model"],
            messages=messages,
            temperature=temperature if temperature is not None else cfg["temperature"],
            # max_tokens=max_tokens if max_tokens is not None else cfg["max_tokens"],
        )

        result = response.choices[0].message.content.strip()
        return extract_json_block(result)  # Clean up the JSON block before returning
    except Exception as e:
        print(f"❌ GPT call failed: {e}")
        raise


# function to create unique UUIDs for users or transactions
def generate_uuid(prefix, i):
    """Generate a unique UUID with a specified prefix and index."""
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


