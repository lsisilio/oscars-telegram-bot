import json
import anthropic

_client: anthropic.Anthropic | None = None


def get_client(api_key: str) -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def normalize_predictions(
    matched: dict[str, str],
    nominees: dict[str, list[str]],
    api_key: str,
) -> tuple[dict[str, str], dict[str, str]]:
    """
    Normalize user nominee picks against the official nominees list using Claude.

    Returns:
        normalized  - dict with corrected values
        changes     - dict of {category: original_value} for picks that were changed
    On any error, returns the original matched dict and an empty changes dict.
    """
    if not matched:
        return matched, {}

    entries = []
    for cat, raw in matched.items():
        nominee_list = nominees.get(cat, [])
        if nominee_list:
            formatted = ", ".join(f'"{n}"' for n in nominee_list)
            entries.append(f'- {cat}: user said "{raw}" | nominees: [{formatted}]')
        else:
            entries.append(f'- {cat}: user said "{raw}" | nominees: [any — return unchanged]')

    prompt = (
        "You are normalizing Oscar prediction inputs.\n"
        "For each entry, return the official nominee name that best matches the user's input.\n"
        "Rules:\n"
        "- Correct spelling, accents, and partial names to the exact official nominee.\n"
        "- If nominees list is [any — return unchanged], return the input unchanged.\n"
        "- If there is no good match, return the input unchanged.\n"
        "- Return ONLY a valid JSON object: {\"Category\": \"Normalized Name\", ...}\n\n"
        + "\n".join(entries)
    )

    try:
        client = get_client(api_key)
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        normalized_raw = json.loads(text)

        normalized = {cat: normalized_raw.get(cat, raw) for cat, raw in matched.items()}
        changes = {cat: raw for cat, raw in matched.items() if normalized[cat] != raw}
        return normalized, changes

    except Exception:
        return matched, {}
