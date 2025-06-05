import yaml
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ ERROR: config.yaml not found at {CONFIG_PATH}")
        print("💡 Tip: Copy the default template or create a config.yaml with necessary keys.")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def save_config(cfg_obj):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg_obj, f)
