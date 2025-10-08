# generate_personas.py

import os
import json
import asyncio
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
# from kirkomi_utils.logging.logger import log
from .config import load_config
from .helpers import log, get_llm, generate_uuid, extract_json_block
from promptlib.personas import full_persona_1_shot


def create_prompt(n: int = 5):
    """
    Build an OpenAI-style messages array for generating `n` personas.
    """
    return [
        {
            "role": "user",
            "content": full_persona_1_shot.format(n=n),
        }
    ]


def _validate_positive_int(name: str, value):
    if not isinstance(value, int) or value <= 0:
        log.error(f"{name} must be a positive integer. Got: {value!r}")
        return False
    return True


def generate_personas():
    """
    Synchronous persona generation.
    Uses LLMClient.chat for each batch, writes a single personas.csv at the end.
    """
    cfg = load_config()
    llm = get_llm()

    num_users = cfg["num_users"]
    batch_size = cfg["batch_size"]

    if not (_validate_positive_int("num_users", num_users) and _validate_positive_int("batch_size", batch_size)):
        return

    if batch_size > num_users:
        log.warning(f"Reducing batch_size ({batch_size}) to num_users ({num_users}).")
        batch_size = num_users

    log.info(f"Generating {num_users} personas in batches of {batch_size}...", tag="PERSONA")
    all_rows = []

    with log.tag("PERSONA_GEN"):
        for i in tqdm(range(0, num_users, batch_size)):
            n = min(batch_size, num_users - i)
            messages = create_prompt(n)

            with log.tag_timer("LLM", f"batch {i // batch_size + 1}"):
                try:
                    res = llm.chat(messages, cache=True)
                    text = res.content or ""
                    # Be tolerant of fenced JSON:
                    data = json.loads(extract_json_block(text))
                except Exception as e:
                    log.exception(f"JSON parse error for batch starting at index {i}: {e}", tag="PERSONA")
                    continue

            for idx, persona in enumerate(data):
                persona["user_id"] = generate_uuid("user", i + idx)
                all_rows.append(persona)

    if not all_rows:
        log.error("No personas generated. Check your configuration and try again.", tag="PERSONA")
        return

    df = pd.DataFrame(all_rows)
    output_dir = Path(cfg.get("output_dir", "data")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "personas.csv"

    df.to_csv(out_path, index=False)
    log.info(f"✅ Generated {len(all_rows)} personas. Saved to {out_path}", tag="PERSONA")


async def generate_personas_async():
    """
    Asynchronous persona generation.
    Batches prompts + fires them concurrently with llm.chat_async,
    then writes personas.csv.
    """
    cfg = load_config()
    llm = get_llm()

    num_users = cfg["num_users"]
    batch_size = cfg["batch_size"]

    if not (_validate_positive_int("num_users", num_users) and _validate_positive_int("batch_size", batch_size)):
        return

    if batch_size > num_users:
        log.warning(f"Reducing batch_size ({batch_size}) to num_users ({num_users}).")
        batch_size = num_users

    num_batches = (num_users + batch_size - 1) // batch_size
    log.info(f"Generating {num_users} personas asynchronously in {num_batches} batches of {batch_size}...", tag="PERSONA")

    prompts = []
    batch_sizes = []
    for start in range(0, num_users, batch_size):
        n = min(batch_size, num_users - start)
        prompts.append(create_prompt(n))
        batch_sizes.append((start, n))

    with log.tag("PERSONA_GEN"):
        # Launch async calls
        log.info("Dispatching async LLM calls...", tag="LLM")
        tasks = [llm.chat_async(p, cache=True) for p in prompts]
        results = await tqdm_asyncio.gather(*tasks, desc="Generating Persona Batches", total=num_batches)

        # Process results
        all_rows = []
        for (start, n), res in zip(batch_sizes, results):
            try:
                text = res.content or ""
                parsed = json.loads(extract_json_block(text))
            except Exception as e:
                log.exception(f"JSON parse error for batch starting at {start}: {e}", tag="PERSONA")
                continue

            for j, persona in enumerate(parsed):
                persona["user_id"] = generate_uuid("user", start + j)
                all_rows.append(persona)

    if not all_rows:
        log.error("No personas generated. Check your configuration and try again.", tag="PERSONA")
        return

    df = pd.DataFrame(all_rows)
    output_dir = Path(cfg.get("output_dir", "data")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "personas.csv"

    df.to_csv(out_path, index=False)
    log.info(f"✅ Generated {len(all_rows)} personas. Saved to {out_path}", tag="PERSONA")


def main():
    log.info("Starting persona generation...", tag="APP")
    # Choose sync or async path:
    # generate_personas()
    asyncio.run(generate_personas_async())
    log.info("Persona generation complete.", tag="APP")


if __name__ == "__main__":
    main()
