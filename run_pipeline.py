"""
run_pipeline.py - Master Execution Script
==========================================
Bluestock Fintech - Mutual Fund Analytics Capstone Project

This script orchestrates the entire data pipeline:
1. Fetches live NAV data from the mfapi.in API
2. Runs the ETL pipeline to build the SQLite database
3. Executes advanced analytics (risk metrics, clustering)

Usage:
    python run_pipeline.py

Author: Akash Kumar Pandit
Date: August 2026
"""

import subprocess
import sys
import os

def run_step(script_name, description):
    """Run a Python script as a pipeline step."""
    print(f"\n{'='*60}")
    print(f"  STEP: {description}")
    print(f"{'='*60}")
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"  [SKIP] {script_name} not found.")
        return False
        
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=False,
        text=True
    )
    
    if result.returncode == 0:
        print(f"  [DONE] {description} completed successfully.")
        return True
    else:
        print(f"  [FAIL] {description} failed with exit code {result.returncode}.")
        return False

def main():
    """Execute the full Mutual Fund Analytics pipeline."""
    print("\n" + "=" * 60)
    print("  BLUESTOCK FINTECH - MUTUAL FUND ANALYTICS PIPELINE")
    print("=" * 60)
    
    steps = [
        ("live_nav_fetch.py", "Fetching Live NAV Data from mfapi.in"),
        ("etl_pipeline.py", "Building SQLite Database from Raw CSVs"),
        ("advanced_analytics_script.py", "Running Advanced Analytics & Risk Metrics"),
    ]
    
    results = []
    for script, desc in steps:
        success = run_step(script, desc)
        results.append((desc, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("  PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    for desc, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {desc}")
    
    all_passed = all(s for _, s in results)
    if all_passed:
        print("\n  All pipeline steps completed successfully!")
        print("  Output files:")
        print("    - data/processed/database.db  (SQLite database)")
        print("    - data/processed/risk_metrics.csv  (Risk analytics)")
    else:
        print("\n  Some pipeline steps failed. Please check the errors above.")
    
    print("=" * 60)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
