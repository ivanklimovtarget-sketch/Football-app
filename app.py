import os
from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = os.getenv("8bd7548e336c4f338735954ad91ae239")  # ключ в Render → Environment
headers = {"X-Auth-Token": API_KEY}

# Доступные турниры (можешь расширять список)
COMPETITIONS = {
    "PL": "Английская Премьер-лига",
    "PD": "Ла Лига (Испания)",
    "SA": "Серия А (Италия)",
    "BL1": "Бундеслига (Германия)",
    "FL1": "Лига 1 (Франция)",
    "CL": "Лига Чемпионов"
}


def fetch_matches(page, competition=None, page_size=20):
    """Забираем матчи за последние полгода с API"""
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

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        matches = data.get("matches", [])

        # постраничный вывод
        start = (page - 1) * page_size
        end = start + page_size
        paginated_matches = matches[start:end]

        total_pages = (len(matches) + page_size - 1) // page_size

        return paginated_matches, total_pages
    except Exception as e:
        print(f"Ошибка при запросе API: {e}")
        return [], 0


@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    competition = request.args.get("competition", None)

    matches, total_pages = fetch_matches(page, competition)

    return render_template(
        "index.html",
        matches=matches,
        page=page,
        total_pages=total_pages,
        competitions=COMPETITIONS,
        current_competition=competition,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))