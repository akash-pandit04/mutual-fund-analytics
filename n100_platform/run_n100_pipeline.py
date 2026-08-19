"""
run_n100_pipeline.py - N100 Master Pipeline Runner (Sprint 1 & Sprint 2)
========================================================================
Author: Akash Kumar Pandit
"""

import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.etl.loader import populate_n100_database
from src.analytics.ratios import calculate_profitability_ratios, calculate_leverage_ratios, calculate_efficiency_ratios
from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import calculate_cashflow_kpis, classify_capital_allocation

def run_full_n100_pipeline(db_path='n100_platform/nifty100.db'):
    print("=" * 60)
    print("  N100 FINANCIAL INTELLIGENCE PLATFORM — MASTER PIPELINE")
    print("=" * 60)
    
    # 1. Run Sprint 1: ETL & Database Population
    print("\n--- SPRINT 1: DATA FOUNDATION ---")
    populate_n100_database(db_path=db_path)
    
    # 2. Run Sprint 2: Financial Ratio Engine
    print("\n--- SPRINT 2: FINANCIAL RATIO ENGINE ---")
    conn = sqlite3.connect(db_path)
    
    pl_df = pd.read_sql("SELECT * FROM profit_loss", conn)
    bs_df = pd.read_sql("SELECT * FROM balance_sheet", conn)
    cf_df = pd.read_sql("SELECT * FROM cash_flow", conn)
    
    ratios_records = []
    alloc_records = []
    edge_logs = []
    
    for idx, row_pl in pl_df.iterrows():
        cid = row_pl['company_id']
        yr = row_pl['year']
        
        # Match BS & CF rows
        bs_match = bs_df[(bs_df['company_id'] == cid) & (bs_df['year'] == yr)]
        cf_match = cf_df[(cf_df['company_id'] == cid) & (cf_df['year'] == yr)]
        
        if bs_match.empty or cf_match.empty:
            continue
            
        row_bs = bs_match.iloc[0]
        row_cf = cf_match.iloc[0]
        
        # Ratios
        prof = calculate_profitability_ratios(
            row_pl['revenue'], row_pl['pat'], row_pl['opm_percent'],
            row_pl['ebit'], row_bs['total_shareholders_equity'], row_bs['total_assets']
        )
        lev = calculate_leverage_ratios(
            row_bs['total_debt'], row_bs['total_shareholders_equity'],
            row_pl['ebit'], row_pl['interest_expense']
        )
        eff = calculate_efficiency_ratios(row_pl['revenue'], row_bs['total_assets'])
        
        # CAGR (3-Year lookback)
        pl_past = pl_df[(pl_df['company_id'] == cid) & (pl_df['year'] == (yr - 3))]
        rev_cagr, cagr_flag = 0.0, "NORMAL"
        pat_cagr = 0.0
        eps_cagr = 0.0
        
        if not pl_past.empty:
            row_past = pl_past.iloc[0]
            rev_cagr, cagr_flag = calculate_cagr(row_past['revenue'], row_pl['revenue'], 3)
            pat_cagr, _ = calculate_cagr(row_past['pat'], row_pl['pat'], 3)
            eps_cagr, _ = calculate_cagr(row_past['eps'], row_pl['eps'], 3)
            
        if cagr_flag != "NORMAL":
            edge_logs.append(f"Company {cid} Year {yr}: CAGR Flag = {cagr_flag}")
            
        cf_kpis = calculate_cashflow_kpis(row_cf['cfo'], row_cf['capex'], row_pl['pat'], row_pl['revenue'])
        
        # Capital Allocation Classifier
        alloc_pattern, alloc_desc = classify_capital_allocation(row_cf['cfo'], row_cf['capex'], row_cf['cff'], row_cf['cfi'])
        
        ratios_records.append({
            'company_id': cid, 'year': yr,
            'net_profit_margin_pct': prof['net_profit_margin_pct'],
            'opm_pct': prof['opm_pct'],
            'roe_pct': prof['roe_pct'],
            'roce_pct': prof['roce_pct'],
            'roa_pct': prof['roa_pct'],
            'debt_to_equity': lev['debt_to_equity'],
            'interest_coverage': lev['interest_coverage'],
            'asset_turnover': eff['asset_turnover'],
            'revenue_cagr_3yr': rev_cagr,
            'pat_cagr_3yr': pat_cagr,
            'eps_cagr_3yr': eps_cagr,
            'cagr_flag': cagr_flag,
            'fcf': cf_kpis['fcf'],
            'cfo_quality_score': cf_kpis['cfo_quality_score'],
            'capex_intensity': cf_kpis['capex_intensity'],
            'fcf_conversion_rate': cf_kpis['fcf_conversion_rate']
        })
        
        alloc_records.append({
            'company_id': cid, 'year': yr,
            'pattern_label': alloc_pattern,
            'description': alloc_desc
        })

    df_ratios = pd.DataFrame(ratios_records)
    df_alloc = pd.DataFrame(alloc_records)
    
    df_ratios.to_sql('financial_ratios', conn, if_exists='replace', index=False)
    df_alloc.to_sql('capital_allocation', conn, if_exists='replace', index=False)
    
    # Save CSV deliverables
    df_alloc.to_csv('n100_platform/output/capital_allocation.csv', index=False)
    
    with open('n100_platform/output/ratio_edge_cases.log', 'w') as f:
        f.write("\n".join(edge_logs))
        
    conn.close()
    
    print("Financial Ratio Engine successfully populated.")
    print(f"  - Total Ratio Rows Populated: {len(df_ratios)}")
    print(f"  - Capital Allocation Labels Saved: {len(df_alloc)}")
    print(f"  - Ratio Edge Cases Logged: {len(edge_logs)}")
    print("=" * 60)

if __name__ == "__main__":
    run_full_n100_pipeline()
