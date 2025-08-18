from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Примеры прошедших матчей (можно потом заменить на реальные данные/API)
past_matches = [
    # date, teams, HT, FT, тотал-линия, фора(на хозяев), коэфы (примерные)
    {"date":"2025-08-10","home":"Барселона","away":"Реал Мадрид","ht":"1:0","ft":"2:1",
     "total_line":2.5,"handicap_home":-0.5,"k_over":1.95,"k_under":1.90,"k_btts_yes":1.70,"k_btts_no":2.10},
    {"date":"2025-08-11","home":"Ман Сити","away":"Арсенал","ht":"2:0","ft":"3:0",
     "total_line":2.5,"handicap_home":-1.0,"k_over":1.75,"k_under":2.10,"k_btts_yes":1.85,"k_btts_no":1.95},
    {"date":"2025-08-12","home":"Бавария","away":"Боруссия Д","ht":"0:1","ft":"1:1",
     "total_line":2.5,"handicap_home":-0.25,"k_over":1.85,"k_under":2.00,"k_btts_yes":1.65,"k_btts_no":2.20},
    {"date":"2025-08-13","home":"Интер","away":"Ювентус","ht":"0:0","ft":"0:1",
     "total_line":2.25,"handicap_home":0.0,"k_over":2.02,"k_under":1.82,"k_btts_yes":2.05,"k_btts_no":1.75},
    {"date":"2025-08-14","home":"ПСЖ","away":"Марсель","ht":"1:1","ft":"3:2",
     "total_line":3.0,"handicap_home":-1.0,"k_over":2.05,"k_under":1.78,"k_btts_yes":1.60,"k_btts_no":2.30},
    {"date":"2025-08-15","home":"Челси","away":"Ливерпуль","ht":"0:1","ft":"1:2",
     "total_line":2.75,"handicap_home":0.25,"k_over":1.98,"k_under":1.86,"k_btts_yes":1.72,"k_btts_no":2.15},
    {"date":"2025-08-16","home":"Атлетико","away":"Севилья","ht":"1:1","ft":"2:1",
     "total_line":2.25,"handicap_home":-0.25,"k_over":1.90,"k_under":1.92,"k_btts_yes":1.95,"k_btts_no":1.85},
    {"date":"2025-08-17","home":"Наполи","away":"Рома","ht":"0:0","ft":"1:0",
     "total_line":2.25,"handicap_home":-0.5,"k_over":2.00,"k_under":1.82,"k_btts_yes":1.90,"k_btts_no":1.90},
]

def parse_score(s):
    a,b = s.split(":"); return int(a), int(b)

def approx(a, b, tol=0.05):
    try:
        return abs(float(a) - float(b)) <= tol
    except:
        return False

def analyze(history, form):
    stats = {}
    # TOTAL
    tl = form.get("total_line")
    kov = form.get("k_over")
    kund = form.get("k_under")
    if tl:
        tl = float(tl)
        subset = [m for m in history if m["total_line"] == tl and (
                  not kov or approx(m["k_over"], kov) or
                  not kund or approx(m["k_under"], kund))]
        wins_over = sum( (lambda x: sum(parse_score(x["ft"])) > tl)(m) for m in subset )
        stats["total"] = {"n":len(subset), "wins_over":wins_over,
                          "p_over": round(100*wins_over/len(subset),1) if subset else 0}
    # HANDICAP (на хозяев)
    hcap = form.get("handicap_home")
    kh = form.get("k_handicap_home")
    if hcap:
        h = float(hcap)
        subset = [m for m in history if m["handicap_home"] == h and (not kh or approx(m["k_handicap_home"] if "k_handicap_home" in m else m["k_over"], kh))]
        def cover(m):
            hgs, ags = parse_score(m["ft"])
            return (hgs + h) > ags  # простая проверка прохода форы -0.5/-1.0 и т.п.
        wins = sum(cover(m) for m in subset)
        stats["handicap"] = {"n":len(subset), "wins":wins,
                             "p": round(100*wins/len(subset),1) if subset else 0}
    # BTTS
    ky = form.get("k_btts_yes"); kn = form.get("k_btts_no")
    if ky or kn:
        subset = [m for m in history if (not ky or approx(m["k_btts_yes"], ky)) or (not kn or approx(m["k_btts_no"], kn))]
        wins_yes = sum( (lambda x: all(v>0 for v in parse_score(x["ft"])))(m) for m in subset)
        stats["btts"] = {"n":len(subset), "yes":wins_yes,
                         "p_yes": round(100*wins_yes/len(subset),1) if subset else 0}
    return stats

@app.route("/", methods=["GET", "POST"])
def index():
    stats = {}
    if request.method == "POST":
        stats = analyze(past_matches, request.form)
    # подготовим поля для таблицы
    rows = []
    for m in past_matches:
        ht1, ht2 = parse_score(m["ht"]); ft1, ft2 = parse_score(m["ft"])
        rows.append({
            **m,
            "sum_goals": ft1+ft2,
            "btts": "Да" if ft1>0 and ft2>0 else "Нет"
        })
    return render_template("index.html", matches=rows, stats=stats, today=datetime.today().strftime("%d.%m.%Y"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
