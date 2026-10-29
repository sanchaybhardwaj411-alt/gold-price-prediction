# live_prices.py
# Fetches the real gold and silver price from the internet and converts it to
# Indian Rupees per gram / per kg.
#
#   api.gold-api.com        -> price of 1 troy ounce in USD (no key needed)
#   open.er-api.com         -> today's USD to INR exchange rate (no key needed)
#
# If the internet is down we fall back on data/live_cache.json (the last price
# we managed to fetch) so the dashboard still opens. The "stale" flag in the
# result tells the UI to show a "reconnecting" warning instead of real numbers.
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.normpath(os.path.join(HERE, "..", "data", "live_cache.json"))

GRAMS_PER_OUNCE = 31.1034768  # one troy ounce = 31.1035 grams
FALLBACK_RATE = 95.0          # only used if the API and the cache both fail

ENDPOINTS = {
    "gold": "https://api.gold-api.com/price/XAU",
    "silver": "https://api.gold-api.com/price/XAG",
}
RATE_URL = "https://open.er-api.com/v6/latest/USD"


def _get_json(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "gold-price-dashboard/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _save_cache(data):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w") as f:
        json.dump(data, f, indent=2)


def _load_cache():
    if not os.path.exists(CACHE):
        return None
    with open(CACHE) as f:
        return json.load(f)


def _bundle(usd_oz, rate, source):
    # build the rupee numbers for one metal
    inr_gram = usd_oz * rate / GRAMS_PER_OUNCE
    return {
        "usd_ounce": round(usd_oz, 2),
        "inr_gram": round(inr_gram, 2),
        "inr_kg": round(inr_gram * 1000, 2),
        "source": source,
    }


def fetch():
    """Return live gold + silver prices in INR. Never raises."""
    try:
        rate = float(_get_json(RATE_URL)["rates"]["INR"])
        out = {
            "ok": True,
            "stale": False,
            "usd_inr": round(rate, 3),
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metals": {},
        }
        for metal, url in ENDPOINTS.items():
            usd = float(_get_json(url)["price"])
            out["metals"][metal] = _bundle(usd, rate, "live api")
        _save_cache(out)
        return out
    except Exception as e:
        cached = _load_cache()
        if cached is None:
            return {"ok": False, "stale": True, "error": str(e), "metals": {}}
        cached["stale"] = True
        cached["error"] = str(e)
        for m in cached.get("metals", {}):
            cached["metals"][m]["source"] = "cached (offline)"
        return cached


if __name__ == "__main__":
    p = fetch()
    print(json.dumps(p, indent=2))
