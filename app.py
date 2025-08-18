from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "ТВОЙ_API_KEY"  # 8bd7548e336c4f338735954ad91ae239вставь сюда ключ
BASE_URL = "https://api.football-data.org/v4/matches"

def get_matches():
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(BASE_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        matches = []
        for match in data.get("matches", []):
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            score_home = match["score"]["fullTime"]["home"] if match["score"]["fullTime"]["home"] is not None else "-"
            score_away = match["score"]["fullTime"]["away"] if match["score"]["fullTime"]["away"] is not None else "-"
            status = match["status"]

            matches.append({
                "home": home,
                "away": away,
                "score": f"{score_home}:{score_away}",
                "status": status
            })
        return matches
    else:
        print("Ошибка API:", response.status_code, response.text)
        return []

@app.route("/")
def index():
    matches = get_matches()
    return render_template("index.html", matches=matches)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)