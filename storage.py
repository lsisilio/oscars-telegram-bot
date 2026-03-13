import json
import os
from config import DATA_FILE, CATEGORIES


def _default() -> dict:
    return {
        "state": "closed",
        "categories": CATEGORIES[:],
        "winners": {},
        "speech_seconds": None,
        "llm_enabled": False,
        "predictions": {},
    }


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        data = _default()
        save_data(data)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)
