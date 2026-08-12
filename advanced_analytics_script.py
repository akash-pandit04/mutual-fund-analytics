import pandas as pd
import numpy as np
import sqlite3
from sklearn.cluster import KMeans
import os
import warnings
warnings.filterwarnings('ignore')

def calculate_max_drawdown(series):
    cumulative_max = series.cummax()
    drawdown = (series - cumulative_max) / cumulative_max
    return drawdown.min()

def run_analytics():
    db_path = 'data/processed/database.db'
    if not os.path.exists(db_path):
        print("Database not found. Run ETL first.")
        return

    conn = sqlite3.connect(db_path)
    
    print("Loading data for analytics...")
    
    # We will try loading nav_history if it exists, otherwise use individual nav files
    try:
        nav_df = pd.read_sql("SELECT * FROM nav_history", conn)
    except:
        print("Warning: nav_history table not found, combining individual nav tables...")
        nav_tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'nav_%'").fetchall() if 'history' not in t[0]]
        df_list = []
        for t in nav_tables:
            df_list.append(pd.read_sql(f"SELECT * FROM {t}", conn))
        nav_df = pd.concat(df_list, ignore_index=True)
        
    nav_df['date'] = pd.to_datetime(nav_df['date'], dayfirst=True, errors='coerce')
    nav_df = nav_df.sort_values('date')
    
    bench_df = pd.read_sql("SELECT * FROM benchmark_indices WHERE index_name='NIFTY50'", conn)
    bench_df['date'] = pd.to_datetime(bench_df['date'], errors='coerce')
    bench_df = bench_df.sort_values('date')
    
    # Calculate daily returns for Nifty 50
    bench_df['bench_return'] = bench_df['close_value'].pct_change()
    bench_df = bench_df.dropna(subset=['bench_return'])
    
    metrics = []
    
    print("Calculating volatility, alpha, and beta...")
    # Analyze each fund
    scheme_code_col = 'amfi_code' if 'amfi_code' in nav_df.columns else 'scheme_code'
    
    for amfi_code, group in nav_df.groupby(scheme_code_col):
        if len(group) < 30: continue
        
        group = group.sort_values('date')
        group['daily_return'] = group['nav'].pct_change()
        
        # Volatility (Annualized standard deviation, assuming 252 trading days)
        std_dev = group['daily_return'].std() * np.sqrt(252)
        
        # Max Drawdown
        max_dd = calculate_max_drawdown(group['nav'])
        
        # SMA and EMA
        group['sma_30'] = group['nav'].rolling(window=30).mean()
        group['ema_30'] = group['nav'].ewm(span=30, adjust=False).mean()
        group['sma_90'] = group['nav'].rolling(window=90).mean()
        group['ema_90'] = group['nav'].ewm(span=90, adjust=False).mean()
        
        # Beta & Alpha calculation
        merged = pd.merge(group, bench_df[['date', 'bench_return']], on='date', how='inner').dropna(subset=['daily_return', 'bench_return'])
        if len(merged) > 30:
            cov = np.cov(merged['daily_return'], merged['bench_return'])[0, 1]
            var = np.var(merged['bench_return'])
            beta = cov / var if var != 0 else np.nan
            
            # Annualized returns
            fund_annual_ret = (1 + merged['daily_return'].mean())**252 - 1
            bench_annual_ret = (1 + merged['bench_return'].mean())**252 - 1
            risk_free_rate = 0.05 # Assumed 5% risk-free rate
            
            alpha = fund_annual_ret - (risk_free_rate + beta * (bench_annual_ret - risk_free_rate))
        else:
            beta, alpha = np.nan, np.nan
            
        scheme_name = group['scheme_name'].iloc[0] if 'scheme_name' in group.columns else f"Scheme {amfi_code}"
        
        metrics.append({
            'amfi_code': amfi_code,
            'scheme_name': scheme_name,
            'annualized_std_dev': std_dev,
            'max_drawdown': max_dd,
            'beta': beta,
            'alpha': alpha,
            'latest_nav': group['nav'].iloc[-1],
            'sma_30_latest': group['sma_30'].iloc[-1] if not group['sma_30'].isna().all() else np.nan,
            'ema_30_latest': group['ema_30'].iloc[-1] if not group['ema_30'].isna().all() else np.nan,
        })
        
    metrics_df = pd.DataFrame(metrics).dropna(subset=['annualized_std_dev', 'alpha'])
    
    print("Running K-Means Clustering...")
    if len(metrics_df) >= 3:
        features = metrics_df[['annualized_std_dev', 'alpha']]
        features_norm = (features - features.mean()) / features.std()
        
        kmeans = KMeans(n_clusters=3, random_state=42)
        metrics_df['cluster'] = kmeans.fit_predict(features_norm)
        
        cluster_centers = metrics_df.groupby('cluster')['annualized_std_dev'].mean().sort_values()
        risk_mapping = {
            cluster_centers.index[0]: 'Low Risk',
            cluster_centers.index[1]: 'Medium Risk',
            cluster_centers.index[2]: 'High Risk'
        }
        metrics_df['risk_profile'] = metrics_df['cluster'].map(risk_mapping)
    else:
        metrics_df['cluster'] = -1
        metrics_df['risk_profile'] = 'Unknown'
        
    os.makedirs('data/processed', exist_ok=True)
    out_path = 'data/processed/risk_metrics.csv'
    metrics_df.to_csv(out_path, index=False)
    print(f"Analytics complete. Output saved to {out_path}")
    
    metrics_df.to_sql('risk_metrics', conn, if_exists='replace', index=False)
    conn.close()

if __name__ == "__main__":
    run_analytics()
