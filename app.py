import requests
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify

app = Flask(__name__)

DB_NAME = "matches.db"

# создаём таблицу, если её ещё нет
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    team_a TEXT,
                    team_b TEXT,
                    halftime TEXT,
                    fulltime TEXT,
                    total_line TEXT,
                    handicap TEXT,
                    btts TEXT,
                    goals INTEGER
                )''')
    conn.commit()
    conn.close()

# функция загрузки матчей из API
def fetch_matches():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    today = datetime.today().date()

    for i in range(180):  # 180 дней назад
        date = today - timedelta(days=i)
        url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={date}"

        headers = {
            "x-rapidapi-key": "YOUR_API_KEY",  # замени на свой ключ
            "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
        }

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"Ошибка {r.status_code} при запросе {date}")
                continue

            data = r.json()
            if "response" not in data:
                continue

            for match in data["response"]:
                team_a = match["teams"]["home"]["name"]
                team_b = match["teams"]["away"]["name"]
                halftime = match["score"]["halftime"]["home"], match["score"]["halftime"]["away"]
                fulltime = match["score"]["fulltime"]["home"], match["score"]["fulltime"]["away"]
                goals = (fulltime[0] or 0) + (fulltime[1] or 0)

                # для простоты коэффициенты оставим пустыми
                c.execute('''INSERT INTO matches (date, team_a, team_b, halftime, fulltime, total_line, handicap, btts, goals)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (str(date), team_a, team_b,
                           f"{halftime[0]}-{halftime[1]}",
                           f"{fulltime[0]}-{fulltime[1]}",
                           "", "", "", goals))

        except Exception as e:
            print(f"Ошибка при обработке {date}: {e}")
            continue

    conn.commit()
    conn.close()

# маршрут главной страницы
@app.route("/")
def index():
    return render_template("index.html")

# API для отдачи матчей
@app.route("/api/matches")
def get_matches():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, team_a, team_b, halftime, fulltime, total_line, handicap, btts, goals FROM matches ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()

    matches = []
    for row in rows:
        matches.append({
            "date": row[0],
            "team_a": row[1],
            "team_b": row[2],
            "halftime": row[3],
            "fulltime": row[4],
            "total_line": row[5],
            "handicap": row[6],
            "btts": row[7],
            "goals": row[8]
        })

    return jsonify(matches)

if __name__ == "__main__":
    init_db()
    fetch_matches()
    app.run(host="0.0.0.0", port=5000)