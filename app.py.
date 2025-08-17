from flask import Flask, render_template_string, request
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
    day = request.args.get("date", dt.date.today().isoformat())
    rows = []
    for m in fixtures(day):
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        time = m["fixture"]["date"]
        rows.append(f"{time}: {home} vs {away}")
    html = "<h1>Матчи</h1><p>?date=YYYY-MM-DD</p><ul>" + "".join(f"<li>{x}</li>" for x in rows) + "</ul>"
    return render_template_string(html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
