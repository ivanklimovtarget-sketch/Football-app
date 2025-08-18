import os
from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# ⚽ ТВОЙ API ключ ВСТАВЬ СЮДА
API_KEY = "8bd7548e336c4f338735954ad912..."   # <-- замени на свой ключ
headers = {"X-Auth-Token": API_KEY}

# Доступные турниры
COMPETITIONS = {
    "PL": "Английская Премьер-лига",
    "PD": "Ла Лига (Испания)",
    "SA": "Серия А (Италия)",
    "BL1": "Бундеслига (Германия)",
    "FL1": "Лига 1 (Франция)",
    "CL": "Лига Чемпионов"
}

def fetch_matches(page, competition=None, page_size=20):
    """Забираем матчи за последние полгода"""
    today = datetime.today()
    date_from = (today - timedelta(days=180)).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")

    params = {
        "dateFrom": date_from,
        "dateTo": date_to,
    }

    if competition:
        url = f"https://api.football-data.org/v4/competitions/{competition}/matches"
    else:
        url = "https://api.football-data.org/v4/matches"

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Ошибка запроса:", response.text)
        return []

    data = response.json()
    matches = data.get("matches", [])

    # Пагинация по 20 матчей
    start = (page - 1) * page_size
    end = start + page_size
    return matches[start:end]

@app.route("/")
def index():
    page = int(request.args.get("page", 1))
    competition = request.args.get("competition")

    matches = fetch_matches(page, competition)

    return render_template(
        "index.html",
        matches=matches,
        competitions=COMPETITIONS,
        current_competition=competition,
        page=page
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)