"""
test_loader.py - 35 Unit Tests for ETL Loader & Normalisation
============================================================
Author: Akash Kumar Pandit
"""

import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.etl.normaliser import normalize_ticker, normalize_year, clean_financial_value
from src.etl.validator import DataQualityValidator

# Ticker Normalization Tests (10 tests)
def test_ticker_upper(): assert normalize_ticker("tcs") == "TCS"
def test_ticker_space(): assert normalize_ticker("infy ") == "INFY"
def test_ticker_special(): assert normalize_ticker("HDFC-BANK") == "HDFCBANK"
def test_ticker_dots(): assert normalize_ticker("B.S.E") == "BSE"
def test_ticker_none(): assert normalize_ticker(None) == ""
def test_ticker_num(): assert normalize_ticker("m500") == "M500"
def test_ticker_clean(): assert normalize_ticker("RELIANCE") == "RELIANCE"
def test_ticker_symbol(): assert normalize_ticker("ITC@NSE") == "ITCNSE"
def test_ticker_int(): assert normalize_ticker(123) == ""
def test_ticker_empty(): assert normalize_ticker("") == ""

# Year Normalization Tests (10 tests)
def test_year_str(): assert normalize_year("2024") == 2024
def test_year_fy(): assert normalize_year("FY24") == 2024
def test_year_float(): assert normalize_year(2024.0) == 2024
def test_year_int(): assert normalize_year(2023) == 2023
def test_year_fy_full(): assert normalize_year("FY2022") == 2022
def test_year_none(): assert normalize_year(None) is None
def test_year_dash(): assert normalize_year("2021-22") == 2021
def test_year_space(): assert normalize_year(" 2020 ") == 2020
def test_year_short(): assert normalize_year("19") == 2019
def test_year_invalid(): assert normalize_year("ABCD") is None

# Value Cleaning Tests (10 tests)
def test_clean_val_float(): assert clean_financial_value(100.5) == 100.5
def test_clean_val_str(): assert clean_financial_value("1,500.25") == 1500.25
def test_clean_val_dash(): assert clean_financial_value("-") == 0.0
def test_clean_val_none(): assert clean_financial_value(None) == 0.0
def test_clean_val_nan(): assert clean_financial_value(float('nan')) == 0.0
def test_clean_val_int(): assert clean_financial_value(500) == 500.0
def test_clean_val_negative(): assert clean_financial_value("-250.0") == -250.0
def test_clean_val_space(): assert clean_financial_value("  10  ") == 10.0
def test_clean_val_empty(): assert clean_financial_value("") == 0.0
def test_clean_val_na(): assert clean_financial_value("N/A") == 0.0

# Validator Tests (5 tests)
def test_validator_company_fail():
    v = DataQualityValidator()
    v.validate_companies(pd.DataFrame([{'company_id': 1, 'ticker': '', 'company_name': 'Test'}]))
    assert len(v.failures) == 1
    assert v.failures[0]['rule_id'] == 'DQ-01'

def test_validator_pl_fail():
    v = DataQualityValidator()
    v.validate_profit_loss(pd.DataFrame([{'company_id': 1, 'year': 2024, 'revenue': -100, 'operating_expenses': 50, 'pat': 10}]))
    assert len(v.failures) == 1
    assert v.failures[0]['rule_id'] == 'DQ-03'

def test_validator_bs_fail():
    v = DataQualityValidator()
    v.validate_balance_sheet(pd.DataFrame([{'company_id': 1, 'year': 2024, 'total_assets': -500, 'total_liabilities': 100, 'total_shareholders_equity': 100}]))
    assert len(v.failures) == 1

def test_validator_stock_fail():
    v = DataQualityValidator()
    v.validate_stock_prices(pd.DataFrame([{'company_id': 1, 'date': '2024-01-01', 'close_price': -10.0}]))
    assert len(v.failures) == 1

def test_validator_pass():
    v = DataQualityValidator()
    v.validate_companies(pd.DataFrame([{'company_id': 1, 'ticker': 'TCS', 'company_name': 'TCS Ltd'}]))
    assert len(v.failures) == 0
