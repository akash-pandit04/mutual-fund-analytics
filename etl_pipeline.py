"""
etl_pipeline.py - ETL Pipeline (CSV → SQLite)
===============================================
Loads all raw CSV files from data/raw/ into a single SQLite database
at data/processed/database.db. Cleans column names and normalizes
table names for downstream analytics and Power BI consumption.

Author: Akash Kumar Pandit
Date: August 2026
"""

import pandas as pd
import sqlite3
import os
import glob

def create_database(raw_dir='data/raw', db_path='data/processed/database.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    csv_files = glob.glob(os.path.join(raw_dir, '*.csv'))
    
    print(f"Loading {len(csv_files)} CSV files into SQLite database ({db_path})...")
    
    for file in csv_files:
        table_name = os.path.basename(file).replace('.csv', '')
        # Clean up table name (e.g., '01_fund_master' -> 'fund_master')
        if table_name[0].isdigit():
            table_name = table_name.split('_', 1)[1]
            
        print(f"Processing table: {table_name}")
        try:
            df = pd.read_csv(file)
            
            # Clean column names to be SQL friendly
            df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
            
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        except Exception as e:
            print(f"Failed to load {file}: {e}")
            
    conn.close()
    print("Database creation complete.")

if __name__ == "__main__":
    create_database()
