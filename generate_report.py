"""
Generate Report.py
Retail Inventory Analytics — final academic PDF report generator.

Run from the project root:
    python "Generate Report.py"

Install:
    python -m pip install reportlab pandas openpyxl

This script reads the project's existing cleaned CSV and charts. It does not
train a forecasting model; it reports the supplied Demand Forecast values
and the MAE calculation implemented in src/analysis.py.
"""

from pathlib import Path
from datetime import datetime
import os
import platform
import subprocess
import sys
import math
import html

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table,
    TableStyle, KeepTogether
)

# ---------------------------------------------------------------------------
# PROJECT DETAILS — edit the institution name if needed.
# ---------------------------------------------------------------------------
PROJECT_TITLE = "INVENTORY DEMAND FORECASTING"
PROJECT_SUBTITLE = "Inventory Demand Analysis and Forecasting Using Python"

STUDENTS = [
    {
        "name": "Arnab Halder",
        "roll": "430124010155",
        "registration": "241270110419",
    },
    {
        "name": "Sagnik Paul",
        "roll": "430124010152",
        "registration": "241270110533",
    },
    {
        "name": "Adarsh Raj",
        "roll": "430124010161",
        "registration": "241270110374",
    },
    {
        "name": "Shristi Kumari Agarwal",
        "roll": "430124020248",
        "registration": "241270110554",
    },
    {
        "name": "Shashwato Bose",
        "roll": "430124010150",
        "registration": "241270110547",
    },
    {
        "name": "Anshudip Bar",
        "roll": "430124010158",
        "registration": "241270110406",
    },
    {
        "name": "Shivani Singh",
        "roll": "430124020252",
        "registration": "241270110549",
    },
]
INSTITUTE = "Narula Institute of Technology, Kolkata"
DEPARTMENT = "Department of Computer Science and Engineering"
ACADEMIC_YEAR = "2024-2028"

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PDF = BASE_DIR / "Retail_Inventory_Analytics_Final_Report_22_Pages_Expanded.pdf"

CLEANED_CSV_CANDIDATES = [
    BASE_DIR / "data" / "cleandata" / "retail_store_inventory_cleaned.csv",
    BASE_DIR / "outputs" / "retail_store_inventory_cleaned.csv",
    BASE_DIR / "data" / "cleaned_retail_inventory_2025_2026.csv",
]
RAW_XLSX = BASE_DIR / "data" / "rawdata" / "retail_store_inventory_extended_messy_2025_2026.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"

CHARTS = [
    ("01_category_revenue.png", "Revenue by Product Category"),
    ("02_seasonal_units_distribution.png", "Units Sold by Seasonality"),
    ("03_top_demand_products.png", "Top 10 Highest-Demand Products"),
    ("04_demand_trend_7day_moving_avg.png", "Daily Demand and 7-Day Moving Average"),
    ("05_forecast_vs_actual.png", "Provided Demand Forecast vs Actual Units Sold"),
    ("06_high_demand_categories.png", "High-Demand Product Categories"),
    ("07_region_revenue.png", "Revenue by Region"),
    ("08_region_category_countplot.png", "Regional and Category Distribution"),
]

# ---------------------------------------------------------------------------
# VISUAL STYLE
# ---------------------------------------------------------------------------
NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2C6EAA")
PALE_BLUE = colors.HexColor("#EAF2F8")
PALE_GREY = colors.HexColor("#F4F6F8")
MID_GREY = colors.HexColor("#637381")
DARK = colors.HexColor("#263746")
BORDER = colors.HexColor("#D5DEE6")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=23, leading=29, alignment=TA_CENTER, textColor=NAVY,
    spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="CoverSubtitle", parent=styles["Normal"], fontName="Helvetica",
    fontSize=13, leading=19, alignment=TA_CENTER, textColor=BLUE,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=15, leading=19, textColor=NAVY, spaceAfter=8, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="Subsection", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=10, leading=13, textColor=BLUE, spaceBefore=5, spaceAfter=4,
    keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="BodyReport", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=8.5, leading=12.2, textColor=DARK, alignment=TA_JUSTIFY,
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="SmallReport", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=7.5, leading=10, textColor=MID_GREY, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="TableHeadReport", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=7.3, leading=9, textColor=WHITE,
))
styles.add(ParagraphStyle(
    name="TableCellReport", parent=styles["Normal"], fontName="Helvetica",
    fontSize=7.2, leading=9, textColor=DARK,
))
styles.add(ParagraphStyle(
    name="CenterReport", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9, leading=13, textColor=DARK, alignment=TA_CENTER, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="CoverLabel", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=9, leading=12, textColor=NAVY, alignment=TA_CENTER,
))

# ---------------------------------------------------------------------------
# DATA LOADING AND METRICS
# ---------------------------------------------------------------------------
def find_dataset():
    for path in CLEANED_CSV_CANDIDATES:
        if path.exists():
            return path
    # A convenient fallback if the project has a differently named CSV.
    candidates = [
        p for p in BASE_DIR.rglob("*.csv")
        if "inventory" in p.name.lower() or "retail" in p.name.lower()
    ]
    candidates = [
        p for p in candidates
        if not any(part.lower() in {".git", ".venv", "venv", "node_modules", "__pycache__"}
                   for part in p.parts)
    ]
    if candidates:
        candidates.sort(key=lambda p: ("clean" not in p.name.lower(), len(p.parts)))
        return candidates[0]
    raise FileNotFoundError(
        "Could not locate the cleaned retail inventory CSV. Expected: "
        "data/cleandata/retail_store_inventory_cleaned.csv"
    )


def load_data(path):
    df = pd.read_csv(path)
    required = {
        "Date", "Product ID", "Category", "Region", "Inventory Level",
        "Units Sold", "Demand Forecast", "Price", "Discount", "Seasonality"
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(
            "The selected CSV is missing columns required by this project: "
            + ", ".join(missing)
        )
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in [
        "Inventory Level", "Units Sold", "Demand Forecast",
        "Price", "Discount", "Units Ordered", "Competitor Pricing",
        "Holiday/Promotion"
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["Category", "Region", "Seasonality", "Product ID"]:
        df[col] = df[col].fillna("Unknown").astype(str)
    # Use the same revenue formula documented in src/analysis.py.
    df["Total Revenue"] = (
        df["Units Sold"] * df["Price"] * (1 - df["Discount"] / 100)
    )
    return df, path


def product_summary(df):
    p = (
        df.groupby("Product ID", dropna=False)
        .agg(
            Total_Demand=("Units Sold", "sum"),
            Average_Daily_Demand=("Units Sold", "mean"),
            Current_Inventory=("Inventory Level", "mean"),
            Average_Forecast=("Demand Forecast", "mean"),
        )
        .reset_index()
    )
    p["Stock_Status"] = "Optimal"
    p.loc[
        p["Current_Inventory"] < p["Average_Daily_Demand"] * 3,
        "Stock_Status"
    ] = "Under-stocked"
    p.loc[
        p["Current_Inventory"] > p["Average_Daily_Demand"] * 15,
        "Stock_Status"
    ] = "Over-stocked"
    return p


def calculate_metrics(df):
    forecast = df.dropna(subset=["Demand Forecast", "Units Sold"]).copy()
    mae = (
        (forecast["Units Sold"] - forecast["Demand Forecast"]).abs().mean()
        if not forecast.empty else float("nan")
    )
    ps = product_summary(df)
    valid_dates = df["Date"].dropna()
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "date_min": valid_dates.min().strftime("%d %b %Y") if not valid_dates.empty else "Unavailable",
        "date_max": valid_dates.max().strftime("%d %b %Y") if not valid_dates.empty else "Unavailable",
        "unique_products": int(df["Product ID"].nunique()),
        "unique_categories": int(df["Category"].nunique()),
        "unique_regions": int(df["Region"].nunique()),
        "units_sold": float(df["Units Sold"].sum()),
        "average_unit_price": float(df["Price"].mean()),
        "total_revenue": float(df["Total Revenue"].sum()),
        "forecast_mae": float(mae) if pd.notna(mae) else float("nan"),
        "forecast_rows": int(len(forecast)),
        "stock_summary": ps,
        "category_revenue": df.groupby("Category")["Total Revenue"].sum().sort_values(ascending=False),
        "category_units": df.groupby("Category")["Units Sold"].sum().sort_values(ascending=False),
        "region_revenue": df.groupby("Region")["Total Revenue"].sum().sort_values(ascending=False),
        "top_products": ps.sort_values("Total_Demand", ascending=False).head(10),
        "low_products": ps.sort_values("Total_Demand", ascending=True).head(5),
    }


def fmt(value, decimals=2):
    try:
        if value is None or pd.isna(value) or (isinstance(value, float) and not math.isfinite(value)):
            return "N/A"
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def safe(text):
    return html.escape(str(text), quote=False)


# ---------------------------------------------------------------------------
# REPORTLAB HELPERS
# ---------------------------------------------------------------------------
def P(text, style="BodyReport"):
    return Paragraph(safe(text), styles[style])


def rich(text, style="BodyReport"):
    # Only use this for hard-coded markup authored in this script.
    return Paragraph(text, styles[style])


def bullets(items):
    return [
        Paragraph("&#8226;&nbsp;&nbsp;" + safe(item), styles["BodyReport"])
        for item in items
    ]


def make_table(rows, widths=None, header=True, font_size=7.2):
    if not rows:
        return P("No records were available for this table.")
    result = []
    for ri, row in enumerate(rows):
        out = []
        for value in row:
            text = safe(value)
            if ri == 0 and header:
                out.append(Paragraph(text, styles["TableHeadReport"]))
            else:
                out.append(Paragraph(text, styles["TableCellReport"]))
        result.append(out)
    tbl = Table(
        result, colWidths=widths, repeatRows=1 if header else 0,
        hAlign="LEFT"
    )
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
        if len(result) > 1:
            commands.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_GREY]))
    tbl.setStyle(TableStyle(commands))
    return tbl


def make_sample_table(rows, widths):
    """Compact table style for showing the first six raw-data records."""
    sample_head = ParagraphStyle(
        "RawSampleHead", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=5.2, leading=6.1, textColor=WHITE,
    )
    sample_cell = ParagraphStyle(
        "RawSampleCell", parent=styles["Normal"], fontName="Helvetica",
        fontSize=5.1, leading=6.0, textColor=DARK,
    )
    result = []
    for ri, row in enumerate(rows):
        result.append([
            Paragraph(safe(value), sample_head if ri == 0 else sample_cell)
            for value in row
        ])
    tbl = Table(result, colWidths=widths, repeatRows=1, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_GREY]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


def add_chart(story, filename, caption, max_w=16.5 * cm, max_h=10.4 * cm):
    path = OUTPUT_DIR / filename
    if not path.exists():
        story.append(P(f"Chart not found: outputs/{filename}", "SmallReport"))
        story.append(P("The report generator preserves the project content and continues without this image."))
        return
    img = Image(str(path))
    img._restrictSize(max_w, max_h)
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Spacer(1, 4))
    story.append(P(caption, "SmallReport"))


def draw_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(1.7 * cm, h - 1.35 * cm, w - 1.7 * cm, h - 1.35 * cm)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(NAVY)
        canvas.drawString(1.7 * cm, h - 1.08 * cm, "RETAIL INVENTORY ANALYTICS")
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MID_GREY)
        canvas.drawRightString(w - 1.7 * cm, h - 1.08 * cm, "FINAL PROJECT REPORT")
    canvas.setStrokeColor(BORDER)
    canvas.line(1.7 * cm, 1.35 * cm, w - 1.7 * cm, 1.35 * cm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MID_GREY)
    canvas.drawString(1.7 * cm, 0.98 * cm, "Inventory Demand Forecasting | Academic Project")
    canvas.drawRightString(w - 1.7 * cm, 0.98 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ---------------------------------------------------------------------------
# BUILD 22 SEPARATE REPORT SECTIONS/PAGES
# Each section stays on its own page; short, section-specific discussion notes
# use available space without changing the existing heading or body font sizes.
# ---------------------------------------------------------------------------
def build_report():
    csv_path = find_dataset()
    df, _ = load_data(csv_path)
    m = calculate_metrics(df)
    ps = m["stock_summary"]

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF), pagesize=A4,
        rightMargin=1.7 * cm, leftMargin=1.7 * cm,
        topMargin=1.75 * cm, bottomMargin=1.65 * cm,
        title=PROJECT_TITLE,
        author="; ".join(s["name"] for s in STUDENTS),
        subject="Retail inventory analytics and demand forecasting",
    )
    story = []

    def heading(title):
        story.append(Paragraph(safe(title), styles["Section"]))
    def subheading(title):
        story.append(Paragraph(safe(title), styles["Subsection"]))
    def body(text):
        story.append(P(text))

    # Small, human-written interpretation notes make use of otherwise empty
    # space while staying relevant to each section. They do not alter fonts.
    page_notes = {
        2: "These statements clarify what the report covers and distinguish the work completed in the repository from work that has not been claimed. The final PDF should be checked against the submitted code and data before academic submission. Clear documentation also supports fair review: readers can distinguish implemented features from recommendations for later work, and can reproduce the calculations by following the repository instructions and using the same input files.",
        3: "In short, the project turns a large spreadsheet into information that is easier to inspect. Its value lies in making patterns visible and giving a reviewer a clear path from the source data to the reported results. The report therefore focuses on transparent methods and interpretable outputs rather than claiming a production-ready forecasting system. Its sections move from source data and preparation to metrics, visual evidence, practical implications and areas that need further validation.",
        4: "The main benefit of this workflow is consistency: the same cleaned file and calculation rules can be used again when the data is refreshed. The charts are intended to support human review, not replace business judgement. The folder layout mirrors these responsibilities, reducing the chance that original data is confused with processed output. It also makes it easier for another student or reviewer to identify the entry point, dependencies and scripts without searching through unrelated files.",
        5: "These objectives connect the technical tasks to practical questions a retailer may ask. Each objective can be reviewed by checking whether the project produces the relevant table, metric, chart or documented rule. A clear objective list is important because exploratory projects can easily expand beyond their available data. The present scope stays close to the columns and operations implemented in the repository, while more advanced optimization is reserved for future development.",
        6: "The questions define the boundary of the current work. They focus on description and comparison; decisions such as how much to order would require additional information about lead times, supplier constraints and service targets. These questions are useful because they connect each chart or summary to a decision-relevant topic. They do not, on their own, establish causation; any proposed action should be checked against stock availability, supplier lead times, pricing strategy and business priorities.",
        7: "The raw sample is included to make the source structure transparent. The cleaned dataset may differ from these original rows because the cleaning stage standardizes fields and handles selected invalid or missing values. The sample should be treated as a small illustration, not as a representative summary of every product or period. The full dataset is used for the calculations, and the displayed rows help readers understand the original column names and value formats.",
        8: "Cleaning improves consistency, but it does not make every record perfect. Median filling is a practical choice for this project and can influence averages and totals, so the cleaning rules should remain visible to anyone interpreting the findings. The cleaned output should still be reviewed for unusual values and remaining missing fields. In a business deployment, cleaning rules would ideally be documented alongside row counts before and after each step so that data changes can be audited.",
        9: "Keeping the stages separate makes the project easier to debug and maintain. If an output looks unexpected, the data, cleaning rules, aggregation formula and chart code can be inspected independently. This staged design supports reproducibility: the same entry point can be run again after replacing the input workbook, and the derived outputs can be refreshed. The README also documents separate commands for running cleaning or analysis independently when troubleshooting.",
        10: "Summary metrics are most useful when their definitions are clear. They describe the dataset that was actually loaded at report-generation time, so values can change if the input file is updated. Counts and averages should be read together because no single metric captures the full business picture. Revenue can be influenced by both volume and price, while forecast error should be compared with typical demand levels and a simple baseline.",
        11: "A chart is a starting point for investigation rather than proof of a cause. The pattern should be compared with the underlying data and interpreted alongside the business context before drawing conclusions. Category totals may be affected by differences in product prices, discount rates and the number of records in each group. A useful follow-up would compare both units and revenue and examine whether the pattern remains consistent across dates and regions.",
        12: "Seasonality labels provide a simple way to compare groups in the source data. They should not be confused with a formal seasonal forecasting model, which would require a defined time-series method and evaluation process. Seasonal groupings are descriptive labels inherited from the source data. They can help compare observed sales across groups, but a stronger seasonal conclusion would require checking the time coverage, label definitions and repeated patterns across multiple years.",
        13: "Product-level rankings help narrow attention to items with unusually high or low recorded demand. Reviewing the underlying time periods and inventory availability can help explain whether the ranking reflects a stable pattern or a temporary spike. High-demand products deserve attention, but a ranking does not show whether stock was available whenever customers wanted to buy. Reviewing stockout periods and the dates behind each product total would help distinguish persistent demand from isolated peaks.",
        14: "The moving average smooths daily variation and makes the broad direction easier to see. It can also hide short-lived peaks, so the original daily series remains important when planning for sudden changes. Moving averages are useful for communication because they reduce day-to-day noise, although the chosen window affects how quickly the line responds to change. Alternative windows could be compared to decide which is most informative for the intended planning horizon.",
        15: "MAE is easy to explain because it reports an average absolute difference in units. It does not show the direction of errors, and it should ideally be compared with a baseline before judging forecast quality. Forecast evaluation would be stronger if the project documented how the supplied forecasts were created and compared them with a naïve baseline. Error should also be examined by product and date to avoid hiding weak performance within an overall average.",
        16: "Unit volume and revenue answer different questions. A category with many low-priced sales may lead in units while another category contributes more revenue, so both views should be considered together. Considering unit volume alongside revenue gives a more balanced view of category performance. The results can guide further investigation, but decisions about assortment or promotion should also consider margins, customer needs, stock availability and operating costs.",
        17: "Regional differences can reflect product mix, store coverage, promotions or data availability. A fair comparison should consider these factors before interpreting a region as stronger or weaker. Regional comparisons are most informative when the underlying coverage is comparable. If regions contain different numbers of stores or records, totals may need to be supplemented with per-store or per-period measures before drawing conclusions about relative performance.",
        18: "The combined view can reveal differences in category mix across regions. It is useful for deciding where to investigate further, but the underlying counts and chart labels should be checked before making assortment changes. A combined region-category view helps identify where category mixes differ, which can support targeted questions for managers. The chart should be used to prioritize investigation rather than as a stand-alone reason to change stock allocations.",
        19: "The stock labels are screening signals created by simple thresholds. They are useful for identifying records to review, but should not be treated as purchase instructions without operational context. Thresholds should be reviewed with operational stakeholders before use in replenishment. Real stock decisions commonly depend on supplier lead time, minimum order quantity, demand variability, service targets and current purchase orders, none of which is fully represented by this simple heuristic.",
        20: "The findings bring together the main outputs of the implemented analysis. They are descriptive results from this dataset, and their reliability depends on the quality, coverage and assumptions of the source records. The findings are strongest when they are traceable to a visible metric, table or chart. Any final recommendation should state the evidence behind it, acknowledge data limitations and specify what additional information would be needed to make the decision more reliable.",
        21: "A sensible next step is to validate the most important findings with domain knowledge, then improve the pipeline incrementally. Better evaluation and clearer stock policies would make the project more useful for real decisions. Future improvements should be introduced in small, testable steps, with each change evaluated against the current implementation. Keeping a documented baseline will make it easier to determine whether a new forecast, metric or inventory rule actually improves the quality of decisions.",
    }
    current_page = 1
    def new_page():
        nonlocal current_page
        if current_page in page_notes:
            story.append(Spacer(1, 0.20 * cm))
            note = Table([[Paragraph("<b>Section takeaway</b><br/>" + safe(page_notes[current_page]), styles["SmallReport"])]], colWidths=[16.0 * cm])
            note.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(note)
        story.append(PageBreak())
        current_page += 1

    # PAGE 1 — COVER
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("ACADEMIC PROJECT REPORT", styles["CoverLabel"]))
    story.append(Spacer(1, 0.55 * cm))
    story.append(Paragraph(PROJECT_TITLE, styles["CoverTitle"]))
    story.append(Paragraph(PROJECT_SUBTITLE, styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph(
        "Python  |  Pandas  |  NumPy  |  Matplotlib  |  Streamlit",
        styles["CenterReport"]
    ))
    story.append(Spacer(1, 0.65 * cm))
    story.append(Paragraph("SUBMITTED BY", styles["CoverLabel"]))
    student_rows = [["Student Name", "Roll Number", "Registration Number"]]
    for s in STUDENTS:
        student_rows.append([s["name"], s["roll"], s["registration"]])
    story.append(make_table(student_rows, [5.3 * cm, 4.8 * cm, 5.9 * cm]))
    story.append(Spacer(1, 0.65 * cm))
    story.append(Paragraph(safe(DEPARTMENT), styles["CenterReport"]))
    story.append(Paragraph(safe(INSTITUTE), styles["CenterReport"]))
    story.append(Paragraph("Academic Year " + ACADEMIC_YEAR, styles["CenterReport"]))
    story.append(Spacer(1, 0.65 * cm))
    story.append(Paragraph(
        "A data analytics project for examining retail demand, product inventory, "
        "category and regional performance, and the quality of supplied demand forecasts.",
        styles["CenterReport"]
    ))
    new_page()

    # PAGE 2 — DECLARATION AND ACKNOWLEDGEMENT
    heading("2. Declaration and Acknowledgement")
    subheading("Declaration")
    body(
        "We submit this report as documentation of the Retail Inventory Analytics project. "
        "The report describes the data-processing pipeline, the analysis implemented in the "
        "project scripts, and the visual outputs included in the repository. Quantitative "
        "values are calculated from the selected project CSV when the report is generated."
    )
    body(
        "The project evaluates the Demand Forecast field already present in the dataset. "
        "It does not claim that a new forecasting model was trained by this report generator. "
        "Inventory classifications use the thresholds implemented in the project's analysis code."
    )
    subheading("Acknowledgement")
    body(
        "We thank our faculty and institution for the opportunity to complete this project. "
        "We acknowledge the Python open-source ecosystem, particularly Pandas, NumPy, "
        "Matplotlib and ReportLab, for supporting data processing, visualization and report creation."
    )
    body(
        "We also acknowledge the project repository's README, cleaning and analysis scripts, "
        "cleaned dataset, and existing visualization files as the source material for this report."
    )
    story.append(Spacer(1, 0.3 * cm))
    # story.append(make_table([
    #     # ["Student", "Signature", "Date"],
    #     # [STUDENTS[0]["name"], "________________________", "____________"],
    #     # [STUDENTS[1]["name"], "________________________", "____________"],
    # ], [4.0 * cm, 7.0 * cm, 5.0 * cm]))
    new_page()

    # PAGE 3 — ABSTRACT AND CONTENTS
    heading("3. Abstract")
    body(
        "Retailers need to balance product availability against the cost of holding inventory. "
        "This project analyzes historical retail inventory and sales records to examine product "
        "demand, category and regional revenue, seasonality labels, daily demand trends, and "
        "the difference between supplied forecasts and observed units sold."
    )
    body(
        "The repository uses Python and Pandas for data preparation and aggregation, NumPy for "
        "numerical operations, Matplotlib and Seaborn for visualizations, and Streamlit for a "
        "simple dashboard. Its cleaning stage removes exact duplicate rows, standardizes selected "
        "categorical fields, parses dates, handles invalid numeric values, and fills selected "
        "missing values according to documented project rules."
    )
    body(
        "The analysis computes revenue as Units Sold × Price × (1 − Discount / 100), summarizes "
        "demand by product, applies heuristic stock-status thresholds, and calculates mean "
        "absolute error (MAE) between supplied Demand Forecast values and actual Units Sold. "
        "These results support exploratory business analysis, but should be interpreted with "
        "the dataset's limitations and assumptions in mind."
    )
    subheading("Report Contents")
    contents = [
        ["Page", "Section"],
        ["4–6", "Introduction, problem, objectives and project scope"],
        ["7–10", "Dataset, cleaning, workflow and key metrics"],
        ["11–18", "Existing charts and their interpretation"],
        ["19–21", "Inventory status, findings, recommendations and limitations"],
        ["22", "Conclusion, future scope and references"],
    ]
    story.append(make_table(contents, [2.5 * cm, 13.5 * cm]))
    new_page()

    # PAGE 4 — INTRODUCTION
    heading("4. Introduction")
    body(
        "Inventory management is a core retail activity. A business needs enough stock to satisfy "
        "customer demand, but excess stock can increase holding costs and tie up working capital. "
        "Products may also differ in their sales volume, price, seasonality and regional demand."
    )
    body(
        "Data analytics helps convert historical records into summaries and visual evidence. "
        "Product-level demand analysis can highlight fast-moving items; category analysis can "
        "compare sales contribution; time-series views can show whether daily sales fluctuate; "
        "and forecast comparisons can indicate how close supplied estimates are to observed sales."
    )
    subheading("Project Overview")
    body(
        "The project, Retail Inventory Analytics, processes a retail inventory workbook covering "
        "2025–2026. Its pipeline separates data cleaning from analysis, saves a cleaned CSV, "
        "calculates business metrics and creates charts. A Streamlit dashboard presents key "
        "metrics, stock-status counts, charts and product-demand tables."
    )
    subheading("Business Scenario")
    body(
        "Imagine a retail manager opening a large spreadsheet and trying to work out which products sell quickly, which categories contribute to sales, and whether inventory looks unusually low or high. This project organizes those records into summaries and charts, making it easier to spot patterns and decide what deserves a closer look. The results are exploratory indicators, not automatic business decisions."
    )
    subheading("Project Folder Structure")
    body(
        "The repository is arranged so that source data, processing code, generated outputs and the dashboard are easy to locate. The raw workbook is kept separate from the cleaned CSV, while reusable cleaning and analysis logic lives in the src folder. This separation makes the workflow easier to maintain and helps reviewers trace each result back to its source."
    )
    structure_rows = [
        [Paragraph("<font color='#FFFFFF'><b>Inventory_Forecast-main/</b></font>", styles["SmallReport"])],
        [Paragraph("├── data/", styles["SmallReport"])],
        [Paragraph("│   ├── rawdata/  — original Excel workbook", styles["SmallReport"])],
        [Paragraph("│   └── cleandata/  — cleaned CSV dataset", styles["SmallReport"])],
        [Paragraph("├── src/", styles["SmallReport"])],
        [Paragraph("│   ├── data_cleaning.py  — cleaning rules", styles["SmallReport"])],
        [Paragraph("│   └── analysis.py  — metrics and charts", styles["SmallReport"])],
        [Paragraph("├── outputs/  — charts and exported data", styles["SmallReport"])],
        [Paragraph("├── main.py  — pipeline entry point", styles["SmallReport"])],
        [Paragraph("├── dashboard.py  — Streamlit interface", styles["SmallReport"])],
        [Paragraph("├── generate_report.py  — Reportlab", styles["SmallReport"])],
        [Paragraph("├── Inventory_Demand_Forecasting.pdf ", styles["SmallReport"])],
        [Paragraph("├── requirements.txt  — Python dependencies", styles["SmallReport"])],
        [Paragraph("└── README.md  — setup and workflow notes", styles["SmallReport"])],
    ]
    structure = Table(structure_rows, colWidths=[16.0 * cm], hAlign="LEFT")
    structure.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, -1), PALE_GREY),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(structure)
    new_page()

    # PAGE 5 — PROBLEM AND OBJECTIVES
    heading("5. Problem Statement and Objectives")
    subheading("Problem Statement")
    body(
        "Raw sales and inventory records can be difficult to interpret without cleaning, aggregation "
        "and visualization. A retailer may struggle to identify high-demand products, compare "
        "category and regional revenue, recognize broad demand trends, and evaluate the supplied "
        "forecast values. This project organizes the available data to make these questions easier "
        "to investigate."
    )


    subheading("Main Objective")
    body(
        "To analyze retail inventory and sales data with Python, produce meaningful visualizations, "
        "compare supplied demand forecasts with actual units sold, and summarize possible inventory "
        "risks using the project's stated rules."
    )


    subheading("Specific Objectives")
    story.extend(bullets([
        "Inspect and prepare the source workbook for analysis.",
        "Remove exact duplicate rows and handle selected data-quality issues.",
        "Calculate revenue, unit sales and average price metrics.",
        "Identify products with the highest and lowest recorded demand.",
        "Compare revenue and units sold across categories and regions.",
        "Visualize daily demand with a seven-day moving average.",
        "Calculate forecast MAE from supplied forecast and actual values.",
        "Classify products using the project's inventory thresholds.",
    ]))
    new_page()

    # PAGE 6 — SCOPE, QUESTIONS, TECHNOLOGY
    heading("6. Scope, Business Questions and Technology")
    subheading("Business Questions")
    story.extend(bullets([
        "Which product IDs have the highest and lowest recorded demand?",
        "Which product categories contribute most to revenue and units sold?",
        "How does daily unit sales volume change over time?",
        "How are units sold distributed across seasonality labels?",
        "How closely do supplied demand forecasts match actual units sold?",
        "Which products meet the project's under-stock or over-stock rules?",
        "How do revenue and category distribution vary by region?",
    ]))


    subheading("Technology Stack")
    story.append(make_table([
        ["Technology", "Use in this project"],
        ["Python", "Core programming language for the pipeline and dashboard."],
        ["Pandas", "Data loading, cleaning, grouping and summary calculations."],
        ["NumPy", "Numerical operations, including forecast-error calculation."],
        ["Matplotlib / Seaborn", "Generation of static charts and comparisons."],
        ["Streamlit", "Interactive dashboard interface."],
        ["ReportLab", "Automated PDF report layout and export."],
        ["Excel / CSV", "Source workbook and processed data storage."],
    ], [4.1 * cm, 11.9 * cm]))
    subheading("Scope Boundary")
    body(
        "This is an exploratory analytics project, not a real-time inventory-control system. "
        "It evaluates the forecasts provided in the dataset; the existing analysis script does "
        "not train a forecasting model. Business thresholds should be validated before operational use."
    )
    new_page()

    # PAGE 7 — DATASET
    heading("7. Dataset Description and Data Dictionary")
    body(
        "The report reads the cleaned CSV from the project-relative path data/cleandata/"
        "retail_store_inventory_cleaned.csv when available. The selected CSV contains "
        f"{m['rows']:,} rows and {m['columns']:,} columns at report-generation time. "
        "Its date range after parsing is shown below."
    )
    story.append(make_table([
        ["Dataset measure", "Observed value"],
        ["Selected file", str(csv_path.relative_to(BASE_DIR)) if csv_path.is_relative_to(BASE_DIR) else csv_path.name],
        ["Records", f"{m['rows']:,}"],
        ["Columns", f"{m['columns']:,}"],
        ["Date range", f"{m['date_min']} to {m['date_max']}"],
        ["Distinct product IDs", f"{m['unique_products']:,}"],
        ["Distinct categories", f"{m['unique_categories']:,}"],
        ["Distinct regions", f"{m['unique_regions']:,}"],
        ["Missing cells in selected CSV", f"{m['missing_cells']:,}"],
        ["Duplicate rows in selected CSV", f"{m['duplicate_rows']:,}"],
    ], [7.0 * cm, 9.0 * cm]))

    subheading("First Six Rows of the Raw Dataset")
    body(
        "The following preview shows the first six records from the original raw Excel workbook. "
        "The columns are split into two compact tables so that all source fields remain visible."
    )
    raw_path = RAW_XLSX
    if not raw_path.exists():
        raw_candidates = list(BASE_DIR.rglob("*extended_messy*.xlsx"))
        if raw_candidates:
            raw_path = raw_candidates[0]
    if raw_path.exists():
        raw_preview = pd.read_excel(raw_path).head(6).copy()
        raw_preview = raw_preview.where(pd.notna(raw_preview), "—")
        raw_preview = raw_preview.astype(str)
        raw_cols_1 = [
            "Date", "Store ID", "Product ID", "Category", "Region",
            "Inventory Level", "Units Sold", "Units Ordered"
        ]
        raw_cols_2 = [
            "Demand Forecast", "Price", "Discount", "Weather Condition",
            "Holiday/Promotion", "Competitor Pricing", "Seasonality"
        ]
        # Keep only columns present in the workbook, while preserving source order.
        raw_cols_1 = [c for c in raw_cols_1 if c in raw_preview.columns]
        raw_cols_2 = [c for c in raw_cols_2 if c in raw_preview.columns]
        sample_1 = [raw_cols_1] + raw_preview[raw_cols_1].values.tolist()
        sample_2 = [raw_cols_2] + raw_preview[raw_cols_2].values.tolist()
        story.append(make_sample_table(sample_1, [2.0 * cm, 1.5 * cm, 1.6 * cm, 2.0 * cm, 1.5 * cm, 2.2 * cm, 1.6 * cm, 1.6 * cm][:len(raw_cols_1)]))
        story.append(Spacer(1, 3))
        story.append(make_sample_table(sample_2, [2.2 * cm, 1.6 * cm, 1.5 * cm, 2.4 * cm, 2.1 * cm, 2.2 * cm, 1.8 * cm][:len(raw_cols_2)]))
    else:
        body("Raw Excel workbook not found; the raw-row preview could not be included. Place the workbook at data/rawdata/retail_store_inventory_extended_messy_2025_2026.xlsx.")

    subheading("Main Fields")
    dictionary = [
        ["Field", "Description based on project usage"],
        ["Date", "Sales or inventory date; used for daily trend analysis."],
        ["Store ID", "Store identifier in the source dataset."],
        ["Product ID", "Product identifier used for product-level summaries."],
        ["Category", "Product category used for revenue and demand grouping."],
        ["Region", "Region label used for regional comparisons."],
        ["Inventory Level", "Recorded inventory measure used for stock-status proxy."],
        ["Units Sold", "Observed sales volume / demand measure."],
        ["Demand Forecast", "Forecast values supplied in the dataset."],
        ["Price / Discount", "Inputs to the project's revenue formula."],
        ["Seasonality", "Label used to group units sold by seasonality."],
    ]
    story.append(make_table(dictionary, [4.2 * cm, 11.8 * cm]))
    new_page()

    # PAGE 8 — DATA CLEANING
    heading("8. Data Cleaning and Preprocessing")
    body(
        "The cleaning rules below are implemented in src/data_cleaning.py and described in the "
        "repository README. They are project-specific rules rather than universal inventory policies."
    )
    story.append(make_table([
        ["Issue", "Implemented handling"],
        ["Exact duplicate records", "Drop exact duplicate rows."],
        ["Category, Region, Weather Condition, Seasonality", "Trim whitespace, title-case labels, and convert text representations of missing values to null."],
        ["Invalid dates", "Parse dates with coercion and drop rows whose dates cannot be parsed."],
        ["Negative Inventory Level", "Treat as missing, then fill with the dataset median."],
        ["Negative Units Sold", "Treat as missing, then fill with the dataset median."],
        ["Discount outside 0–100", "Treat as missing; the script does not impute this field."],
        ["Price above $1,000", "Treat as missing, then fill using the category median."],
        ["Missing Category", "Fill with 'Uncategorized'."],
    ], [5.1 * cm, 10.9 * cm]))
    subheading("Data Quality Notes")
    body(
        "The report's missing-cell and duplicate counts describe the CSV that is actually read when "
        "the report runs. They do not represent the raw workbook unless that raw workbook is selected. "
        "The cleaning script does not currently impute every missing field, so some null values may "
        "remain in the cleaned CSV."
    )
    subheading("Why Cleaning Matters")
    body(
        "Duplicate rows can inflate sales totals, invalid dates can distort time trends, and invalid "
        "numeric values can make demand or inventory comparisons unreliable. Cleaning decisions "
        "should be recorded because imputation can affect downstream totals."
    )
    new_page()

    # PAGE 9 — METHODOLOGY
    heading("9. Project Workflow and Methodology")
    story.append(make_table([
        ["Stage", "Project action", "Purpose"],
        ["1. Load", "Read source Excel workbook.", "Make records available for processing."],
        ["2. Clean", "Remove duplicates; standardize labels; parse dates; handle selected invalid values.", "Improve consistency."],
        ["3. Export", "Save cleaned records as CSV.", "Create reusable analysis input."],
        ["4. Calculate", "Compute revenue, product summaries, stock status and forecast MAE.", "Answer business questions."],
        ["5. Visualize", "Save charts to outputs/.", "Communicate comparisons and trends."],
        ["6. Dashboard", "Display metrics, charts and product summaries in Streamlit.", "Provide a user-facing view."],
        ["7. Report", "Summarize project design, data and results in PDF.", "Document findings and limitations."],
    ], [2.0 * cm, 7.3 * cm, 6.7 * cm]))
    subheading("End-to-End Process Flow")
    body(
        "The README identifies main.py as the recommended entry point. It coordinates the cleaning stage, writes the cleaned dataset, runs the analysis, and refreshes the saved visual outputs. The dashboard then presents selected results for exploration, while this PDF documents the process, interpretation and limitations. Each stage can also be inspected separately when debugging or validating an output."
    )
    flow_rows = [
        [Paragraph("<b>Source Excel</b><br/>data/rawdata/", styles["CenterReport"])],
        [Paragraph("<b>Clean & standardize</b><br/>src/data_cleaning.py", styles["CenterReport"])], 
        [Paragraph("<b>Cleaned CSV</b><br/>data/cleandata/", styles["CenterReport"])],
        [Paragraph("<b>Analyze metrics</b><br/>src/analysis.py", styles["CenterReport"])],
        [Paragraph("<b>Charts & summaries</b><br/>outputs/", styles["CenterReport"])], 
        [Paragraph("<b>Review results</b><br/>dashboard.py + PDF report", styles["CenterReport"])],
    ]
    flow = Table(flow_rows, colWidths=[5.3 * cm, 5.3 * cm, 5.3 * cm], rowHeights=[1.25 * cm] * len(flow_rows))
    flow.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(flow)
    subheading("Revenue Calculation")
    story.append(Paragraph(
        "Total Revenue = Units Sold × Price × (1 − Discount / 100)",
        styles["CenterReport"]
    ))
    body(
        "The formula applies the discount percentage to the row-level price and multiplies by units sold. "
        "The repository notes that this calculation does not account for taxes, returns, shipping or "
        "other accounting adjustments."
    )
    subheading("Forecast Evaluation")
    story.append(Paragraph(
        "MAE = Mean of (Actual Units Sold − Demand Forecast)",
        styles["CenterReport"]
    ))
    body(
        "The MAE measures average absolute difference in units. It evaluates the forecast values already "
        "present in the dataset; it does not prove that the forecast is unbiased or accurate for every "
        "product, region or season."
    )
    new_page()

    # PAGE 10 — OVERALL EDA / KPIs
    heading("10. Exploratory Data Analysis and Key Metrics")
    body(
        "Exploratory Data Analysis summarizes the data before interpreting individual charts. "
        "The values below are calculated dynamically from the CSV selected by this script."
    )
    story.append(make_table([
        ["Metric", "Observed value"],
        ["Total units sold", fmt(m["units_sold"], 0)],
        ["Total revenue (dataset currency)", fmt(m["total_revenue"])],
        ["Average row-level unit price", fmt(m["average_unit_price"])],
        ["Forecast MAE (units)", fmt(m["forecast_mae"])],
        ["Rows with actual and forecast values", f"{m['forecast_rows']:,}"],
        ["Product IDs", f"{m['unique_products']:,}"],
        ["Categories", f"{m['unique_categories']:,}"],
        ["Regions", f"{m['unique_regions']:,}"],
    ], [7.0 * cm, 9.0 * cm]))
    subheading("How to Read These Metrics")
    body(
        "Total units sold summarizes recorded volume. Total revenue follows the project's discount "
        "formula. Average unit price is an unweighted mean of row-level prices, not a sales-weighted "
        "average. MAE is an aggregate error measure and should be interpreted alongside product-level "
        "errors and the scale of demand."
    )
    subheading("Data Caveat")
    body(
        "The figures depend on the selected input file and its current contents. If the dataset or "
        "cleaning rules change, rerun the report to refresh these results."
    )
    new_page()

    # PAGE 11 — REVENUE BY CATEGORY
    heading("11. Revenue by Product Category")
    add_chart(
        story, CHARTS[0][0],
        "Figure 1. Total revenue distribution by product category. The original chart is included from outputs/."
    )
    subheading("Category Revenue Summary")
    rows = [["Category", "Total Revenue"]]
    for name, value in m["category_revenue"].head(8).items():
        rows.append([name, fmt(value)])
    story.append(make_table(rows, [8.0 * cm, 8.0 * cm]))
    body(
        "Category revenue helps identify which product groups contribute the most recorded sales value. "
        "Management can review the strongest categories and investigate lower-contributing categories. "
        "Revenue alone does not indicate profit because product costs and operating expenses are not "
        "included in this project metric."
    )
    new_page()

    # PAGE 12 — SEASONALITY
    heading("12. Units Sold by Seasonality")
    add_chart(
        story, CHARTS[1][0],
        "Figure 2. Distribution of recorded units sold across the Seasonality labels in the dataset."
    )
    body(
        "The seasonality chart groups units sold by the Seasonality field. It is a descriptive comparison "
        "of the labels present in the dataset. It should not automatically be interpreted as proof of "
        "yearly seasonal behavior, because that conclusion requires repeated observations across enough "
        "time periods and a clear definition of each season label."
    )
    subheading("Business Use")
    body(
        "If demand differences are consistent and supported by historical observations, a retailer can "
        "review purchasing plans before expected high-demand periods. The chart should be considered "
        "alongside date-level demand, promotions and stock availability."
    )
    new_page()

    # PAGE 13 — TOP PRODUCTS
    heading("13. Highest-Demand Products")
    add_chart(
        story, CHARTS[2][0],
        "Figure 3. The ten product IDs with the highest total recorded demand."
    )
    subheading("Top Products by Total Demand")
    rows = [["Product ID", "Total Demand", "Average / Row", "Avg. Inventory", "Avg. Forecast"]]
    for _, r in m["top_products"].head(8).iterrows():
        rows.append([
            str(r["Product ID"]), fmt(r["Total_Demand"], 0),
            fmt(r["Average_Daily_Demand"]), fmt(r["Current_Inventory"]),
            fmt(r["Average_Forecast"])
        ])
    story.append(make_table(rows, [2.8 * cm, 3.1 * cm, 3.0 * cm, 3.3 * cm, 3.8 * cm]))
    body(
        "High total demand can indicate products that deserve frequent stock monitoring. The average "
        "demand and current inventory proxy add context, but replenishment decisions should also consider "
        "supplier lead time, order constraints and stockout history."
    )
    new_page()

    # PAGE 14 — DAILY DEMAND TREND
    heading("14. Daily Demand and 7-Day Moving Average")
    add_chart(
        story, CHARTS[3][0],
        "Figure 4. Daily total units sold with the seven-day moving-average line."
    )
    subheading("Moving Average")
    story.append(Paragraph(
        "7-day moving average = mean of the most recent seven daily observations",
        styles["CenterReport"]
    ))
    body(
        "The moving average smooths some short-term variation so that broader changes are easier to see. "
        "It can help identify sustained rises or falls in demand. It can also respond slowly to sudden "
        "changes and is meaningful only when the observations are correctly ordered and represent "
        "consistent daily intervals."
    )
    subheading("Interpretation Guidance")
    body(
        "Read the daily series and smoothed line together. Large gaps or spikes should be investigated "
        "rather than automatically treated as normal demand behavior."
    )
    new_page()

    # PAGE 15 — FORECAST VS ACTUAL
    heading("15. Supplied Forecast Versus Actual Units Sold")
    add_chart(
        story, CHARTS[4][0],
        "Figure 5. Scatter plot comparing supplied Demand Forecast values with observed Units Sold."
    )
    story.append(make_table([
        ["Evaluation metric", "Value from selected CSV"],
        ["Mean Absolute Error (MAE)", f"{fmt(m['forecast_mae'])} units"],
        ["Rows with both values available", f"{m['forecast_rows']:,}"],
    ], [8.0 * cm, 8.0 * cm]))
    subheading("Interpretation")
    body(
        "In the scatter plot, points close to the ideal equality line represent rows where the forecast "
        "and actual units are similar. Points far from the line indicate larger differences. MAE "
        "summarizes the average absolute error, but does not show whether the model tends to overpredict "
        "or underpredict."
    )
    body(
        "The existing project evaluates forecasts supplied in the dataset. It does not train a new "
        "forecasting model. Stronger evaluation could include MAE by product and period, RMSE, bias, "
        "and a time-based holdout test."
    )
    new_page()

    # PAGE 16 — CATEGORY DEMAND
    heading("16. High-Demand Product Categories")
    add_chart(
        story, CHARTS[5][0],
        "Figure 6. Product categories ranked by total recorded units sold."
    )
    subheading("Units Sold by Category")
    rows = [["Category", "Total Units Sold"]]
    for name, value in m["category_units"].head(8).items():
        rows.append([name, fmt(value, 0)])
    story.append(make_table(rows, [8.0 * cm, 8.0 * cm]))
    body(
        "This view ranks categories by sales volume rather than revenue. A category can sell many units "
        "without being the largest revenue contributor if its prices are lower. Comparing this chart "
        "with category revenue gives a more complete picture of sales performance."
    )
    new_page()

    # PAGE 17 — REGIONAL REVENUE
    heading("17. Regional Revenue Analysis")
    add_chart(
        story, CHARTS[6][0],
        "Figure 7. Revenue comparison across the regions recorded in the dataset."
    )
    subheading("Regional Revenue Summary")
    rows = [["Region", "Total Revenue"]]
    for name, value in m["region_revenue"].items():
        rows.append([name, fmt(value)])
    story.append(make_table(rows, [8.0 * cm, 8.0 * cm]))
    body(
        "Regional comparison can highlight differences in recorded sales contribution. Before making "
        "regional decisions, consider the number of stores, product mix, promotions, demand coverage "
        "and inventory availability represented in each region."
    )
    new_page()

    # PAGE 18 — REGION / CATEGORY DISTRIBUTION
    heading("18. Regional and Category Distribution")
    add_chart(
        story, CHARTS[7][0],
        "Figure 8. Existing project visualization showing category distribution by region."
    )
    body(
        "This visualization provides a combined regional and category view. It can help identify whether "
        "the mix of recorded products or observations differs by region. The exact interpretation should "
        "follow the axes, legend and counting method shown in the original chart."
    )
    subheading("Potential Business Use")
    body(
        "If category demand varies by region, the retailer can investigate whether local assortment or "
        "replenishment plans should differ. Any change should be based on demand and stock measures, "
        "not chart appearance alone."
    )
    new_page()

    # PAGE 19 — STOCK STATUS
    heading("19. Product-Level Inventory Status")
    under = int((ps["Stock_Status"] == "Under-stocked").sum())
    optimal = int((ps["Stock_Status"] == "Optimal").sum())
    over = int((ps["Stock_Status"] == "Over-stocked").sum())
    story.append(make_table([
        ["Stock status", "Product count", "Rule implemented in project"],
        ["Under-stocked", f"{under:,}", "Mean inventory < 3 × average demand"],
        ["Optimal", f"{optimal:,}", "Does not meet either threshold"],
        ["Over-stocked", f"{over:,}", "Mean inventory > 15 × average demand"],
    ], [3.2 * cm, 2.8 * cm, 9.2 * cm]))
    subheading("Product Summary — Highest Demand")
    rows = [["Product ID", "Total Demand", "Avg Demand", "Mean Inventory", "Status"]]
    for _, r in m["top_products"].head(10).iterrows():
        rows.append([
            str(r["Product ID"]), fmt(r["Total_Demand"], 0),
            fmt(r["Average_Daily_Demand"]), fmt(r["Current_Inventory"]),
            str(r["Stock_Status"])
        ])
    story.append(make_table(rows, [2.8 * cm, 3.1 * cm, 3.0 * cm, 3.4 * cm, 2.9 * cm]))
    body(
        "These classifications follow the repository's heuristic: average inventory per product is "
        "compared with three and fifteen times that product's average recorded demand. They are not "
        "formal replenishment rules. Real inventory policies should account for lead time, safety stock, "
        "service level, stockouts and replenishment frequency."
    )
    new_page()

    # PAGE 20 — FINDINGS
    heading("20. Findings and Business Insights")
    subheading("Findings from the Implemented Analysis")
    story.extend(bullets([
        f"The selected data file contains {m['rows']:,} records and {m['columns']:,} columns.",
        f"The selected CSV has {m['missing_cells']:,} missing cells and {m['duplicate_rows']:,} exact duplicate rows at report time.",
        f"The dataset includes {m['unique_products']:,} distinct product IDs across {m['unique_categories']:,} categories and {m['unique_regions']:,} regions.",
        f"Total recorded units sold are {fmt(m['units_sold'], 0)}.",
        f"Revenue calculated with the project formula is {fmt(m['total_revenue'])} in the dataset's currency units.",
        f"The supplied forecasts have an aggregate MAE of {fmt(m['forecast_mae'])} units over {m['forecast_rows']:,} usable rows.",
        f"The project's inventory heuristic classifies {under:,} products as under-stocked, {optimal:,} as optimal, and {over:,} as over-stocked.",
    ]))
    subheading("Business Insights")
    body(
        "The product and category tables can guide attention toward high-volume products and important "
        "categories. The demand trend can support review of recent movement. Forecast error provides a "
        "baseline signal of how far supplied forecasts differ from observed sales. Inventory status can "
        "be used as a screening indicator for products requiring further review."
    )
    body(
        "These are analytical indicators rather than guaranteed business outcomes. The dataset may not "
        "contain all information needed to explain demand changes or optimize purchasing."
    )
    new_page()

    # PAGE 21 — RECOMMENDATIONS, LIMITATIONS, FUTURE SCOPE
    heading("21. Recommendations, Limitations and Future Scope")
    subheading("Recommendations")
    story.extend(bullets([
        "Review the highest-demand products regularly and compare demand with current stock.",
        "Use regional and category summaries to identify where deeper investigation is needed.",
        "Validate missing values and duplicate rows before relying on totals.",
        "Evaluate forecast errors separately by product and time period.",
        "Compare simple moving-average baselines with other forecasting methods.",
        "Calibrate stock-status thresholds against supplier lead times and desired service levels.",
        "Keep the source workbook, cleaned CSV, scripts and generated charts version-aligned.",
    ]))
    subheading("Limitations")
    story.extend(bullets([
        "Historical demand may not represent future customer behavior.",
        "Median imputation can affect sales and inventory summaries.",
        "The project uses simple inventory thresholds that are not calibrated operational policies.",
        "Aggregate MAE does not reveal forecast bias or performance for each product.",
        "Revenue excludes taxes, returns, shipping and other accounting adjustments.",
        "External factors may affect demand but are not fully modeled in the current pipeline.",
    ]))
    subheading("Future Scope")
    story.extend(bullets([
        "Compare 7-, 14- and 30-day moving-average forecasts.",
        "Add weighted moving average or simple exponential smoothing.",
        "Report MAE, RMSE and forecast bias by product and period.",
        "Estimate safety stock and reorder points using lead time and service level.",
        "Add category-specific forecasts and interactive dashboard filters.",
    ]))
    new_page()

    # PAGE 22 — CONCLUSION AND REFERENCES
    heading("22. Conclusion and References")
    subheading("Conclusion")
    body(
        "The Retail Inventory Analytics project demonstrates a practical Python workflow for cleaning "
        "retail records, summarizing product demand, calculating revenue, reviewing inventory indicators, "
        "comparing supplied forecasts with observed sales, and communicating patterns through charts and "
        "a Streamlit dashboard. The analysis is organized into reproducible steps and can be rerun when "
        "the dataset is updated."
    )
    body(
        "The results can support exploratory inventory review, but should not be treated as automatic "
        "purchasing instructions. Data quality, forecast limitations and the heuristic nature of stock "
        "thresholds must be considered before applying the findings in a real retail operation. A useful "
        "next iteration would test alternative forecasting baselines, report errors over time, and tune "
        "inventory rules with realistic supplier lead times and service targets. This would build on the "
        "current work without overstating what the existing analysis can prove."
    )
    subheading("References")
    references = [
        "Project README.md — Retail Inventory Analytics repository.",
        "src/data_cleaning.py — implemented data-cleaning rules.",
        "src/analysis.py — metrics, stock-status heuristics and chart generation.",
        "dashboard.py — Streamlit dashboard implementation.",
        "Python documentation: https://docs.python.org/3/",
        "Pandas documentation: https://pandas.pydata.org/docs/",
        "NumPy documentation: https://numpy.org/doc/",
        "Matplotlib documentation: https://matplotlib.org/stable/",
        "Streamlit documentation: https://docs.streamlit.io/",
        "ReportLab documentation: https://docs.reportlab.com/",
    ]

    subheading("GitHub Repository")
    references = [
        "Github Repo Link : "
    ]
    story.extend(bullets(references))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("END OF REPORT", styles["CoverLabel"]))

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    print("\nReport generated:")
    print(OUTPUT_PDF)
    print(f"Input dataset: {csv_path}")
    print(f"Charts found: {sum((OUTPUT_DIR / f).exists() for f, _ in CHARTS)} / {len(CHARTS)}")
    print("Attempting to open the PDF...")

    try:
        if platform.system() == "Windows":
            os.startfile(str(OUTPUT_PDF))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(OUTPUT_PDF)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_PDF)])
    except Exception as exc:
        print(f"Automatic PDF opening failed: {exc}")
        print(f"Open the file manually: {OUTPUT_PDF}")


if __name__ == "__main__":
    try:
        build_report()
    except Exception as exc:
        print(f"\nREPORT GENERATION FAILED: {type(exc).__name__}: {exc}")
        raise