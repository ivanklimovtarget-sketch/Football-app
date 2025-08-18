import os
import time
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

# ========== НАСТРОЙКИ ==========
API_KEY = os.environ.get("8bd7548e336c4f338735954ad91ae239")  # ключ берём из переменных окружения
BASE_URL = "https://api.football-data.org/v4/matches"

DB_FILE = "matches.db"

app = Flask(__name__)

# ========== БАЗА ДАННЫХ ==========
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                date TEXT,
                home TEXT,
                away TEXT,
                score_home INTEGER,
                score_away INTEGER,
                status TEXT,
                total_line REAL,
                handicap_home REAL,
                oz INTEGER
            )
        """)
        conn.commit()

def save_matches(matches: list[dict]):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        for m in matches:
            c.execute("""
                INSERT OR REPLACE INTO matches
                (id, date, home, away, score_home, score_away, status, total_line, handicap_home, oz)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m["id"], m["date"], m["home"], m["away"],
                m["score_home"], m["score_away"], m["status"],
                m["total_line"], m["handicap_home"], m["oz"]
            ))
        conn.commit()

def load_matches(limit: int = 50):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM matches ORDER BY date DESC LIMIT ?", (limit,))
        return [dict(row) for row in c.fetchall()]

# ========== ЗАПРОСЫ К API ==========
def fetch_by_date(day_iso: str) -> list[dict]:
    params = {"dateFrom": day_iso, "dateTo": day_iso}
    headers = {"X-Auth-Token": API_KEY}
    r = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()

    items = data.get("matches") or []
    if isinstance(items, dict):  # на всякий случай
        items = list(items.values())

    result = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        result.append({
            "id": raw.get("id"),
            "date": (raw.get("utcDate") or "")[:10],
            "home": (raw.get("homeTeam") or {}).get("name"),
            "away": (raw.get("awayTeam") or {}).get("name"),
            "score_home": ((raw.get("score") or {}).get("fullTime") or {}).get("home"),
            "score_away": ((raw.get("score") or {}).get("fullTime") or {}).get("away"),
            "status": raw.get("status"),
            "total_line": None,
            "handicap_home": None,
            "oz": None,
        })
    return result

def fetch_history(days: int = 30) -> list[dict]:
    all_matches = []
    today = datetime.utcnow().date()
    for i in range(days):
        day = (today - timedelta(days=i)).isoformat()
        print("Загружаю:", day)
        all_matches.extend(fetch_by_date(day))
        time.sleep(1)  # защита от rate-limit API
    return all_matches

# ========== РОУТЫ ==========
@app.route("/")
def index():
    matches = load_matches(50)
    return render_template("index.html", matches=matches)

@app.route("/update", methods=["POST"])
def update():
    days = int(request.form.get("days", 1))
    matches = fetch_history(days)
    save_matches(matches)
    return jsonify({"status": "ok", "loaded": len(matches)})

# ========== СТАРТ ==========
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)