"""
data_ingestion.py - Data Loading, Exploration & Validation
===========================================================
Loads all CSV datasets from the raw data directory, prints shape/dtype/head
summaries, explores the fund_master dataset for unique categories, and
validates AMFI codes across fund_master and nav_history.

Author: Akash Kumar Pandit
Date: July 2026
"""

import pandas as pd
import os
import glob


def load_and_explore_datasets(data_dir='data/raw'):
    print(f"Exploring datasets in {data_dir}...")
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    if not csv_files:
        print("No CSV files found. Please place the 10 provided CSV datasets in data/raw/")
        return {}
    
    datasets = {}
    for file in csv_files:
        filename = os.path.basename(file)
        try:
            df = pd.read_csv(file)
            datasets[filename] = df
            print(f"\n--- {filename} ---")
            print(f"Shape: {df.shape}")
            print("\nDtypes:")
            print(df.dtypes)
            print("\nHead:")
            print(df.head())
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    return datasets

def explore_fund_master(datasets):
    # Try to find the fund master dataset
    master_file = next((f for f in datasets.keys() if 'master' in f.lower()), None)
    if not master_file:
        print("\nCould not identify fund_master dataset for exploration.")
        return
        
    df_master = datasets[master_file]
    print(f"\n--- Exploring Fund Master ({master_file}) ---")
    
    columns_of_interest = {
        'fund house': ['fund_house', 'fund house', 'amc', 'AMC_Name', 'Mutual_Fund_Family'],
        'category': ['category', 'scheme_category', 'Scheme_Category'],
        'sub-category': ['sub_category', 'sub-category', 'sub category', 'Scheme_Sub_Category'],
        'risk grade': ['risk_grade', 'risk grade', 'risk', 'Riskometer_Scheme']
    }
    
    for concept, possible_cols in columns_of_interest.items():
        found = False
        for col in possible_cols:
            if col in df_master.columns:
                print(f"\nUnique {concept}s:")
                print(df_master[col].unique())
                found = True
                break
        if not found:
            print(f"\nColumn for '{concept}' not found in {master_file}")
            
    # AMFI scheme code structure understanding would typically be inferred from the 'Scheme_Code' column if present
    code_cols = [c for c in df_master.columns if 'code' in c.lower() or 'amfi' in c.lower()]
    if code_cols:
        print(f"\nScheme code columns found: {code_cols}")
        for col in code_cols:
            print(f"Sample of {col}: {df_master[col].head().tolist()}")

def validate_amfi_codes(datasets):
    # Try to find fund master and nav history
    master_file = next((f for f in datasets.keys() if 'master' in f.lower()), None)
    nav_file = next((f for f in datasets.keys() if 'nav' in f.lower() and 'history' in f.lower()), None)
    
    if not master_file or not nav_file:
        print("\nNeed both fund_master and nav_history datasets to validate AMFI codes.")
        return
        
    df_master = datasets[master_file]
    df_nav = datasets[nav_file]
    
    # Try to identify scheme code columns
    master_code_col = next((c for c in df_master.columns if 'code' in c.lower() or 'amfi' in c.lower()), None)
    nav_code_col = next((c for c in df_nav.columns if 'code' in c.lower() or 'amfi' in c.lower()), None)
    
    if master_code_col and nav_code_col:
        master_codes = set(df_master[master_code_col].dropna().unique())
        nav_codes = set(df_nav[nav_code_col].dropna().unique())
        
        missing_in_nav = master_codes - nav_codes
        
        print("\n--- Data Quality Summary: AMFI Code Validation ---")
        print(f"Total unique codes in Fund Master: {len(master_codes)}")
        print(f"Total unique codes in NAV History: {len(nav_codes)}")
        
        if len(missing_in_nav) == 0:
            print("Validation PASSED: All codes in fund_master exist in nav_history.")
        else:
            print(f"Validation FAILED: {len(missing_in_nav)} codes from fund_master are missing in nav_history.")
            print(f"Sample missing codes: {list(missing_in_nav)[:5]}")
    else:
        print("\nCould not identify scheme code columns in the datasets.")

if __name__ == "__main__":
    datasets = load_and_explore_datasets()
    if datasets:
        explore_fund_master(datasets)
        validate_amfi_codes(datasets)
