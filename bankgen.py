#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import datetime
from scripts.config import load_config, save_config, LOG_DIR
from scripts.helpers import load_config, estimate_cost_tokens
from scripts import generate_personas, generate_transactions


def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(f"{LOG_DIR}/bankgen.log", "a") as f:
        f.write(f"{timestamp} [{level}] {msg}\n")
    print(f"[{level}] {msg}")

def confirm_cost(stage):
    cfg = load_config()
    tokens, cost = estimate_cost_tokens(stage, cfg)
    print(f"\n💡 Estimated token usage for {stage}: {tokens:,} tokens")
    print(f"💰 Approximate cost: ${cost:.2f} USD using {cfg['gpt_model']}")
    proceed = input("⚠️  Proceed with generation? (y/yes to continue): ").strip().lower()
    if proceed not in {"y", "yes"}:
        print("🚫 Aborted.")
        sys.exit(0)


def run_personas():
    log("Running persona generation...")
    # subprocess.run(["python", "scripts/generate_personas.py"], check=True)
    generate_personas.main()
    log("Persona generation complete.")

def run_transactions():
    log("Running transaction generation...")
    # subprocess.run(["python", "scripts/generate_transactions.py"], check=True)
    generate_transactions.main()
    log("Transaction generation complete.")

def update_config(key, value):
    cfg = load_config()
    if key not in cfg:
        log(f"Invalid config key: {key}", level="ERROR")
        log(f"Valid keys are: {list(cfg.keys())}", level="INFO")
        return
    try:
        cast_value = type(cfg[key])(value)
        cfg[key] = cast_value
        save_config(cfg)
        log(f"✅ Updated config: {key} = {cast_value}")
    except Exception as e:
        log(f"❌ Failed to update config: {e}", level="ERROR")


def handle_generation(args):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts')))
    os.makedirs("logs", exist_ok=True)
    cfg = load_config()

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


def get_parser():
    parser = argparse.ArgumentParser(description="Synthetic Bank Generator CLI")
    parser.add_argument(
        "-r", "--run",
        choices=["personas", "transactions"],
        help="Run a specific stage (personas or transactions). If not provided, runs both."
    )
    parser.add_argument(
        "--validate-config", action="store_true",
        help="Validate config.yaml keys and types"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate what would be executed"
    )
    parser.add_argument(
        "--set-config", nargs='*',
        help="Set config key and value (e.g., num_users 500)"
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.validate_config:
        log("🔍 Validating config...")
        default = {
            "num_users": int,
            "months": int,
            "gpt_model": str,
            "openai_api_key": str,
            "batch_size": int,
            "output_dir": str,
            "max_tokens": int,
            "temperature": float
        }

        errors = []

        cfg = load_config()
        for k, expected_type in default.items():
            if k not in cfg:
                errors.append(f"Missing key: {k}")
            elif not isinstance(cfg[k], expected_type):
                errors.append(f"Invalid type for {k}: expected {expected_type.__name__}, got {type(cfg[k]).__name__}")
        if errors:
            for e in errors:
                log(e, level="ERROR")
            log("❌ Config validation failed.")
        else:
            log("✅ Config is valid.")
        return

    if args.dry_run:
        log("🔧 DRY RUN")
        if args.run:
            log(f"Would run: generate-{args.run}")
        else:
            log("Would run: generate-personas and generate-transactions")
        return

    if args.set_config:
        if len(args.set_config) != 2:
            log("❌ Usage: bankgen set-config <key> <value>", level="ERROR")
        else:
            update_config(*args.set_config)
        return
    
    handle_generation(args)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🔧 Use --help to see available commands.")
    main()
    sys.exit(0)

