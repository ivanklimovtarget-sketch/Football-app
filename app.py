import requests
import sqlite3
from datetime import datetime, timedelta

API_KEY = "ТВОЙ_API_КЛЮЧ"   # вставь сюда свой ключ
DB_FILE = "matches.db"

# Создание таблицы, если нет
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            date TEXT,
            home_team TEXT,
            away_team TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Сохраняем матч в базу
def save_match(game_id, date, home, away, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO matches (game_id, date, home_team, away_team, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (game_id, date, home, away, status))
    conn.commit()
    conn.close()

# Получение матчей за 1 день
def fetch_by_date(day):
    url = f"https://api.sportsdata.io/v4/soccer/scores/json/GamesByDate/{day}?key={API_KEY}"
    response = requests.get(url)

    try:
        data = response.json()
    except Exception as e:
        print(f"Ошибка парсинга JSON за {day}: {e}")
        return

    if not isinstance(data, list):
        print(f"⚠ API вернуло не список за {day}: {data}")
        return

    for m in data:
        if isinstance(m, dict):
            game_id = m.get("GameId")
            home = m.get("HomeTeamName")
            away = m.get("AwayTeamName")
            status = m.get("Status")

            print(f"{day}: {home} vs {away} ({status})")
            save_match(game_id, day, home, away, status)

# Получение матчей за последние N дней
def fetch_history(days=180):
    today = datetime.today()
    for i in range(days):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"Загружаю: {day}")
        fetch_by_date(day)

if __name__ == "__main__":
    init_db()
    fetch_history(180)   # загружаем полгода назад