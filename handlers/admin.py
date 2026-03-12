import functools

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID
from parser import parse_predictions, normalize
from storage import load_data, save_data


def require_admin(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("⛔ Not authorized.")
            return
        return await func(update, context)
    return wrapper


@require_admin
async def open_submissions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    data["state"] = "open"
    save_data(data)
    await update.message.reply_text("✅ Submissions are now OPEN.")


@require_admin
async def close_submissions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    data["state"] = "closed"
    save_data(data)
    await update.message.reply_text("🔒 Submissions are now CLOSED.")


@require_admin
async def setwinners(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()

    text = update.message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text(
            "Usage: /setwinners\nBest Picture: Conclave\nBest Director: Brady Corbet\n..."
        )
        return

    matched, _, unrecognized = parse_predictions(parts[1], data["categories"])

    if not matched:
        msg = "⚠️ No winners parsed."
        if unrecognized:
            msg += "\nUnrecognized:\n" + "\n".join(f"• {l}" for l in unrecognized)
        await update.message.reply_text(msg)
        return

    data["winners"].update(matched)
    save_data(data)

    reply = f"✅ Winners set for {len(matched)} category(ies):\n"
    for cat, winner in matched.items():
        reply += f"  • {cat}: {winner}\n"
    reply += f"\n📊 Total winners recorded: {len(data['winners'])}/23"

    if unrecognized:
        reply += "\n\n⚠️ Unrecognized:\n" + "\n".join(f"  • {l}" for l in unrecognized)

    await update.message.reply_text(reply)


@require_admin
async def setspeech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()

    text = update.message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        await update.message.reply_text("Usage: /setspeech <seconds>\nExample: /setspeech 127")
        return

    try:
        seconds = int(parts[1].strip())
    except ValueError:
        await update.message.reply_text("⚠️ Please provide an integer number of seconds.")
        return

    data["speech_seconds"] = seconds
    save_data(data)
    await update.message.reply_text(f"⏱ Best Picture speech duration set: {seconds} seconds.")


@require_admin
async def scores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()

    if not data["winners"]:
        await update.message.reply_text("⚠️ No winners have been set yet. Use /setwinners first.")
        return

    winners = data["winners"]
    speech_actual = data.get("speech_seconds")

    for uid, entry in data["predictions"].items():
        score = 0
        for cat, actual_winner in winners.items():
            user_pick = entry["predictions"].get(cat, "")
            if normalize(user_pick) == normalize(actual_winner):
                score += 1
        entry["score"] = score

    save_data(data)

    # Build sorted leaderboard
    def sort_key(entry):
        score = entry.get("score", 0) or 0
        if speech_actual is not None and entry.get("speech_guess") is not None:
            speech_diff = abs(entry["speech_guess"] - speech_actual)
        else:
            speech_diff = float("inf")
        return (-score, speech_diff, entry.get("name", ""))

    ranked = sorted(data["predictions"].values(), key=sort_key)

    lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, entry in enumerate(ranked):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = entry["name"]
        score = entry["score"]
        count = len(entry["predictions"])
        speech_str = ""
        if speech_actual is not None and entry.get("speech_guess") is not None:
            diff = abs(entry["speech_guess"] - speech_actual)
            speech_str = f" | ⏱ {entry['speech_guess']}s (off by {diff}s)"
        elif entry.get("speech_guess") is not None:
            speech_str = f" | ⏱ {entry['speech_guess']}s"
        lines.append(f"{medal} {name}  {score} pts ({count}/23 predicted){speech_str}")

    msg = f"🏆 Final Scores ({len(winners)} categories judged)\n\n" + "\n".join(lines)
    if speech_actual is not None:
        msg += f"\n\n⏱ Actual speech duration: {speech_actual}s"

    await update.message.reply_text(msg)
