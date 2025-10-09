# generate_transactions.py (refactored to kirkomi-utils: log + llm)

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from .config import load_config
from .helpers import log, get_llm, extract_json_block
# from kirkomi_utils.logging.logger import log
from kirkomi_utils.llm import LLMClient
from promptlib.transactions import full_transaction_1_shot


def create_prompt(user: Dict[str, Any], months: int = 6) -> List[Dict[str, str]]:
    """
    Build an OpenAI-style messages array to generate transactions for a user.
    """
    return [
        {
            "role": "user",
            "content": full_transaction_1_shot.format(
                months=months,
                persona=json.dumps(user, indent=2)
            ),
        }
    ]

@log.log_timed("SIMULATE_TXN")
def simulate_transactions(llm: LLMClient, user: Dict[str, Any], months: int = 6) -> List[Dict[str, Any]]:
    """
    Synchronous: generate transactions for a single user.
    """
    messages = create_prompt(user, months)
    with log.tag_timer("LLM", f"simulate txns for {user.get('user_id','<unknown>')}"):
        try:
            with log.tag_timer("LLM_CALL"):
                res = llm.chat(messages, cache=True)
            text = res.content or ""
            txns = json.loads(extract_json_block(text))
        except Exception as e:
            log.exception(f"JSON parse error while generating txns for {user.get('user_id')}: {e}", tag="TXN")
            return []

    # Ensure user_id is attached (if not already in template response)
    for txn in txns:
        txn["user_id"] = user["user_id"]
    return txns


async def simulate_transactions_async(llm: LLMClient, user: Dict[str, Any], months: int = 6) -> List[Dict[str, Any]]:
    """
    Asynchronous: generate transactions for a single user.
    """
    messages = create_prompt(user, months)
    with log.tag("LLM"):
        try:
            res = await llm.chat_async(messages, cache=True)
            text = res.content or ""
            txns = json.loads(extract_json_block(text))
        except Exception as e:
            log.exception(f"[async] JSON parse error for {user.get('user_id')}: {e}", tag="TXN")
            return []

    for txn in txns:
        txn["user_id"] = user["user_id"]
    return txns


def generate_transactions():
    """
    Synchronous batch: read personas.csv, generate per-user CSVs under output_dir/transactions/.
    """
    cfg = load_config()
    llm = get_llm()

    personas_path = Path(cfg["output_dir"]) / "personas.csv"
    if not personas_path.exists():
        log.error(f"personas.csv not found at {personas_path}", tag="TXN")
        return

    personas = pd.read_csv(personas_path)
    if personas.empty:
        log.error("❌ personas.csv is empty. Nothing to process.", tag="TXN")
        return

    tx_dir = Path(cfg["output_dir"]) / "transactions"
    tx_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Generating transactions (sync) for {len(personas)} users...", tag="TXN")
    with log.tag("TXN_GEN_SYNC"):
        for _, user_row in tqdm(personas.iterrows(), total=personas.shape[0]):
            user = user_row.to_dict()
            txns = simulate_transactions(llm, user, months=cfg["months"])
            df = pd.DataFrame(txns)
            out_path = tx_dir / f"{user['user_id']}.csv"
            df.to_csv(out_path, index=False)

    log.info(f"✅ Transactions written to {tx_dir}", tag="TXN")

@log.log_timed("TXN_GEN_ASYNC")
async def generate_transactions_async():
    """
    Asynchronous batch: read personas.csv, generate per-user CSVs concurrently.
    """
    cfg = load_config()
    llm = get_llm()

    log.debug("Config and LLM client loaded.", tag="TXN")

    personas_path = Path(cfg["output_dir"]) / "personas.csv"
    if not personas_path.exists():
        log.error(f"❌ personas.csv not found at {personas_path}", tag="TXN")
        return

    personas = pd.read_csv(personas_path)
    if personas.empty:
        log.error("❌ personas.csv is empty. Nothing to process.", tag="TXN")
        return

    log.debug(f"Loaded {len(personas)} personas.", tag="TXN")

    tx_dir = Path(cfg["output_dir"]) / "transactions"
    tx_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Generating transactions (async) for {len(personas)} users...", tag="TXN")

    # Build all tasks
    tasks = []
    users: List[Dict[str, Any]] = []
    for _, user_row in personas.iterrows():
        user = user_row.to_dict()
        users.append(user)
        tasks.append(simulate_transactions_async(llm, user, months=cfg["months"]))

    # Dispatch and show progress
    with log.tag("TXN_GEN_ASYNC"):
    
        log.debug("Dispatching async LLM calls...", tag="TXN")
    
        results = await tqdm_asyncio.gather(*tasks, desc="Generating Tx Batches", total=len(tasks))

    log.debug("All async LLM calls complete.", tag="TXN")

    # Write each user's CSV
    for user, txns in zip(users, results):
        df = pd.DataFrame(txns)
        out_path = tx_dir / f"{user['user_id']}.csv"
        df.to_csv(out_path, index=False)

    log.info(f"✅ Transactions written to {tx_dir}", tag="TXN")


def main():
    log.info("🔍 Generating transactions...", tag="APP")
    generate_transactions()  # sync path if preferred
    # asyncio.run(generate_transactions_async())  # async path
    log.info("✅ Transactions generation complete.", tag="APP")


if __name__ == "__main__":
    main()
