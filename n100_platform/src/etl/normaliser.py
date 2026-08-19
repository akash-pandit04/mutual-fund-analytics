"""
normaliser.py - Data Normalization Functions for N100 Platform
=============================================================
Author: Akash Kumar Pandit
"""

import re
import pandas as pd

def normalize_ticker(ticker_raw):
    """Normalize company tickers to uppercase, alphanumeric format."""
    if not isinstance(ticker_raw, str):
        return ""
    clean = re.sub(r'[^A-Za-z0-9]', '', ticker_raw).upper()
    return clean

def normalize_year(year_val):
    """Normalize year representations (e.g., 'FY24', '2024.0', 2024) to integer 2024."""
    if pd.isna(year_val):
        return None
    val_str = str(year_val).upper().strip()
    match = re.search(r'\d{4}', val_str)
    if match:
        return int(match.group(0))
    match_short = re.search(r'\d{2}', val_str)
    if match_short:
        return 2000 + int(match_short.group(0))
    return None

def clean_financial_value(val):
    """Clean financial numbers, handling nulls, dashes, and strings."""
    if pd.isna(val) or val in ['-', '--', 'N/A', 'NaN', '']:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0
