import sys
import requests
from flask import Flask, render_template, jsonify

# Перехват ошибок
def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("⚠️ Поймана ошибка:", exc_value, file=sys.stderr)

sys.excepthook = log_exception

# Flask-приложение
app = Flask(__name__)

# ⚠️ Замени на свой API-ключ с football-data.org
API_KEY = "8bd7548e336c4f338735954ad91ae239"
BASE_URL = "https://api.football-data.org/v4/matches"

# Функция получения матчей
def get_matches():
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(BASE_URL, headers=headers)

    matches = []
    if response.status_code == 200:
        data = response.json()
        for match in data.get("matches", []):
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            score_home = match["score"]["fullTime"]["home"]
            score_away = match["score"]["fullTime"]["away"]
            status = match["status"]

            matches.append({
                "home": home,
                "away": away,
                "score": f"{score_home if score_home is not None else 0} : {score_away if score_away is not None else 0}",
                "status": status
            })
    return matches

# Главная страница
@app.route("/")
def index():
    matches = get_matches()
    return render_template("index.html", matches=matches)

# API для AJAX-обновлений
@app.route("/api/matches")
def api_matches():
    return jsonify(get_matches())

# Запуск (локально)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)