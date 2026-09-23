import os
from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_config():
    config_path = os.getenv(
        "APP_CONFIG",
        "config/config.yaml",
    )

    config_path = ROOT_DIR / config_path

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)