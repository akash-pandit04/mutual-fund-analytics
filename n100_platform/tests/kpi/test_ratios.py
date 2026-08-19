"""
test_ratios.py - 20 Formula Unit Tests for Sprint 2 Ratio Engine
================================================================
Author: Akash Kumar Pandit
"""

import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.analytics.ratios import calculate_profitability_ratios, calculate_leverage_ratios, calculate_efficiency_ratios
from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import calculate_cashflow_kpis, classify_capital_allocation

# Profitability Tests (4 tests)
def test_npm():
    res = calculate_profitability_ratios(1000, 150, 25, 200, 500, 1000)
    assert res['net_profit_margin_pct'] == 15.0

def test_roe():
    res = calculate_profitability_ratios(1000, 100, 20, 150, 500, 1000)
    assert res['roe_pct'] == 20.0

def test_roce():
    res = calculate_profitability_ratios(1000, 100, 20, 140, 500, 1000)
    assert res['roce_pct'] == (140 / 700.0 * 100.0)

def test_roa():
    res = calculate_profitability_ratios(1000, 100, 20, 150, 500, 1000)
    assert res['roa_pct'] == 10.0

# Leverage & Efficiency Tests (4 tests)
def test_de_ratio():
    res = calculate_leverage_ratios(200, 500, 100, 20)
    assert res['debt_to_equity'] == 0.4

def test_icr():
    res = calculate_leverage_ratios(200, 500, 100, 20)
    assert res['interest_coverage'] == 5.0

def test_asset_turnover():
    res = calculate_efficiency_ratios(1500, 1000)
    assert res['asset_turnover'] == 1.5

def test_zero_equity_de():
    res = calculate_leverage_ratios(200, 0, 100, 20)
    assert res['debt_to_equity'] == 0.0

# CAGR Edge Case Tests (6 tests)
def test_cagr_normal():
    val, flag = calculate_cagr(100, 133.1, 3)
    assert abs(val - 10.0) < 0.1
    assert flag == "NORMAL"

def test_cagr_turnaround():
    val, flag = calculate_cagr(-50, 100, 3)
    assert flag == "TURNAROUND"

def test_cagr_decline_to_loss():
    val, flag = calculate_cagr(100, -50, 3)
    assert flag == "DECLINE_TO_LOSS"

def test_cagr_both_negative():
    val, flag = calculate_cagr(-100, -50, 3)
    assert flag == "BOTH_NEGATIVE"

def test_cagr_zero_base():
    val, flag = calculate_cagr(0, 100, 3)
    assert flag == "ZERO_BASE"

def test_cagr_insufficient():
    val, flag = calculate_cagr(100, 150, 0)
    assert flag == "INSUFFICIENT"

# Cash Flow & Capital Allocation Tests (6 tests)
def test_fcf():
    res = calculate_cashflow_kpis(500, 200, 300, 2000)
    assert res['fcf'] == 300.0

def test_cfo_quality():
    res = calculate_cashflow_kpis(450, 200, 300, 2000)
    assert res['cfo_quality_score'] == 1.5

def test_capex_intensity():
    res = calculate_cashflow_kpis(500, 200, 300, 2000)
    assert res['capex_intensity'] == 10.0

def test_alloc_expansion():
    label, desc = classify_capital_allocation(1000, 700, 0, -700)
    assert label == "AGGRESSIVE_EXPANSION"

def test_alloc_dividend():
    label, desc = classify_capital_allocation(1000, 100, -500, -100)
    assert label == "DIVIDEND_DISTRIBUTOR"

def test_alloc_distress():
    label, desc = classify_capital_allocation(-200, 50, 300, -50)
    assert label == "LIQUIDITY_DISTRESS"
