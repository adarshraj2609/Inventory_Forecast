# Retail Inventory Analytics

A Python analytics pipeline and Streamlit dashboard for cleaning retail inventory data, evaluating product demand and stock levels, comparing supplied demand forecasts with observed sales, and presenting the results through charts and a PDF report viewer.

## Project Overview

This project processes a retail inventory workbook covering 2025–2026. It separates data preparation from analysis so that the source data can be cleaned and standardized before business metrics and visual summaries are generated.

The end-to-end workflow is:

1. Read the source Excel workbook.
2. Remove duplicate records and clean selected date, category, price, inventory, sales, and discount values.
3. Save the cleaned records as a CSV file.
4. Calculate revenue, demand, inventory-risk indicators, and forecast error.
5. Export analysis charts to the `outputs/` directory.
6. Display the cleaned data and analysis results in the Streamlit dashboard.
7. Open the final project PDF report from the dashboard's **Open Report** button.

## Key Features

### Data Pipeline

- Reads the source Excel workbook.
- Removes exact duplicate rows.
- Standardizes selected text and date fields.
- Handles invalid and missing values according to the project cleaning rules.
- Exports a cleaned CSV file.
- Calculates revenue, demand, stock-status indicators, and forecast MAE.

### Streamlit Dashboard

- Displays total revenue, units sold, average unit price, and forecast MAE.
- Summarizes under-stocked, optimal, and over-stocked products.
- Shows eight charts covering category revenue, seasonality, product demand, daily demand trends, forecast comparisons, and regional performance.
- Provides tables for highest-demand products, lowest-demand products, and stock status.
- Displays a **Cronus Consultants** welcome dialog with the seven project team members before the dashboard is used in a new Streamlit session.
- Includes an **Open Report** button to display the project's PDF report inside the Streamlit app, plus a PDF download button.

## Analytical Questions

The pipeline and dashboard are designed to help explore:

- How much revenue and sales volume are represented in the dataset?
- Which product IDs have the highest and lowest recorded demand?
- Which categories contribute the most revenue and units sold?
- How does daily sales volume change over time?
- How closely do the provided demand forecasts match observed units sold?
- Which products meet the project's under-stock or over-stock heuristics?
- How are units sold distributed across seasonality labels?
- How does revenue and transaction volume vary by region?

## Data and Assumptions

### Input

The full pipeline expects this workbook at the project-relative path:

```text
data/rawdata/retail_store_inventory_extended_messy_2025_2026.xlsx
```

The analysis uses fields including `Date`, `Product ID`, `Category`, `Seasonality`, `Units Sold`, `Price`, `Discount`, `Inventory Level`, and `Demand Forecast`.

### Cleaning Rules

Implemented in `src/data_cleaning.py`:

| Data quality issue | Current handling |
| --- | --- |
| Duplicate records | Exact duplicate rows are removed. |
| Category, region, weather, and seasonality labels | Leading/trailing whitespace is removed and text is title-cased; string values representing missing data are converted to nulls. |
| Invalid dates | Dates are parsed with coercion; rows with unparseable dates are dropped. |
| Negative inventory and units sold | Values are treated as missing and filled using the respective dataset-wide median. |
| Discounts outside 0–100 | Values are treated as missing. |
| Prices above $1,000 | Values are treated as missing and filled using the median price for the corresponding category. |
| Missing categories | Filled with `Uncategorized`. |

These are project-specific rules, not universal retail accounting or inventory policies. The cleaning script does not currently impute every missing field in the workbook.

### Metric Definitions

- **Total revenue:** `Units Sold × Price × (1 − Discount / 100)`, summed across rows. This uses the dataset's discount percentage; it does not account for taxes, returns, shipping, or other adjustments.
- **Average unit price:** Mean of the row-level `Price` values; this is not weighted by units sold.
- **Product average daily demand:** Mean of that product's `Units Sold` values across its available rows.
- **Stock status:** Uses the mean recorded inventory per product as a proxy. A product is marked under-stocked below three times its average daily demand, over-stocked above fifteen times its average daily demand, and otherwise optimal.
- **Forecast MAE:** Mean absolute difference between the provided `Demand Forecast` and `Units Sold` for rows with both values available. The project evaluates the supplied forecasts; it does not train a forecasting model.

## Analysis and Outputs

The analysis stage prints the financial summary, top and bottom demand products, stock-status counts, and forecast mean absolute error (MAE).

### Pipeline Charts

The analysis pipeline exports six charts under `outputs/`:

| File | Contents |
| --- | --- |
| `01_category_revenue.png` | Revenue by product category |
| `02_seasonal_units_distribution.png` | Share of units sold by seasonality |
| `03_top_demand_products.png` | Ten products with the highest total demand |
| `04_demand_trend_7day_moving_avg.png` | Daily sales and a seven-day moving average |
| `05_forecast_vs_actual.png` | Provided demand forecast compared with observed units sold |
| `06_high_demand_categories.png` | Units sold by product category |

### Additional Dashboard Charts

The Streamlit dashboard also generates two regional charts in `outputs/`:

| File | Contents |
| --- | --- |
| `07_region_revenue.png` | Revenue performance by region |
| `08_region_category_countplot.png` | Transaction counts by region and product category |

The pipeline writes the cleaned dataset to:

```text
data/cleandata/retail_store_inventory_cleaned.csv
```

The dashboard looks for the cleaned CSV in `data/cleandata/` first and then in `outputs/`.

## Repository Structure

```text
Retail_Inventory_Analytics/
├── data/
│   ├── rawdata/
│   │   └── retail_store_inventory_extended_messy_2025_2026.xlsx
│   └── cleandata/
│       └── retail_store_inventory_cleaned.csv
├── outputs/
│   ├── 01_category_revenue.png
│   ├── 02_seasonal_units_distribution.png
│   ├── 03_top_demand_products.png
│   ├── 04_demand_trend_7day_moving_avg.png
│   ├── 05_forecast_vs_actual.png
│   ├── 06_high_demand_categories.png
│   ├── 07_region_revenue.png
│   └── 08_region_category_countplot.png
├── src/
│   ├── analysis.py
│   └── data_cleaning.py
├── dashboard.py
├── main.py
├── requirements.txt
├── Retail_Inventory_Analytics_Final_Report.pdf
└── README.md
```

The PDF report should be placed in the same directory as `dashboard.py`. The dashboard also contains a local Windows fallback path for the original development machine; that absolute path will not work on another computer. Keeping the PDF beside `dashboard.py` is the recommended portable setup.

## Requirements

- Python 3
- Packages listed in `requirements.txt`
- The source workbook at the input path described above
- The PDF report beside `dashboard.py` to use the in-app report viewer

Install the project dependencies from the project root:

```bash
python -m pip install -r requirements.txt
```

The dashboard's embedded PDF viewer uses Streamlit's `st.pdf()` feature. Install its optional PDF dependency with:

```bash
python -m pip install "streamlit[pdf]"
```

This command can also be added to the environment setup process if the dashboard is deployed to another machine. See the [Streamlit PDF viewer documentation](https://docs.streamlit.io/develop/api-reference/media/st.pdf) for details.

If you have multiple Python installations, use the interpreter that will run the pipeline for both installation and execution. For example, in PowerShell:

```powershell
D:\python.exe -m pip install -r requirements.txt
```

## Run the Full Pipeline

Run these commands from the project root:

```bash
python main.py
```

The entry point cleans the workbook, writes the cleaned CSV, runs the analysis, and saves the pipeline charts. Existing output files with the same names are overwritten.

To run data cleaning or analysis separately, use:

```bash
python -m src.data_cleaning
python -m src.analysis
```

The standalone analysis script looks for a cleaned CSV in `outputs/retail_store_inventory_cleaned.csv`, then `data/cleaned_retail_inventory_2025_2026.csv`; if neither exists, it tries the workbook at the project root. For the standard project input and output paths, `python main.py` is the recommended command.

## Run the Streamlit Dashboard

After generating the cleaned CSV, start the dashboard from the project root:

```bash
python -m streamlit run dashboard.py
```