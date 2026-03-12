import re
import difflib


def normalize(s: str) -> str:
    """Lowercase and collapse all whitespace."""
    return " ".join(s.lower().split())


def _match_category(raw: str, categories: list[str]) -> str | None:
    """Return canonical category name or None."""
    norm_raw = normalize(raw)

    # Exact match
    for cat in categories:
        if normalize(cat) == norm_raw:
            return cat

    # Fuzzy match
    best_score = 0.0
    best_cat = None
    for cat in categories:
        score = difflib.SequenceMatcher(None, norm_raw, normalize(cat)).ratio()
        if score > best_score:
            best_score = score
            best_cat = cat

    if best_score >= 0.6:
        return best_cat
    return None


_SPEECH_RE = re.compile(r"^speech", re.IGNORECASE)


def parse_predictions(
    text: str, categories: list[str]
) -> tuple[dict, int | None, list[str]]:
    """
    Parse free-form prediction text.

    Returns:
        matched       - dict of {canonical_category: nominee_string}
        speech_guess  - int seconds if provided, else None
        unrecognized  - list of raw lines that couldn't be matched
    """
    matched: dict = {}
    speech_guess: int | None = None
    unrecognized: list[str] = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if ":" not in line:
            unrecognized.append(line)
            continue

        raw_cat, _, raw_val = line.partition(":")
        raw_cat = raw_cat.strip()
        raw_val = raw_val.strip()

        if not raw_val:
            unrecognized.append(line)
            continue

        # Speech duration tiebreaker
        if _SPEECH_RE.match(raw_cat):
            try:
                speech_guess = int(raw_val)
            except ValueError:
                unrecognized.append(line)
            continue

        canonical = _match_category(raw_cat, categories)
        if canonical is None:
            unrecognized.append(line)
        else:
            matched[canonical] = raw_val  # last occurrence wins

    return matched, speech_guess, unrecognized
