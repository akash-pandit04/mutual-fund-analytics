# 📊 Mutual Fund Analytics — Capstone Project

> **Bluestock Fintech 24J Internship**
> Capstone Project I — Mutual Fund Analytics

## 🎯 Project Overview

This project performs end-to-end data analytics on Indian mutual fund data, covering ETL pipelines, exploratory data analysis (EDA), advanced risk metrics computation, predictive trend modeling, and interactive dashboard development.

**Key Highlights:**
- Analyzed **40 mutual fund schemes** across **10 AMCs (Asset Management Companies)**
- Processed **32,778 investor transactions** and **8,050 benchmark index records**
- Computed risk metrics: **Alpha, Beta, Sharpe Ratio, Max Drawdown, Volatility**
- K-Means clustering into **3 risk profiles** (Low / Medium / High Risk)
- SMA & EMA trend analysis for NAV prediction
- Interactive Power BI dashboard with 4 analytical pages

---

## 📁 Project Structure

```
mutual-fund-analytics/
├── data/
│   ├── raw/                          # Original 10 CSV datasets + live NAV data
│   │   ├── 01_fund_master.csv
│   │   ├── 02_nav_history.csv
│   │   ├── 03_aum_by_fund_house.csv
│   │   ├── 04_monthly_sip_inflows.csv
│   │   ├── 05_category_inflows.csv
│   │   ├── 06_industry_folio_count.csv
│   │   ├── 07_scheme_performance.csv
│   │   ├── 08_investor_transactions.csv
│   │   ├── 09_portfolio_holdings.csv
│   │   ├── 10_benchmark_indices.csv
│   │   └── nav_*.csv                 # Live NAV data from mfapi.in
│   └── processed/
│       ├── database.db               # SQLite database (all tables)
│       └── risk_metrics.csv          # Computed risk analytics
├── notebooks/                        # Jupyter notebooks for EDA & analysis
├── reports/
│   ├── Final_Report.pdf              # 15-20 page project report
│   └── Bluestock_MF_Presentation.pptx  # 12-slide presentation
├── dashboard/                        # Power BI dashboard files
├── sql/                              # SQL queries
├── data_ingestion.py                 # Day 1: Data loading & exploration
├── live_nav_fetch.py                 # Fetches live NAV from mfapi.in API
├── etl_pipeline.py                   # ETL: CSV → SQLite database
├── advanced_analytics_script.py      # Risk metrics, clustering, SMA/EMA
├── run_pipeline.py                   # Master execution script
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 🛠️ Tech Stack

| Tool / Library | Purpose |
|---------------|---------|
| Python 3.10+ | Core programming language |
| Pandas | Data manipulation & analysis |
| NumPy | Numerical computation |
| Scikit-learn | K-Means clustering |
| Matplotlib / Seaborn | Data visualization |
| Plotly | Interactive charts |
| SQLite / SQLAlchemy | Database management |
| Requests | API data fetching |
| ReportLab | PDF report generation |
| python-pptx | PowerPoint generation |
| Power BI | Interactive dashboard |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/akash-pandit04/mutual-fund-analytics.git
cd mutual-fund-analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install python-pptx reportlab scikit-learn
```

### 3. Run the Full Pipeline
```bash
python run_pipeline.py
```

This will:
1. Fetch live NAV data from the mfapi.in API
2. Build a SQLite database from all raw CSV files
3. Run advanced analytics (volatility, alpha/beta, SMA/EMA, K-Means clustering)

---

## 📊 Data Sources

| Dataset | Records | Description |
|---------|---------|-------------|
| `01_fund_master.csv` | 40 schemes | Fund metadata: AMC, category, sub-category, SEBI codes |
| `02_nav_history.csv` | ~5,000+ | Historical NAV values for all 40 schemes |
| `03_aum_by_fund_house.csv` | ~40 | AUM (Assets Under Management) by fund house |
| `04_monthly_sip_inflows.csv` | ~36 | Monthly SIP inflow trends (2022–2025) |
| `05_category_inflows.csv` | ~48 | Category-wise inflow/outflow data |
| `06_industry_folio_count.csv` | ~12 | Industry-level folio counts |
| `07_scheme_performance.csv` | 40 | Performance metrics, ratings, risk grades |
| `08_investor_transactions.csv` | 32,778 | Individual investor transaction records |
| `09_portfolio_holdings.csv` | 322 | Stock-level portfolio holdings |
| `10_benchmark_indices.csv` | 8,050 | Daily benchmark index values (Nifty 50, etc.) |
| Live NAV (API) | ~3,000+ each | Real-time NAV from mfapi.in for 6 key schemes |

---

## 📈 Key Findings

### Risk-Return Clustering (K-Means, k=3)
- **Low Risk**: Debt and liquid funds with annualized std dev < 0.4
- **Medium Risk**: Diversified equity and balanced funds
- **High Risk**: Small-cap and sector-specific funds with high volatility

### Top Performing Funds (by Alpha)
Funds with the highest alpha values significantly outperformed the Nifty 50 benchmark, indicating strong fund management.

### Industry Trends
- Total industry AUM: ₹81 Lakh Crore
- Monthly SIP inflows: ₹31,000 Crore
- Total folios: 26.12 Crore
- Active schemes analyzed: 1,908

---

## 👤 Author

**Akash Kumar Pandit**
- Email: akashpandit9691077552@gmail.com
- GitHub: [akash-pandit04](https://github.com/akash-pandit04)
- Internship: Bluestock Fintech 24J Batch

---

## 📄 License

This project was developed as part of the Bluestock Fintech Internship Program.
