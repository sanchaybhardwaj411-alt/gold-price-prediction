# make_ppt.py
# Builds the college presentation for the Gold & Silver Price Prediction project.
# Produces BOTH a real PowerPoint (.pptx) and a PDF mirror (for older Office PCs).
#   python make_ppt.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")
LOGO = os.path.join(HERE, "assets", "college_logo.jpg")
LOGO_NAVY = os.path.join(HERE, "assets", "college_logo_navy.png")
SHOT_LIVE = os.path.join(DOCS, "dashboard_overview.png")
SHOT_FORECAST = os.path.join(DOCS, "dashboard_forecast.png")
SHOT_ACCURACY = os.path.join(DOCS, "dashboard_accuracy.png")
RESULTS_CHART = os.path.join(DOCS, "results_chart.png")

TITLE = "Live Gold & Silver Price Prediction using Machine Learning"
SHORT = "Gold & Silver Predictor"
STUDENT = "Sanchay Bhardwaj"
ROLL = "2300650100104"
GUIDE = "Mrs. Ashna Thakur"
COLLEGE = "B.S.A. College of Engineering & Technology, Mathura"
DEPT = "Dept. of Computer Science & Engineering   |   Session 2026-27"

# model, gold MAE, gold R2, silver MAE, silver R2   (matches model/metrics.json)
MODELS = [
    ("Random Forest", 44.34, 0.9910, 0.54, 0.9942),
    ("Linear Regression", 54.12, 0.9889, 0.62, 0.9909),
    ("Ridge", 53.54, 0.9889, 0.64, 0.9903),
    ("Naive baseline", 56.93, 0.9875, 0.64, 0.9897),
]
BEST = "Random Forest"
TABLE_HDR = ["Model", "Gold MAE (US$/oz)", "Gold R-sq", "Silver MAE (US$/oz)", "Silver R-sq"]
NOTE = ("Random Forest wins on both metals and beats the naive baseline. "
        "Test window: last 60 months, from Oct 2021. Lower MAE and higher R-squared are better.")

SLIDES = [
    {"kind": "title"},
    {"kind": "bullets", "title": "Introduction", "bullets": [
        "Gold and silver are the two most tracked precious metals, priced in US dollars per troy ounce.",
        "Their prices move with demand, inflation, the dollar and global market sentiment.",
        "This project fetches the LIVE price of both metals and converts it into Indian Rupees per gram.",
        "A Machine Learning model then forecasts the price for the next 12 months.",
        "Everything is shown on one web dashboard, so the numbers can be read without any training.",
    ]},
    {"kind": "bullets", "title": "Problem Statement", "bullets": [
        "Given the historical monthly price of gold and silver, predict their price for the coming months.",
        "This is a supervised regression problem: past behaviour is the input, future price is the output.",
        "Several models are trained, scored on data they have never seen, and the best one is kept.",
        "The winning model is connected to a live price feed and presented on a dashboard in rupees.",
    ]},
    {"kind": "bullets", "title": "Objectives", "bullets": [
        "Build a clean monthly price dataset for gold and silver from the year 2000 up to today.",
        "Read the live price of both metals and the US dollar to rupee rate from public APIs.",
        "Engineer features that capture short-term momentum instead of raw price levels.",
        "Compare Random Forest, Linear Regression and Ridge against a naive baseline.",
        "Deliver an attractive dashboard showing present and future prices in Indian Rupees.",
    ]},
    {"kind": "bullets", "title": "Live Data Sources", "bullets": [
        "api.gold-api.com/price/XAU  -  live gold price in US dollars per troy ounce.",
        "api.gold-api.com/price/XAG  -  live silver price in US dollars per troy ounce.",
        "open.er-api.com  -  today's US dollar to Indian rupee exchange rate.",
        "All three are free public feeds, so no key or login is needed.",
        "Conversion:  Rs per gram = US$ per ounce x USD-INR rate / 31.1035  (one troy ounce = 31.1035 g).",
    ]},
    {"kind": "bullets", "title": "Dataset", "bullets": [
        "Two files: gold_prices.csv and silver_prices.csv - one row per month since January 2000.",
        "Columns: Date, Year, Month and Price (US dollars per troy ounce).",
        "Yearly anchors are approximate LBMA annual averages, interpolated month to month with momentum.",
        "Model features: the last 3 monthly returns, plus the month and the year.",
        "The live API price is appended as the latest point, so the forecast always starts from today.",
    ]},
    {"kind": "bullets", "title": "Methodology", "bullets": [
        "The model predicts the month-to-month RETURN, never the raw price.",
        "Why: a tree model cannot guess a price higher than anything it saw, so a 25 year rising trend breaks it.",
        "Price is rebuilt as   next price = last price x (1 + predicted return).",
        "Forecasting rolls forward one month at a time, feeding each answer back as the next input.",
        "The split is chronological - the last 60 months are held out and never used for fitting.",
    ]},
    {"kind": "bullets", "title": "Technology Used", "bullets": [
        "Language: Python.",
        "Data handling: pandas and NumPy.",
        "Models: scikit-learn - Random Forest, Linear Regression, Ridge.",
        "Backend: Flask, serving one JSON summary to the page.",
        "Frontend: Chart.js on a dark dashboard.   Model save / load: Joblib.",
    ]},
    {"kind": "table", "title": "Results"},
    {"kind": "image", "title": "Application - Live Dashboard", "image": SHOT_LIVE,
     "caption": "Today's live gold and silver price in rupees per gram, per kg and per 10 gram, "
                "with the monthly history since 2000."},
    {"kind": "image", "title": "Application - 12 Month Forecast", "image": SHOT_FORECAST,
     "caption": "Solid line = actual price, dashed line = model forecast, plus the month by month "
                "expected price in rupees."},
    {"kind": "image", "title": "Application - Model Accuracy", "image": SHOT_ACCURACY,
     "caption": "Error of every model on 60 unseen months, compared against the naive "
                "'next month = this month' baseline."},
    {"kind": "bullets", "title": "Conclusion", "bullets": [
        "Random Forest gave the lowest error on both metals and beat the naive baseline.",
        "Predicting returns instead of raw prices made the models reliable on a strongly trending series.",
        "Live prices, rupee conversion and the forecast are combined in one self-explanatory dashboard.",
        "The project demonstrates a complete Machine Learning pipeline - data, model, API, interface.",
    ]},
    {"kind": "bullets", "title": "Future Scope", "bullets": [
        "Add real economic features such as inflation, the dollar index and interest rates.",
        "Try deep-learning time-series models like LSTM for longer horizons.",
        "Show a confidence range around the forecast instead of a single number.",
        "Extend to other metals and to jewelers' rate cards used in the local market.",
        "Publish the dashboard online with a scheduled daily data refresh.",
    ]},
    {"kind": "end"},
]


def make_results_chart():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = [m[0].replace(" ", "\n") for m in MODELS]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 4.2), dpi=130)
    for ax, col, title, color in ((axes[0], 1, "Gold  (US$ / oz)", "#C9A227"),
                                  (axes[1], 3, "Silver  (US$ / oz)", "#4A6FA5")):
        vals = [m[col] for m in MODELS]
        bars = ax.bar(range(len(vals)), vals,
                      color=[color if m[0] == BEST else "#1F3864" for m in MODELS])
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(names, fontsize=7)
        ax.set_title("MAE - " + title, color="#1F3864", fontsize=11, fontweight="bold")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, "%.2f" % v,
                    ha="center", va="bottom", fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(RESULTS_CHART, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ PPTX
def render_pptx(path):
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE

    NAVY = RGBColor(0x1F, 0x38, 0x64)
    GOLD = RGBColor(0xC9, 0xA2, 0x27)
    DARK = RGBColor(0x22, 0x22, 0x22)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    MUT = RGBColor(0x6B, 0x72, 0x80)
    LIGHT = RGBColor(0xEE, 0xF3, 0xFA)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    W, H = prs.slide_width, prs.slide_height
    blank = prs.slide_layouts[6]

    def rect(slide, l, t, w, h, color):
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
        s.fill.solid(); s.fill.fore_color.rgb = color
        s.line.fill.background(); s.shadow.inherit = False
        return s

    def tb(slide, l, t, w, h, anchor=None):
        box = slide.shapes.add_textbox(l, t, w, h)
        tf = box.text_frame
        tf.word_wrap = True
        if anchor is not None:
            tf.vertical_anchor = anchor
        return tf

    def para(tf, text, size, color, bold=False, align=PP_ALIGN.LEFT, first=False, after=6):
        p = tf.paragraphs[0] if (first and not tf.paragraphs[0].runs) else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(after)
        r = p.add_run(); r.text = text
        r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
        r.font.name = "Calibri"
        return p

    def header(slide, title):
        rect(slide, 0, 0, W, Inches(1.05), NAVY)
        rect(slide, 0, Inches(1.05), W, Inches(0.07), GOLD)
        tf = tb(slide, Inches(0.5), Inches(0.15), W - Inches(4.2), Inches(0.8), MSO_ANCHOR.MIDDLE)
        para(tf, title, 26, WHITE, bold=True, first=True)
        tf2 = tb(slide, W - Inches(4.0), Inches(0.15), Inches(3.5), Inches(0.8), MSO_ANCHOR.MIDDLE)
        para(tf2, SHORT, 12, GOLD, bold=True, align=PP_ALIGN.RIGHT, first=True)

    def footer(slide, n):
        rect(slide, 0, H - Inches(0.42), W, Inches(0.42), NAVY)
        rect(slide, 0, H - Inches(0.42), Inches(0.14), Inches(0.42), GOLD)
        tf = tb(slide, Inches(0.3), H - Inches(0.42), W - Inches(2.0), Inches(0.42), MSO_ANCHOR.MIDDLE)
        para(tf, "%s (%s)  |  %s" % (STUDENT, ROLL, COLLEGE), 9, WHITE, first=True)
        tf2 = tb(slide, W - Inches(1.6), H - Inches(0.42), Inches(1.3), Inches(0.42), MSO_ANCHOR.MIDDLE)
        para(tf2, "Slide %d" % n, 9, GOLD, bold=True, align=PP_ALIGN.RIGHT, first=True)

    for idx, sl in enumerate(SLIDES, start=1):
        slide = prs.slides.add_slide(blank)
        kind = sl["kind"]

        if kind == "title":
            rect(slide, 0, 0, W, H, NAVY)
            rect(slide, 0, Inches(4.35), W, Inches(0.06), GOLD)
            slide.shapes.add_picture(LOGO_NAVY, int((W - Inches(1.9)) / 2), Inches(0.6), Inches(1.9), Inches(1.9))
            tf = tb(slide, Inches(0.8), Inches(2.55), W - Inches(1.6), Inches(1.6))
            para(tf, TITLE, 32, WHITE, bold=True, align=PP_ALIGN.CENTER, first=True, after=6)
            para(tf, "A Mini Project in Machine Learning", 18, GOLD, align=PP_ALIGN.CENTER)
            tf2 = tb(slide, Inches(1.0), Inches(4.7), W - Inches(2.0), Inches(2.4))
            para(tf2, "Submitted by", 13, GOLD, bold=True, align=PP_ALIGN.CENTER, first=True, after=2)
            para(tf2, "%s  (%s)" % (STUDENT, ROLL), 22, WHITE, bold=True, align=PP_ALIGN.CENTER, after=14)
            para(tf2, "Project Guide:  %s" % GUIDE, 15, WHITE, align=PP_ALIGN.CENTER, after=4)
            para(tf2, COLLEGE, 14, WHITE, align=PP_ALIGN.CENTER, after=4)
            para(tf2, DEPT, 12, GOLD, align=PP_ALIGN.CENTER)

        elif kind == "bullets":
            header(slide, sl["title"])
            footer(slide, idx)
            rect(slide, Inches(0.55), Inches(1.7), Inches(0.09), Inches(4.7), GOLD)
            tf = tb(slide, Inches(0.95), Inches(1.5), W - Inches(1.6), H - Inches(2.4), MSO_ANCHOR.MIDDLE)
            first = True
            for b in sl["bullets"]:
                para(tf, "•   " + b, 19, DARK, first=first, after=18)
                first = False

        elif kind == "table":
            header(slide, sl["title"])
            footer(slide, idx)
            rows = len(MODELS) + 1
            gt = slide.shapes.add_table(rows, 5, Inches(0.55), Inches(2.0),
                                        Inches(8.1), Inches(3.2)).table
            for c, h in enumerate(TABLE_HDR):
                cell = gt.cell(0, c)
                cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
                cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                para(cell.text_frame, h, 12, WHITE, bold=True, align=PP_ALIGN.CENTER, first=True)
            for r, m in enumerate(MODELS, start=1):
                vals = [m[0], "%.2f" % m[1], "%.4f" % m[2], "%.2f" % m[3], "%.4f" % m[4]]
                is_best = (m[0] == BEST)
                for c, val in enumerate(vals):
                    cell = gt.cell(r, c)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = LIGHT if r % 2 else WHITE
                    cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                    col = GOLD if is_best else DARK
                    para(cell.text_frame, val, 12, col, bold=is_best,
                         align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER, first=True)
            slide.shapes.add_picture(RESULTS_CHART, Inches(8.85), Inches(1.75), Inches(4.1), Inches(3.5))
            tf = tb(slide, Inches(0.55), Inches(5.6), Inches(8.1), Inches(1.2))
            para(tf, NOTE, 12, MUT, first=True)

        elif kind == "image":
            header(slide, sl["title"])
            footer(slide, idx)
            from PIL import Image
            iw, ih = Image.open(sl["image"]).size
            max_w = W - Inches(1.6)
            max_h = H - Inches(2.6)
            scale = min(max_w / iw, max_h / ih)
            pw, ph = int(iw * scale), int(ih * scale)
            slide.shapes.add_picture(sl["image"], int((W - pw) / 2), Inches(1.45), pw, ph)
            tf = tb(slide, Inches(1.0), H - Inches(1.35), W - Inches(2.0), Inches(0.7))
            para(tf, sl["caption"], 13, MUT, align=PP_ALIGN.CENTER, first=True)

        elif kind == "end":
            rect(slide, 0, 0, W, H, NAVY)
            rect(slide, 0, Inches(3.55), W, Inches(0.06), GOLD)
            slide.shapes.add_picture(LOGO_NAVY, int((W - Inches(1.4)) / 2), Inches(0.9), Inches(1.4), Inches(1.4))
            tf = tb(slide, Inches(1.0), Inches(2.7), W - Inches(2.0), Inches(1.2))
            para(tf, "Thank You", 54, WHITE, bold=True, align=PP_ALIGN.CENTER, first=True)
            tf2 = tb(slide, Inches(1.0), Inches(4.0), W - Inches(2.0), Inches(2.6))
            para(tf2, "Questions & suggestions are welcome", 18, GOLD, align=PP_ALIGN.CENTER, first=True, after=16)
            para(tf2, "%s  (%s)" % (STUDENT, ROLL), 15, WHITE, align=PP_ALIGN.CENTER, after=3)
            para(tf2, "Guide: %s" % GUIDE, 14, WHITE, align=PP_ALIGN.CENTER, after=3)
            para(tf2, COLLEGE, 13, GOLD, align=PP_ALIGN.CENTER)

    prs.save(path)
    print("pptx:", path)


# ------------------------------------------------------------------ PDF
def render_pdf(path):
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors as rcolors

    NAVY = HexColor("#1F3864")
    GOLD = HexColor("#C9A227")
    DARK = HexColor("#222222")
    MUT = HexColor("#6B7280")
    WHITE = HexColor("#FFFFFF")
    LIGHT = HexColor("#EEF3FA")

    PW, PH = 13.333 * inch, 7.5 * inch
    c = pdfcanvas.Canvas(path, pagesize=(PW, PH))
    c.setTitle(TITLE)
    c.setAuthor(STUDENT)

    def wrap(text, font, size, maxw):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if c.stringWidth(t, font, size) <= maxw:
                cur = t
            else:
                lines.append(cur); cur = w
        if cur:
            lines.append(cur)
        return lines

    def header(title):
        c.setFillColor(NAVY); c.rect(0, PH - 1.05 * inch, PW, 1.05 * inch, fill=1, stroke=0)
        c.setFillColor(GOLD); c.rect(0, PH - 1.12 * inch, PW, 0.07 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 24)
        c.drawString(0.5 * inch, PH - 0.68 * inch, title)
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 12)
        c.drawRightString(PW - 0.5 * inch, PH - 0.66 * inch, SHORT)

    def footer(n):
        c.setFillColor(NAVY); c.rect(0, 0, PW, 0.42 * inch, fill=1, stroke=0)
        c.setFillColor(GOLD); c.rect(0, 0, 0.14 * inch, 0.42 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica", 9)
        c.drawString(0.3 * inch, 0.16 * inch, "%s (%s)  |  %s" % (STUDENT, ROLL, COLLEGE))
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 9)
        c.drawRightString(PW - 0.3 * inch, 0.16 * inch, "Slide %d" % n)

    def bullets(items):
        size, lead, gap = 18, 25, 14
        block = []
        total = 0
        for b in items:
            lines = wrap("•  " + b, "Helvetica", size, PW - 1.6 * inch)
            block.append(lines)
            total += len(lines) * lead + gap
        total -= gap
        top = PH - 1.15 * inch
        bottom = 0.55 * inch
        y = top - ((top - bottom) - total) / 2.0
        c.setFillColor(GOLD); c.rect(0.55 * inch, bottom, 0.09 * inch, top - bottom, fill=1, stroke=0)
        for lines in block:
            c.setFillColor(DARK); c.setFont("Helvetica", size)
            for ln in lines:
                c.drawString(0.95 * inch, y - size, ln)
                y -= lead
            y -= gap

    # ---- title slide ----
    c.setFillColor(NAVY); c.rect(0, 0, PW, PH, fill=1, stroke=0)
    c.drawImage(LOGO_NAVY, (PW - 1.9 * inch) / 2, PH - 0.6 * inch - 1.9 * inch, 1.9 * inch, 1.9 * inch)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 28)
    for i, ln in enumerate(wrap(TITLE, "Helvetica-Bold", 28, PW - 2.4 * inch)):
        c.drawCentredString(PW / 2, PH - 3.05 * inch - i * 36, ln)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(PW / 2, PH - 4.25 * inch, "A Mini Project in Machine Learning")
    c.setFillColor(GOLD); c.rect(0, PH - 4.6 * inch, PW, 0.05 * inch, fill=1, stroke=0)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(PW / 2, PH - 5.0 * inch, "Submitted by")
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PW / 2, PH - 5.45 * inch, "%s  (%s)" % (STUDENT, ROLL))
    c.setFont("Helvetica", 14)
    c.drawCentredString(PW / 2, PH - 6.0 * inch, "Project Guide:  %s" % GUIDE)
    c.drawCentredString(PW / 2, PH - 6.35 * inch, COLLEGE)
    c.setFillColor(GOLD); c.setFont("Helvetica", 12)
    c.drawCentredString(PW / 2, PH - 6.7 * inch, DEPT)
    c.showPage()

    idx = 2
    for sl in SLIDES:
        kind = sl["kind"]
        if kind == "title":
            continue
        if kind == "bullets":
            header(sl["title"]); footer(idx); bullets(sl["bullets"])
            c.showPage(); idx += 1
        elif kind == "table":
            header(sl["title"]); footer(idx)
            data = [TABLE_HDR]
            for m in MODELS:
                data.append([m[0], "%.2f" % m[1], "%.4f" % m[2], "%.2f" % m[3], "%.4f" % m[4]])
            t = Table(data, colWidths=[1.9 * inch, 1.7 * inch, 1.2 * inch, 1.8 * inch, 1.2 * inch],
                      rowHeights=[0.75 * inch] + [0.55 * inch] * len(MODELS))
            style = [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 1), (-1, -1), 12),
                ("FONTNAME", (0, 1), (0, 1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 1), (0, 1), GOLD),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.6, HexColor("#C9D6EA")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
            t.setStyle(TableStyle(style))
            tw, th = t.wrap(8.0 * inch, 4 * inch)
            t.drawOn(c, 0.55 * inch, PH - 1.5 * inch - th)
            c.drawImage(RESULTS_CHART, 8.85 * inch, PH - 1.7 * inch - 3.5 * inch,
                        4.1 * inch, 3.5 * inch)
            note = wrap(NOTE, "Helvetica-Oblique", 11, 8.0 * inch)
            c.setFillColor(MUT); c.setFont("Helvetica-Oblique", 11)
            ny = PH - 1.5 * inch - th - 0.5 * inch
            for ln in note:
                c.drawString(0.55 * inch, ny, ln); ny -= 15
            c.showPage(); idx += 1
        elif kind == "image":
            header(sl["title"]); footer(idx)
            from PIL import Image as PImage
            iw, ih = PImage.open(sl["image"]).size
            max_w, max_h = PW - 1.6 * inch, PH - 2.7 * inch
            scale = min(max_w / iw, max_h / ih)
            pw, ph = iw * scale, ih * scale
            c.drawImage(sl["image"], (PW - pw) / 2, PH - 1.35 * inch - ph, pw, ph)
            c.setFillColor(MUT); c.setFont("Helvetica", 12)
            c.drawCentredString(PW / 2, 0.7 * inch, sl["caption"])
            c.showPage(); idx += 1
        elif kind == "end":
            c.setFillColor(NAVY); c.rect(0, 0, PW, PH, fill=1, stroke=0)
            c.drawImage(LOGO_NAVY, (PW - 1.4 * inch) / 2, PH - 0.9 * inch - 1.4 * inch, 1.4 * inch, 1.4 * inch)
            c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 50)
            c.drawCentredString(PW / 2, PH - 3.1 * inch, "Thank You")
            c.setFillColor(GOLD); c.rect(0, PH - 3.4 * inch, PW, 0.05 * inch, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 17)
            c.drawCentredString(PW / 2, PH - 4.1 * inch, "Questions & suggestions are welcome")
            c.setFillColor(WHITE); c.setFont("Helvetica", 15)
            c.drawCentredString(PW / 2, PH - 4.8 * inch, "%s  (%s)" % (STUDENT, ROLL))
            c.setFont("Helvetica", 14)
            c.drawCentredString(PW / 2, PH - 5.15 * inch, "Guide: %s" % GUIDE)
            c.setFillColor(GOLD); c.setFont("Helvetica", 13)
            c.drawCentredString(PW / 2, PH - 5.5 * inch, COLLEGE)
            c.showPage(); idx += 1

    c.save()
    print("pdf:", path)


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    make_results_chart()
    render_pptx(os.path.join(DOCS, "Gold-Price-Prediction-Presentation.pptx"))
    render_pdf(os.path.join(DOCS, "Gold-Price-Prediction-Presentation.pdf"))
