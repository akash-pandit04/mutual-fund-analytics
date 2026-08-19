"""
cagr.py - CAGR Engine with 6 Edge Case Handlers
===============================================
Author: Akash Kumar Pandit
"""

import numpy as np

def calculate_cagr(start_val, end_val, periods=3):
    """
    Compute CAGR with 6 edge case flag categories:
    1. INSUFFICIENT
    2. ZERO_BASE
    3. BOTH_NEGATIVE
    4. TURNAROUND (Negative -> Positive)
    5. DECLINE_TO_LOSS (Positive -> Negative)
    6. NORMAL
    """
    if periods <= 0:
        return 0.0, "INSUFFICIENT"
    if start_val == 0:
        return 0.0, "ZERO_BASE"
    if start_val < 0 and end_val < 0:
        return 0.0, "BOTH_NEGATIVE"
    if start_val < 0 and end_val > 0:
        return 0.0, "TURNAROUND"
    if start_val > 0 and end_val < 0:
        return -100.0, "DECLINE_TO_LOSS"
    
    # Normal computation
    cagr_val = ((end_val / start_val) ** (1.0 / periods) - 1.0) * 100.0
    return cagr_val, "NORMAL"
