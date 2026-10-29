# price_model.py
# Shared model code - the trainer and the dashboard both import this file.
#
# We do NOT ask the model to guess the raw price. A tree model can never
# extrapolate a rising trend, so it looks broken. Instead the model predicts the
# month to month RETURN, which stays in a small stable range. To get a price back
# we multiply last month's price by (1 + predicted return).
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
FEATURES = ["ret1", "ret2", "ret3", "Month", "Year"]

# model file per metal, so gold and silver never get mixed up
METALS = {
    "gold": {
        "csv": os.path.join(ROOT, "data", "gold_prices.csv"),
        "job": os.path.join(ROOT, "model", "gold_model.joblib"),
    },
    "silver": {
        "csv": os.path.join(ROOT, "data", "silver_prices.csv"),
        "job": os.path.join(ROOT, "model", "silver_model.joblib"),
    },
}


def load_data(metal):
    df = pd.read_csv(METALS[metal]["csv"])
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m")
    return df[["Date", "Year", "Month", "Price"]].copy()


def build_features(df):
    out = df.copy()
    out["ret"] = out["Price"].pct_change()      # this month's return = the target
    out["PrevPrice"] = out["Price"].shift(1)    # needed to turn a return into a price
    out["ret1"] = out["ret"].shift(1)           # the last 3 returns are the clues
    out["ret2"] = out["ret"].shift(2)
    out["ret3"] = out["ret"].shift(3)
    return out.dropna().reset_index(drop=True)


def make_xy(df):
    feats = build_features(df)
    return feats[FEATURES], feats["ret"], feats


def _price_metrics(actual_price, prev_price, pred_ret):
    # score in dollars per ounce - easier to trust than a raw return error
    pred_price = prev_price * (1 + pred_ret)
    return {
        "MAE": round(float(mean_absolute_error(actual_price, pred_price)), 2),
        "RMSE": round(float(np.sqrt(mean_squared_error(actual_price, pred_price))), 2),
        "R2": round(float(r2_score(actual_price, pred_price)), 4),
    }


def train(df, test_months=60):
    X, y, feats = make_xy(df)
    split = len(X) - test_months
    X_tr, X_te, y_tr, y_te = X.iloc[:split], X.iloc[split:], y.iloc[:split], y.iloc[split:]
    act = feats.iloc[split:]["Price"].values
    prev = feats.iloc[split:]["PrevPrice"].values

    models = {
        "RandomForest": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(),
    }
    best_name, best_mae, best_model = None, 1e18, None
    scores = {}
    for name, mdl in models.items():
        mdl.fit(X_tr, y_tr)
        sc = _price_metrics(act, prev, mdl.predict(X_te))
        scores[name] = sc
        if sc["MAE"] < best_mae:
            best_mae, best_name, best_model = sc["MAE"], name, mdl

    # plain "next month = this month" so the numbers can be compared honestly
    scores["Naive"] = _price_metrics(act, prev, np.zeros(len(act)))

    return {
        "model": best_model,
        "best_model": best_name,
        "features": FEATURES,
        "test_period": str(feats.iloc[split]["Date"].date()),
        "scores": scores,
    }


def forecast(model, last_prices, start_year, start_month, months_ahead):
    # roll the prediction forward one month at a time, feeding each answer back in
    prices = list(last_prices)
    rets = []
    for i in range(len(prices) - 1, 0, -1):
        rets.append(prices[i] / prices[i - 1] - 1)
    rets = rets[:3]                      # rets[0] = most recent return
    while len(rets) < 3:
        rets.append(0.0)

    preds = []
    year, month = start_year, start_month
    for _ in range(months_ahead):
        row = pd.DataFrame([[rets[0], rets[1], rets[2], month, year]], columns=FEATURES)
        r = float(model.predict(row)[0])
        new_price = prices[-1] * (1 + r)
        prices.append(new_price)
        rets = [r, rets[0], rets[1]]
        preds.append(("%04d-%02d" % (year, month), round(new_price, 2)))
        month += 1
        if month > 12:
            month, year = 1, year + 1
    return preds
