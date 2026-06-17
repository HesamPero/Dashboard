"""
Shared data layer for Her Travel Map.
Stores cities as a JSON file: travel_places.json
Each entry: { id, name, country, lat, lon, status, note, photo_path, added_at }
"""

import json, os, uuid
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "travel_places.json")
PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "photos")
os.makedirs(PHOTOS_DIR, exist_ok=True)


def _load() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _save(places: list):
    with open(DATA_FILE, "w") as f:
        json.dump(places, f, indent=2, ensure_ascii=False)


def all_places() -> list:
    return _load()


def add_place(name: str, country: str, lat: float, lon: float,
              status: str, note: str = "", photo_path: str = "") -> dict:
    """status: 'dream' or 'visited'"""
    places = _load()
    entry = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "country": country,
        "lat": lat,
        "lon": lon,
        "status": status,
        "note": note,
        "photo_path": photo_path,
        "added_at": datetime.now().isoformat(),
    }
    places.append(entry)
    _save(places)
    return entry


def update_status(place_id: str, new_status: str) -> bool:
    places = _load()
    for p in places:
        if p["id"] == place_id:
            p["status"] = new_status
            _save(places)
            return True
    return False


def delete_place(place_id: str) -> bool:
    places = _load()
    new = [p for p in places if p["id"] != place_id]
    if len(new) < len(places):
        _save(new)
        return True
    return False


def save_photo(place_id: str, data: bytes, ext: str = "jpg") -> str:
    path = os.path.join(PHOTOS_DIR, f"{place_id}.{ext}")
    with open(path, "wb") as f:
        f.write(data)
    return path


def geocode(city: str) -> dict | None:
    """Use Nominatim (free, no key) to get lat/lon/country."""
    import requests
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "HerTravelMap/1.0"},
            timeout=6,
        )
        results = r.json()
        if results:
            res = results[0]
            # get country via reverse or display_name
            display = res.get("display_name", "")
            country = display.split(",")[-1].strip() if "," in display else ""
            return {
                "name": city,
                "country": country,
                "lat": float(res["lat"]),
                "lon": float(res["lon"]),
            }
    except Exception:
        pass
    return None
