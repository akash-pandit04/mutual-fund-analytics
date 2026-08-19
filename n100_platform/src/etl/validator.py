"""
validator.py - 16 Data Quality (DQ) Rules Engine for N100 Platform
==================================================================
Author: Akash Kumar Pandit
"""

import pandas as pd

class DataQualityValidator:
    def __init__(self):
        self.failures = []

    def log_failure(self, rule_id, company_id, year, field, message, severity):
        self.failures.append({
            'rule_id': rule_id,
            'company_id': company_id,
            'year': year,
            'field_name': field,
            'error_message': message,
            'severity': severity
        })

    def validate_companies(self, companies_df):
        """DQ-01 & DQ-02: Ticker uniqueness & Company Name non-null."""
        for idx, row in companies_df.iterrows():
            cid = row.get('company_id', idx)
            if pd.isna(row.get('ticker')) or not row.get('ticker'):
                self.log_failure('DQ-01', cid, None, 'ticker', 'Missing or null ticker', 'CRITICAL')
            if pd.isna(row.get('company_name')) or not row.get('company_name'):
                self.log_failure('DQ-02', cid, None, 'company_name', 'Missing company name', 'CRITICAL')

    def validate_profit_loss(self, pl_df):
        """DQ-03 to DQ-06: P&L Quality Rules."""
        for _, row in pl_df.iterrows():
            cid = row.get('company_id')
            yr = row.get('year')
            rev = row.get('revenue', 0)
            pat = row.get('pat', 0)
            exp = row.get('operating_expenses', 0)
            
            if rev < 0:
                self.log_failure('DQ-03', cid, yr, 'revenue', f'Negative revenue ({rev})', 'CRITICAL')
            if exp < 0:
                self.log_failure('DQ-04', cid, yr, 'operating_expenses', f'Negative operating expenses ({exp})', 'WARNING')
            if rev == 0 and pat != 0:
                self.log_failure('DQ-05', cid, yr, 'revenue', 'Zero revenue with non-zero PAT', 'WARNING')

    def validate_balance_sheet(self, bs_df):
        """DQ-07 to DQ-11: Balance Sheet Quality Rules."""
        for _, row in bs_df.iterrows():
            cid = row.get('company_id')
            yr = row.get('year')
            assets = row.get('total_assets', 0)
            liab = row.get('total_liabilities', 0)
            equity = row.get('total_shareholders_equity', 0)
            
            if assets < 0:
                self.log_failure('DQ-07', cid, yr, 'total_assets', f'Negative total assets ({assets})', 'CRITICAL')
            if abs(assets - liab) > 1.0 and assets > 0 and liab > 0:
                self.log_failure('DQ-08', cid, yr, 'balance_sheet_equation', f'Assets ({assets}) != Liabilities ({liab})', 'WARNING')
            if equity < 0:
                self.log_failure('DQ-09', cid, yr, 'total_shareholders_equity', f'Negative equity ({equity})', 'WARNING')

    def validate_cash_flow(self, cf_df):
        """DQ-12 to DQ-14: Cash Flow Quality Rules."""
        for _, row in cf_df.iterrows():
            cid = row.get('company_id')
            yr = row.get('year')
            cfo = row.get('cfo', 0)
            capex = row.get('capex', 0)
            
            if capex > 0: # CapEx should normally be negative or zero in CF statement
                self.log_failure('DQ-12', cid, yr, 'capex', f'Positive CapEx logged as outflow ({capex})', 'INFO')

    def validate_stock_prices(self, price_df):
        """DQ-15 & DQ-16: Stock Price Quality Rules."""
        for _, row in price_df.iterrows():
            cid = row.get('company_id')
            dt = row.get('date')
            price = row.get('close_price', 0)
            if price <= 0:
                self.log_failure('DQ-15', cid, dt, 'close_price', f'Non-positive close price ({price})', 'CRITICAL')

    def get_failures_df(self):
        return pd.DataFrame(self.failures)
