# make_ppt.py
# Builds the college presentation for the Gold Price Prediction project.
# Produces BOTH a real PowerPoint (.pptx) and a PDF mirror (for older Office PCs).
#   python make_ppt.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")
LOGO = os.path.join(HERE, "assets", "college_logo.jpg")
SHOT_PREDICT = os.path.join(DOCS, "screenshot_predict.png")
SHOT_TRAIN = os.path.join(DOCS, "screenshot_train.png")

TITLE = "Gold Price Prediction using Machine Learning"

TEAM_LINES = [
    "Submitted by:  Tapesh Sharma   (2300650100118)",
    "Team:  Sanchay Bhardwaj (2300650100104)   |   Vivek (2300650100127)",
    "Project Guide:  Mrs. Ashna Thakur",
    "B.S.A. College of Engineering & Technology, Mathura",
    "Dept. of Computer Science & Engineering   |   Session 2026-27",
]

# kind, then fields
SLIDES = [
    {"kind": "title"},
    {"kind": "bullets", "title": "Introduction", "bullets": [
        "Gold is a globally traded precious metal and a traditional safe-haven asset.",
        "Its price is affected by demand, inflation, currency value and market sentiment.",
        "Being able to forecast gold prices helps investors and analysts take better decisions.",
        "This project builds a Machine Learning model that predicts the monthly price of gold.",
    ]},
    {"kind": "bullets", "title": "Problem Statement", "bullets": [
        "Given the historical monthly price of gold, predict its price for the coming months.",
        "This is a supervised regression problem: past behaviour is the input, future price is the output.",
        "Multiple models are trained and the most accurate one is kept for prediction.",
    ]},
    {"kind": "bullets", "title": "Objectives", "bullets": [
        "Prepare a clean monthly gold price dataset for the years 2000 to 2024.",
        "Engineer features that capture the trend and the short-term momentum of prices.",
        "Train and compare RandomForest, Linear Regression and Ridge models.",
        "Measure accuracy using MAE, RMSE and R-squared against a naive baseline.",
        "Provide a simple desktop GUI so anyone can run a prediction.",
    ]},
    {"kind": "bullets", "title": "Dataset", "bullets": [
        "Monthly gold price in USD per troy ounce, from 2000 to 2024 (300 records).",
        "Columns in the file: Date, Year, Month and Price.",
        "Built from public annual-average anchors with a small momentum effect added.",
        "Model features: the last 3 monthly returns, plus the month and the year.",
    ]},
    {"kind": "bullets", "title": "Methodology", "bullets": [
        "The model predicts the month-to-month RETURN, not the raw price.",
        "Why: tree models cannot guess a price higher than they have seen, so a rising trend breaks them.",
        "Price is rebuilt as:  next price = last price x (1 + predicted return).",
        "Forecasting rolls forward one month at a time, feeding each answer back as the next input.",
        "A chronological split is used - the last 60 months are kept for testing.",
    ]},
    {"kind": "bullets", "title": "Technology Used", "bullets": [
        "Language: Python.",
        "Data handling: pandas and NumPy.",
        "Models: scikit-learn - RandomForest, Linear Regression, Ridge.",
        "Charts: Matplotlib.   Interface: Tkinter.   Save/Load: Joblib.",
    ]},
    {"kind": "table", "title": "Results",
     "header": ["Model", "MAE (USD)", "RMSE (USD)", "R-squared"],
     "rows": [["RandomForest (best)", "32.71", "44.47", "0.9613"],
              ["Linear Regression", "32.91", "44.60", "0.9611"],
              ["Ridge", "33.33", "45.50", "0.9595"],
              ["Naive baseline", "36.14", "47.97", "0.9549"]],
     "note": "Test window: last 60 months (from Jan 2020). Lower MAE / RMSE and higher R-squared are better."},
    {"kind": "image", "title": "Application - Prediction", "image": SHOT_PREDICT,
     "caption": "Desktop GUI: choose a horizon and forecast the gold price month by month."},
    {"kind": "image", "title": "Application - Model Comparison", "image": SHOT_TRAIN,
     "caption": "Train tab: accuracy table and the error comparison across models."},
    {"kind": "bullets", "title": "Conclusion", "bullets": [
        "RandomForest gave the best accuracy and clearly beat the naive baseline.",
        "Predicting returns instead of raw prices made the models reliable on a trending series.",
        "The Tkinter GUI turns the trained model into an easy-to-use forecasting tool.",
        "The project demonstrates a complete Machine Learning pipeline from data to interface.",
    ]},
    {"kind": "bullets", "title": "Future Scope", "bullets": [
        "Add real economic features such as inflation, USD index and interest rates.",
        "Try deep-learning time-series models like LSTM for longer forecasts.",
        "Connect a live gold price API so predictions always use current data.",
        "Show a confidence range instead of a single predicted value.",
    ]},
    {"kind": "end"},
]


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

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    W, H = prs.slide_width, prs.slide_height
    blank = prs.slide_layouts[6]

    def box(slide, l, t, w, h):
        tb = slide.shapes.add_textbox(l, t, w, h)
        tb.text_frame.word_wrap = True
        return tb.text_frame

    def setp(p, text, size, color, bold=False, align=PP_ALIGN.LEFT, after=6):
        p.text = text
        p.alignment = align
        p.space_after = Pt(after)
        r = p.runs[0] if p.runs else p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = "Calibri"

    def rect(slide, l, t, w, h, color):
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
        s.fill.solid()
        s.fill.fore_color.rgb = color
        s.line.fill.background()
        s.shadow.inherit = False
        return s

    def header(slide, title):
        rect(slide, 0, 0, W, Inches(1.05), NAVY)
        rect(slide, 0, Inches(1.05), W, Inches(0.06), GOLD)
        tf = box(slide, Inches(0.5), Inches(0.12), W - Inches(1.0), Inches(0.85))
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        setp(tf.paragraphs[0], title, 26, WHITE, bold=True)

    for sl in SLIDES:
        slide = prs.slides.add_slide(blank)
        kind = sl["kind"]
        if kind == "title":
            rect(slide, 0, 0, W, H, NAVY)
            rect(slide, 0, Inches(4.55), W, Inches(0.08), GOLD)
            slide.shapes.add_picture(LOGO, int((W - Inches(1.7)) / 2), Inches(0.7), Inches(1.7), Inches(1.7))
            tf = box(slide, Inches(0.8), Inches(2.6), W - Inches(1.6), Inches(1.6))
            setp(tf.paragraphs[0], TITLE, 34, WHITE, bold=True, align=PP_ALIGN.CENTER, after=4)
            setp(tf.add_paragraph(), "A Mini Project in Machine Learning", 18, GOLD, align=PP_ALIGN.CENTER)
            tf2 = box(slide, Inches(0.8), Inches(4.8), W - Inches(1.6), Inches(2.3))
            first = True
            for line in TEAM_LINES:
                p = tf2.paragraphs[0] if first else tf2.add_paragraph()
                setp(p, line, 13, WHITE, align=PP_ALIGN.CENTER, after=3)
                first = False
        elif kind == "bullets":
            header(slide, sl["title"])
            tf = box(slide, Inches(0.7), Inches(1.5), W - Inches(1.4), H - Inches(2.0))
            first = True
            for b in sl["bullets"]:
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                setp(p, "•   " + b, 18, DARK, after=14)
                first = False
        elif kind == "table":
            header(slide, sl["title"])
            rows = len(sl["rows"]) + 1
            cols = len(sl["header"])
            gt = slide.shapes.add_table(rows, cols, Inches(1.2), Inches(1.7),
                                        W - Inches(2.4), Inches(0.9 + 0.55 * rows)).table
            for c, h in enumerate(sl["header"]):
                cell = gt.cell(0, c)
                cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
                setp(cell.text_frame.paragraphs[0], h, 15, WHITE, bold=True, align=PP_ALIGN.CENTER)
            for r, row in enumerate(sl["rows"], start=1):
                for c, val in enumerate(row):
                    cell = gt.cell(r, c)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xEE, 0xF3, 0xFA) if r % 2 else WHITE
                    col = GOLD if (r == 1 and c == 0) else DARK
                    setp(cell.text_frame.paragraphs[0], val, 14, col,
                         bold=(r == 1 and c == 0), align=PP_ALIGN.CENTER)
            tf = box(slide, Inches(1.2), Inches(5.9), W - Inches(2.4), Inches(0.9))
            setp(tf.paragraphs[0], sl["note"], 12, MUT, align=PP_ALIGN.CENTER)
        elif kind == "image":
            header(slide, sl["title"])
            from PIL import Image
            iw, ih = Image.open(sl["image"]).size
            max_w = W - Inches(2.0)
            scale = min(max_w / iw, (H - Inches(2.2)) / ih)
            pw, ph = int(iw * scale), int(ih * scale)
            slide.shapes.add_picture(sl["image"], int((W - pw) / 2), Inches(1.5), pw, ph)
            tf = box(slide, Inches(1.0), Inches(6.7), W - Inches(2.0), Inches(0.6))
            setp(tf.paragraphs[0], sl["caption"], 13, MUT, align=PP_ALIGN.CENTER)
        elif kind == "end":
            rect(slide, 0, 0, W, H, NAVY)
            rect(slide, 0, Inches(3.9), W, Inches(0.06), GOLD)
            tf = box(slide, Inches(1.0), Inches(2.6), W - Inches(2.0), Inches(1.4))
            setp(tf.paragraphs[0], "Thank You", 54, WHITE, bold=True, align=PP_ALIGN.CENTER)
            tf2 = box(slide, Inches(1.0), Inches(4.2), W - Inches(2.0), Inches(1.2))
            setp(tf2.paragraphs[0], "Questions & suggestions are welcome", 18, GOLD, align=PP_ALIGN.CENTER, after=8)
            setp(tf2.add_paragraph(), TITLE, 14, WHITE, align=PP_ALIGN.CENTER)

    prs.save(path)
    print("pptx:", path)


# ------------------------------------------------------------------ PDF
def render_pdf(path):
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                    Table, TableStyle, PageBreak)
    from reportlab.lib.enums import TA_CENTER

    NAVY = HexColor("#1F3864")
    GOLD = HexColor("#C9A227")
    DARK = HexColor("#222222")
    MUT = HexColor("#6B7280")
    LIGHT = HexColor("#EEF3FA")

    PW, PH = 13.333 * inch, 7.5 * inch

    st_bar = ParagraphStyle("bar", fontName="Helvetica-Bold", fontSize=22, leading=28,
                            textColor=HexColor("#FFFFFF"), backColor=NAVY,
                            borderPadding=(10, 12, 10, 12))
    st_body = ParagraphStyle("body", fontName="Helvetica", fontSize=15, leading=24,
                             textColor=DARK, leftIndent=8, spaceAfter=10)
    st_note = ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=11,
                             leading=15, textColor=MUT, alignment=TA_CENTER)
    st_cap = ParagraphStyle("cap", fontName="Helvetica", fontSize=12, leading=16,
                            textColor=MUT, alignment=TA_CENTER)

    story = []

    def bar(title):
        story.append(Paragraph(title, st_bar))
        story.append(Spacer(1, 14))

    # ---- title slide ----
    def title_slide():
        logo = Image(LOGO, width=1.5 * inch, height=1.5 * inch)
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 26))
        story.append(Paragraph(TITLE, ParagraphStyle(
            "t", fontName="Helvetica-Bold", fontSize=26, leading=32,
            textColor=NAVY, alignment=TA_CENTER)))
        story.append(Spacer(1, 6))
        story.append(Paragraph("A Mini Project in Machine Learning", ParagraphStyle(
            "s", fontName="Helvetica-Bold", fontSize=14, leading=20,
            textColor=GOLD, alignment=TA_CENTER)))
        story.append(Spacer(1, 22))
        for line in TEAM_LINES:
            story.append(Paragraph(line, ParagraphStyle(
                "d", fontName="Helvetica", fontSize=11.5, leading=18,
                textColor=DARK, alignment=TA_CENTER)))
        story.append(PageBreak())

    title_slide()

    for sl in SLIDES:
        kind = sl["kind"]
        if kind == "title":
            continue
        if kind == "bullets":
            bar(sl["title"])
            for b in sl["bullets"]:
                story.append(Paragraph("&bull;&nbsp;&nbsp;" + b, st_body))
            story.append(PageBreak())
        elif kind == "table":
            bar(sl["title"])
            data = [sl["header"]] + sl["rows"]
            t = Table(data, colWidths=[3.4 * inch, 2.0 * inch, 2.0 * inch, 2.0 * inch])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("FONTNAME", (0, 1), (0, 1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 1), (0, 1), GOLD),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#C9D6EA")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))
            t.hAlign = "CENTER"
            story.append(t)
            story.append(Spacer(1, 16))
            story.append(Paragraph(sl["note"], st_note))
            story.append(PageBreak())
        elif kind == "image":
            bar(sl["title"])
            from PIL import Image as PImage
            iw, ih = PImage.open(sl["image"]).size
            max_w, max_h = 9.6 * inch, 4.7 * inch
            scale = min(max_w / iw, max_h / ih)
            img = Image(sl["image"], width=iw * scale, height=ih * scale)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 12))
            story.append(Paragraph(sl["caption"], st_cap))
            story.append(PageBreak())
        elif kind == "end":
            story.append(Spacer(1, 150))
            story.append(Paragraph("Thank You", ParagraphStyle(
                "ty", fontName="Helvetica-Bold", fontSize=40, leading=48,
                textColor=NAVY, alignment=TA_CENTER)))
            story.append(Spacer(1, 14))
            story.append(Paragraph("Questions & suggestions are welcome", ParagraphStyle(
                "q", fontName="Helvetica-Bold", fontSize=15, leading=22,
                textColor=GOLD, alignment=TA_CENTER)))
            story.append(Spacer(1, 8))
            story.append(Paragraph(TITLE, ParagraphStyle(
                "tt", fontName="Helvetica", fontSize=12, leading=18,
                textColor=MUT, alignment=TA_CENTER)))

    doc = SimpleDocTemplate(path, pagesize=(PW, PH),
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                            title=TITLE, author="Tapesh Sharma")
    doc.build(story)
    print("pdf:", path)


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    render_pptx(os.path.join(DOCS, "Gold-Price-Prediction-Presentation.pptx"))
    render_pdf(os.path.join(DOCS, "Gold-Price-Prediction-Presentation.pdf"))
