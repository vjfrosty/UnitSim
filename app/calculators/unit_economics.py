"""Unit Economics Calculator"""

def calculate_ltv(mrr: float, gm: float, churn: float) -> float:
    gm_decimal = gm / 100.0
    churn_decimal = churn / 100.0
    if churn_decimal == 0:
        return float('inf')
    return round((mrr * gm_decimal) / churn_decimal, 2)

def calculate_unit_economics(mrr: float, gm: float, churn: float, cac: float):
    ltv = calculate_ltv(mrr, gm, churn)
    ratio = ltv / cac if cac > 0 else float('inf')
    
    monthly_margin = mrr * (gm / 100.0)
    payback = cac / monthly_margin if monthly_margin > 0 else float('inf')
    
    if ratio >= 3.0 and payback <= 12:
        status, color, msg = "Healthy", "green", "Strong unit economics"
    elif ratio >= 1.5 and payback <= 24:
        status, color, msg = "Warning", "yellow", "Needs improvement"
    else:
        status, color, msg = "Critical", "red", "Unsustainable"
    
    return {
        "ltv": round(ltv, 2),
        "cac": round(cac, 2),
        "ltv_cac_ratio": round(ratio, 2),
        "payback_months": round(payback, 1),
        "status": status,
        "status_color": color,
        "status_message": msg,
        "monthly_recurring_revenue": round(mrr, 2),
        "annual_recurring_revenue": round(mrr * 12, 2),
        "gross_margin_percent": round(gm, 1),
        "monthly_churn_rate": round(churn, 1),
        "customer_lifetime_months": round(1 / (churn / 100.0), 1) if churn > 0 else "∞",
        "monthly_margin_dollars": round(monthly_margin, 2)
    }

def validate_inputs(mrr: float, gm: float, churn: float, cac: float):
    if mrr <= 0:
        return False, "MRR must be positive"
    if gm < 0 or gm > 100:
        return False, "Gross Margin must be 0-100%"
    if churn < 0 or churn > 50:
        return False, "Churn must be 0-50%"
    if cac < 0:
        return False, "CAC must be non-negative"
    return True, ""
