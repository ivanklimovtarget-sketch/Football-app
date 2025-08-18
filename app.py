from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

API_KEY = os.getenv("8bd7548e336c4f338735954ad91ae239")  
DB_NAME = "matches.db"

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

def fetch_history(days=180):
    today = datetime.today()
    for i in range(days):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        print("Загружаю:", day)
        fetch_by_date(day)

def get_matches(limit=20, offset=0):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT date, home_team, away_team, score_home, score_away
        FROM matches
        ORDER BY date DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    matches = c.fetchall()
    conn.close()
    return matches

@app.route("/")
def index():
    init_db()
    today = datetime.today().strftime("%Y-%m-%d")
    fetch_by_date(today)

    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page

    matches = get_matches(limit=per_page, offset=offset)

    return render_template("index.html", matches=matches, page=page)

if __name__ == "__main__":
    init_db()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM matches")
    count = c.fetchone()[0]
    conn.close()

    if count == 0:
        fetch_history(180)

    app.run(host="0.0.0.0", port=5000)