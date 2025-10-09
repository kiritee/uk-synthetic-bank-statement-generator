#!/usr/bin/env python3
# scripts/bankgen.py  (refactored to kirkomi-utils logger + relative imports)

import argparse
import sys
from typing import Dict, Any

# Project-local modules (relative imports since this file is inside scripts/)
from scripts.config import load_config, save_config
from scripts.helpers import estimate_cost_tokens
from scripts import generate_personas, generate_transactions
import logging

# Shared logger from kirkomi_utils
from kirkomi_utils.logging.logger import log


def confirm_cost(stage: str) -> None:
    """
    Show a stage-specific cost estimate (project logic) and confirm with the user.
    """
    cfg = load_config()
    tokens, cost = estimate_cost_tokens(stage, cfg)

    log.info(f"Estimated token usage for {stage}: {tokens:,} tokens", tag="COST")
    log.info(f"Approximate cost: ${cost:.2f} USD using model={cfg.get('model')}", tag="COST")

    proceed = input("⚠️  Proceed with generation? (y/yes to continue): ").strip().lower()
    if proceed not in {"y", "yes"}:
        log.warning("Aborted by user.", tag="COST")
        sys.exit(0)


def run_personas() -> None:
    log.info("Running persona generation...", tag="RUN")
    generate_personas.main()
    log.info("Persona generation complete.", tag="RUN")


def run_transactions() -> None:
    log.info("Running transaction generation...", tag="RUN")
    generate_transactions.main()
    log.info("Transaction generation complete.", tag="RUN")


def update_config(key: str, value: str) -> None:
    """
    Update a single config key with type preserved from the existing config.
    """
    cfg: Dict[str, Any] = load_config()
    if key not in cfg:
        log.error(f"Invalid config key: {key}", tag="CFG")
        log.info(f"Valid keys are: {list(cfg.keys())}", tag="CFG")
        return

    try:
        cast_value = type(cfg[key])(value)
    except Exception:
        # If casting fails (e.g., bools), try a small helper
        lowered = value.strip().lower()
        if isinstance(cfg[key], bool):
            if lowered in {"true", "1", "yes", "y"}:
                cast_value = True
            elif lowered in {"false", "0", "no", "n"}:
                cast_value = False
            else:
                log.error(f"Failed to parse boolean value for {key}: {value!r}", tag="CFG")
                return
        else:
            log.error(f"Failed to cast value for {key}: {value!r} to {type(cfg[key]).__name__}", tag="CFG")
            return

    try:
        cfg[key] = cast_value
        save_config(cfg)
        log.info(f"✅ Updated config: {key} = {cast_value!r}", tag="CFG")
    except Exception as e:
        log.exception(f"Failed to update config: {e}", tag="CFG")


def handle_generation(args) -> None:
    """
    Orchestrate which generation stages to run based on CLI args.
    """
    log.debug("Starting generation pipeline")
    cfg = load_config()  # noqa: F841 (kept to ensure config load errors surface early)
    log.debug(f"Loaded config")

    if args.run == "personas":
        confirm_cost("personas")
        run_personas()
    elif args.run == "transactions":
        confirm_cost("transactions")
        run_transactions()
    else:
        confirm_cost("personas")
        run_personas()
        confirm_cost("transactions")
        run_transactions()


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthetic Bank Generator CLI")
    parser.add_argument(
        "-r", "--run",
        choices=["personas", "transactions"],
        help="Run a specific stage (personas or transactions). If not provided, runs both.",
    )
    parser.add_argument(
        "--validate-config", action="store_true",
        help="Validate config.yaml keys and types",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate what would be executed",
    )
    parser.add_argument(
        "--set-config", nargs=2, metavar=("KEY", "VALUE"),
        help="Set config key and value (e.g., num_users 500)",
    )
    return parser


def _validate_config() -> None:
    """
    Validate expected keys/types in the project config.
    Note: DO NOT validate API keys here — LLM keys live in env/.env and are managed by kirkomi_utils.llm.
    """
    required_schema = {
        "num_users": int,
        "months": int,
        "batch_size": int,
        "tx_batch_size": int,
        "output_dir": str,
    }

    errors = []
    cfg = load_config()
    for k, expected_type in required_schema.items():
        if k not in cfg:
            errors.append(f"Missing key: {k}")
        elif not isinstance(cfg[k], expected_type):
            errors.append(f"Invalid type for {k}: expected {expected_type.__name__}, got {type(cfg[k]).__name__}")

    if errors:
        for e in errors:
            log.error(e, tag="CFG")
        log.error("❌ Config validation failed.", tag="CFG")
    else:
        log.info("✅ Config is valid.", tag="CFG")


def main() -> None:
    parser = get_parser()
    log.debug("Parsing CLI args")

    args = parser.parse_args()
    log.debug(f"Parsed args: {args}", tag="CLI")

    if args.validate_config:
        log.info("🔍 Validating config...", tag="CFG")
        _validate_config()
        return

    if args.dry_run:
        log.info("🔧 DRY RUN", tag="DRYRUN")
        if args.run:
            log.info(f"Would run: generate-{args.run}", tag="DRYRUN")
        else:
            log.info("Would run: generate-personas and generate-transactions", tag="DRYRUN")
        return

    if args.set_config:
        key, value = args.set_config
        update_config(key, value)
        return

    handle_generation(args)


if __name__ == "__main__":
    log.set_levels(console_level=logging.DEBUG)
    log.info("🔧 BankGen CLI starting...", tag="APP")
    if len(sys.argv) == 1:
        print("🔧 Use --help to see available commands.")
    log.debug("Starting main")
    main()
    sys.exit(0)
