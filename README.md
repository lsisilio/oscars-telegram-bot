# 🎬 Oscar 2026 Predictions Bot

A Telegram bot for running Oscar prediction pools with friends. Everyone submits their picks before the ceremony, and the bot automatically scores and ranks everyone after the winners are announced.

---

## Features

- Free-form text predictions — no buttons or menus required
- Fuzzy category matching handles typos and abbreviations
- Optional **LLM normalization** via Claude API to fix nominee name variations
- Tiebreaker: closest guess to the Best Picture acceptance speech duration
- Admin controls to open/close submissions, enter winners, and reveal scores

---

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the **bot token** you receive

### 2. Get your Telegram User ID

Message [@userinfobot](https://t.me/userinfobot) — it will reply with your numeric user ID.

### 3. Configure Environment

Create a `.env` file in the project root:

```
BOT_TOKEN=7123456789:AAF...your_token_here
ADMIN_IDS=123456789,987654321
```

For a single admin, just one ID is fine: `ADMIN_IDS=123456789`. The old `ADMIN_ID` key is also accepted for backwards compatibility.

To enable LLM normalization (optional), also add:

```
ANTHROPIC_API_KEY=sk-ant-...your_key_here
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run

```bash
python app.py
```

---

## Deploying to Fly.io (Free Hosting)

Fly.io's free tier (3 shared VMs + 1GB persistent volume) is enough to run this bot continuously.

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Sign up / log in
fly auth signup

# Initialize the app (don't deploy yet)
fly launch --no-deploy

# Set secrets (these are encrypted — only you can read them)
fly secrets set BOT_TOKEN=your_token ADMIN_ID=your_id

# Optional: add Anthropic key for LLM normalization
fly secrets set ANTHROPIC_API_KEY=sk-ant-...

# Create persistent storage for data.json
fly volumes create oscar_data --size 1

# Deploy
fly deploy
```

**Other free hosting options:**
- **Koyeb** — free starter plan, Docker deploy
- **Oracle Always Free** — 2 AMD VMs, free forever (more setup required)

---

## How Predictions Work

Friends submit picks by sending `/predict` followed by their predictions, one per line:

```
/predict
Best Picture: Conclave
Best Director: Brady Corbet
Best Actor: Adrien Brody
Best Actress: Demi Moore
Best Supporting Actor: Kieran Culkin
Speech Duration: 142
```

**Rules:**
- Category names are case-insensitive and typo-tolerant (`best pic` → Best Picture)
- You can submit partial predictions (not all 23 required)
- Re-submitting updates only the categories you include — others are kept
- `Speech Duration` (in seconds) is a tiebreaker for tied scores, not a scored category

---

## All Commands

### User Commands

| Command | Description |
|---|---|
| `/start` | Welcome message and format instructions |
| `/categories` | List all 23 Oscar categories |
| `/predict <predictions>` | Submit or update your predictions |
| `/mypredictions` | View your current predictions and score |
| `/leaderboard` | See the current rankings |

### Admin Commands

> Admin commands only work for the Telegram user whose ID is set as `ADMIN_ID`.

| Command | Description |
|---|---|
| `/open` | Open the submission window — friends can now submit predictions |
| `/close` | Close the submission window — no more predictions accepted |
| `/setwinners <winners>` | Enter actual Oscar winners (same format as predictions) |
| `/setspeech <seconds>` | Set the Best Picture acceptance speech duration for tiebreaking |
| `/scores` | Calculate and reveal the final leaderboard |
| `/llmon` | Enable LLM normalization (requires `ANTHROPIC_API_KEY`) |
| `/llmoff` | Disable LLM normalization, revert to fuzzy matching |
| `/llmstatus` | Check whether LLM is enabled and API key is configured |

---

## Typical Ceremony Workflow

**Before the ceremony:**

1. `/open` — open submissions
2. Share the bot with friends; they each send `/predict` with their picks
3. `/close` — lock submissions before the show starts

**During / after the ceremony:**

4. `/setwinners` — enter winners as they're announced (can be called multiple times)

   ```
   /setwinners
   Best Picture: The Brutalist
   Best Director: Brady Corbet
   Best Actor: Adrien Brody
   ```

5. `/setspeech 127` — enter the Best Picture speech duration in seconds

6. `/scores` — calculate everyone's score and post the final leaderboard

---

## Scoring

- **1 point** for each correctly predicted category
- **Tiebreaker**: among tied players, the one whose `Speech Duration` guess is closest to the actual duration wins
- Players who didn't submit a speech guess are ranked last among tied peers

---

## LLM Normalization (Optional)

When enabled, each submission is passed through Claude before saving. This corrects common issues:

| User typed | Stored as |
|---|---|
| `Timothee Chalamet` | `Timothée Chalamet` |
| `Brutal` | `The Brutalist` |
| `Demi` | `Demi Moore` |
| `emilia perez` | `Emilia Pérez` |

The bot will show `✨ (was: original)` next to any pick that was changed.

**How to enable:**

1. Add `ANTHROPIC_API_KEY=sk-ant-...` to your `.env` or Fly.io secrets
2. Send `/llmon` in Telegram

**Security:** The API key is never sent through Telegram. It lives only in your server environment (`.env` locally, `fly secrets` in production). Each deployment uses its own key.

If LLM is off or the key is missing, the bot falls back to fuzzy matching. Submissions are never blocked by an LLM failure.

---

## Nominees List

The official 2026 nominees are stored in [`nominees.py`](nominees.py). **Verify this file before opening submissions** — it was pre-filled based on the announced nominees but should be double-checked.

The nominees list is only used by the LLM normalization layer. The bot works without it.

---

## Data Storage

All data is saved to `data.json` (path configurable via `DATA_FILE` environment variable). The file is created automatically on first run. On Fly.io, it's stored on a persistent volume so it survives redeployments.

**Back up `data.json` before the ceremony** if you want to preserve everyone's predictions.

---

## Project Structure

```
oscar/
├── app.py          # Bot entry point
├── config.py       # Environment variable loading
├── storage.py      # JSON read/write
├── parser.py       # Prediction text parsing + fuzzy matching
├── nominees.py     # Official 2026 Oscar nominees
├── llm.py          # Claude API normalization
├── handlers/
│   ├── user.py     # User-facing commands
│   └── admin.py    # Admin-only commands
├── data.json       # Runtime data (auto-created)
├── requirements.txt
├── Dockerfile
└── fly.toml
```
