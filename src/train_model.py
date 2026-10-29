# train_model.py
# Run this once (or press "Retrain" in the app) to fit the model and save it.
#   python src/train_model.py
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import gold_model as gm

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.normpath(os.path.join(HERE, "..", "model"))


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = gm.load_data()
    res = gm.train(df)

    import joblib
    joblib.dump(res["model"], os.path.join(MODEL_DIR, "model.joblib"))

    meta = {
        "best_model": res["best_model"],
        "features": res["features"],
        "test_period": res["test_period"],
        "trained_on_rows": int(len(df)),
        "scores": res["scores"],
    }
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # chart: actual vs one-step-ahead predicted price over the test window
    X, y, feats = gm.make_xy(df)
    split = len(X) - 60
    te = feats.iloc[split:]
    pred_price = te["PrevPrice"].values * (1 + res["model"].predict(X.iloc[split:]))
    plt.figure(figsize=(9, 4))
    plt.plot(te["Date"], te["Price"], label="Actual", color="#1F3864")
    plt.plot(te["Date"], pred_price, label="Predicted", color="#C9A227")
    plt.title("Gold price - actual vs predicted (test window)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, "fit_chart.png"), dpi=120)
    plt.close()

    print("Model trained and saved to", MODEL_DIR)
    print("Best model:", res["best_model"], "| test from", res["test_period"])
    for name, sc in res["scores"].items():
        print("  %-16s MAE=%8.2f  RMSE=%8.2f  R2=%6.3f" % (name, sc["MAE"], sc["RMSE"], sc["R2"]))


if __name__ == "__main__":
    main()
