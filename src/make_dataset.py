# make_dataset.py
# Builds data/gold_prices.csv and data/silver_prices.csv.
# Each file is one row per month: Date, Year, Month, Price (USD per troy ounce).
#
# The yearly numbers are approximate LBMA annual averages read off public market
# data. In between we move the price smoothly and add an AR(1) wobble so short
# term momentum exists for the model to find. This is a college demo dataset -
# check an official feed before trusting any single month.
import csv
import datetime
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))

# average price of one year (USD/oz)
GOLD = {
    2000: 279, 2001: 271, 2002: 310, 2003: 363, 2004: 409,
    2005: 444, 2006: 603, 2007: 695, 2008: 872, 2009: 972,
    2010: 1224, 2011: 1571, 2012: 1669, 2013: 1411, 2014: 1266,
    2015: 1160, 2016: 1250, 2017: 1257, 2018: 1268, 2019: 1392,
    2020: 1770, 2021: 1799, 2022: 1800, 2023: 1942, 2024: 2386,
    2025: 3200, 2026: 3900,
}

SILVER = {
    2000: 4.93, 2001: 4.21, 2002: 4.60, 2003: 4.88, 2004: 6.67,
    2005: 7.31, 2006: 11.55, 2007: 13.38, 2008: 14.10, 2009: 14.60,
    2010: 20.14, 2011: 30.00, 2012: 31.16, 2013: 23.79, 2014: 19.07,
    2015: 15.67, 2016: 17.14, 2017: 17.05, 2018: 15.71, 2019: 16.20,
    2020: 20.53, 2021: 25.15, 2022: 21.73, 2023: 23.36, 2024: 28.30,
    2025: 37.00, 2026: 49.00,
}

# metals often drift up a little in the festive / last months of the year
MONTH_TILT = {1: -0.010, 2: -0.006, 3: 0.000, 4: 0.004, 5: 0.002, 6: -0.002,
              7: 0.001, 8: 0.006, 9: 0.004, 10: 0.010, 11: 0.006, 12: 0.002}


def last_closed_month():
    # we only build history up to the month before the current one
    today = datetime.date.today()
    y, m = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
    return y, m


def build_rows(year_avg, seed):
    random.seed(seed)
    stop_y, stop_m = last_closed_month()
    rows = []
    shock = 0.0
    for y in sorted(year_avg):
        this_avg = year_avg[y]
        next_avg = year_avg.get(y + 1, this_avg)
        for m in range(1, 13):
            if (y, m) > (stop_y, stop_m):
                break
            part = (m - 1) / 11.0
            base = this_avg + (next_avg - this_avg) * part * 0.5
            # half of last month's surprise plus a fresh surprise = momentum
            shock = 0.55 * shock + random.uniform(-0.022, 0.022)
            price = base * (1 + MONTH_TILT[m]) * (1 + shock)
            rows.append(("%04d-%02d" % (y, m), y, m, round(price, 2)))
        if (y, 12) > (stop_y, stop_m):
            break
    return rows


def write_csv(name, rows):
    out = os.path.join(DATA_DIR, name)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Year", "Month", "Price"])
        w.writerows(rows)
    print("wrote", out, "-", len(rows), "rows")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    write_csv("gold_prices.csv", build_rows(GOLD, 42))
    write_csv("silver_prices.csv", build_rows(SILVER, 7))
    print("history ends at %04d-%02d" % last_closed_month())


if __name__ == "__main__":
    main()
