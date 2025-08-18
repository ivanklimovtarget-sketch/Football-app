import sys
import requests
from flask import Flask, render_template, jsonify

# Перехват всех ошибок и вывод в консоль
def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("⚠️ Поймана ошибка:", exc_value, file=sys.stderr)

sys.excepthook = log_exception

# Создаём Flask-приложение
app = Flask(__name__)

# ⚠️ Вставь сюда свой ключ с football-data.org
API_KEY = "ТВОЙ_API_KEY"
BASE_URL = "https://api.football-data.org/v4/matches"

# Функция для получения матчей
def get_matches():
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(BASE_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        matches = []
        for match in data.get("matches", []):
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            score_home = match["score"]["fullTime"]["home"]
            score_away = match["score"]["fullTime"]["away"]
            status = match["status"]

            matches.append({
                "home": home,
                "away": away,
                "score": f"{score_home} : {score_away}",
                "status": status
            })
        return matches
    else:
        print("Ошибка API:", response.status_code, response.text)
        return []

# Роут главной страницы
@app.route("/")
def index():
    matches = get_matches()
    return jsonify(matches)  # пока отдаём в JSON для проверки

# Точка входа
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)