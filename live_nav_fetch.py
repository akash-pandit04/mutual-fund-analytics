"""
live_nav_fetch.py - Live NAV Data Fetcher
==========================================
Fetches real-time Net Asset Value (NAV) data for specified mutual fund
schemes from the mfapi.in public API and saves them as CSV files.

Author: Akash Kumar Pandit
Date: July 2026
"""

import requests
import pandas as pd
import os


def fetch_nav(scheme_code, save_dir='data/raw'):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'SUCCESS':
            df = pd.DataFrame(data['data'])
            # Add scheme metadata
            df['scheme_code'] = scheme_code
            df['scheme_name'] = data['meta']['scheme_name']
            
            # Ensure output directory exists
            os.makedirs(save_dir, exist_ok=True)
            
            # Save to CSV
            output_file = os.path.join(save_dir, f'nav_{scheme_code}.csv')
            df.to_csv(output_file, index=False)
            print(f"Successfully fetched and saved data for {scheme_code} - {data['meta']['scheme_name']}")
        else:
            print(f"Failed to fetch valid data for {scheme_code}: Status is not SUCCESS")
    else:
        print(f"API request failed for {scheme_code} with status code: {response.status_code}")

if __name__ == "__main__":
    # Key schemes to fetch as per Day 1 task
    schemes = [
        125497, # HDFC Top 100 Direct
        119551, # SBI Bluechip
        120503, # ICICI Bluechip
        118632, # Nippon Large Cap
        119092, # Axis Bluechip
        120841  # Kotak Bluechip
    ]
    
    print("Fetching live NAV data...")
    for code in schemes:
        fetch_nav(code)
    print("NAV data fetching complete.")
