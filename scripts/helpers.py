# helpers.py
"""
Refactored project helpers.

This module provides a thin, backward-compatible shim over the new kirkomi_utils
packages so the rest of your project can keep calling the same functions while
internally using the provider-agnostic LLM facade and SmartLogger.


Environment:
    OPENAI_API_KEY=sk-...           # required for OpenAI provider
    LLM_PROVIDER=openai             # default provider (extensible)
    LLM_MODEL=gpt-4o                # optional, can be overridden from app config
    LLM_TEMPERATURE=0.2             # optional, can be overridden from app config
    LLM_MAX_TOKENS=4096             # optional

Usage (unchanged from the rest of your code’s perspective):
    from helpers import call_gpt, call_gpt_async

    result = call_gpt(messages, model="gpt-4o", temperature=0.2)
    # or
    result = await call_gpt_async(messages)

If you want direct access to the facade:
    from helpers import get_llm
    llm = get_llm()                        # returns a cached singleton LLMClient
    res = llm.chat(messages, cache=True)
    print(res.content, res.usage)

"""

from __future__ import annotations

from typing import Optional, Sequence, Dict, Any
import json

# --- kirkomi_utils (new) ---
from kirkomi_utils.llm import LLMClient, estimate_prompt_cost_by_tokens
from kirkomi_utils.logging.logger import log

# Keep your existing project config/pricing imports.
# We try both locations for load_config for flexibility.
try:
    from scripts.config import load_config  # old path
except Exception:  # pragma: no cover
    from config import load_config          # new path at project root

try:
    from scripts.model_pricing import price_per_1k
except Exception:  # pragma: no cover
    price_per_1k = {
        # sensible fallbacks if the pricing table is unavailable
        "gpt-4": 0.03,         # example per 1K tokens (edit to match your model_pricing)
        "gpt-4o": 0.005,
        "gpt-4o-mini": 0.0015,
    }

# Optional dependency (token counting). Keep same semantics as before.
try:  # pragma: no cover
    import tiktoken
except Exception:  # pragma: no cover
    tiktoken = None


# -----------------------------------------------------------------------------
# LLM facade: create a single lazy, cached client that reads app config overrides
# -----------------------------------------------------------------------------

# Tune this TTL to cache identical prompts for a while (saves cost/time in dev/batch runs)
_DEFAULT_CACHE_TTL_SECONDS = 3600

# Internal singleton
__LLM_SINGLETON: Optional[LLMClient] = None


def _build_llm_from_app_config() -> LLMClient:
    """
    Construct an LLMClient using overrides from the app's own config
    (model/temperature/max_tokens), while credentials/provider come from env/.env.

    Returns:
        LLMClient: ready-to-use client with retries + optional in-memory caching.
    """
    cfg = load_config()  # your app’s domain config (num_users, months, gpt_model, etc.)
    overrides = {
        "model": cfg.get("gpt_model"),
        "temperature": cfg.get("temperature"),
        "max_tokens": cfg.get("max_tokens"),
        # You can add "provider" here if you want to select a non-default provider from app config:
        # "provider": cfg.get("llm_provider", "openai"),
    }
    # Create facade; all provider keys (e.g., OPENAI_API_KEY) are read from env/.env.
    llm = LLMClient(cfg_overrides=overrides, log=log, cache_ttl=_DEFAULT_CACHE_TTL_SECONDS)
    return llm


def get_llm(force_new: bool = False) -> LLMClient:
    """
    Return the process-wide LLMClient singleton. Create it lazily on first use.

    Args:
        force_new: if True, rebuild the client (e.g., after changing env/config).

    Returns:
        LLMClient
    """
    global __LLM_SINGLETON
    if force_new or __LLM_SINGLETON is None:
        __LLM_SINGLETON = _build_llm_from_app_config()
    return __LLM_SINGLETON


# -----------------------------------------------------------------------------
# Backward-compatible GPT helpers (now delegate to the facade)
# -----------------------------------------------------------------------------

def call_gpt(
    messages: Sequence[Dict[str, str]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    clean_json_block: bool = True,
) -> str:
    """
    Back-compat synchronous GPT call that now routes through LLMClient.

    Args:
        messages: OpenAI-style list of {"role": "...", "content": "..."}.
        model: optional model override for this call.
        temperature: optional temperature override for this call.
        max_tokens: optional max_tokens for this call.
        clean_json_block: if True, strip markdown fences (```json ... ```) before returning.

    Returns:
        str: model output (possibly JSON text). If clean_json_block=True, fences are stripped.
    """
    # Optional: time the block + tag logs for context
    with log.tag_timer("LLM", "call_gpt"):
        res = get_llm().chat(
            messages,
            cache=True,  # identical prompts will be cached for _DEFAULT_CACHE_TTL_SECONDS
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = res.content or ""
        return extract_json_block(text) if clean_json_block else text


async def call_gpt_async(
    messages: Sequence[Dict[str, str]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    clean_json_block: bool = True,
) -> str:
    """
    Back-compat asynchronous GPT call that now routes through LLMClient.

    Args:
        messages: OpenAI-style list of {"role": "...", "content": "..."}.
        model: optional model override for this call.
        temperature: optional temperature override for this call.
        max_tokens: optional max_tokens for this call.
        clean_json_block: if True, strip markdown fences before returning.

    Returns:
        str: model output.
    """
    with log.tag("LLM"):
        res = await get_llm().chat_async(
            messages,
            cache=True,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = res.content or ""
        return extract_json_block(text) if clean_json_block else text


# -----------------------------------------------------------------------------
# Other functions
# -----------------------------------------------------------------------------

def generate_uuid(prefix: str, i: int) -> str:
    """
    Generate a simple, human-readable UUID by prefix + zero-padded index.

    Example:
        >>> generate_uuid("user", 7)
        'user_00007'
    """
    return f"{prefix}_{str(i).zfill(5)}"


def estimate_cost_tokens(stage: str, cfg: Dict[str, Any]) -> tuple[int, float]:
    """
    Estimate total tokens and approximate cost based on your app's configuration.

    Args:
        stage: one of {"personas", "transactions"}
        cfg:   app config dict (expects: gpt_model, max_tokens, num_users, months, batch_size)

    Returns:
        (tokens: int, cost_usd: float)

    Notes:
        - Uses scripts.model_pricing.price_per_1k if available; otherwise a small fallback table.
        - This is a *rough* estimate using your max_tokens as the per-call token size.
    """
    gpt_model = cfg.get("gpt_model", "gpt-4")
    max_tokens = int(cfg.get("max_tokens", 4096))
    num_users = int(cfg["num_users"])
    months = int(cfg["months"])

    if stage == "personas":
        calls = (num_users / float(cfg["batch_size"]))
        tokens = int(calls * max_tokens)
    elif stage == "transactions":
        calls = int(num_users) * int(months)
        tokens = int(calls * max_tokens)
    else:
        raise ValueError("Invalid stage for estimation")

    # Use your project’s pricing table:
    cost = estimate_prompt_cost_by_tokens(tokens, gpt_model, price_per_1k)
    return tokens, cost


def extract_json_block(text: str) -> str:
    """
    Strip Markdown code fences around JSON content (if present).

    Accepts:
        ```json
        { ... }
        ```
    Returns:
        The inner text without fences and whitespace.
    """
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()
    return text.rstrip("```").strip()