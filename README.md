# 📊 Bluestock Fintech Analytics & Intelligence Platforms

> **Bluestock Fintech Internship Portfolio**  
> **Author:** Akash Kumar Pandit (`akashpandit9691077552@gmail.com`)  
> **GitHub:** [akash-pandit04/mutual-fund-analytics](https://github.com/akash-pandit04/mutual-fund-analytics)

---

## 🚀 Projects Overview

This repository contains all code, analytics engines, SQL databases, Jupyter notebooks, data quality pipelines, and report deliverables across all assigned projects:

### 1. 📈 Capstone Project I — Mutual Fund Analytics (100% Complete)
- **ETL & Data Pipeline:** Extract live NAV from `mfapi.in` API, transform 10 production datasets, load to `data/processed/database.db` (16 tables).
- **Risk Metrics:** Annualized StdDev (Volatility), Max Drawdown, Beta, Alpha vs Nifty 50.
- **K-Means Clustering:** Risk-return segmentation into 3 clusters (Low, Medium, High Risk).
- **Interactive Dashboard:** 4-page Plotly Dash application (`dashboard/dashboard_app.py`) + Power BI Setup Guide (`dashboard/powerbi_setup_guide.txt`).
- **Reports & Presentation:** Multi-page PDF report (`reports/Final_Report.pdf`) + 12-slide presentation (`reports/Bluestock_MF_Presentation.pptx`).

### 2. 🎓 Data Analyst Internship — Week 1 & Week 2 Prerequisites (100% Complete)
- **Week 1 Foundation:** Excel sales dataset (`prerequisites/cleaned_sales_dataset.csv`), SQL queries (`prerequisites/sql_practice_queries.sql`), and Python EDA notebook (`prerequisites/python_data_analysis.ipynb`).
- **Week 2 FinTech & Software Fundamentals:**
  - Stock Market Summary & Reliance Industries Deep-Dive (`prerequisites/week2/stock_market_summary.md`)
  - REST API Data Extraction Engine (`prerequisites/week2/api_extraction.py` → `api_extracted_data.csv`)
  - Software Architecture & Data Flow Diagram (`prerequisites/week2/software_architecture.md`)
  - FinTech Domain Research Report — Zerodha Case Study (`prerequisites/week2/fintech_research_report.md`)

### 3. 🏦 N100 Financial Intelligence Platform (Sprint 1 & Sprint 2 Complete)
- **Sprint 1 — Data Foundation:**
  - 10-table SQLite schema (`n100_platform/db/schema.sql` → `nifty100.db`)
  - 12-source Excel loader (`n100_platform/src/etl/loader.py`) populating 92 companies, 1,288 P&L, 1,288 BS, 1,288 CF, 5,520 prices
  - 16 Data Quality (DQ) validation rules engine (`n100_platform/src/etl/validator.py`)
  - 10 analytical SQL queries (`n100_platform/notebooks/exploratory_queries.sql`)
  - 35+ unit tests (`n100_platform/tests/etl/test_loader.py`)
- **Sprint 2 — Financial Ratio Engine:**
  - Ratio Calculation Engine (`n100_platform/src/analytics/ratios.py`): NPM, OPM, ROE, ROCE, ROA, D/E, ICR, Asset Turnover
  - CAGR Engine (`n100_platform/src/analytics/cagr.py`): 6 edge-case handlers (`NORMAL`, `TURNAROUND`, `DECLINE_TO_LOSS`, `BOTH_NEGATIVE`, `ZERO_BASE`, `INSUFFICIENT`)
  - Cash Flow KPIs & 8-Pattern Capital Allocation Classifier (`n100_platform/src/analytics/cashflow_kpis.py`)
  - Populated 1,288 financial ratio records into `nifty100.db`
  - 20 formula unit tests (`n100_platform/tests/kpi/test_ratios.py`)

---

## 📁 Repository Structure

```
mutual-fund-analytics/
├── data/                             # Capstone raw & processed data
│   ├── raw/
│   └── processed/
│       ├── database.db               # SQLite Database (16 tables)
│       └── risk_metrics.csv
├── notebooks/                        # Capstone Jupyter Notebooks (.ipynb)
│   ├── eda_notebook.ipynb
│   ├── performance_metrics.ipynb
│   └── advanced_analytics.ipynb
├── dashboard/                        # Web Dashboard & Power BI guide
│   ├── dashboard_app.py
│   └── powerbi_setup_guide.txt
├── reports/                          # Capstone Final PDF & PPTX Presentation
│   ├── Final_Report.pdf
│   └── Bluestock_MF_Presentation.pptx
├── prerequisites/                    # Prerequisite assignments (Week 1 & Week 2)
│   ├── week2/
│   │   ├── stock_market_summary.md
│   │   ├── api_extraction.py
│   │   ├── software_architecture.md
│   │   └── fintech_research_report.md
│   ├── sql_practice_queries.sql
│   ├── cleaned_sales_dataset.csv
│   └── python_data_analysis.ipynb
├── n100_platform/                    # N100 Financial Intelligence Platform
│   ├── db/
│   │   └── schema.sql                # 10-table SQLite schema
│   ├── src/
│   │   ├── etl/                      # loader.py, validator.py, normaliser.py
│   │   └── analytics/                # ratios.py, cagr.py, cashflow_kpis.py
│   ├── tests/                        # 55+ unit tests (pytest)
│   ├── output/                       # load_audit.csv, validation_failures.csv, capital_allocation.csv
│   ├── run_n100_pipeline.py          # Master N100 execution script
│   └── nifty100.db                   # Populated N100 SQLite database
├── etl_pipeline.py                   # Capstone ETL script
├── advanced_analytics_script.py      # Capstone Risk Analytics
├── run_pipeline.py                   # Capstone Master script
├── requirements.txt                  # Environment dependencies
└── README.md                         # Main repository documentation
```

---

## ⚡ How to Run

### 1. Run Capstone Pipeline
```bash
python run_pipeline.py
python dashboard/dashboard_app.py
```

### 2. Run N100 Platform Pipeline & Tests
```bash
python n100_platform/run_n100_pipeline.py
pytest n100_platform/tests/
```
