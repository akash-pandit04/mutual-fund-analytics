"""
cashflow_kpis.py - Cash Flow KPIs & 8-Pattern Capital Allocation Classifier
==========================================================================
Author: Akash Kumar Pandit
"""

def calculate_cashflow_kpis(cfo, capex, pat, revenue):
    """Compute FCF, CFO Quality, CapEx Intensity, FCF Conversion."""
    fcf = cfo - capex
    cfo_quality = (cfo / pat) if pat > 0 else 0.0
    capex_intensity = (capex / revenue * 100.0) if revenue > 0 else 0.0
    fcf_conversion = (fcf / pat * 100.0) if pat > 0 else 0.0
    return {
        'fcf': fcf,
        'cfo_quality_score': cfo_quality,
        'capex_intensity': capex_intensity,
        'fcf_conversion_rate': fcf_conversion
    }

def classify_capital_allocation(cfo, capex, cff, cfi):
    """
    Classify company capital allocation into 1 of 8 distinct patterns:
    1. AGGRESSIVE_EXPANSION
    2. BALANCED_GROWTH
    3. CAPITAL_PRESERVATION
    4. DEBT_PAYDOWN
    5. DIVIDEND_DISTRIBUTOR
    6. ASSET_STRIPPING
    7. LIQUIDITY_DISTRESS
    8. STABLE_REINVESTMENT
    """
    if cfo > 0 and capex > (0.6 * cfo):
        return "AGGRESSIVE_EXPANSION", "Reinvesting >60% CFO into CapEx"
    elif cfo > 0 and capex > (0.3 * cfo) and cff < 0:
        return "BALANCED_GROWTH", "Reinvesting CFO while reducing debt/paying dividend"
    elif cfo > 0 and cff < -(0.4 * cfo):
        return "DIVIDEND_DISTRIBUTOR", "Distributing high cash to shareholders"
    elif cfo > 0 and capex < (0.2 * cfo):
        return "CAPITAL_PRESERVATION", "Low CapEx reinvestment, hoarding cash"
    elif cfo < 0 and cff > 0:
        return "LIQUIDITY_DISTRESS", "Negative CFO funded by debt/equity issuance"
    elif cfi > 0:
        return "ASSET_STRIPPING", "Selling fixed assets/investments for cash"
    elif cff < 0 and capex < (0.3 * cfo):
        return "DEBT_PAYDOWN", "Prioritizing debt repayment"
    else:
        return "STABLE_REINVESTMENT", "Steady operations and baseline reinvestment"
