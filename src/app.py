# app.py
# Gold Price Predictor - desktop GUI (tkinter + matplotlib).
# Run:  python src/app.py
import json
import os
import threading
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox

import joblib
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gold_model as gm

NAVY = "#1F3864"
GOLD = "#C9A227"
BG = "#F4F6FB"
PANEL = "#FFFFFF"
TXT = "#222222"
MUT = "#6B7280"

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.normpath(os.path.join(HERE, "..", "model"))
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
META_PATH = os.path.join(MODEL_DIR, "metrics.json")


class GoldApp:
    def __init__(self, root):
        self.root = root
        self.model = None
        self.meta = None
        self.hist = gm.load_data()

        root.title("Gold Price Predictor  -  Machine Learning")
        root.geometry("1060x700")
        root.minsize(920, 620)
        root.configure(bg=BG)
        try:
            icon = os.path.normpath(os.path.join(HERE, "..", "assets", "icon.ico"))
            if os.path.exists(icon):
                root.iconbitmap(icon)
        except Exception:
            pass

        self._style()
        self._header()

        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=14, pady=12)
        self.nb.add(self._predict_tab(), text="   Predict   ")
        self.nb.add(self._train_tab(), text="   Train Model   ")
        self.nb.add(self._about_tab(), text="   About   ")

        self._load_model()

    # ---------- look and feel ----------
    def _style(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(16, 8))
        st.map("TNotebook.Tab", background=[("selected", NAVY)],
               foreground=[("selected", "#FFFFFF")])
        st.configure("Card.TFrame", background=PANEL)
        st.configure("Root.TFrame", background=BG)
        st.configure("TLabel", background=PANEL, foreground=TXT, font=("Segoe UI", 10))
        st.configure("Head.TLabel", background=PANEL, foreground=NAVY, font=("Segoe UI", 12, "bold"))
        st.configure("Mut.TLabel", background=PANEL, foreground=MUT, font=("Segoe UI", 9))
        st.configure("Gold.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8))
        st.map("Gold.TButton", background=[("active", "#B08D1F")])
        st.configure("Treeview", font=("Consolas", 10), rowheight=26, background=PANEL)
        st.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _header(self):
        bar = tk.Frame(self.root, bg=NAVY, height=74)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="Gold Price Predictor", bg=NAVY, fg="#FFFFFF",
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=(12, 0))
        tk.Label(bar, text="Machine Learning  |  Random Forest  |  BSA CET Mathura",
                 bg=NAVY, fg=GOLD, font=("Segoe UI", 10)).pack(side="left", padx=20, pady=(34, 0))

    # ---------- Predict tab ----------
    def _predict_tab(self):
        tab = ttk.Frame(self.nb, style="Root.TFrame")
        left = ttk.Frame(tab, style="Card.TFrame", padding=16)
        left.pack(side="left", fill="y", padx=(0, 10), pady=4)
        right = ttk.Frame(tab, style="Card.TFrame", padding=10)
        right.pack(side="left", fill="both", expand=True, pady=4)

        ttk.Label(left, text="Forecast", style="Head.TLabel").pack(anchor="w")
        ttk.Label(left, text="How many months ahead?", style="Mut.TLabel").pack(anchor="w", pady=(2, 6))

        row = ttk.Frame(left, style="Card.TFrame")
        row.pack(anchor="w")
        ttk.Label(row, text="Months:", style="Card.TFrame").pack(side="left")
        self.horizon = tk.StringVar(value="6")
        sp = ttk.Spinbox(row, from_=1, to=24, width=6, textvariable=self.horizon,
                         font=("Segoe UI", 11))
        sp.pack(side="left", padx=8)

        last = self.hist.iloc[-1]
        info = "Last known: %s  =  $%.2f" % (last["Date"].strftime("%b %Y"), last["Price"])
        ttk.Label(left, text=info, style="Mut.TLabel").pack(anchor="w", pady=(12, 2))

        ttk.Button(left, text="Run Prediction", style="Gold.TButton",
                   command=self.on_predict).pack(anchor="w", pady=(8, 14))

        ttk.Label(left, text="Predicted price", style="Head.TLabel").pack(anchor="w")
        cols = ("month", "price")
        self.fc_table = ttk.Treeview(left, columns=cols, show="headings", height=10)
        self.fc_table.heading("month", text="Month")
        self.fc_table.heading("price", text="Price (USD/oz)")
        self.fc_table.column("month", width=90, anchor="center")
        self.fc_table.column("price", width=130, anchor="center")
        self.fc_table.pack(fill="x", pady=(4, 0))

        self.fig = Figure(figsize=(6.6, 4.6), dpi=100, facecolor=PANEL)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._draw_history()
        return tab

    def _draw_history(self):
        self.ax.clear()
        h = self.hist.tail(96)
        self.ax.plot(h["Date"], h["Price"], color=NAVY, linewidth=1.6, label="Actual")
        self.ax.set_title("Gold price history (last 8 years)", color=NAVY, fontsize=11)
        self.ax.legend(loc="upper left", fontsize=8)
        self._style_ax(self.ax)
        self.fig.tight_layout()
        self.canvas.draw()

    def on_predict(self):
        if self.model is None:
            messagebox.showwarning("Model needed", "Please train the model first (Train Model tab).")
            return
        try:
            months = int(self.horizon.get())
        except ValueError:
            months = 6
        last = self.hist.iloc[-1]
        y, m = last["Date"].year, last["Date"].month + 1
        if m > 12:
            m, y = 1, y + 1
        fc = gm.forecast(self.model, self.hist["Price"].tail(4).tolist(), y, m, months)

        for i in self.fc_table.get_children():
            self.fc_table.delete(i)
        for d, p in fc:
            self.fc_table.insert("", "end", values=(d, "%.2f" % p))

        self.ax.clear()
        h = self.hist.tail(72)
        self.ax.plot(h["Date"], h["Price"], color=NAVY, linewidth=1.6, label="Actual")
        fx = [datetime.strptime(d, "%Y-%m") for d, _ in fc]
        fy = [p for _, p in fc]
        self.ax.plot([h["Date"].iloc[-1]] + fx, [h["Price"].iloc[-1]] + fy,
                     color=GOLD, linewidth=2.0, marker="o", markersize=3, label="Forecast")
        self.ax.set_title("Gold price forecast (next %d months)" % months, color=NAVY, fontsize=11)
        self.ax.legend(loc="upper left", fontsize=8)
        self._style_ax(self.ax)
        self.fig.tight_layout()
        self.canvas.draw()

    # ---------- Train tab ----------
    def _train_tab(self):
        tab = ttk.Frame(self.nb, style="Root.TFrame")
        left = ttk.Frame(tab, style="Card.TFrame", padding=16)
        left.pack(side="left", fill="y", padx=(0, 10), pady=4)
        right = ttk.Frame(tab, style="Card.TFrame", padding=10)
        right.pack(side="left", fill="both", expand=True, pady=4)

        ttk.Label(left, text="Train / evaluate", style="Head.TLabel").pack(anchor="w")
        ttk.Label(left, text="Fits RandomForest, Linear and Ridge on the\ngold price series and compares their accuracy.",
                  style="Mut.TLabel", justify="left").pack(anchor="w", pady=(2, 10))
        self.train_btn = ttk.Button(left, text="Retrain Model", style="Gold.TButton",
                                    command=self.on_train)
        self.train_btn.pack(anchor="w")
        self.train_status = ttk.Label(left, text="", style="Mut.TLabel", wraplength=220, justify="left")
        self.train_status.pack(anchor="w", pady=(10, 0))

        ttk.Label(left, text="Accuracy on the test window", style="Head.TLabel").pack(anchor="w", pady=(16, 4))
        cols = ("model", "mae", "rmse", "r2")
        self.metric_table = ttk.Treeview(left, columns=cols, show="headings", height=6)
        for c, t, w in zip(cols, ("Model", "MAE", "RMSE", "R2"), (110, 60, 60, 60)):
            self.metric_table.heading(c, text=t)
            self.metric_table.column(c, width=w, anchor="center")
        self.metric_table.pack(fill="x")

        self.fig2 = Figure(figsize=(5.4, 4.2), dpi=100, facecolor=PANEL)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=right)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True)
        return tab

    def on_train(self):
        self.train_btn.config(state="disabled")
        self.train_status.config(text="Training, please wait...")
        self.root.update_idletasks()
        threading.Thread(target=self._train_worker, daemon=True).start()

    def _train_worker(self):
        res = gm.train()
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(res["model"], MODEL_PATH)
        meta = {"best_model": res["best_model"], "features": res["features"],
                "test_period": res["test_period"], "trained_on_rows": int(len(self.hist)),
                "scores": res["scores"]}
        with open(META_PATH, "w") as f:
            json.dump(meta, f, indent=2)
        self.root.after(0, self._after_train, res)

    def _after_train(self, res):
        self.model = res["model"]
        self.meta = json.load(open(META_PATH))
        self._fill_metrics()
        self._draw_mae_chart()
        self.train_status.config(text="Done. Best model: %s" % res["best_model"])
        self.train_btn.config(state="normal")

    def _draw_mae_chart(self):
        if not self.meta:
            return
        s = self.meta["scores"]
        names = list(s)
        maes = [s[n]["MAE"] for n in names]
        self.ax2.clear()
        bars = self.ax2.bar(names, maes, color=[GOLD if n == self.meta["best_model"] else NAVY for n in names])
        self.ax2.set_title("Mean Absolute Error by model (lower is better)", color=NAVY, fontsize=10)
        self.ax2.set_ylabel("MAE (USD)")
        for b, v in zip(bars, maes):
            self.ax2.text(b.get_x() + b.get_width() / 2, v, "%.1f" % v, ha="center", va="bottom", fontsize=8)
        self._style_ax(self.ax2)
        self.fig2.tight_layout()
        self.canvas2.draw()

    # ---------- About tab ----------
    def _about_tab(self):
        tab = ttk.Frame(self.nb, style="Card.TFrame", padding=20)
        txt = tk.Text(tab, wrap="word", font=("Segoe UI", 11), bg=PANEL, fg=TXT,
                      relief="flat", padx=16, pady=12)
        txt.pack(fill="both", expand=True)
        body = (
            "GOLD PRICE PREDICTOR - PROJECT SUMMARY\n"
            "========================================\n\n"
            "This project uses Machine Learning to predict the monthly price of gold\n"
            "(USD per troy ounce) from its own history.\n\n"
            "HOW IT WORKS\n"
            "  1. Load monthly gold prices (2000 - 2024) from data/gold_prices.csv.\n"
            "  2. Build features: the last 3 monthly returns plus month and year.\n"
            "  3. The model predicts the next month's RETURN, not the raw price,\n"
            "     because returns stay in a small stable range. Price = last price x (1 + return).\n"
            "  4. RandomForest, Linear Regression and Ridge are compared; the best is saved.\n"
            "  5. The GUI rolls the prediction forward month by month for the chosen horizon.\n\n"
            "TECH STACK\n"
            "  Python, pandas, NumPy, scikit-learn, Matplotlib, Tkinter, Joblib.\n\n"
            "WHY GOLD\n"
            "  Gold is a heavily traded asset with a clear long term trend and short term\n"
            "  momentum, which makes it a good, honest regression problem to learn on.\n\n"
            "NOTE\n"
            "  The bundled dataset is a compiled sample for a college demonstration.\n"
            "  This is a learning project, not financial advice.\n\n"
            "B.S.A. College of Engineering & Technology, Mathura - CSE, Session 2026-27.\n"
        )
        txt.insert("1.0", body)
        txt.config(state="disabled")
        return tab

    # ---------- helpers ----------
    def _style_ax(self, ax):
        ax.set_facecolor(PANEL)
        for sp in ax.spines.values():
            sp.set_color("#D5DBE8")
        ax.tick_params(colors=MUT, labelsize=8)
        ax.xaxis.set_visible(True)
        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_ha("right")

    def _fill_metrics(self):
        for i in self.metric_table.get_children():
            self.metric_table.delete(i)
        if not self.meta:
            return
        for name, sc in self.meta["scores"].items():
            tag = "best" if name == self.meta["best_model"] else ""
            self.metric_table.insert("", "end",
                                     values=(name, sc["MAE"], sc["RMSE"], sc["R2"]))

    def _load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(META_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.meta = json.load(open(META_PATH))
            self._fill_metrics()
            self._draw_mae_chart()
            self.train_status.config(text="Model loaded. Best: %s" % self.meta["best_model"])
        else:
            self.train_status.config(text="No trained model yet - press Retrain Model.")


def main():
    root = tk.Tk()
    GoldApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
