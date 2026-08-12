"""
Final Report PDF Generator
Bluestock Mutual Fund Analytics - Capstone Project
Generates a professional 15-20 page PDF report using ReportLab.
"""

import os
import csv
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem,
    Frame, PageTemplate, BaseDocTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Circle
from reportlab.graphics import renderPDF

# ─────────────────────────── colour palette ────────────────────────────
PRIMARY      = HexColor("#1a237e")   # deep indigo
SECONDARY    = HexColor("#283593")
ACCENT       = HexColor("#3949ab")
LIGHT_BG     = HexColor("#e8eaf6")
TABLE_HEADER = HexColor("#1a237e")
TABLE_ALT    = HexColor("#f5f5f5")
TEXT_DARK     = HexColor("#212121")
TEXT_LIGHT    = HexColor("#757575")
BORDER        = HexColor("#bdbdbd")
SUCCESS       = HexColor("#2e7d32")
WARNING       = HexColor("#f57f17")
HIGHLIGHT     = HexColor("#0d47a1")

WIDTH, HEIGHT = A4  # 595.27 × 841.89 points

# ──────────────────────── load risk metrics ────────────────────────────
def load_risk_metrics():
    """Load the processed risk metrics CSV and return a list of dicts."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "processed", "risk_metrics.csv"
    )
    csv_path = os.path.normpath(csv_path)
    rows = []
    if not os.path.exists(csv_path):
        return rows
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

# ─────────────────────── reusable styles ───────────────────────────────
def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "TitleMain", fontName="Helvetica-Bold", fontSize=28,
        textColor=white, alignment=TA_CENTER, spaceAfter=6, leading=34
    ))
    styles.add(ParagraphStyle(
        "SubTitle", fontName="Helvetica", fontSize=16,
        textColor=HexColor("#c5cae9"), alignment=TA_CENTER,
        spaceAfter=12, leading=22
    ))
    styles.add(ParagraphStyle(
        "AuthorLine", fontName="Helvetica", fontSize=12,
        textColor=HexColor("#e8eaf6"), alignment=TA_CENTER,
        spaceBefore=4, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        "SectionHeading", fontName="Helvetica-Bold", fontSize=18,
        textColor=PRIMARY, spaceBefore=24, spaceAfter=10, leading=22,
        borderPadding=(0, 0, 4, 0)
    ))
    styles.add(ParagraphStyle(
        "SubSectionHeading", fontName="Helvetica-Bold", fontSize=14,
        textColor=SECONDARY, spaceBefore=16, spaceAfter=8, leading=18
    ))
    styles.add(ParagraphStyle(
        "SubSubHeading", fontName="Helvetica-Bold", fontSize=12,
        textColor=ACCENT, spaceBefore=12, spaceAfter=6, leading=15
    ))
    styles.add(ParagraphStyle(
        "BodyText2", fontName="Helvetica", fontSize=10.5,
        textColor=TEXT_DARK, alignment=TA_JUSTIFY,
        spaceBefore=4, spaceAfter=6, leading=15
    ))
    styles.add(ParagraphStyle(
        "BodyBold", fontName="Helvetica-Bold", fontSize=10.5,
        textColor=TEXT_DARK, alignment=TA_JUSTIFY,
        spaceBefore=2, spaceAfter=4, leading=15
    ))
    styles.add(ParagraphStyle(
        "BulletText", fontName="Helvetica", fontSize=10.5,
        textColor=TEXT_DARK, alignment=TA_LEFT,
        leftIndent=24, spaceBefore=2, spaceAfter=2, leading=14,
        bulletIndent=12, bulletFontName="Helvetica", bulletFontSize=10
    ))
    styles.add(ParagraphStyle(
        "FooterStyle", fontName="Helvetica", fontSize=8,
        textColor=TEXT_LIGHT, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "CaptionStyle", fontName="Helvetica-Oblique", fontSize=9,
        textColor=TEXT_LIGHT, alignment=TA_CENTER,
        spaceBefore=4, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        "CodeStyle", fontName="Courier", fontSize=9,
        textColor=HexColor("#263238"), backColor=HexColor("#eceff1"),
        spaceBefore=4, spaceAfter=4, leading=12,
        leftIndent=12, rightIndent=12,
        borderPadding=6
    ))
    styles.add(ParagraphStyle(
        "TOCEntry", fontName="Helvetica", fontSize=11,
        textColor=TEXT_DARK, spaceBefore=6, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        "CalloutBox", fontName="Helvetica", fontSize=10,
        textColor=PRIMARY, backColor=LIGHT_BG,
        borderPadding=10, spaceBefore=8, spaceAfter=8,
        leading=14, alignment=TA_LEFT
    ))
    return styles

# ─────────────────────── helper functions ──────────────────────────────
def section_heading(text, styles):
    """Return a list of flowables for a numbered section heading with underline."""
    return [
        Spacer(1, 6),
        Paragraph(text, styles["SectionHeading"]),
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY,
                    spaceAfter=8, spaceBefore=0),
    ]


def sub_heading(text, styles):
    return [Paragraph(text, styles["SubSectionHeading"])]


def body(text, styles):
    return [Paragraph(text, styles["BodyText2"])]


def bullet_list(items, styles):
    """Create a styled bullet list."""
    flowables = []
    for item in items:
        flowables.append(Paragraph(f"• {item}", styles["BulletText"]))
    return flowables


def callout_box(text, styles):
    """A highlighted box for key statistics."""
    return [Paragraph(text, styles["CalloutBox"])]


def build_table(headers, data_rows, col_widths=None):
    """Build a styled Table flowable."""
    header_paras = [
        Paragraph(f'<font color="white"><b>{h}</b></font>', 
                  ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9,
                                 textColor=white, alignment=TA_CENTER, leading=12))
        for h in headers
    ]
    styled_rows = []
    for row in data_rows:
        styled_rows.append([
            Paragraph(str(cell),
                      ParagraphStyle("td", fontName="Helvetica", fontSize=9,
                                     textColor=TEXT_DARK, alignment=TA_CENTER, leading=12))
            for cell in row
        ])
    table_data = [header_paras] + styled_rows
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND",   (0, 0), (-1, 0), TABLE_HEADER),
        ("TEXTCOLOR",    (0, 0), (-1, 0), white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 8),
        ("TOPPADDING",   (0, 0), (-1, 0), 8),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("BOTTOMPADDING",(0, 1), (-1, -1), 6),
        ("TOPPADDING",   (0, 1), (-1, -1), 6),
        ("GRID",         (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, TABLE_ALT]),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def kpi_card_table(kpis, styles):
    """Create a row of KPI cards.  kpis = [(label, value), ...]"""
    cells_top = []
    cells_bot = []
    for label, value in kpis:
        cells_top.append(Paragraph(
            f'<font color="white"><b>{value}</b></font>',
            ParagraphStyle("kv", fontName="Helvetica-Bold", fontSize=16,
                           textColor=white, alignment=TA_CENTER, leading=20)))
        cells_bot.append(Paragraph(
            f'<font color="#c5cae9">{label}</font>',
            ParagraphStyle("kl", fontName="Helvetica", fontSize=9,
                           textColor=HexColor("#c5cae9"), alignment=TA_CENTER,
                           leading=12)))
    col_w = (WIDTH - 2 * inch) / len(kpis)
    t = Table([cells_top, cells_bot], colWidths=[col_w] * len(kpis))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 14),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
        ("BOX",        (0, 0), (-1, -1), 1, PRIMARY),
        ("LINEAFTER",  (0, 0), (-2, -1), 0.5, HexColor("#3949ab")),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return t


# ───────────────────── header / footer callbacks ───────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1.5)
    canvas.line(inch, HEIGHT - 0.6 * inch, WIDTH - inch, HEIGHT - 0.6 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(TEXT_LIGHT)
    canvas.drawString(inch, HEIGHT - 0.52 * inch,
                      "Bluestock Fintech  |  Mutual Fund Analytics")
    canvas.drawRightString(WIDTH - inch, HEIGHT - 0.52 * inch,
                           "Capstone Project Report")
    # Footer
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(inch, 0.55 * inch, WIDTH - inch, 0.55 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(TEXT_LIGHT)
    canvas.drawString(inch, 0.38 * inch, "Confidential — For Internal Use Only")
    canvas.drawRightString(WIDTH - inch, 0.38 * inch,
                           f"Page {doc.page}")
    canvas.restoreState()


def _title_page_bg(canvas, doc):
    """Custom background for the title page."""
    canvas.saveState()
    # full-page gradient block
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, HEIGHT * 0.35, WIDTH, HEIGHT * 0.65, fill=1, stroke=0)
    canvas.setFillColor(SECONDARY)
    canvas.rect(0, HEIGHT * 0.30, WIDTH, HEIGHT * 0.05, fill=1, stroke=0)
    # decorative accent bar
    canvas.setFillColor(ACCENT)
    canvas.rect(0, 0, WIDTH, HEIGHT * 0.30, fill=1, stroke=0)
    # subtle circles
    canvas.setFillColor(Color(1, 1, 1, 0.04))
    canvas.circle(WIDTH * 0.8, HEIGHT * 0.75, 120, fill=1, stroke=0)
    canvas.circle(WIDTH * 0.15, HEIGHT * 0.55, 80, fill=1, stroke=0)
    canvas.restoreState()


# ═══════════════════════ MAIN BUILD FUNCTION ═══════════════════════════
def build_report():
    output_path = os.path.join(os.path.dirname(__file__), "Final_Report.pdf")
    metrics = load_risk_metrics()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=inch,
        rightMargin=inch,
        title="Mutual Fund Analytics - Capstone Project Report",
        author="Akash Kumar Pandit",
    )
    styles = build_styles()
    story = []

    # ────────────────────── 1. TITLE PAGE ──────────────────────────────
    # Title page gets its own background via afterPage
    story.append(Spacer(1, 2.2 * inch))
    story.append(Paragraph("Mutual Fund Analytics", styles["TitleMain"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Capstone Project Report", styles["SubTitle"]))
    story.append(Spacer(1, 0.6 * inch))
    story.append(HRFlowable(width="40%", thickness=1, color=HexColor("#5c6bc0"),
                             spaceAfter=16, spaceBefore=0))
    story.append(Paragraph("Prepared for", styles["AuthorLine"]))
    story.append(Paragraph("<b>Bluestock Fintech</b>", styles["SubTitle"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Author: <b>Akash Kumar Pandit</b>", styles["AuthorLine"]))
    story.append(Paragraph("Date: August 2026", styles["AuthorLine"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Version 1.0", styles["AuthorLine"]))
    story.append(PageBreak())

    # ────────────────────── TABLE OF CONTENTS ──────────────────────────
    story.extend(section_heading("Table of Contents", styles))
    story.append(Spacer(1, 8))
    toc_items = [
        ("1.", "Executive Summary", "3"),
        ("2.", "Data Sources & Collection", "4"),
        ("3.", "ETL Pipeline Design", "6"),
        ("4.", "Exploratory Data Analysis", "8"),
        ("5.", "Performance & Risk Analysis", "10"),
        ("6.", "Key Metrics & Fund Rankings", "12"),
        ("7.", "Dashboard Overview", "14"),
        ("8.", "Limitations & Constraints", "16"),
        ("9.", "Recommendations & Future Scope", "17"),
        ("10.", "Appendix — Technology Stack", "19"),
    ]
    toc_data = [[
        Paragraph(f'<font color="#1a237e"><b>{no}</b></font>',
                  ParagraphStyle("tn", fontName="Helvetica-Bold", fontSize=11,
                                 textColor=PRIMARY, leading=14)),
        Paragraph(title,
                  ParagraphStyle("tt", fontName="Helvetica", fontSize=11,
                                 textColor=TEXT_DARK, leading=14)),
        Paragraph(pg,
                  ParagraphStyle("tp", fontName="Helvetica", fontSize=11,
                                 textColor=TEXT_LIGHT, alignment=TA_RIGHT, leading=14)),
    ] for no, title, pg in toc_items]
    toc_table = Table(toc_data, colWidths=[0.5 * inch, 4.2 * inch, 0.6 * inch])
    toc_table.setStyle(TableStyle([
        ("VALIGN",   (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LINEBELOW",    (0, 0), (-1, -1), 0.3, BORDER),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ───────────────── 2. EXECUTIVE SUMMARY ────────────────────────────
    story.extend(section_heading("1.  Executive Summary", styles))

    story.extend(body(
        "This report presents the findings of the <b>Mutual Fund Analytics Capstone Project</b> "
        "undertaken at <b>Bluestock Fintech</b>. The project involved ingesting, cleaning, and "
        "analysing data for <b>40 mutual fund schemes</b> across <b>10 major Indian fund houses</b>, "
        "covering both Equity and Debt categories. The primary objectives were to build a robust "
        "ETL pipeline, compute risk-adjusted performance metrics, and deliver an interactive "
        "analytical dashboard.", styles))
    story.append(Spacer(1, 6))

    story.extend(body(
        "The analytical workflow spanned the full data-science lifecycle — from raw CSV ingestion "
        "and SQLite warehousing, through exploratory data analysis, to advanced quantitative "
        "modelling. Key deliverables include:", styles))
    story.append(Spacer(1, 4))

    story.extend(bullet_list([
        "A <b>Python-based ETL pipeline</b> loading 10 CSV datasets and live NAV data into a "
        "normalised SQLite database with 16 tables.",
        "Computation of <b>risk metrics</b> — annualized volatility, maximum drawdown, beta, and "
        "Jensen's alpha — for every scheme, benchmarked against the Nifty 50 index.",
        "<b>K-Means clustering</b> of funds into three risk profiles (Low / Medium / High Risk), "
        "enabling portfolio-level risk categorisation.",
        "Moving-average trend indicators (<b>SMA-30, EMA-30</b>) for short-term momentum analysis.",
        "A <b>4-page interactive dashboard</b> covering Industry Overview, Fund Performance, "
        "Investor Analytics, and SIP & Market Trends.",
    ], styles))
    story.append(Spacer(1, 8))

    # KPI cards
    low = sum(1 for m in metrics if m.get("risk_profile") == "Low Risk")
    med = sum(1 for m in metrics if m.get("risk_profile") == "Medium Risk")
    high = sum(1 for m in metrics if m.get("risk_profile") == "High Risk")

    kpi = kpi_card_table([
        ("Schemes Analysed", "40"),
        ("Fund Houses", "10"),
        ("Low Risk", str(low)),
        ("Medium Risk", str(med)),
        ("High Risk", str(high)),
    ], styles)
    story.append(kpi)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Figure 1: Key project metrics at a glance",
                           styles["CaptionStyle"]))
    story.append(PageBreak())

    # ────────────────── 3. DATA SOURCES ────────────────────────────────
    story.extend(section_heading("2.  Data Sources & Collection", styles))

    story.extend(body(
        "The project consumed two distinct data channels: (a) <b>ten structured CSV files</b> "
        "supplied by Bluestock Fintech, each capturing a different dimension of the Indian mutual "
        "fund ecosystem, and (b) <b>live Net Asset Value (NAV) data</b> fetched via the open REST "
        "API at <font color='#1a237e'><i>mfapi.in</i></font>.", styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("2.1  Static CSV Datasets", styles))
    story.extend(body(
        "The ten CSV files were placed under <font name='Courier' size='9.5'>data/raw/</font> "
        "and collectively represent the most critical facets of mutual fund operations — from "
        "scheme metadata to investor transaction logs. The table below summarises each file:",
        styles))
    story.append(Spacer(1, 6))

    ds_headers = ["#", "Dataset", "Description", "Key Columns"]
    ds_rows = [
        ["1", "fund_master", "Scheme metadata (40 schemes)", "amfi_code, fund_house, category"],
        ["2", "nav_history", "Historical daily NAV data", "date, nav, amfi_code"],
        ["3", "aum_by_fund_house", "AUM across fund houses", "fund_house, aum_cr"],
        ["4", "monthly_sip_inflows", "Monthly SIP flow trends", "month, inflow_cr"],
        ["5", "category_inflows", "Category-level fund flows", "category, net_inflow"],
        ["6", "industry_folio_count", "Total folio counts over time", "year, folio_count"],
        ["7", "scheme_performance", "Return metrics per scheme", "amfi_code, 1yr_return"],
        ["8", "investor_transactions", "Individual transaction logs", "investor_id, txn_type, amount"],
        ["9", "portfolio_holdings", "Top holdings per scheme", "amfi_code, stock, weight"],
        ["10", "benchmark_indices", "Nifty 50 / Sensex daily data", "date, close_value"],
    ]
    story.append(build_table(ds_headers, ds_rows,
                             col_widths=[0.35*inch, 1.4*inch, 2.1*inch, 1.65*inch]))
    story.append(Paragraph("Table 1: Summary of 10 CSV datasets provided by Bluestock",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("2.2  Live NAV API", styles))
    story.extend(body(
        "To supplement the static datasets, live NAV history was fetched from the "
        "<b>mfapi.in</b> REST API for six key large-cap schemes. The API returns daily NAV records "
        "since inception, giving us granular time-series data that enabled moving-average and "
        "drawdown calculations. Each API response is saved as a separate CSV file under "
        "<font name='Courier' size='9.5'>data/raw/nav_&lt;scheme_code&gt;.csv</font>.", styles))
    story.append(Spacer(1, 6))

    api_headers = ["Scheme Code", "Fund House", "Scheme Type"]
    api_rows = [
        ["125497", "HDFC Mutual Fund", "Large Cap — Direct Growth"],
        ["119551", "SBI Mutual Fund", "Large Cap — Direct Growth"],
        ["120503", "ICICI Prudential", "Large Cap — Direct Growth"],
        ["118632", "Nippon India", "Large Cap — Direct Growth"],
        ["119092", "Axis Mutual Fund", "Large Cap — Direct Growth"],
        ["120841", "Kotak Mahindra", "Large Cap — Direct Growth"],
    ]
    story.append(build_table(api_headers, api_rows,
                             col_widths=[1.1*inch, 2.0*inch, 2.4*inch]))
    story.append(Paragraph("Table 2: Schemes fetched via live NAV API (mfapi.in)",
                           styles["CaptionStyle"]))
    story.append(PageBreak())

    # ────────────────── 4. ETL DESIGN ──────────────────────────────────
    story.extend(section_heading("3.  ETL Pipeline Design", styles))

    story.extend(body(
        "A lightweight yet robust <b>Extract-Transform-Load (ETL)</b> pipeline was developed in "
        "Python to automate data ingestion into a local SQLite database. The design philosophy "
        "favoured simplicity and reproducibility — the entire pipeline can be re-run with a "
        "single command, making it suitable for both development and demonstration environments.",
        styles))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("3.1  Architecture Overview", styles))

    # Pipeline flow table
    flow_data = [
        [Paragraph('<font color="white"><b>Phase</b></font>',
                   ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10,
                                  textColor=white, alignment=TA_CENTER)),
         Paragraph('<font color="white"><b>Description</b></font>',
                   ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10,
                                  textColor=white, alignment=TA_CENTER)),
         Paragraph('<font color="white"><b>Tool / Library</b></font>',
                   ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10,
                                  textColor=white, alignment=TA_CENTER))],
        [Paragraph("Extract", ParagraphStyle("e", fontName="Helvetica-Bold", fontSize=10,
                                             textColor=PRIMARY)),
         Paragraph("Read 10 CSV files from <font name='Courier'>data/raw/</font>; "
                   "fetch live NAV via REST API",
                   ParagraphStyle("e2", fontName="Helvetica", fontSize=9.5, leading=13)),
         Paragraph("pandas, requests",
                   ParagraphStyle("e3", fontName="Courier", fontSize=9, leading=12))],
        [Paragraph("Transform", ParagraphStyle("e", fontName="Helvetica-Bold", fontSize=10,
                                               textColor=PRIMARY)),
         Paragraph("Normalise column names (lowercase, underscores); parse dates; "
                   "handle missing values; strip whitespace",
                   ParagraphStyle("e2", fontName="Helvetica", fontSize=9.5, leading=13)),
         Paragraph("pandas",
                   ParagraphStyle("e3", fontName="Courier", fontSize=9, leading=12))],
        [Paragraph("Load", ParagraphStyle("e", fontName="Helvetica-Bold", fontSize=10,
                                          textColor=PRIMARY)),
         Paragraph("Write each DataFrame to a SQLite table "
                   "(<font name='Courier'>to_sql</font> with <font name='Courier'>"
                   "if_exists='replace'</font>)",
                   ParagraphStyle("e2", fontName="Helvetica", fontSize=9.5, leading=13)),
         Paragraph("sqlite3, pandas",
                   ParagraphStyle("e3", fontName="Courier", fontSize=9, leading=12))],
    ]
    flow_table = Table(flow_data, colWidths=[1.1*inch, 3.0*inch, 1.4*inch])
    flow_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), TABLE_HEADER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [white, TABLE_ALT]),
    ]))
    story.append(flow_table)
    story.append(Paragraph("Table 3: ETL pipeline phases", styles["CaptionStyle"]))

    story.extend(sub_heading("3.2  Database Schema", styles))
    story.extend(body(
        "The resulting SQLite database (<font name='Courier' size='9.5'>data/processed/database.db"
        "</font>) contains <b>16 tables</b>: 10 from the static CSVs, 6 from the live NAV API "
        "feeds, and a derived <font name='Courier' size='9.5'>risk_metrics</font> table produced "
        "by the analytics module. Key design decisions:", styles))
    story.append(Spacer(1, 4))
    story.extend(bullet_list([
        "All column names converted to <font name='Courier'>snake_case</font> for SQL "
        "compatibility (e.g., <i>Fund House</i> → <font name='Courier'>fund_house</font>).",
        "Numeric prefixes stripped from table names (e.g., <font name='Courier'>01_fund_master"
        "</font> → <font name='Courier'>fund_master</font>).",
        "Tables are created with <font name='Courier'>if_exists='replace'</font> to ensure "
        "idempotent re-runs without manual cleanup.",
        "Date columns parsed with <font name='Courier'>dayfirst=True</font> to handle the "
        "DD-MM-YYYY format common in Indian datasets.",
        "The SQLite database is self-contained at <b>~6.9 MB</b>, portable across environments.",
    ], styles))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("3.3  Data Quality Checks", styles))
    story.extend(body(
        "An automated validation step cross-references AMFI scheme codes between the "
        "<font name='Courier'>fund_master</font> and <font name='Courier'>nav_history</font> "
        "tables, flagging orphan records. Additional checks include:", styles))
    story.extend(bullet_list([
        "Null / NaN detection across all columns with logging of affected row counts.",
        "Duplicate row identification and removal in transaction logs.",
        "Date-range validation — ensuring NAV dates do not extend beyond the analysis window.",
        "Data-type enforcement — ensuring NAV values are numeric and non-negative.",
    ], styles))
    story.append(PageBreak())

    # ────────────── 5. EXPLORATORY DATA ANALYSIS ───────────────────────
    story.extend(section_heading("4.  Exploratory Data Analysis", styles))

    story.extend(body(
        "A comprehensive EDA was conducted to understand the structure, distribution, and "
        "inter-relationships within the ingested data. The analysis uncovered the following "
        "high-level statistics:", styles))
    story.append(Spacer(1, 6))

    kpi2 = kpi_card_table([
        ("Schemes", "40"),
        ("Fund Houses", "10"),
        ("Categories", "2"),
        ("Sub-Categories", "12"),
    ], styles)
    story.append(kpi2)
    story.append(Spacer(1, 6))
    kpi3 = kpi_card_table([
        ("Transactions", "32,778"),
        ("Benchmark Records", "8,050"),
        ("NAV Data Points", "~115K"),
        ("Holdings Rows", "~600"),
    ], styles)
    story.append(kpi3)
    story.append(Paragraph("Figure 2: Dataset dimensions at a glance",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("4.1  Fund Universe Composition", styles))
    story.extend(body(
        "The fund master file contains <b>40 schemes</b> issued by 10 fund houses. "
        "These are split across <b>2 broad categories</b> — Equity and Debt — and further "
        "granulated into <b>12 sub-categories</b> such as Large Cap, Mid Cap, Small Cap, "
        "Flexi Cap, ELSS, Short Duration, Corporate Bond, Dynamic Bond, and others.", styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("4.2  Fund House Coverage", styles))
    fund_houses = [
        ["1", "SBI Mutual Fund", "Equity + Debt"],
        ["2", "HDFC Mutual Fund", "Equity + Debt"],
        ["3", "ICICI Prudential MF", "Equity + Debt"],
        ["4", "Nippon India MF", "Equity + Debt"],
        ["5", "Axis Mutual Fund", "Equity + Debt"],
        ["6", "Kotak Mahindra MF", "Equity + Debt"],
        ["7", "Aditya Birla SL MF", "Equity + Debt"],
        ["8", "UTI Mutual Fund", "Equity + Debt"],
        ["9", "DSP Mutual Fund", "Equity + Debt"],
        ["10", "Tata Mutual Fund", "Equity + Debt"],
    ]
    story.append(build_table(["#", "Fund House", "Categories Covered"], fund_houses,
                             col_widths=[0.4*inch, 2.8*inch, 2.3*inch]))
    story.append(Paragraph("Table 4: Fund houses in the analysis universe",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("4.3  Transaction Analysis", styles))
    story.extend(body(
        "The <font name='Courier'>investor_transactions</font> dataset contains <b>32,778 "
        "records</b> covering purchases (lump-sum and SIP), redemptions, and switches. "
        "Key observations from the transaction data:", styles))
    story.extend(bullet_list([
        "SIP transactions constitute the majority of purchase volume, aligning with the "
        "industry-wide trend toward systematic investment plans.",
        "Redemption activity peaks around financial-year-end (March), suggesting tax-loss "
        "harvesting and rebalancing behaviour.",
        "Average transaction amount varies significantly across categories — equity "
        "transactions average higher than debt.",
        "Transaction frequency is highest for large-cap equity schemes, consistent with "
        "their higher liquidity and retail investor preference.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("4.4  Benchmark Index Data", styles))
    story.extend(body(
        "The benchmark dataset includes <b>8,050 daily records</b> for key indices including "
        "Nifty 50 and Sensex. This data was used to compute relative performance metrics "
        "(alpha and beta) for each scheme. The Nifty 50 was chosen as the primary benchmark "
        "given the equity-heavy composition of the fund universe.", styles))
    story.append(PageBreak())

    # ───────── 6. PERFORMANCE & RISK ANALYSIS ──────────────────────────
    story.extend(section_heading("5.  Performance & Risk Analysis", styles))

    story.extend(body(
        "The core analytical module (<font name='Courier' size='9.5'>advanced_analytics_script.py"
        "</font>) computes a battery of quantitative risk and return metrics for each of the 40 "
        "schemes. The methodology is described below.", styles))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("5.1  Risk Metrics Methodology", styles))

    metrics_desc = [
        ["Annualised Std Dev (σ)", "Daily return standard deviation × √252. Measures total "
         "volatility over the observation window."],
        ["Maximum Drawdown", "Largest peak-to-trough decline in NAV, expressed as a fraction. "
         "Captures worst-case capital loss."],
        ["Beta (β)", "Covariance of fund daily returns with Nifty 50 returns divided by the "
         "variance of the benchmark. β > 1 indicates amplified market sensitivity."],
        ["Jensen's Alpha (α)", "Excess return over the CAPM-predicted return: α = R_fund − "
         "[R_f + β × (R_mkt − R_f)]. A risk-free rate of 5% was assumed."],
        ["SMA-30 / EMA-30", "30-day Simple and Exponential Moving Averages of NAV, used as "
         "short-term trend indicators."],
    ]
    metrics_desc_headers = ["Metric", "Definition & Interpretation"]
    story.append(build_table(metrics_desc_headers, metrics_desc,
                             col_widths=[1.6*inch, 3.9*inch]))
    story.append(Paragraph("Table 5: Risk metrics computed for each scheme",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("5.2  K-Means Risk Clustering", styles))
    story.extend(body(
        "After computing per-scheme risk metrics, <b>K-Means clustering (k=3)</b> was applied "
        "on the normalised feature space of <i>annualised volatility</i> and <i>alpha</i> to "
        "segment funds into three intuitive risk profiles:", styles))
    story.append(Spacer(1, 4))

    cluster_data = [
        ["Low Risk", str(low), "Low volatility, moderate alpha",
         "Suitable for conservative investors"],
        ["Medium Risk", str(med), "Moderate volatility, higher alpha",
         "Balanced risk-return profile"],
        ["High Risk", str(high), "High volatility, extreme alpha",
         "For aggressive, risk-tolerant investors"],
    ]
    story.append(build_table(
        ["Risk Profile", "Count", "Characteristics", "Investor Fit"],
        cluster_data,
        col_widths=[1.0*inch, 0.6*inch, 1.9*inch, 2.0*inch]))
    story.append(Paragraph("Table 6: K-Means cluster summary (k=3)",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("5.3  Trend Analysis — Moving Averages", styles))
    story.extend(body(
        "For each scheme, 30-day Simple Moving Average (SMA) and Exponential Moving Average "
        "(EMA) were computed on the NAV time series. These indicators serve as momentum signals:",
        styles))
    story.extend(bullet_list([
        "<b>NAV above SMA-30</b>: indicates short-term bullish momentum.",
        "<b>NAV below SMA-30</b>: suggests potential weakness or mean-reversion opportunity.",
        "<b>EMA-30</b> is more responsive to recent price changes due to its exponential "
        "weighting, making it useful for detecting trend reversals earlier than SMA.",
        "Golden / death crosses (SMA-30 crossing SMA-90) were used as supplementary "
        "signals during the analysis window.",
    ], styles))
    story.append(PageBreak())

    # ──────────── 7. KEY METRICS & FUND RANKINGS ───────────────────────
    story.extend(section_heading("6.  Key Metrics & Fund Rankings", styles))

    story.extend(body(
        "This section presents the actual computed risk metrics from the analysis pipeline. "
        "Data is sourced from <font name='Courier' size='9.5'>data/processed/risk_metrics.csv"
        "</font>, which contains metrics for all 40 analysed schemes.", styles))
    story.append(Spacer(1, 8))

    # Top 5 funds by alpha
    story.extend(sub_heading("6.1  Top 5 Funds by Alpha", styles))
    story.extend(body(
        "Jensen's alpha represents the excess risk-adjusted return over the benchmark. "
        "The five schemes with the highest alpha are:", styles))
    story.append(Spacer(1, 4))

    sorted_by_alpha = sorted(metrics, key=lambda x: float(x.get("alpha", 0)), reverse=True)
    top5_alpha = sorted_by_alpha[:5]
    top5_data = []
    for i, m in enumerate(top5_alpha, 1):
        top5_data.append([
            str(i),
            m.get("scheme_name", "N/A"),
            f'{float(m.get("alpha", 0)):.4f}',
            f'{float(m.get("beta", 0)):.4f}',
            f'{float(m.get("annualized_std_dev", 0)):.4f}',
            m.get("risk_profile", "N/A"),
        ])
    story.append(build_table(
        ["Rank", "Scheme", "Alpha (α)", "Beta (β)", "Std Dev (σ)", "Risk Profile"],
        top5_data,
        col_widths=[0.4*inch, 1.2*inch, 0.85*inch, 0.8*inch, 0.85*inch, 1.0*inch]))
    story.append(Paragraph("Table 7: Top 5 funds ranked by Jensen's alpha",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 8))

    # Bottom 5 (lowest alpha / most conservative)
    story.extend(sub_heading("6.2  Most Conservative Funds (Lowest Volatility)", styles))
    sorted_by_vol = sorted(metrics, key=lambda x: float(x.get("annualized_std_dev", 999)))
    bottom5_vol = sorted_by_vol[:5]
    b5_data = []
    for i, m in enumerate(bottom5_vol, 1):
        b5_data.append([
            str(i),
            m.get("scheme_name", "N/A"),
            f'{float(m.get("annualized_std_dev", 0)):.4f}',
            f'{float(m.get("max_drawdown", 0)):.4f}',
            f'₹{float(m.get("latest_nav", 0)):,.2f}',
            m.get("risk_profile", "N/A"),
        ])
    story.append(build_table(
        ["Rank", "Scheme", "Std Dev (σ)", "Max DD", "Latest NAV", "Risk Profile"],
        b5_data,
        col_widths=[0.4*inch, 1.2*inch, 0.85*inch, 0.8*inch, 1.0*inch, 0.85*inch]))
    story.append(Paragraph("Table 8: Top 5 most conservative funds by volatility",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 8))

    # Risk distribution summary
    story.extend(sub_heading("6.3  Risk Profile Distribution", styles))
    story.extend(body(
        "The K-Means clustering resulted in the following distribution across the 40 schemes:",
        styles))
    story.append(Spacer(1, 4))

    total = len(metrics)
    dist_data = [
        ["Low Risk", str(low), f"{low/total*100:.1f}%" if total else "—",
         "Debt schemes & low-volatility equity"],
        ["Medium Risk", str(med), f"{med/total*100:.1f}%" if total else "—",
         "Large-cap & diversified equity"],
        ["High Risk", str(high), f"{high/total*100:.1f}%" if total else "—",
         "Small/mid-cap or thematic equity"],
    ]
    story.append(build_table(
        ["Profile", "Count", "% of Universe", "Typical Composition"],
        dist_data,
        col_widths=[1.0*inch, 0.7*inch, 1.0*inch, 2.8*inch]))
    story.append(Paragraph("Table 9: Risk profile distribution across 40 schemes",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 8))

    # Full metrics table (compact — showing a selection)
    story.extend(sub_heading("6.4  Complete Risk Metrics Summary", styles))
    story.extend(body(
        "The following table provides an abridged view of the risk metrics for all analysed "
        "schemes, sorted by alpha (descending). Full data is available in the CSV output file.",
        styles))
    story.append(Spacer(1, 4))

    all_data = []
    for m in sorted_by_alpha:
        all_data.append([
            m.get("amfi_code", ""),
            f'{float(m.get("alpha", 0)):.3f}',
            f'{float(m.get("beta", 0)):.3f}',
            f'{float(m.get("annualized_std_dev", 0)):.3f}',
            f'{float(m.get("max_drawdown", 0)):.3f}',
            m.get("risk_profile", "")[0] if m.get("risk_profile") else "—",
        ])
    story.append(build_table(
        ["AMFI Code", "Alpha", "Beta", "Std Dev", "Max DD", "Risk"],
        all_data,
        col_widths=[0.9*inch, 0.8*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.6*inch]))
    story.append(Paragraph("Table 10: All 40 schemes — risk metrics (sorted by alpha desc)",
                           styles["CaptionStyle"]))
    story.append(PageBreak())

    # ──────────── 8. DASHBOARD OVERVIEW ────────────────────────────────
    story.extend(section_heading("7.  Dashboard Overview", styles))

    story.extend(body(
        "A <b>4-page interactive analytical dashboard</b> was designed to provide stakeholders "
        "with an intuitive, visual interface for exploring the mutual fund analytics. The "
        "dashboard was architected to support drill-down analysis across multiple dimensions.",
        styles))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("7.1  Page 1 — Industry Overview", styles))
    story.extend(body(
        "The first dashboard page presents a macro view of the Indian mutual fund industry. "
        "It includes:", styles))
    story.extend(bullet_list([
        "<b>Total AUM Distribution</b> — horizontal bar chart showing assets under management "
        "by fund house, enabling quick identification of market leaders.",
        "<b>Industry Folio Growth</b> — line chart tracking the year-over-year growth in total "
        "folio counts, reflecting increasing retail participation.",
        "<b>Category-Level Inflows</b> — stacked bar chart comparing net inflows across Equity, "
        "Debt, Hybrid, and other categories.",
        "<b>Fund House Market Share</b> — donut chart showing the relative market share based "
        "on AUM.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("7.2  Page 2 — Fund Performance", styles))
    story.extend(body(
        "The performance page enables scheme-level analysis:", styles))
    story.extend(bullet_list([
        "<b>NAV Time Series</b> — interactive line chart with date-range selector showing "
        "historical NAV trends for selected schemes.",
        "<b>Risk-Return Scatter Plot</b> — alpha vs. volatility scatter with colour-coded "
        "risk clusters, allowing visual identification of efficient frontier outliers.",
        "<b>Rolling Returns</b> — 1-year rolling return chart to assess performance consistency.",
        "<b>Drawdown Chart</b> — peak-to-trough drawdown visualisation for selected funds.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("7.3  Page 3 — Investor Analytics", styles))
    story.extend(body(
        "This page focuses on investor behaviour patterns derived from the 32,778 transaction "
        "records:", styles))
    story.extend(bullet_list([
        "<b>Transaction Volume Heatmap</b> — monthly transaction counts by fund house.",
        "<b>Purchase vs Redemption Trends</b> — dual-axis chart comparing inflows and outflows "
        "over time.",
        "<b>Investor Segmentation</b> — distribution of investors by transaction frequency and "
        "average ticket size.",
        "<b>Top Holdings Analysis</b> — treemap showing portfolio concentration across "
        "top stocks.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("7.4  Page 4 — SIP & Market Trends", styles))
    story.extend(body(
        "The final dashboard page tracks systematic investment plan (SIP) flows and market "
        "conditions:", styles))
    story.extend(bullet_list([
        "<b>Monthly SIP Inflows</b> — area chart showing the steady growth of SIP contributions, "
        "which have become the dominant mode of retail mutual fund investment.",
        "<b>SIP vs Lump-Sum Comparison</b> — bar chart contrasting SIP inflows against lump-sum "
        "purchases.",
        "<b>Nifty 50 Overlay</b> — benchmark index movement overlaid with SIP inflow trends to "
        "identify correlation between market sentiment and investment behaviour.",
        "<b>Category Rotation</b> — stacked area chart showing how investors rotate between "
        "equity and debt categories based on market conditions.",
    ], styles))
    story.append(PageBreak())

    # ──────────── 9. LIMITATIONS ───────────────────────────────────────
    story.extend(section_heading("8.  Limitations & Constraints", styles))

    story.extend(body(
        "While the project delivers actionable insights and a functional analytics pipeline, "
        "several limitations should be noted when interpreting the findings:", styles))
    story.append(Spacer(1, 8))

    limitations = [
        ["L1", "Historical Data Only",
         "The analysis is based entirely on historical NAV and transaction data. It does not "
         "incorporate forward-looking indicators such as fund manager guidance, economic "
         "forecasts, or market sentiment signals. Past performance does not guarantee future "
         "results."],
        ["L2", "No Real-Time Streaming",
         "While live NAV data is fetched via the mfapi.in API, this is a batch pull rather "
         "than a streaming pipeline. The system does not support real-time alerts, live "
         "dashboards, or intra-day NAV tracking."],
        ["L3", "Indian MF Market Only",
         "The dataset and analysis are limited to the Indian mutual fund ecosystem (AMFI-"
         "registered schemes). International funds, ETFs listed on foreign exchanges, and "
         "offshore fund-of-funds are not covered."],
        ["L4", "Simplistic Clustering (k=3)",
         "The K-Means clustering with k=3 provides a coarse-grained segmentation. More "
         "sophisticated methods (DBSCAN, Gaussian Mixture Models) or a higher k value could "
         "reveal nuanced sub-profiles. The silhouette score was not optimised."],
        ["L5", "Single Benchmark",
         "All schemes are benchmarked against the Nifty 50 index. Debt schemes and hybrid "
         "schemes would be more appropriately measured against fixed-income benchmarks such "
         "as CRISIL Composite Bond Index."],
        ["L6", "No Expense Ratio Adjustment",
         "Returns are computed on NAV data which is net of expense ratios, but the analysis "
         "does not separately account for total expense ratio (TER) as a factor in "
         "performance attribution."],
        ["L7", "Static Risk-Free Rate",
         "A fixed risk-free rate of 5% (approximating 10-year government bond yields) was "
         "used for alpha computation. In reality, this rate varies over time and should "
         "ideally use the contemporaneous T-bill rate."],
    ]
    lim_headers = ["ID", "Limitation", "Impact / Detail"]
    story.append(build_table(lim_headers, limitations,
                             col_widths=[0.45*inch, 1.45*inch, 3.6*inch]))
    story.append(Paragraph("Table 11: Project limitations and their implications",
                           styles["CaptionStyle"]))
    story.append(PageBreak())

    # ──────── 10. RECOMMENDATIONS ──────────────────────────────────────
    story.extend(section_heading("9.  Recommendations & Future Scope", styles))

    story.extend(body(
        "Based on the analysis conducted and the limitations identified, the following "
        "recommendations are proposed for extending this project into a production-grade "
        "analytics platform:", styles))
    story.append(Spacer(1, 8))

    story.extend(sub_heading("9.1  Enhanced Risk Modelling", styles))
    story.extend(bullet_list([
        "Implement <b>Value-at-Risk (VaR)</b> and <b>Conditional VaR (CVaR)</b> metrics to "
        "quantify downside risk with greater precision.",
        "Incorporate <b>Sortino Ratio</b> and <b>Calmar Ratio</b> for downside-adjusted "
        "performance measurement.",
        "Explore <b>Factor Models</b> (Fama-French 3-factor or 5-factor) for more granular "
        "performance attribution beyond single-index CAPM.",
        "Use <b>GARCH models</b> for time-varying volatility estimation rather than static "
        "annualised standard deviation.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("9.2  Sentiment Analysis Integration", styles))
    story.extend(bullet_list([
        "Integrate <b>NLP-based sentiment analysis</b> of financial news, RBI policy "
        "announcements, and SEBI circulars to create a forward-looking signal layer.",
        "Monitor <b>social media sentiment</b> (Twitter/X, Reddit) around fund houses and "
        "specific schemes for retail investor mood detection.",
        "Correlate sentiment scores with NAV movements and fund flows to identify leading "
        "indicators.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("9.3  International Fund Expansion", styles))
    story.extend(bullet_list([
        "Extend the data pipeline to ingest data from <b>Morningstar API</b> or "
        "<b>Bloomberg</b> for international mutual funds and ETFs.",
        "Enable cross-border performance comparison — e.g., Indian large-cap vs. S&P 500 "
        "index funds.",
        "Support <b>currency-adjusted returns</b> for a global investor perspective.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("9.4  Real-Time NAV Tracking", styles))
    story.extend(bullet_list([
        "Migrate from batch API pulls to a <b>streaming architecture</b> using WebSockets or "
        "server-sent events (SSE) for real-time NAV updates.",
        "Implement <b>alert mechanisms</b> — email/SMS notifications when a fund's NAV crosses "
        "SMA thresholds or drawdown exceeds a set limit.",
        "Deploy the dashboard on a cloud platform (AWS/GCP) with auto-refresh capabilities.",
    ], styles))
    story.append(Spacer(1, 6))

    story.extend(sub_heading("9.5  Advanced Clustering & ML", styles))
    story.extend(bullet_list([
        "Optimise cluster count using the <b>elbow method</b> and <b>silhouette analysis</b>.",
        "Experiment with <b>DBSCAN</b> and <b>Gaussian Mixture Models</b> to capture "
        "non-spherical cluster shapes.",
        "Build <b>predictive models</b> (Random Forest, XGBoost) to forecast short-term NAV "
        "movements based on lagged features.",
        "Implement <b>portfolio optimisation</b> using Markowitz Mean-Variance framework with "
        "the computed risk metrics.",
    ], styles))
    story.append(PageBreak())

    # ──────── APPENDIX — TECHNOLOGY STACK ──────────────────────────────
    story.extend(section_heading("10.  Appendix — Technology Stack", styles))

    story.extend(body(
        "The following technologies and libraries were used throughout the project:", styles))
    story.append(Spacer(1, 6))

    tech_data = [
        ["Python 3.10+", "Primary programming language", "Core"],
        ["pandas", "Data manipulation & transformation", "ETL, EDA"],
        ["NumPy", "Numerical computation", "Analytics"],
        ["scikit-learn", "K-Means clustering", "Risk profiling"],
        ["SQLite3", "Lightweight relational database", "Data storage"],
        ["requests", "HTTP client for API calls", "Live NAV fetch"],
        ["ReportLab", "PDF report generation", "Reporting"],
        ["python-pptx", "PowerPoint generation", "Presentations"],
        ["Streamlit / Plotly", "Interactive dashboard framework", "Visualisation"],
        ["mfapi.in", "Open NAV REST API", "Data source"],
        ["Git / GitHub", "Version control & collaboration", "DevOps"],
    ]
    story.append(build_table(
        ["Technology", "Purpose", "Phase"],
        tech_data,
        col_widths=[1.3*inch, 2.5*inch, 1.3*inch]))
    story.append(Paragraph("Table 12: Technology stack and tooling",
                           styles["CaptionStyle"]))
    story.append(Spacer(1, 12))

    story.extend(sub_heading("Project Repository Structure", styles))
    code_text = (
        "<font name='Courier' size='9'>"
        "BlueStock Intern/<br/>"
        "├── data/<br/>"
        "│   ├── raw/                  # 10 CSV datasets + live NAV files<br/>"
        "│   └── processed/<br/>"
        "│       ├── database.db       # SQLite database (~6.9 MB)<br/>"
        "│       └── risk_metrics.csv  # Computed risk metrics<br/>"
        "├── reports/<br/>"
        "│   ├── generate_final_report.py<br/>"
        "│   └── Final_Report.pdf<br/>"
        "├── dashboard/                # Interactive dashboard files<br/>"
        "├── notebooks/                # Jupyter notebooks for EDA<br/>"
        "├── sql/                      # SQL query scripts<br/>"
        "├── data_ingestion.py         # Dataset exploration & validation<br/>"
        "├── etl_pipeline.py           # CSV → SQLite ETL pipeline<br/>"
        "├── live_nav_fetch.py         # mfapi.in NAV fetcher<br/>"
        "├── advanced_analytics_script.py  # Risk metrics & clustering<br/>"
        "└── requirements.txt<br/>"
        "</font>"
    )
    story.append(Paragraph(code_text, styles["CodeStyle"]))
    story.append(Spacer(1, 16))

    # ──────── CLOSING STATEMENT ────────────────────────────────────────
    story.extend(section_heading("Closing Statement", styles))
    story.extend(body(
        "This capstone project demonstrates a complete, end-to-end analytics workflow for "
        "the Indian mutual fund industry — from raw data ingestion through to actionable "
        "insights and interactive visualisation. The modular architecture ensures that the "
        "pipeline can be readily extended to support additional data sources, more "
        "sophisticated analytical models, and production-scale deployment.", styles))
    story.append(Spacer(1, 8))
    story.extend(body(
        "The project was completed as part of the <b>Bluestock Fintech Internship Programme</b> "
        "by <b>Akash Kumar Pandit</b> in August 2026. All code, data artefacts, and documentation "
        "are maintained in the project repository for reproducibility and peer review.", styles))
    story.append(Spacer(1, 20))

    # Signature line
    sig_data = [
        [Paragraph("", ParagraphStyle("e", fontSize=1)),
         Paragraph("", ParagraphStyle("e", fontSize=1))],
        [Paragraph("_" * 35, ParagraphStyle("sig", fontName="Helvetica",
                                            fontSize=10, alignment=TA_CENTER)),
         Paragraph("_" * 35, ParagraphStyle("sig", fontName="Helvetica",
                                            fontSize=10, alignment=TA_CENTER))],
        [Paragraph("<b>Akash Kumar Pandit</b><br/>Project Author",
                   ParagraphStyle("sn", fontName="Helvetica", fontSize=10,
                                  alignment=TA_CENTER, leading=14)),
         Paragraph("<b>Bluestock Fintech</b><br/>Project Sponsor",
                   ParagraphStyle("sn", fontName="Helvetica", fontSize=10,
                                  alignment=TA_CENTER, leading=14))],
    ]
    sig_table = Table(sig_data, colWidths=[2.6*inch, 2.6*inch])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sig_table)

    # ═══════════════════════ BUILD PDF ═════════════════════════════════
    def on_first_page(canvas, doc):
        _title_page_bg(canvas, doc)

    def on_later_pages(canvas, doc):
        _header_footer(canvas, doc)

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f"✅ Report generated successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    build_report()
