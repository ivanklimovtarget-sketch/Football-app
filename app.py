import sqlite3
import requests
import time
from threading import Thread
from flask import Flask, render_template

app = Flask(__name__)

API_KEY = "8bd7548e336c4f338735954ad91ae239"
DB_FILE = "matches.db"

# Создание базы если нет
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            team_home TEXT,
            team_away TEXT,
            score_home INTEGER,
            score_away INTEGER,
            total_line REAL,
            handicap REAL,
            bts TEXT
        )
    """)
    conn.commit()
    conn.close()

# Функция подгрузки матчей
def fetch_matches():
    while True:
        try:
            # пример запроса, можно менять дату на today
            url = f"https://api.sportsdata.io/v4/soccer/scores/json/GamesByDate/2025-AUG-18?key={API_KEY}"
            data = requests.get(url).json()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            for m in data:
                cursor.execute("""
                    INSERT OR IGNORE INTO matches
                    (date, team_home, team_away, score_home, score_away, total_line, handicap, bts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    m.get("Day"),
                    m.get("HomeTeamName"),
                    m.get("AwayTeamName"),
                    m.get("HomeTeamScore"),
                    m.get("AwayTeamScore"),
                    2.5,    # пока фикс, потом можно динамически
                    -0.5,   # тоже фикс
                    "Да" if (m.get("HomeTeamScore") and m.get("AwayTeamScore")) else "Нет"
                ))

            conn.commit()
            conn.close()
            print("✅ Матчи обновлены")

        except Exception as e:
            print("❌ Ошибка обновления:", e)

        time.sleep(1800)  # каждые 30 минут

@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT date, team_home, team_away, score_home, score_away, total_line, handicap, bts FROM matches ORDER BY date DESC LIMIT 20")
    matches = cursor.fetchall()
    conn.close()

    return render_template("index.html", matches=matches)

if __name__ == "__main__":
    init_db()
    Thread(target=fetch_matches, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)