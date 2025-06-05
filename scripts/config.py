import yaml
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

LOG_DIR = "logs"

class QuotedStringDumper(yaml.SafeDumper):
    pass

def quoted_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')

QuotedStringDumper.add_representer(str, quoted_str_representer)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ ERROR: config.yaml not found at {CONFIG_PATH}")
        print("💡 Tip: Copy the default template or create a config.yaml with necessary keys.")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def save_config(config: dict, config_path="scripts/config.yaml"):
    with open(config_path, "w") as f:
        yaml.dump(
            config,
            f,
            Dumper=QuotedStringDumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=100
        )
