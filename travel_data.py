"""
Shared data layer — Supabase database + Cloudinary photos
"""

import os, uuid
from datetime import datetime

import cloudinary
import cloudinary.uploader
from supabase import create_client

# ── Clients ────────────────────────────────────────────────────────────────────
_sb = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", ""),
)

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)


def all_places() -> list:
    res = _sb.table("places").select("*").order("added_at", desc=False).execute()
    return res.data or []


def add_place(name, country, lat, lon, status, note="", photo_url="") -> dict:
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
    _sb.table("places").insert(entry).execute()
    return entry


def update_status(place_id: str, new_status: str) -> bool:
    _sb.table("places").update({"status": new_status}).eq("id", place_id).execute()
    return True


def delete_place(place_id: str) -> bool:
    _sb.table("places").delete().eq("id", place_id).execute()
    return True


def update_photo_url(place_id: str, photo_url: str):
    _sb.table("places").update({"photo_url": photo_url}).eq("id", place_id).execute()


def upload_photo(image_bytes: bytes, place_id: str) -> str:
    try:
        result = cloudinary.uploader.upload(
            image_bytes,
            public_id=f"her_travel_map/{place_id}",
            overwrite=True,
            resource_type="image",
        )
        return result.get("secure_url", "")
    except Exception as e:
        print(f"Cloudinary error: {e}")
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
