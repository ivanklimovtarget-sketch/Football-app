from flask import Flask, render_template, request
import os, requests, datetime as dt

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

app = Flask(__name__)

def fixtures(day, league=39, season=2025):
    url = f"{BASE_URL}/fixtures"
    r = requests.get(url, headers=HEADERS,
                     params={"date": day, "league": league, "season": season})
    return r.json().get("response", [])

@app.route("/")
def index():
    # Берём дату из параметра запроса (?date=2025-08-18),
    # если её нет, то используем сегодняшнюю
    date = request.args.get("date")
    if not date:
        date = dt.datetime.today().strftime("%Y-%m-%d")

    matches = fixtures(date)

    return render_template("index.html", matches=matches, date=date)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
