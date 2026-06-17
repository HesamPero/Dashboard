import streamlit as st
import requests
from datetime import datetime, date
import json
import os
import random

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Her Dashboard",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Inter:wght@300;400&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-weight: 300;
}

/* Background */
.stApp {
    background-color: #F7F5F0;
    color: #2C2C2C;
}

/* Hide streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 680px;
}

/* Display title */
.display-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 300;
    color: #2C2C2C;
    letter-spacing: 0.04em;
    margin-bottom: 0.1rem;
    line-height: 1.1;
}
.display-sub {
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9A8F82;
    margin-bottom: 2.5rem;
}

/* Divider */
.thin-rule {
    border: none;
    border-top: 1px solid #E0DAD2;
    margin: 1.8rem 0;
}

/* Cards */
.card {
    background: #FFFFFF;
    border-radius: 3px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    border: 1px solid #EDE8E1;
}
.card-label {
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #B5A99A;
    margin-bottom: 0.5rem;
}
.card-main {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.45rem;
    font-weight: 300;
    color: #2C2C2C;
    line-height: 1.45;
}
.card-detail {
    font-size: 0.82rem;
    color: #9A8F82;
    margin-top: 0.3rem;
}

/* Weather row */
.weather-row {
    display: flex;
    gap: 1.2rem;
    align-items: center;
}
.weather-temp {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    font-weight: 300;
    line-height: 1;
}
.weather-info {
    flex: 1;
}

/* Habit checkboxes */
.stCheckbox label {
    font-size: 0.9rem !important;
    color: #4A4440 !important;
    letter-spacing: 0.02em;
}

/* Note box */
.note-box {
    background: #FBF9F6;
    border-left: 2px solid #D4C9BB;
    padding: 1.1rem 1.4rem;
    border-radius: 0 3px 3px 0;
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.2rem;
    color: #5A4F46;
    line-height: 1.6;
}

/* Buttons */
.stButton > button {
    background: #2C2C2C;
    color: #F7F5F0;
    border: none;
    border-radius: 2px;
    padding: 0.5rem 1.4rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 400;
    cursor: pointer;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: #4A4440;
    color: #F7F5F0;
    border: none;
}
.stTextInput > div > div > input,
.stTextArea textarea {
    background: #FFFFFF;
    border: 1px solid #EDE8E1;
    border-radius: 2px;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #2C2C2C;
}
.stSelectbox > div > div {
    background: #FFFFFF;
    border: 1px solid #EDE8E1;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "her_dashboard_data.json")

def load_data():
    defaults = {
        "city": "Heidelberg",
        "habits": ["Drink water 💧", "Morning stretch 🌸", "Read 10 pages 📖"],
        "habit_log": {},
        "love_notes": [
            "The way you laugh at your own jokes before you finish telling them — I could listen to that forever.",
            "You make ordinary days feel like something worth remembering.",
            "I noticed you again today, the way I always do.",
            "You are my favorite part of every single day.",
            "There is nowhere I would rather be than wherever you are.",
        ],
        "custom_note": "",
        "note_date": "",
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                saved = json.load(f)
            defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=5)
        j = r.json()
        cur = j["current_condition"][0]
        temp_c = int(cur["temp_C"])
        feels = int(cur["FeelsLikeC"])
        desc = cur["weatherDesc"][0]["value"]
        humidity = cur["humidity"]
        return {"temp": temp_c, "feels": feels, "desc": desc, "humidity": humidity, "ok": True}
    except Exception:
        return {"ok": False}

def get_quote():
    quotes = [
        ("She is water. Powerful enough to drown you, soft enough to cleanse you, deep enough to save you.", "Adrian Michael"),
        ("You yourself, as much as anybody in the entire universe, deserve your love and affection.", "Buddha"),
        ("Dwell on the beauty of life.", "Marcus Aurelius"),
        ("She remembered who she was and the game changed.", "Lalah Delia"),
        ("Do small things with great love.", "Mother Teresa"),
        ("Be the energy you want to attract.", "Anonymous"),
        ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
        ("Everything you can imagine is real.", "Pablo Picasso"),
        ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
    ]
    return random.choice(quotes)

today_str = date.today().isoformat()
now = datetime.now()
greeting_hour = now.hour
if greeting_hour < 12:
    greeting = "Good morning"
elif greeting_hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_name = day_names[date.today().weekday()]
month_names = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
date_display = f"{day_name}, {date.today().day} {month_names[date.today().month-1]} {date.today().year}"


# ── Load state ─────────────────────────────────────────────────────────────────
data = load_data()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="display-title">{greeting} ✦</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-sub">{date_display}</div>', unsafe_allow_html=True)

# ── Weather ────────────────────────────────────────────────────────────────────
weather = get_weather(data["city"])
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-label">Weather</div>', unsafe_allow_html=True)
if weather["ok"]:
    icon = "☀️" if "sun" in weather["desc"].lower() or "clear" in weather["desc"].lower() \
        else "🌧️" if "rain" in weather["desc"].lower() \
        else "☁️" if "cloud" in weather["desc"].lower() \
        else "❄️" if "snow" in weather["desc"].lower() \
        else "🌤️"
    st.markdown(f"""
    <div class="weather-row">
        <div style="font-size:2.4rem">{icon}</div>
        <div class="weather-info">
            <span class="weather-temp">{weather['temp']}°C</span>
            <div class="card-detail">{weather['desc']} · feels like {weather['feels']}°C · humidity {weather['humidity']}%</div>
            <div class="card-detail" style="margin-top:0.15rem">{data['city']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="card-detail">Weather unavailable right now.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Quote ──────────────────────────────────────────────────────────────────────
q_text, q_author = get_quote()
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-label">A thought for today</div>', unsafe_allow_html=True)
st.markdown(f'<div class="card-main" style="font-style:italic">"{q_text}"</div>', unsafe_allow_html=True)
st.markdown(f'<div class="card-detail">— {q_author}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Love note ──────────────────────────────────────────────────────────────────
# Show a fixed note per calendar day, cycling through the list
note_index = date.today().toordinal() % len(data["love_notes"])
daily_note = data["love_notes"][note_index]

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-label">From him, for you</div>', unsafe_allow_html=True)
st.markdown(f'<div class="note-box">{daily_note}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Habits ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
st.markdown('<div class="card-label" style="margin-bottom:0.8rem">Today\'s intentions</div>', unsafe_allow_html=True)

today_log = data["habit_log"].get(today_str, {})
for habit in data["habits"]:
    checked = st.checkbox(habit, value=today_log.get(habit, False), key=f"habit_{habit}")
    today_log[habit] = checked

data["habit_log"][today_str] = today_log
done = sum(1 for v in today_log.values() if v)
total = len(data["habits"])
if total > 0:
    pct = int(done / total * 100)
    st.progress(pct / 100)
    st.markdown(f'<div class="card-detail">{done} of {total} done · {pct}%</div>', unsafe_allow_html=True)

save_data(data)

# ── Settings expander ──────────────────────────────────────────────────────────
st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
with st.expander("⚙  Personalise"):
    st.markdown("**City for weather**")
    new_city = st.text_input("City", value=data["city"], label_visibility="collapsed")

    st.markdown("**Daily intentions** (one per line)")
    habits_text = st.text_area(
        "Habits",
        value="\n".join(data["habits"]),
        height=110,
        label_visibility="collapsed"
    )

    st.markdown("**Love notes** (one per line — he writes these for you 💌)")
    notes_text = st.text_area(
        "Notes",
        value="\n".join(data["love_notes"]),
        height=160,
        label_visibility="collapsed"
    )

    if st.button("Save"):
        data["city"] = new_city.strip() or data["city"]
        data["habits"] = [h.strip() for h in habits_text.splitlines() if h.strip()]
        data["love_notes"] = [n.strip() for n in notes_text.splitlines() if n.strip()]
        save_data(data)
        st.success("Saved ✓")
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;margin-top:2.5rem;font-size:0.72rem;'
    'letter-spacing:0.15em;text-transform:uppercase;color:#C5BAB0">made with love ✦</div>',
    unsafe_allow_html=True
)
