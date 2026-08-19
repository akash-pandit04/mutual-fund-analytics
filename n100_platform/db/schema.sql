-- ============================================================
-- N100 FINANCIAL INTELLIGENCE PLATFORM — SQLITE SCHEMA
-- 10 Tables Schema with Constraints & Foreign Keys
-- ============================================================

PRAGMA foreign_keys = ON;

-- Table 1: Companies
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    industry TEXT,
    isin TEXT UNIQUE,
    market_cap_category TEXT DEFAULT 'LargeCap'
);

-- Table 2: Profit & Loss Statement
CREATE TABLE IF NOT EXISTS profit_loss (
    pl_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    revenue REAL DEFAULT 0,
    operating_expenses REAL DEFAULT 0,
    opm_percent REAL,
    ebitda REAL,
    depreciation REAL,
    ebit REAL,
    interest_expense REAL,
    other_income REAL,
    pbt REAL,
    tax REAL,
    pat REAL,
    eps REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, year)
);

-- Table 3: Balance Sheet
CREATE TABLE IF NOT EXISTS balance_sheet (
    bs_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    equity_capital REAL DEFAULT 0,
    reserves REAL DEFAULT 0,
    total_shareholders_equity REAL,
    borrowings_long_term REAL DEFAULT 0,
    borrowings_short_term REAL DEFAULT 0,
    total_debt REAL,
    other_liabilities REAL DEFAULT 0,
    total_liabilities REAL,
    fixed_assets REAL DEFAULT 0,
    cwip REAL DEFAULT 0,
    investments REAL DEFAULT 0,
    other_assets REAL DEFAULT 0,
    total_assets REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, year)
);

-- Table 4: Cash Flow Statement
CREATE TABLE IF NOT EXISTS cash_flow (
    cf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    cfo REAL DEFAULT 0,
    cfi REAL DEFAULT 0,
    cff REAL DEFAULT 0,
    capex REAL DEFAULT 0,
    free_cash_flow REAL,
    net_change_in_cash REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, year)
);

-- Table 5: Stock Prices
CREATE TABLE IF NOT EXISTS stock_prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    close_price REAL NOT NULL,
    volume INTEGER,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, date)
);

-- Table 6: Financial Ratios (Sprint 2 Output)
CREATE TABLE IF NOT EXISTS financial_ratios (
    ratio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    net_profit_margin_pct REAL,
    opm_pct REAL,
    roe_pct REAL,
    roce_pct REAL,
    roa_pct REAL,
    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,
    revenue_cagr_3yr REAL,
    pat_cagr_3yr REAL,
    eps_cagr_3yr REAL,
    cagr_flag TEXT,
    fcf REAL,
    cfo_quality_score REAL,
    capex_intensity REAL,
    fcf_conversion_rate REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, year)
);

-- Table 7: Capital Allocation
CREATE TABLE IF NOT EXISTS capital_allocation (
    alloc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    pattern_label TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, year)
);

-- Table 8: Data Audit Log
CREATE TABLE IF NOT EXISTS data_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    rows_loaded INTEGER,
    rows_rejected INTEGER,
    load_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Table 9: Data Quality Rules
CREATE TABLE IF NOT EXISTS data_quality_rules (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('CRITICAL', 'WARNING', 'INFO')),
    description TEXT
);

-- Table 10: Validation Failures
CREATE TABLE IF NOT EXISTS validation_failures (
    failure_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    company_id INTEGER,
    year INTEGER,
    field_name TEXT,
    error_message TEXT,
    severity TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
