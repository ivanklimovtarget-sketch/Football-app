import os
import sqlite3
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

DB_FILE = "football.db"
API_URL = "https://api.football-data.org/v4/matches"
API_KEY = os.environ.get("8bd7548e336c4f338735954ad91ae239", "")  # ⚡ API ключ бери из переменных окружения Render


# ====== Работа с базой ======
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_matches(matches):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for match in matches:
        c.execute('''
            INSERT OR REPLACE INTO matches (id, home_team, away_team, home_score, away_score, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            match["id"],
            match["home_team"],
            match["away_team"],
            match["home_score"],
            match["away_score"],
            match["date"]
        ))
    conn.commit()
    conn.close()


def get_matches():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM matches ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "home_team": row[1],
            "away_team": row[2],
            "home_score": row[3],
            "away_score": row[4],
            "date": row[5]
        }
        for row in rows
    ]


# ====== API ======
def fetch_matches():
    headers = {"X-Auth-Token": API_KEY}
    params = {"dateFrom": "2025-08-15", "dateTo": "2025-08-25"}  # тестовый диапазон
    r = requests.get(API_URL, headers=headers, params=params)

    if r.status_code != 200:
        print("API Error:", r.json())
        return []

    data = r.json()
    matches = []
    for m in data.get("matches", []):
        matches.append({
            "id": m["id"],
            "home_team": m["homeTeam"]["name"],
            "away_team": m["awayTeam"]["name"],
            "home_score": m["score"]["fullTime"]["home"],
            "away_score": m["score"]["fullTime"]["away"],
            "date": m["utcDate"]
        })

    save_matches(matches)
    return matches


# ====== Маршруты ======
@app.route("/")
def index():
    matches = get_matches()
    return render_template("index.html", matches=matches)


@app.route("/api/matches")
def api_matches():
    return jsonify(get_matches())


# ====== Запуск ======
if __name__ == "__main__":
    init_db()
    fetch_matches()
    port = int(os.environ.get("PORT", 5000))  # ⚡ Render подставит сюда свой порт
    app.run(host="0.0.0.0", port=port)