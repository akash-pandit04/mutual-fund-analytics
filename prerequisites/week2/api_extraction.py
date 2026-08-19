"""
api_extraction.py - REST API Data Extraction Script
===================================================
Fetches stock/market data from a public REST API, parses JSON, and saves to CSV.

Author: Akash Kumar Pandit
Date: August 2026
"""

import requests
import pandas as pd
import os

def extract_api_data(save_path='prerequisites/week2/api_extracted_data.csv'):
    # Using public CoinGecko / Market REST API for real-time crypto/fintech asset prices
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 25,
        'page': 1,
        'sparkline': 'false'
    }
    
    print("Fetching live asset price data from REST API...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        # Select relevant columns
        cols = ['id', 'symbol', 'name', 'current_price', 'market_cap', 'market_cap_rank', 'total_volume', 'high_24h', 'low_24h', 'price_change_percentage_24h']
        df_clean = df[cols]
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df_clean.to_csv(save_path, index=False)
        print(f"Data successfully extracted and saved to: {save_path}")
        print(df_clean.head())
    else:
        print(f"API Request failed with status code: {response.status_code}")

if __name__ == "__main__":
    extract_api_data()
