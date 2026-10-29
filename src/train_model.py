# train_model.py
# Fits a forecaster for gold and for silver and saves them into model/.
#   python src/train_model.py
# The dashboard reads model/metrics.json, so run this after changing anything.
import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import price_model as pm

MODEL_DIR = os.path.join(pm.ROOT, "model")


def train_one(metal):
    df = pm.load_data(metal)
    res = pm.train(df)
    joblib.dump(res["model"], os.path.join(MODEL_DIR, "%s_model.joblib" % metal))

    # chart: actual vs one-step-ahead predicted price over the test window
    X, y, feats = pm.make_xy(df)
    split = len(X) - 60
    te = feats.iloc[split:]
    pred_price = te["PrevPrice"].values * (1 + res["model"].predict(X.iloc[split:]))
    plt.figure(figsize=(9, 4))
    plt.plot(te["Date"], te["Price"], label="Actual", color="#1F3864")
    plt.plot(te["Date"], pred_price, label="Predicted", color="#C9A227")
    plt.title("%s price - actual vs predicted (test window)" % metal.capitalize())
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, "%s_fit_chart.png" % metal), dpi=120)
    plt.close()

    return {
        "best_model": res["best_model"],
        "features": res["features"],
        "test_period": res["test_period"],
        "trained_on_rows": int(len(df)),
        "last_month": str(df.iloc[-1]["Date"].date()),
        "scores": res["scores"],
    }


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    out = {}
    for metal in pm.METALS:
        print("\n=== %s ===" % metal.upper())
        out[metal] = train_one(metal)
        print("best:", out[metal]["best_model"], "| test from", out[metal]["test_period"])
        for name, sc in out[metal]["scores"].items():
            print("  %-16s MAE=%9.2f  RMSE=%9.2f  R2=%6.3f"
                  % (name, sc["MAE"], sc["RMSE"], sc["R2"]))

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nsaved models + model/metrics.json")


if __name__ == "__main__":
    main()
