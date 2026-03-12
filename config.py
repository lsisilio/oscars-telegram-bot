import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
ADMIN_ID: int = int(os.environ["ADMIN_ID"])
DATA_FILE: str = os.environ.get("DATA_FILE", "data.json")

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
