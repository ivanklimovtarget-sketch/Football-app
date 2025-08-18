import os
import sqlite3
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

DB_NAME = "matches.db"
API_URL = "https://api.football-data.org/v4/matches"
API_KEY = os.getenv("8bd7548e336c4f338735954ad91ae239")  # <-- ключ теперь берётся из переменных окружения


# ===== База данных =====
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id INTEGER PRIMARY KEY,
                  home_team TEXT,
                  away_team TEXT,
                  home_score INTEGER,
                  away_score INTEGER,
                  date TEXT)''')
    conn.commit()
    conn.close()


def save_matches(matches):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for m in matches:
        c.execute('''INSERT OR REPLACE INTO matches
                     (id, home_team, away_team, home_score, away_score, date)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (m["id"], m["home_team"], m["away_team"],
                   m["home_score"], m["away_score"], m["date"]))
    conn.commit()
    conn.close()


def get_matches():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM matches")
    rows = c.fetchall()
    conn.close()

    matches = []
    for r in rows:
        matches.append({
            "id": r[0],
            "home_team": r[1],
            "away_team": r[2],
            "home_score": r[3],
            "away_score": r[4],
            "date": r[5]
        })
    return matches


# ===== Работа с API =====
def fetch_matches():
    headers = {"X-Auth-Token": API_KEY}
    try:
        r = requests.get(API_URL, headers=headers, timeout=10)
        if r.status_code != 200:
            print("Ошибка API:", r.status_code, r.text)
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
    except Exception as e:
        print("Ошибка при запросе API:", e)
        return []


# ===== Маршруты =====
@app.route("/")
def index():
    matches = get_matches()
    return render_template("index.html", matches=matches)


@app.route("/api/matches")
def api_matches():
    return jsonify(get_matches())


# ===== Запуск =====
if __name__ == "__main__":
    init_db()
    fetch_matches()
    # локально можно запускать app.run(), но на Render/Heroku запускается через gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))