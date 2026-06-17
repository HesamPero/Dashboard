# 🗺️ Her Travel Map

A personal travel app + Telegram bot — dream destinations and memories, all in one place.

---

## What's inside

| File | What it does |
|------|-------------|
| `travel_data.py` | Shared data layer (JSON storage, geocoding) |
| `travel_app.py` | Streamlit web app with interactive map |
| `travel_bot.py` | Telegram bot |
| `requirements.txt` | Python dependencies |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the web app

```bash
streamlit run travel_app.py
```

Opens at `http://localhost:8501`

---

### 3. Set up the Telegram bot

#### Step 1 — Create a bot with BotFather
1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Follow the steps — choose a name and username
4. BotFather gives you a **token** like `123456789:ABCdef...`

#### Step 2 — Run the bot

```bash
export TELEGRAM_BOT_TOKEN=your_token_here
python travel_bot.py
```

Both the web app and bot share the same `travel_places.json` file — so places added in one show up in the other!

---

## Bot commands

| Command | What it does |
|---------|-------------|
| `/start` | Welcome message |
| `/add` | Add a new place (city, dream/visited, note, photo) |
| `/list` | See all places |
| `/dreams` | Dream destinations only 🌙 |
| `/visited` | Visited places only ✓ |

---

## Deploy online (free)

### Web app → Streamlit Community Cloud
1. Push all files to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set main file to `travel_app.py`
4. Deploy → get a public URL

### Telegram bot → Railway or Render
1. Push to GitHub
2. On [railway.app](https://railway.app), create a new project from your repo
3. Add environment variable: `TELEGRAM_BOT_TOKEN=your_token`
4. Set start command: `python travel_bot.py`
5. Deploy — bot runs 24/7 for free

---

*Made with love ✦*
