"""
API d'Open-Meteo (sans cle API)
"""

import requests
from datetime import datetime, date

DEFAULT_LAT = 43.6047
DEFAULT_LON = 1.4442


def geocoder_ville(nom_ville: str) -> dict | None:

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": nom_ville, "count": 1, "language": "fr", "format": "json"}
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return None
        res = results[0]
        return {
            "nom":       res.get("name", nom_ville),
            "latitude":  res["latitude"],
            "longitude": res["longitude"],
            "pays":      res.get("country", ""),
            "region":    res.get("admin1", ""),
        }
    except requests.RequestException:
        return None


def get_previsions(
    latitude: float = DEFAULT_LAT,
    longitude: float = DEFAULT_LON,
    jours: int = 7,
) -> list[dict]:

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min",
                  "precipitation_sum", "weathercode"],
        "timezone": "Europe/Paris",
        "forecast_days": jours,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        print(f"[meteo.py] Erreur : {e}")
        return []

    daily = data.get("daily", {})
    dates  = daily.get("time", [])
    t_max  = daily.get("temperature_2m_max", [])
    t_min  = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    codes  = daily.get("weathercode", [])

    result = []
    for i, d in enumerate(dates):
        tmax = t_max[i] if i < len(t_max) else None
        tmin = t_min[i] if i < len(t_min) else None
        tmoy = round((tmax + tmin) / 2, 1) if tmax is not None and tmin is not None else None
        code = codes[i] if i < len(codes) else 0
        desc, emoji = _decode_wmo(code)
        result.append({
            "date":          datetime.strptime(d, "%Y-%m-%d").date(),
            "temp_max":      tmax,
            "temp_min":      tmin,
            "temp_moyenne":  tmoy,
            "precipitation": precip[i] if i < len(precip) else 0.0,
            "code_meteo":    code,
            "description":   desc,
            "emoji":         emoji,
        })
    return result


def get_temperature_aujourd_hui(
    latitude: float = DEFAULT_LAT,
    longitude: float = DEFAULT_LON,
) -> float | None:
    prevs = get_previsions(latitude, longitude, jours=1)
    return prevs[0]["temp_moyenne"] if prevs else None


def get_prevision_jour(
    target_date: date,
    latitude: float = DEFAULT_LAT,
    longitude: float = DEFAULT_LON,
) -> dict | None:
    for p in get_previsions(latitude, longitude, jours=7):
        if p["date"] == target_date:
            return p
    return None


_WMO_MAP = {
    0:  ("Ciel degage",             "☀️"),
    1:  ("Principalement degage",   "🌤️"),
    2:  ("Partiellement nuageux",   "⛅"),
    3:  ("Couvert",                 "☁️"),
    45: ("Brouillard",              "🌫️"),
    48: ("Brouillard givrant",      "🌫️"),
    51: ("Bruine legere",           "🌦️"),
    53: ("Bruine moderee",          "🌦️"),
    55: ("Bruine dense",            "🌧️"),
    61: ("Pluie legere",            "🌧️"),
    63: ("Pluie moderee",           "🌧️"),
    65: ("Pluie forte",             "🌧️"),
    71: ("Neige legere",            "❄️"),
    73: ("Neige moderee",           "❄️"),
    75: ("Neige forte",             "❄️"),
    77: ("Grains de neige",         "🌨️"),
    80: ("Averses legeres",         "🌦️"),
    81: ("Averses moderees",        "🌦️"),
    82: ("Averses fortes",          "⛈️"),
    85: ("Averses de neige",        "🌨️"),
    86: ("Averses de neige fortes", "🌨️"),
    95: ("Orage",                   "⛈️"),
    96: ("Orage avec grele",        "⛈️"),
    99: ("Orage avec forte grele",  "⛈️"),
}


def _decode_wmo(code: int) -> tuple[str, str]:
    return _WMO_MAP.get(code, ("Conditions inconnues", "🌡️"))