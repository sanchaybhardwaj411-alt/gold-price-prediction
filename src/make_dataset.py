# make_dataset.py
# Builds data/gold_prices.csv - monthly gold price (USD per troy ounce), 2000 to 2024.
# The yearly anchors below are approximate LBMA annual averages taken from public
# market data. We interpolate month to month and add a small seasonal wobble so the
# series looks like a real price line. For a college demo project this is enough -
# verify against an official feed before using it for anything serious.
import csv
import os
import random

random.seed(42)

# average gold price for each year (USD/oz)
YEAR_AVG = {
    2000: 279, 2001: 271, 2002: 310, 2003: 363, 2004: 409,
    2005: 444, 2006: 603, 2007: 695, 2008: 872, 2009: 972,
    2010: 1224, 2011: 1571, 2012: 1669, 2013: 1411, 2014: 1266,
    2015: 1160, 2016: 1250, 2017: 1257, 2018: 1268, 2019: 1392,
    2020: 1770, 2021: 1799, 2022: 1800, 2023: 1942, 2024: 2386,
}

# small month effect - gold usually drifts up a little in the last months of a year
MONTH_TILT = {1: -0.010, 2: -0.006, 3: 0.000, 4: 0.004, 5: 0.002, 6: -0.002,
              7: 0.001, 8: 0.006, 9: 0.004, 10: 0.010, 11: 0.006, 12: 0.002}


def build_rows():
    rows = []
    years = sorted(YEAR_AVG)
    shock = 0.0  # carries over month to month so we get short term momentum
    for y in years:
        this_avg = YEAR_AVG[y]
        next_avg = YEAR_AVG.get(y + 1, this_avg)
        for m in range(1, 13):
            # move the price smoothly from this year average toward next year average
            part = (m - 1) / 11.0
            base = this_avg + (next_avg - this_avg) * part * 0.5
            # AR(1) wobble: half of last month's shock plus a fresh surprise
            shock = 0.55 * shock + random.uniform(-0.022, 0.022)
            price = base * (1 + MONTH_TILT[m]) * (1 + shock)
            rows.append(("%04d-%02d" % (y, m), y, m, round(price, 2)))
    return rows


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "data", "gold_prices.csv")
    out = os.path.normpath(out)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Year", "Month", "Price"])
        w.writerows(build_rows())
    print("wrote", out)


if __name__ == "__main__":
    main()
