import streamlit as st
import folium
from streamlit_folium import st_folium
from travel_data import all_places, add_place, update_status, delete_place, upload_photo, update_photo_url, geocode

st.set_page_config(page_title="Her Travel Map", page_icon="🌸", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400&display=swap');

html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
    font-weight: 300;
}
.stApp {
    background: linear-gradient(135deg, #FFE4EC 0%, #FFF0F5 50%, #FFE8F0 100%);
    color: #3D1C2E;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 920px; }

.display-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 600;
    color: #C2185B;
    letter-spacing: 0.02em;
    line-height: 1.1;
}
.display-sub {
    font-size: 0.78rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #E991B5;
    margin-bottom: 1.8rem;
}
.stat-box {
    background: rgba(255,255,255,0.7);
    border: 1px solid #F8C0D8;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    backdrop-filter: blur(6px);
}
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 600;
    color: #C2185B;
}
.stat-label {
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #E991B5;
}
.place-card {
    background: rgba(255,255,255,0.75);
    border: 1px solid #F8C0D8;
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin-bottom: 0.8rem;
    backdrop-filter: blur(4px);
}
.place-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    font-weight: 400;
    color: #3D1C2E;
}
.place-meta { font-size: 0.76rem; color: #C48FA8; margin-top: 0.1rem; }
.badge-dream {
    display:inline-block; background:#FCE4EC; color:#C2185B;
    font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;
    padding:0.15rem 0.6rem; border-radius:20px; margin-bottom:0.4rem;
    border: 1px solid #F48FB1;
}
.badge-visited {
    display:inline-block; background:#E8F5E9; color:#388E3C;
    font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;
    padding:0.15rem 0.6rem; border-radius:20px; margin-bottom:0.4rem;
    border: 1px solid #A5D6A7;
}
.stButton > button {
    background: #C2185B;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 0.4rem 1.2rem;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    font-family: 'Lato', sans-serif;
}
.stButton > button:hover { background: #AD1457; color: white; border: none; }
section[data-testid="stSidebar"] {
    background: rgba(255, 228, 236, 0.95) !important;
    border-right: 1px solid #F8C0D8;
}
.stTextInput > div > div > input,
.stTextArea textarea {
    background: rgba(255,255,255,0.8);
    border: 1px solid #F8C0D8;
    border-radius: 8px;
    font-family: 'Lato', sans-serif;
}
.stRadio label { font-family: 'Lato', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Playfair Display,serif;font-size:1.7rem;color:#C2185B;margin-bottom:0.2rem">Add a place 🌸</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;letter-spacing:0.15em;text-transform:uppercase;color:#E991B5;margin-bottom:1.2rem">dream or memory</div>', unsafe_allow_html=True)

    city_input = st.text_input("City / Place", placeholder="e.g. Kyoto, Santorini…")
    status_input = st.radio("Type", ["Dream 🌙", "Visited ✓"], horizontal=True)
    note_input = st.text_area("Note (optional)", placeholder="Why I want to go… or a memory…", height=90)
    photo_input = st.file_uploader("Photo (optional)", type=["jpg", "jpeg", "png", "webp"])

    if st.button("Add to map ✨"):
        if not city_input.strip():
            st.error("Please enter a city name.")
        else:
            with st.spinner("Finding on the map…"):
                geo = geocode(city_input.strip())
            if geo is None:
                st.error("Couldn't find that place. Try a different spelling.")
            else:
                status = "dream" if "Dream" in status_input else "visited"
                entry = add_place(
                    name=geo["name"], country=geo["country"],
                    lat=geo["lat"], lon=geo["lon"],
                    status=status, note=note_input.strip(),
                )
                if photo_input:
                    with st.spinner("Uploading photo… ☁️"):
                        photo_url = upload_photo(photo_input.read(), entry["id"])
                    if photo_url:
                        update_photo_url(entry["id"], photo_url)
                st.success(f"Added **{geo['name']}** to your map! 🌸")
                st.rerun()

    st.markdown("---")
    filter_opt = st.radio("Show", ["All 🗺️", "Dreams only 🌙", "Visited only ✓"], index=0)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="display-title">Her Travel Map 🌸</div>', unsafe_allow_html=True)
st.markdown('<div class="display-sub">places to dream about · places already lived</div>', unsafe_allow_html=True)

places = all_places()
dreams = [p for p in places if p["status"] == "dream"]
visited = [p for p in places if p["status"] == "visited"]

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="stat-box"><div class="stat-num">{len(places)}</div><div class="stat-label">Total places</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="stat-box"><div class="stat-num">{len(visited)}</div><div class="stat-label">Visited</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="stat-box"><div class="stat-num">{len(dreams)}</div><div class="stat-label">Dreams</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

if "Dreams only" in filter_opt: display_places = dreams
elif "Visited only" in filter_opt: display_places = visited
else: display_places = places

# ── Map ────────────────────────────────────────────────────────────────────────
if display_places:
    center_lat = sum(p["lat"] for p in display_places) / len(display_places)
    center_lon = sum(p["lon"] for p in display_places) / len(display_places)
else:
    center_lat, center_lon = 20, 10

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=3 if len(display_places) > 1 else 6,
    tiles="CartoDB Positron",
)

for p in display_places:
    color = "#E91E8C" if p["status"] == "dream" else "#43A047"
    popup_html = f'<div style="font-family:Georgia,serif;min-width:160px;max-width:220px"><b style="font-size:1rem;color:#C2185B">{p["name"]}</b><br><span style="font-size:0.8rem;color:#999">{p["country"]}</span><br>'
    if p.get("note"): popup_html += f'<i style="font-size:0.82rem;color:#777">{p["note"]}</i><br>'
    if p.get("photo_url"): popup_html += f'<img src="{p["photo_url"]}" style="width:100%;margin-top:6px;border-radius:8px">'
    popup_html += "</div>"
    folium.CircleMarker(
        location=[p["lat"], p["lon"]], radius=10,
        color=color, fill=True, fill_color=color, fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f'{p["name"]} {"🌙" if p["status"]=="dream" else "✓"}',
    ).add_to(m)

st_folium(m, width="100%", height=450, returned_objects=[])
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Place list ─────────────────────────────────────────────────────────────────
tab_all, tab_dream, tab_visited = st.tabs(["All places 🗺️", "Dream list 🌙", "Visited ✓"])

def render_place_list(place_list):
    if not place_list:
        st.markdown('<div style="font-size:0.88rem;color:#E991B5;padding:1rem 0">Nothing here yet — add your first place! 🌸</div>', unsafe_allow_html=True)
        return
    for p in reversed(place_list):
        badge = f'<span class="badge-{"dream" if p["status"]=="dream" else "visited"}">{"🌙 Dream" if p["status"]=="dream" else "✓ Visited"}</span>'
        note_html = f'<div style="font-size:0.84rem;color:#9C6080;margin-top:0.35rem;font-style:italic">{p["note"]}</div>' if p.get("note") else ""
        st.markdown(f'<div class="place-card">{badge}<div class="place-name">{p["name"]}</div><div class="place-meta">{p["country"]} · {p["added_at"][:10]}</div>{note_html}</div>', unsafe_allow_html=True)
        if p.get("photo_url"):
            with st.expander("📷 View photo"):
                st.image(p["photo_url"], width=300)
        col1, col2 = st.columns([2, 8])
        with col1:
            if p["status"] == "dream":
                if st.button("Mark visited ✓", key=f"vis_{p['id']}"):
                    update_status(p["id"], "visited"); st.rerun()
            else:
                if st.button("Move to dreams 🌙", key=f"drm_{p['id']}"):
                    update_status(p["id"], "dream"); st.rerun()
        with col2:
            if st.button("Remove 🗑", key=f"del_{p['id']}"):
                delete_place(p["id"]); st.rerun()

with tab_all: render_place_list(display_places)
with tab_dream: render_place_list(dreams)
with tab_visited: render_place_list(visited)

st.markdown('<div style="text-align:center;margin-top:2.5rem;font-size:0.72rem;letter-spacing:0.15em;text-transform:uppercase;color:#E991B5">made with love ✦</div>', unsafe_allow_html=True)
