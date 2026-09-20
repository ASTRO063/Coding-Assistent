# config.py
import json
from pathlib import Path

SETTINGS_FILE = Path("settings.json")

# Ensure this is NOT 'async def'
def load_settings() -> dict:
    default_settings = {
        "allowed_directory": "./"
    }
    if SETTINGS_FILE.exists():
        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                default_settings.update(json.load(f))
        except Exception as e:
            print(f"Warning: Failed to load settings.json ({e})")
    return default_settings

# Synchronously load settings at import time
settings = load_settings()

def get_allowed_directory() -> Path:
    raw_path = settings.get("allowed_directory", "./")
    return Path(raw_path).resolve()