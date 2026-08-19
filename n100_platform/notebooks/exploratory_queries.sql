-- ============================================================
-- N100 FINANCIAL INTELLIGENCE PLATFORM — EXPLORATORY QUERIES
-- 10 Analytical SQL Queries interrogating nifty100.db
-- ============================================================

-- 1. Top 10 Companies by Latest Revenue (2024)
SELECT 
    c.ticker, c.company_name, c.sector, pl.revenue, pl.pat
FROM companies c
JOIN profit_loss pl ON c.company_id = pl.company_id
WHERE pl.year = 2024
ORDER BY pl.revenue DESC
LIMIT 10;

-- 2. Sector-wise Average Operating Profit Margin (OPM)
SELECT 
    c.sector,
    COUNT(c.company_id) AS total_companies,
    ROUND(AVG(pl.opm_percent), 2) AS avg_opm_pct
FROM companies c
JOIN profit_loss pl ON c.company_id = pl.company_id
WHERE pl.year = 2024
GROUP BY c.sector
ORDER BY avg_opm_pct DESC;

-- 3. High Leverage Screen: Companies with Debt-to-Equity > 1.5
SELECT 
    c.ticker, c.company_name, bs.year, bs.total_debt, bs.total_shareholders_equity,
    ROUND(bs.total_debt / bs.total_shareholders_equity, 2) AS debt_to_equity
FROM companies c
JOIN balance_sheet bs ON c.company_id = bs.company_id
WHERE bs.year = 2024 AND bs.total_shareholders_equity > 0 AND (bs.total_debt / bs.total_shareholders_equity) > 1.5
ORDER BY debt_to_equity DESC;

-- 4. Free Cash Flow (FCF) Leaders in 2024
SELECT 
    c.ticker, c.company_name, cf.cfo, cf.capex, cf.free_cash_flow
FROM companies c
JOIN cash_flow cf ON c.company_id = cf.company_id
WHERE cf.year = 2024
ORDER BY cf.free_cash_flow DESC
LIMIT 10;

-- 5. Multi-Year Revenue Growth Trends (2020 vs 2024)
SELECT 
    c.ticker, c.company_name,
    p1.revenue AS rev_2020,
    p2.revenue AS rev_2024,
    ROUND(((p2.revenue / p1.revenue) - 1) * 100, 2) AS total_growth_pct
FROM companies c
JOIN profit_loss p1 ON c.company_id = p1.company_id AND p1.year = 2020
JOIN profit_loss p2 ON c.company_id = p2.company_id AND p2.year = 2024
ORDER BY total_growth_pct DESC;

-- 6. Capital Allocation Pattern Distribution
SELECT 
    pattern_label,
    COUNT(*) AS company_year_count
FROM capital_allocation
GROUP BY pattern_label
ORDER BY company_year_count DESC;

-- 7. High ROE & Low Debt Screener (ROE > 15% AND D/E < 1.0)
SELECT 
    c.ticker, c.company_name, r.year, r.roe_pct, r.debt_to_equity, r.net_profit_margin_pct
FROM companies c
JOIN financial_ratios r ON c.company_id = r.company_id
WHERE r.year = 2024 AND r.roe_pct > 15.0 AND r.debt_to_equity < 1.0
ORDER BY r.roe_pct DESC;

-- 8. Data Quality Violation Audit Summary
SELECT 
    rule_id, severity, COUNT(*) AS violation_count
FROM validation_failures
GROUP BY rule_id, severity
ORDER BY violation_count DESC;

-- 9. Stock Price Volatility & 60-Day High/Low
SELECT 
    c.ticker, c.company_name,
    ROUND(MIN(sp.close_price), 2) AS low_price_60d,
    ROUND(MAX(sp.close_price), 2) AS high_price_60d,
    ROUND(AVG(sp.close_price), 2) AS avg_price_60d
FROM companies c
JOIN stock_prices sp ON c.company_id = sp.company_id
GROUP BY c.company_id;

-- 10. Overall Database Table Summary & Row Counts
SELECT 
    table_name, rows_loaded, rows_rejected, load_timestamp
FROM data_audit
ORDER BY rows_loaded DESC;
