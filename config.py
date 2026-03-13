import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
def _parse_admin_ids() -> set[int]:
    raw = os.environ.get("ADMIN_IDS") or os.environ.get("ADMIN_ID", "")
    return {int(x.strip()) for x in raw.split(",") if x.strip()}

ADMIN_IDS: set[int] = _parse_admin_ids()
if not ADMIN_IDS:
    raise ValueError("Set ADMIN_IDS (comma-separated) or ADMIN_ID in your .env")
DATA_FILE: str = os.environ.get("DATA_FILE", "data.json")
ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")

CATEGORIES: list[str] = [
    "Best Picture",
    "Best Director",
    "Best Actor",
    "Best Actress",
    "Best Supporting Actor",
    "Best Supporting Actress",
    "Best Original Screenplay",
    "Best Adapted Screenplay",
    "Best Animated Feature Film",
    "Best International Feature Film",
    "Best Documentary Feature Film",
    "Best Documentary Short Film",
    "Best Live Action Short Film",
    "Best Animated Short Film",
    "Best Cinematography",
    "Best Film Editing",
    "Best Original Score",
    "Best Original Song",
    "Best Sound",
    "Best Production Design",
    "Best Costume Design",
    "Best Makeup and Hairstyling",
    "Best Visual Effects",
]
