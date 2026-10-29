# dashboard.py
# Starts the local web dashboard. This is the main entry point of the project:
#   python src/dashboard.py
# It opens http://127.0.0.1:8000 in your default browser.
#
# The page shows live gold / silver prices in Indian Rupees (from the public
# APIs in live_prices.py), the price history, and the machine learning forecast
# for the next 12 months. Nothing is uploaded anywhere - the model runs locally.
import json
import os
import socket
import threading
import time
import webbrowser
from collections import deque

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template

import live_prices
import price_model as pm

ROOT = pm.ROOT
METRICS_PATH = os.path.join(ROOT, "model", "metrics.json")
HOST, PORT = "127.0.0.1", 8000
GRAMS = live_prices.GRAMS_PER_OUNCE
FORECAST_MONTHS = 12
LIVE_CACHE_SECONDS = 12

app = Flask(__name__)
_live_lock = threading.Lock()
_live = {"ts": 0.0, "data": None}
# the last minute or so of prices, just to show the tick moving on screen
TICKS = deque(maxlen=60)


def usd_to_inr_gram(usd_oz, rate):
    return usd_oz * rate / GRAMS


def get_live(force=False):
    # only hit the internet once in a while even if the page is refreshed a lot
    with _live_lock:
        now = time.time()
        if not force and _live["data"] and now - _live["ts"] < LIVE_CACHE_SECONDS:
            return _live["data"]
        data = live_prices.fetch()
        _live["ts"], _live["data"] = now, data
        return data


def month_label(ym):
    d = pd.to_datetime(ym, format="%Y-%m")
    return d.strftime("%b %y")


def history_block(metal, live_usd, rate):
    """Monthly history plus today's live price as the last point."""
    df = pm.load_data(metal)
    dates = [month_label(d) for d in df["Date"].dt.strftime("%Y-%m")]
    prices = [round(usd_to_inr_gram(p, rate), 2) for p in df["Price"]]
    hist_usd = list(df["Price"])
    if live_usd:
        dates.append("Today")
        prices.append(round(usd_to_inr_gram(live_usd, rate), 2))
        hist_usd.append(live_usd)
    return {"dates": dates, "inr_gram": prices, "usd_oz": hist_usd}


def forecast_block(metal, seed_usd, rate, start):
    model = joblib.load(pm.METALS[metal]["job"])
    hist = pm.load_data(metal)
    last_prices = list(hist["Price"].tail(4)) + [seed_usd]
    raw = pm.forecast(model, last_prices, start.year, start.month, FORECAST_MONTHS)
    rows = []
    for ym, usd in raw:
        rows.append({
            "month": month_label(ym),
            "usd_ounce": usd,
            "inr_gram": round(usd_to_inr_gram(usd, rate), 2),
            "inr_kg": round(usd_to_inr_gram(usd, rate) * 1000, 2),
        })
    return rows


def next_month():
    today = pd.Timestamp.today()
    first = today + pd.offsets.MonthBegin(1)
    return pd.Timestamp(first)


def build_summary(metal, live_usd, rate):
    block = {"live": None, "history": {}, "forecast": []}
    if live_usd and rate:
        live_inr = round(usd_to_inr_gram(live_usd, rate), 2)
        hist = block["history"] = history_block(metal, live_usd, rate)
        block["forecast"] = forecast_block(metal, live_usd, rate, next_month())
        prev_month = hist["inr_gram"][-2] if len(hist["inr_gram"]) > 1 else live_inr
        block["live"] = {
            "usd_ounce": round(live_usd, 2),
            "inr_gram": live_inr,
            "inr_kg": round(live_inr * 1000, 2),
            "month_change_pct": round((live_inr / prev_month - 1) * 100, 2),
            "year_change_pct": round((live_inr / hist["inr_gram"][-13] - 1) * 100, 2)
            if len(hist["inr_gram"]) > 13 else None,
        }
    else:
        block["history"] = history_block(metal, None, rate or 0)
    return block


def metrics_block():
    if not os.path.exists(METRICS_PATH):
        return {}
    with open(METRICS_PATH) as f:
        return json.load(f)


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/api/summary")
def api_summary():
    live = get_live()
    rate = live.get("usd_inr") or live_prices.FALLBACK_RATE
    metals = live.get("metals", {})
    out = {
        "status": "live" if not live.get("stale") and live.get("ok") else "offline",
        "stale": bool(live.get("stale")),
        "error": live.get("error", ""),
        "usd_inr": rate,
        "fetched_at": live.get("fetched_at"),
        "rupee_note": "Historical US$ prices are shown in Rs at today's exchange rate (Rs %.2f per $)." % (rate or 0),
        "metals": {},
        "metrics": metrics_block(),
    }
    for metal in ("gold", "silver"):
        usd = metals.get(metal, {}).get("usd_ounce")
        out["metals"][metal] = build_summary(metal, usd, rate)

    gold = out["metals"]["gold"].get("live")
    silver = out["metals"]["silver"].get("live")
    if gold and silver and not out["stale"]:
        TICKS.append({"t": time.strftime("%H:%M:%S"),
                      "gold": gold["inr_gram"], "silver": silver["inr_gram"]})
    out["ticks"] = list(TICKS)
    return jsonify(out)


@app.route("/api/refresh")
def api_refresh():
    get_live(force=True)
    return api_summary()


def ensure_models():
    # a fresh clone has no saved models - train them once so the dashboard just works
    need = not os.path.exists(METRICS_PATH)
    for metal in pm.METALS:
        if not os.path.exists(pm.METALS[metal]["job"]):
            need = True
    if need:
        print("First run - training the gold and silver models, one moment...")
        import train_model
        train_model.main()


def already_running():
    # Flask allows the port to be reused, so a second copy would quietly start too and
    # the browser would end up talking to a stale one - check before we bind.
    with socket.socket() as s:
        s.settimeout(0.6)
        return s.connect_ex((HOST, PORT)) == 0


def main():
    url = "http://%s:%d" % (HOST, PORT)
    if already_running():
        print("Dashboard is already open - just starting the browser.")
        webbrowser.open(url)
        return
    ensure_models()
    print("Gold & Silver Price Predictor dashboard")
    print("  open ", url)
    print("  press Ctrl+C to stop")
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
