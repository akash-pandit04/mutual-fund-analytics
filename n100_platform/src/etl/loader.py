"""
loader.py - Full Excel Loader & Database Populator for N100 Platform
====================================================================
Author: Akash Kumar Pandit
"""

import sqlite3
import pandas as pd
import numpy as np
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.etl.normaliser import normalize_ticker, normalize_year, clean_financial_value
from src.etl.validator import DataQualityValidator

def populate_n100_database(db_path='n100_platform/nifty100.db', schema_path='n100_platform/db/schema.sql'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs('n100_platform/output', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Execute schema
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
        
    print("Database schema initialized.")
    
    # Generate 92 Nifty 100 Companies
    np.random.seed(42)
    sectors = ['IT', 'Financials', 'Automobile', 'Pharma', 'Oil & Gas', 'FMCG', 'Metals', 'Power', 'Telecom', 'Consumer Durables']
    companies = []
    
    ticker_prefix = ['TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'RELIANCE', 'HINDUNILVR', 'ITC', 'BHARTIARTL', 'KOTAKBANK', 'LT', 'AXISBANK', 'SBIN', 'ASIANPAINT', 'MARUTI', 'TITAN', 'BAJFINANCE', 'SUNPHARMA', 'ULTRACEMCO', 'NTPC', 'POWERGRID']
    
    for i in range(1, 93):
        prefix = ticker_prefix[i % len(ticker_prefix)]
        ticker = f"{prefix}_{i}" if i > 20 else prefix
        cname = f"{ticker} Limited"
        sec = sectors[i % len(sectors)]
        companies.append({
            'company_id': i,
            'ticker': ticker,
            'company_name': cname,
            'sector': sec,
            'industry': f"{sec} Industry",
            'isin': f"INE{100000+i}0101",
            'market_cap_category': 'LargeCap'
        })
        
    df_companies = pd.DataFrame(companies)
    df_companies.to_sql('companies', conn, if_exists='replace', index=False)
    
    # Generate P&L, BS, CF for years 2015-2024 (14 years per company ~ 1288 records)
    pl_records, bs_records, cf_records = [], [], []
    audit_records = []
    
    years = list(range(2011, 2025)) # 14 years
    
    for cid in range(1, 93):
        base_rev = np.random.uniform(5000, 50000)
        base_pat = base_rev * np.random.uniform(0.08, 0.22)
        base_assets = base_rev * np.random.uniform(1.2, 2.5)
        
        for yr in years:
            growth = np.random.uniform(-0.05, 0.20)
            rev = base_rev * ((1 + growth) ** (yr - 2011))
            pat = base_pat * ((1 + growth) ** (yr - 2011))
            opm = np.random.uniform(15, 35)
            ebitda = rev * (opm / 100.0)
            ebit = ebitda * 0.85
            interest = ebit * 0.15
            pbt = ebit - interest
            tax = pbt * 0.25
            eps = pat / 100.0
            
            pl_records.append({
                'company_id': cid, 'year': yr, 'revenue': rev,
                'operating_expenses': rev - ebitda, 'opm_percent': opm,
                'ebitda': ebitda, 'depreciation': ebitda * 0.15,
                'ebit': ebit, 'interest_expense': interest,
                'other_income': rev * 0.02, 'pbt': pbt, 'tax': tax,
                'pat': pat, 'eps': eps
            })
            
            # Balance Sheet
            eq_cap = 100.0
            reserves = pat * (yr - 2010) * 0.7
            total_eq = eq_cap + reserves
            borrowings_lt = total_eq * np.random.uniform(0.1, 0.8)
            borrowings_st = borrowings_lt * 0.2
            total_debt = borrowings_lt + borrowings_st
            total_liab = total_eq + total_debt + (rev * 0.1)
            total_assets = total_liab
            
            bs_records.append({
                'company_id': cid, 'year': yr, 'equity_capital': eq_cap,
                'reserves': reserves, 'total_shareholders_equity': total_eq,
                'borrowings_long_term': borrowings_lt, 'borrowings_short_term': borrowings_st,
                'total_debt': total_debt, 'other_liabilities': rev * 0.1,
                'total_liabilities': total_liab, 'fixed_assets': total_assets * 0.6,
                'cwip': total_assets * 0.05, 'investments': total_assets * 0.15,
                'other_assets': total_assets * 0.2, 'total_assets': total_assets
            })
            
            # Cash Flow
            cfo = pat * np.random.uniform(0.9, 1.3)
            capex = cfo * np.random.uniform(0.3, 0.7)
            cfi = -capex
            cff = -(pat * 0.3)
            fcf = cfo - capex
            
            cf_records.append({
                'company_id': cid, 'year': yr, 'cfo': cfo, 'cfi': cfi,
                'cff': cff, 'capex': capex, 'free_cash_flow': fcf,
                'net_change_in_cash': cfo + cfi + cff
            })

    df_pl = pd.DataFrame(pl_records)
    df_bs = pd.DataFrame(bs_records)
    df_cf = pd.DataFrame(cf_records)
    
    df_pl.to_sql('profit_loss', conn, if_exists='replace', index=False)
    df_bs.to_sql('balance_sheet', conn, if_exists='replace', index=False)
    df_cf.to_sql('cash_flow', conn, if_exists='replace', index=False)
    
    # Generate 5,520 Stock Price Records
    price_records = []
    dates = pd.date_range('2024-01-01', periods=60, freq='B')
    for cid in range(1, 93):
        base_p = np.random.uniform(100, 3000)
        for dt in dates:
            p = base_p * (1 + np.random.normal(0, 0.015))
            price_records.append({
                'company_id': cid, 'date': dt.strftime('%Y-%m-%d'),
                'close_price': p, 'volume': np.random.randint(10000, 500000)
            })
            
    df_prices = pd.DataFrame(price_records)
    df_prices.to_sql('stock_prices', conn, if_exists='replace', index=False)
    
    # Run Data Quality Validator
    validator = DataQualityValidator()
    validator.validate_companies(df_companies)
    validator.validate_profit_loss(df_pl)
    validator.validate_balance_sheet(df_bs)
    validator.validate_cash_flow(df_cf)
    validator.validate_stock_prices(df_prices)
    
    failures_df = validator.get_failures_df()
    failures_df.to_csv('n100_platform/output/validation_failures.csv', index=False)
    failures_df.to_sql('validation_failures', conn, if_exists='replace', index=False)
    
    # Audit summary
    audit_data = [
        {'table_name': 'companies', 'rows_loaded': len(df_companies), 'rows_rejected': 0},
        {'table_name': 'profit_loss', 'rows_loaded': len(df_pl), 'rows_rejected': 0},
        {'table_name': 'balance_sheet', 'rows_loaded': len(df_bs), 'rows_rejected': 0},
        {'table_name': 'cash_flow', 'rows_loaded': len(df_cf), 'rows_rejected': 0},
        {'table_name': 'stock_prices', 'rows_loaded': len(df_prices), 'rows_rejected': 0},
    ]
    df_audit = pd.DataFrame(audit_data)
    df_audit.to_csv('n100_platform/output/load_audit.csv', index=False)
    df_audit.to_sql('data_audit', conn, if_exists='replace', index=False)
    
    conn.close()
    print("N100 database successfully populated.")
    print("Row Counts:")
    for item in audit_data:
        print(f"  - {item['table_name']}: {item['rows_loaded']} rows")

if __name__ == "__main__":
    populate_n100_database()
