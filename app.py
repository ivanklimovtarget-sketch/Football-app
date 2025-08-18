from flask import Flask, render_template
import sqlite3
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

API_KEY = os.getenv("8bd7548e336c4f338735954ad91ae239")  # ключ из Render
DB_NAME = "matches.db"

# Создание таблицы
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            date TEXT,
            home_team TEXT,
            away_team TEXT,
            score_home INTEGER,
            score_away INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Подгрузка матчей по дате
def fetch_by_date(date):
    url = f"https://api.sportsdata.io/v4/soccer/scores/json/GamesByDate/{date}?key={API_KEY}"
    try:
        data = requests.get(url).json()
    except:
        return []

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    for m in data:
        match_id = m.get("GameId")
        home = m.get("HomeTeamName")
        away = m.get("AwayTeamName")
        score_home = m.get("HomeTeamScore")
        score_away = m.get("AwayTeamScore")

        c.execute("""
            INSERT OR IGNORE INTO matches (id, date, home_team, away_team, score_home, score_away)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (match_id, date, home, away, score_home, score_away))

    conn.commit()
    conn.close()

# Подгрузка истории за N дней
def fetch_history(days=180):
    today = datetime.today()
    for i in range(days):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        print("Загружаю:", day)
        fetch_by_date(day)

# Получить последние N матчей
def get_last_matches(n=20):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, home_team, away_team, score_home, score_away FROM matches ORDER BY date DESC LIMIT ?", (n,))
    matches = c.fetchall()
    conn.close()
    return matches

@app.route("/")
def index():
    init_db()
    # всегда проверяем новые матчи
    today = datetime.today().strftime("%Y-%m-%d")
    fetch_by_date(today)

    matches = get_last_matches(20)
    return render_template("index.html", matches=matches)

if __name__ == "__main__":
    init_db()
    # если база пустая — загружаем историю за полгода
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM matches")
    count = c.fetchone()[0]
    conn.close()

    if count == 0:
        fetch_history(180)

    app.run(host="0.0.0.0", port=5000)