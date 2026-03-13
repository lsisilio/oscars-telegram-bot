from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from handlers.user import start, predict, mypredictions, leaderboard, categories
from handlers.admin import open_submissions, close_submissions, setwinners, setspeech, scores, llmon, llmoff, llmstatus


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start",          start))
    app.add_handler(CommandHandler("categories",     categories))
    app.add_handler(CommandHandler("predict",        predict))
    app.add_handler(CommandHandler("mypredictions",  mypredictions))
    app.add_handler(CommandHandler("leaderboard",    leaderboard))

    # Admin commands
    app.add_handler(CommandHandler("open",           open_submissions))
    app.add_handler(CommandHandler("close",          close_submissions))
    app.add_handler(CommandHandler("setwinners",     setwinners))
    app.add_handler(CommandHandler("setspeech",      setspeech))
    app.add_handler(CommandHandler("scores",         scores))
    app.add_handler(CommandHandler("llmon",          llmon))
    app.add_handler(CommandHandler("llmoff",         llmoff))
    app.add_handler(CommandHandler("llmstatus",      llmstatus))

    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
