import streamlit as st
import folium
from streamlit_folium import st_folium
import os
from travel_data import all_places, add_place, update_status, delete_place, save_photo, geocode

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Her Travel Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Inter:wght@300;400&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-weight: 300; }
.stApp { background-color: #F7F5F0; color: #2C2C2C; }
#MainMenu, footer, header { visibility: hidden; }

.display-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem; font-weight: 300;
    color: #2C2C2C; letter-spacing: 0.04em;
    margin-bottom: 0.1rem;
}
.display-sub {
    font-size: 0.75rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: #9A8F82;
    margin-bottom: 1.5rem;
}
.stat-box {
    background: #FFFFFF; border: 1px solid #EDE8E1;
    border-radius: 3px; padding: 1rem 1.2rem; text-align: center;
}
.stat-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.2rem; font-weight: 300; color: #2C2C2C;
}
.stat-label {
    font-size: 0.7rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: #B5A99A;
}
.place-card {
    background: #FFFFFF; border: 1px solid #EDE8E1;
    border-radius: 3px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;
}
.place-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.25rem; font-weight: 400; color: #2C2C2C;
}
.place-meta {
    font-size: 0.76rem; color: #9A8F82;
    letter-spacing: 0.05em; margin-top: 0.1rem;
}
.badge-dream {
    display:inline-block; background:#F0EBE3; color:#8A7060;
    font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;
    padding:0.15rem 0.55rem; border-radius:20px; margin-bottom:0.4rem;
}
.badge-visited {
    display:inline-block; background:#E8F0E8; color:#4A7060;
    font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;
    padding:0.15rem 0.55rem; border-radius:20px; margin-bottom:0.4rem;
}
.stButton > button {
    background: #2C2C2C; color: #F7F5F0;
    border: none; border-radius: 2px;
    padding: 0.45rem 1.2rem;
    font-size: 0.75rem; letter-spacing: 0.1em;
    text-transform: uppercase;
}
.stButton > button:hover { background: #4A4440; color: #F7F5F0; border: none; }
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #EDE8E1; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar — Add a place ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Cormorant Garamond,serif;font-size:1.6rem;font-weight:300;margin-bottom:0.2rem">Add a place</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;letter-spacing:0.15em;text-transform:uppercase;color:#B5A99A;margin-bottom:1.2rem">dream or memory</div>', unsafe_allow_html=True)

    city_input = st.text_input("City / Place", placeholder="e.g. Kyoto, Santorini…")
    status_input = st.radio("Type", ["Dream 🌙", "Visited ✓"], horizontal=True)
    note_input = st.text_area("Note (optional)", placeholder="Why I want to go… or a memory from there…", height=90)
    photo_input = st.file_uploader("Photo (optional)", type=["jpg", "jpeg", "png", "webp"])

    if st.button("Add to map"):
        if not city_input.strip():
            st.error("Please enter a city name.")
        else:
            with st.spinner("Finding on the map…"):
                geo = geocode(city_input.strip())
            if geo is None:
                st.error("Couldn't find that place. Try a different spelling.")
            else:
                status = "dream" if "Dream" in status_input else "visited"
                photo_path = ""
                new_entry = add_place(
                    name=geo["name"], country=geo["country"],
                    lat=geo["lat"], lon=geo["lon"],
                    status=status, note=note_input.strip(),
                )
                if photo_input:
                    ext = photo_input.name.split(".")[-1]
                    photo_path = save_photo(new_entry["id"], photo_input.read(), ext)
                    # update note with photo path (re-save)
                    from travel_data import _load, _save
                    places = _load()
                    for p in places:
                        if p["id"] == new_entry["id"]:
                            p["photo_path"] = photo_path
                    _save(places)
                st.success(f"Added **{geo['name']}** to your map! 🌿")
                st.rerun()

    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:#C5BAB0;margin-bottom:0.6rem">Filter</div>', unsafe_allow_html=True)
    filter_opt = st.radio("Show", ["All", "Dreams only 🌙", "Visited only ✓"], index=0)


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="display-title">Her Travel Map 🗺️</div>', unsafe_allow_html=True)
st.markdown('<div class="display-sub">places to dream about · places already lived</div>', unsafe_allow_html=True)

places = all_places()
dreams = [p for p in places if p["status"] == "dream"]
visited = [p for p in places if p["status"] == "visited"]

# Stats row
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(places)}</div><div class="stat-label">Total places</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(visited)}</div><div class="stat-label">Visited</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(dreams)}</div><div class="stat-label">Dreams</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# Filter
if filter_opt == "Dreams only 🌙":
    display_places = dreams
elif filter_opt == "Visited only ✓":
    display_places = visited
else:
    display_places = places

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
    control_scale=True,
)

for p in display_places:
    color = "#C4956A" if p["status"] == "dream" else "#6A9E7F"
    icon_symbol = "🌙" if p["status"] == "dream" else "✓"
    popup_html = f"""
    <div style="font-family:Georgia,serif;min-width:160px;max-width:220px">
        <b style="font-size:1rem">{p['name']}</b><br>
        <span style="font-size:0.8rem;color:#888">{p['country']}</span><br>
        <span style="font-size:0.75rem;background:{'#F5EDE3' if p['status']=='dream' else '#E5F0E8'};
        padding:2px 8px;border-radius:10px;display:inline-block;margin:4px 0">
        {icon_symbol} {'Dream' if p['status']=='dream' else 'Visited'}</span>
    """
    if p.get("note"):
        popup_html += f'<br><i style="font-size:0.82rem;color:#555">{p["note"]}</i>'
    if p.get("photo_path") and os.path.exists(p["photo_path"]):
        import base64
        with open(p["photo_path"], "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        ext = p["photo_path"].split(".")[-1]
        popup_html += f'<br><img src="data:image/{ext};base64,{img_b64}" style="width:100%;margin-top:6px;border-radius:3px">'
    popup_html += "</div>"

    folium.CircleMarker(
        location=[p["lat"], p["lon"]],
        radius=9,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"{p['name']} {'🌙' if p['status']=='dream' else '✓'}",
    ).add_to(m)

st_folium(m, width="100%", height=440, returned_objects=[])

# ── Place list ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

tab_all, tab_dream, tab_visited = st.tabs(["All places", "Dream list 🌙", "Visited ✓"])

def render_place_list(place_list):
    if not place_list:
        st.markdown('<div style="font-size:0.88rem;color:#B5A99A;padding:1rem 0">Nothing here yet — add your first place from the sidebar.</div>', unsafe_allow_html=True)
        return
    for p in reversed(place_list):
        badge = f'<span class="badge-{"dream" if p["status"]=="dream" else "visited"}">{"🌙 Dream" if p["status"]=="dream" else "✓ Visited"}</span>'
        st.markdown(f"""
        <div class="place-card">
            {badge}
            <div class="place-name">{p['name']}</div>
            <div class="place-meta">{p['country']} · added {p['added_at'][:10]}</div>
            {'<div style="font-size:0.84rem;color:#6A6060;margin-top:0.35rem;font-style:italic">' + p['note'] + '</div>' if p.get('note') else ''}
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 2, 6])
        with col1:
            if p["status"] == "dream":
                if st.button("Mark visited ✓", key=f"vis_{p['id']}"):
                    update_status(p["id"], "visited")
                    st.rerun()
            else:
                if st.button("Move to dreams 🌙", key=f"drm_{p['id']}"):
                    update_status(p["id"], "dream")
                    st.rerun()
        with col2:
            if st.button("Remove", key=f"del_{p['id']}"):
                delete_place(p["id"])
                st.rerun()

        if p.get("photo_path") and os.path.exists(p["photo_path"]):
            with st.expander("📷 View photo"):
                st.image(p["photo_path"], width=300)

with tab_all:
    render_place_list(display_places)
with tab_dream:
    render_place_list(dreams)
with tab_visited:
    render_place_list(visited)

st.markdown(
    '<div style="text-align:center;margin-top:2rem;font-size:0.7rem;'
    'letter-spacing:0.15em;text-transform:uppercase;color:#C5BAB0">made with love ✦</div>',
    unsafe_allow_html=True,
)
