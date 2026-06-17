"""
Shared data layer for Her Travel Map.
Photos stored in Cloudinary. Data in JSON file.
"""

import json, os, uuid
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "travel_places.json")

# ── Cloudinary setup ───────────────────────────────────────────────────────────
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)


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


def add_place(name, country, lat, lon, status, note="", photo_url="") -> dict:
    places = _load()
    entry = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "country": country,
        "lat": lat,
        "lon": lon,
        "status": status,
        "note": note,
        "photo_url": photo_url,
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


def upload_photo(image_bytes: bytes, place_id: str) -> str:
    """Upload photo to Cloudinary, return public URL."""
    try:
        result = cloudinary.uploader.upload(
            image_bytes,
            public_id=f"her_travel_map/{place_id}",
            overwrite=True,
            resource_type="image",
        )
        return result.get("secure_url", "")
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return ""


def geocode(city: str) -> dict | None:
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
