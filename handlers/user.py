from telegram import Update
from telegram.ext import ContextTypes

from parser import parse_predictions, normalize
from storage import load_data, save_data

_INSTRUCTIONS = (
    "Send your predictions using this format (one per line):\n\n"
    "<code>Best Picture: Conclave\n"
    "Best Director: Brady Corbet\n"
    "Best Actor: Adrien Brody\n"
    "Speech Duration: 127</code>\n\n"
    "• You can submit partial predictions and update them anytime while submissions are open.\n"
    "• <b>Speech Duration</b> (seconds) is a tiebreaker — include it!\n"
    "• Use /categories to see all 23 categories."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        "🎬 <b>Oscar 2026 Predictions Bot</b>\n\n"
        "Welcome! Submit your picks for the 2026 Academy Awards and compete with friends.\n\n"
        + _INSTRUCTIONS
    )


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    cats = data["categories"]
    lines = "\n".join(f"{i+1}. {c}" for i, c in enumerate(cats))
    await update.message.reply_text(
        f"📋 Oscar 2026 Categories ({len(cats)}):\n\n{lines}\n\n"
        "Bonus tiebreaker: Speech Duration (seconds)\n"
        "Format: Speech Duration: 127"
    )


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()

    if data["state"] != "open":
        await update.message.reply_text("❌ Submissions are currently closed.")
        return

    # Get text after /predict command
    text = update.message.text or ""
    # Strip the /predict (or /predict@botname) prefix
    parts = text.split(None, 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_html(_INSTRUCTIONS)
        return

    prediction_text = parts[1]
    matched, speech_guess, unrecognized = parse_predictions(prediction_text, data["categories"])

    if not matched and speech_guess is None:
        msg = "⚠️ Couldn't parse any predictions."
        if unrecognized:
            msg += "\n\nUnrecognized lines:\n" + "\n".join(f"• {l}" for l in unrecognized)
        msg += f"\n\n{_INSTRUCTIONS}"
        await update.message.reply_html(msg)
        return

    user = update.effective_user
    uid = str(user.id)

    if uid not in data["predictions"]:
        data["predictions"][uid] = {
            "name": user.full_name,
            "username": user.username or "",
            "predictions": {},
            "speech_guess": None,
            "score": None,
        }

    entry = data["predictions"][uid]
    entry["name"] = user.full_name
    entry["username"] = user.username or ""
    entry["predictions"].update(matched)
    if speech_guess is not None:
        entry["speech_guess"] = speech_guess

    save_data(data)

    # Build reply
    reply = f"✅ Saved {len(matched)} prediction(s):\n"
    for cat, pick in matched.items():
        reply += f"  • {cat}: {pick}\n"

    if speech_guess is not None:
        reply += f"\n⏱ Speech guess: {speech_guess} seconds"

    total = len(entry["predictions"])
    reply += f"\n\n📊 You've now predicted {total}/23 categories."

    if unrecognized:
        reply += "\n\n⚠️ Unrecognized lines:\n" + "\n".join(f"  • {l}" for l in unrecognized)

    await update.message.reply_text(reply)


async def mypredictions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    uid = str(update.effective_user.id)

    entry = data["predictions"].get(uid)
    if not entry or not entry["predictions"]:
        await update.message.reply_text("You haven't submitted any predictions yet.")
        return

    preds = entry["predictions"]
    lines = "\n".join(f"  {cat}: {pick}" for cat, pick in preds.items())

    msg = f"🎬 Your predictions ({len(preds)}/23):\n\n{lines}"

    if entry.get("speech_guess") is not None:
        msg += f"\n\n⏱ Speech guess: {entry['speech_guess']} seconds"

    if entry.get("score") is not None:
        msg += f"\n\n🏆 Score: {entry['score']} points"

    await update.message.reply_text(msg)


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    predictions = data["predictions"]

    if not predictions:
        await update.message.reply_text("No predictions submitted yet.")
        return

    speech_actual = data.get("speech_seconds")
    scores_calculated = any(e.get("score") is not None for e in predictions.values())

    def sort_key(entry):
        score = entry.get("score")
        name = entry.get("name", "")
        if not scores_calculated:
            return (0, 0, name)
        # Tiebreaker: closest speech guess
        if speech_actual is not None and entry.get("speech_guess") is not None:
            speech_diff = abs(entry["speech_guess"] - speech_actual)
        else:
            speech_diff = float("inf")
        return (-(score or 0), speech_diff, name)

    ranked = sorted(predictions.values(), key=sort_key)

    lines = []
    for i, entry in enumerate(ranked, 1):
        name = entry["name"]
        count = len(entry["predictions"])
        score_str = f"{entry['score']} pts" if entry.get("score") is not None else "—"
        speech_str = ""
        if entry.get("speech_guess") is not None:
            speech_str = f" | ⏱ {entry['speech_guess']}s"
        lines.append(f"{i}. {name}  [{score_str} | {count}/23{speech_str}]")

    header = "🏆 Leaderboard" if scores_calculated else "📋 Participants"
    await update.message.reply_text(f"{header}\n\n" + "\n".join(lines))
