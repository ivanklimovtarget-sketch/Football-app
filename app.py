import requests
import sqlite3
import datetime
import time
from flask import Flask, render_template

app = Flask(__name__)

DB_FILE = "matches.db"

# создаем таблицу (если её нет)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            team_a TEXT,
            team_b TEXT,
            score_half TEXT,
            score_final TEXT,
            total_line REAL,
            handicap REAL,
            both_to_score TEXT,
            goals_sum INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# сохраняем матч в базу
def save_match(date, team_a, team_b, score_half, score_final, total_line, handicap, both_to_score, goals_sum):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO matches (date, team_a, team_b, score_half, score_final, total_line, handicap, both_to_score, goals_sum)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, team_a, team_b, score_half, score_final, total_line, handicap, both_to_score, goals_sum))
    conn.commit()
    conn.close()

# получаем данные с API
def fetch_matches():
    today = datetime.date.today()
    days_back = 180  # полгода назад
    for i in range(days_back):
        date = today - datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        url = f"https://api.someservice.com/matches?date={date_str}"  # твой API
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for match in data.get("matches", []):
                    save_match(
                        date_str,
                        match["team_a"],
                        match["team_b"],
                        match.get("score_half", ""),
                        match.get("score_final", ""),
                        match.get("total_line", 0),
                        match.get("handicap", 0),
                        match.get("both_to_score", ""),
                        match.get("goals_sum", 0)
                    )
            else:
                print(f"Нет данных за {date_str}")
        except Exception as e:
            print(f"Ошибка при загрузке {date_str}: {e}")
        time.sleep(1)  # чтобы API не заблокировал

@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM matches ORDER BY date DESC LIMIT 50")
    matches = c.fetchall()
    conn.close()
    return render_template("index.html", matches=matches)

if __name__ == "__main__":
    init_db()
    fetch_matches()
    app.run(host="0.0.0.0", port=5000)