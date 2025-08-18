# -*- coding: utf-8 -*-
import os
import json
import time
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# ===== Настройки =====
API_URL = os.getenv("API_URL", "https://api.football-data.org/v4/matches")
API_KEY = os.getenv("8bd7548e336c4f338735954ad91ae239") or os.getenv("FOOTBALL_API_KEY") or os.getenv("X_AUTH_TOKEN", "")
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "matches.json"
CACHE_TTL = int(os.getenv("CACHE_TTL", "900"))  # 15 минут
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

# Только ASCII в заголовках — иначе будет UnicodeEncodeError
HEADERS = {
    "User-Agent": "football-app/1.0",
    **({"X-Auth-Token": API_KEY} if API_KEY else {})
}


# ===== Вспомогательные =====
def _ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # TTL
            if time.time() - data.get("_ts", 0) <= CACHE_TTL:
                return data.get("matches", [])
        except Exception:
            pass
    return []


def save_cache(matches):
    _ensure_cache_dir()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"_ts": time.time(), "matches": matches}, f, ensure_ascii=False)
    except Exception:
        pass


def normalize_matches(raw):
    matches = []
    items = raw.get("matches", raw.get("data", raw))
    if isinstance(items, dict):
        items = items.get("matches", [])
    if not isinstance(items, list):
        items = []

    for m in items:
        home_obj = m.get("homeTeam") or m.get("home_team") or {}
        away_obj = m.get("awayTeam") or m.get("away_team") or {}
        home = home_obj.get("name") if isinstance(home_obj, dict) else home_obj
        away = away_obj.get("name") if isinstance(away_obj, dict) else away_obj

        score = m.get("score") or {}
        ft = score.get("fullTime") if isinstance(score, dict) else {}
        home_score = (ft.get("home") if isinstance(ft, dict) else None) or m.get("home_score")
        away_score = (ft.get("away") if isinstance(ft, dict) else None) or m.get("away_score")

        matches.append({
            "id": m.get("id") or m.get("match_id"),
            "home_team": home,
            "away_team": away,
            "home_score": home_score,
            "away_score": away_score,
            "date": m.get("utcDate") or m.get("date"),
        })
    return matches


def fetch_matches():
    params = {}
    if os.getenv("MATCH_DATE"):
        params["date"] = os.getenv("MATCH_DATE")

    try:
        r = requests.get(API_URL, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        matches = normalize_matches(data)
        if matches:
            save_cache(matches)
        return matches
    except Exception as e:
        # Пишем в лог и отдаём кеш
        print(f"[fetch_matches] fallback to cache due to: {e}")
        return load_cache()


def get_matches():
    cached = load_cache()
    if cached:
        return cached
    return fetch_matches()


# ===== Маршруты =====
@app.route("/")
def index():
    matches = get_matches()
    return render_template("index.html", matches=matches, page=int(request.args.get("page", 1)))


@app.route("/api/matches")
def api_matches():
    return jsonify(get_matches())


@app.route("/health")
def health():
    return "ok", 200


# ===== Локальный запуск =====
if __name__ == "__main__":
    # Локально можно прогреть кеш, но без фатала при ошибке
    try:
        fetch_matches()
    except Exception:
        pass
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)