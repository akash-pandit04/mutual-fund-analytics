"""
ratios.py - Profitability, Leverage, and Efficiency Ratios Engine
================================================================
Author: Akash Kumar Pandit
"""

import pandas as pd
import numpy as np

def calculate_profitability_ratios(revenue, pat, opm_percent, ebit, total_equity, total_assets):
    """Calculate Net Profit Margin, OPM, ROE, ROCE, ROA."""
    npm = (pat / revenue * 100.0) if revenue > 0 else 0.0
    opm = opm_percent
    roe = (pat / total_equity * 100.0) if total_equity > 0 else 0.0
    capital_employed = total_equity + (total_assets * 0.2)
    roce = (ebit / capital_employed * 100.0) if capital_employed > 0 else 0.0
    roa = (pat / total_assets * 100.0) if total_assets > 0 else 0.0
    return {
        'net_profit_margin_pct': npm,
        'opm_pct': opm,
        'roe_pct': roe,
        'roce_pct': roce,
        'roa_pct': roa
    }

def calculate_leverage_ratios(total_debt, total_equity, ebit, interest_expense):
    """Calculate Debt-to-Equity and Interest Coverage Ratio."""
    de = (total_debt / total_equity) if total_equity > 0 else 0.0
    icr = (ebit / interest_expense) if interest_expense > 0 else 999.0
    return {
        'debt_to_equity': de,
        'interest_coverage': icr
    }

def calculate_efficiency_ratios(revenue, total_assets):
    """Calculate Asset Turnover Ratio."""
    at = (revenue / total_assets) if total_assets > 0 else 0.0
    return {
        'asset_turnover': at
    }
