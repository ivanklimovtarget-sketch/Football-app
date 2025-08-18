from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# <-- вставь свой ключ сюда один раз -->
API_TOKEN = "8bd7548e336c4f338735954ad91ae239"

# Какие турниры берём (можешь расширять список)
COMP_CODES = ["PL", "PD", "SA", "BL1", "FL1", "CL"]  # АПЛ, Ла Лига, Серия A, Бундеслига, Лига 1, ЛЧ

def fetch_matches_last_6_months():
    """Собираем матчи за последние 6 месяцев и нормализуем поля,
    чтобы в шаблоне не было ошибок вида 'dict object has no attribute ...'."""
    headers = {"X-Auth-Token": API_TOKEN}
    today = datetime.utcnow().date()
    date_from = (today - timedelta(days=180)).isoformat()
    date_to = today.isoformat()

    raw = []
    for code in COMP_CODES:
        url = f"https://api.football-data.org/v4/competitions/{code}/matches"
        params = {"dateFrom": date_from, "dateTo": date_to}
        try:
            r = requests.get(url, headers=headers, params=params, timeout=20)
            if r.status_code == 200:
                raw.extend(r.json().get("matches", []))
            else:
                # просто пропускаем проблемный турнир
                continue
        except Exception:
            continue

    # Нормализация — оставляем только нужные, с дефолтами
    norm = []
    for m in raw:
        comp_name = (m.get("competition") or {}).get("name") or ""
        utc = m.get("utcDate") or ""
        home = (m.get("homeTeam") or {}).get("name") or ""
        away = (m.get("awayTeam") or {}).get("name") or ""
        score_ft = (m.get("score") or {}).get("fullTime") or {}
        sh = score_ft.get("home")
        sa = score_ft.get("away")
        status = m.get("status") or ""

        if not utc or not home or not away:
            continue

        norm.append({
            "date": utc[:10],
            "competition": comp_name,
            "home": home,
            "away": away,
            "score_home": "–" if sh is None else sh,
            "score_away": "–" if sa is None else sa,
            "status": status
        })

    # Сортировка от новых к старым
    norm.sort(key=lambda x: x["date"], reverse=True)
    return norm


@app.route("/")
def index():
    tournament = request.args.get("tournament", "all")
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    per_page = 20

    matches = fetch_matches_last_6_months()

    tournaments = sorted({m["competition"] for m in matches if m["competition"]})

    if tournament != "all":
        matches = [m for m in matches if m["competition"] == tournament]

    total = len(matches)
    start = (page - 1) * per_page
    end = start + per_page
    matches_page = matches[start:end]
    total_pages = (total + per_page - 1) // per_page if total else 1

    return render_template(
        "index.html",
        matches=matches_page,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        tournament=tournament,
        tournaments=tournaments
    )


if __name__ == "__main__":
    app.run(debug=True)