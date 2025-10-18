"""
Pricing Tier Simulator
Compare multiple pricing tiers and calculate blended metrics
"""

from typing import List, Dict, Any


def calculate_tier_metrics(
    tier_name: str,
    price: float,
    expected_customers: int,
    conversion_rate: float,
    gross_margin_percent: float,
    monthly_churn_rate: float,
    cac: float
) -> Dict[str, Any]:
    """Calculate metrics for a single pricing tier"""
    
    # Monthly recurring revenue for this tier
    tier_mrr = price * expected_customers
    
    # Calculate LTV for this tier
    gross_margin = gross_margin_percent / 100.0
    churn_rate = monthly_churn_rate / 100.0
    
    if churn_rate > 0:
        ltv = (price * gross_margin) / churn_rate
        customer_lifetime_months = 1 / churn_rate
    else:
        ltv = float('inf')
        customer_lifetime_months = float('inf')
    
    # LTV/CAC ratio for this tier
    ltv_cac_ratio = ltv / cac if cac > 0 else float('inf')
    
    # Annual recurring revenue
    arr = tier_mrr * 12
    
    return {
        "tier_name": tier_name,
        "price": round(price, 2),
        "expected_customers": expected_customers,
        "conversion_rate": round(conversion_rate, 2),
        "monthly_mrr": round(tier_mrr, 2),
        "annual_arr": round(arr, 2),
        "ltv": round(ltv, 2) if ltv != float('inf') else "∞",
        "ltv_cac_ratio": round(ltv_cac_ratio, 2) if ltv_cac_ratio != float('inf') else "∞",
        "customer_lifetime_months": round(customer_lifetime_months, 1) if customer_lifetime_months != float('inf') else "∞",
        "gross_margin_percent": round(gross_margin_percent, 1),
        "monthly_churn_rate": round(monthly_churn_rate, 1),
        "cac": round(cac, 2)
    }


def simulate_pricing_tiers(
    tiers: List[Dict[str, Any]],
    gross_margin_percent: float,
    monthly_churn_rate: float
) -> Dict[str, Any]:
    """
    Simulate multiple pricing tiers and calculate blended metrics
    
    Args:
        tiers: List of tier dicts with {name, price, expected_customers, conversion_rate, cac}
        gross_margin_percent: Overall gross margin (0-100)
        monthly_churn_rate: Overall monthly churn rate (0-100)
    
    Returns:
        Dictionary with tier metrics and blended analysis
    """
    
    tier_results = []
    total_customers = 0
    total_mrr = 0
    total_arr = 0
    weighted_ltv_sum = 0
    weighted_cac_sum = 0
    
    for tier in tiers:
        tier_metrics = calculate_tier_metrics(
            tier_name=tier['name'],
            price=tier['price'],
            expected_customers=tier['expected_customers'],
            conversion_rate=tier.get('conversion_rate', 0),
            gross_margin_percent=gross_margin_percent,
            monthly_churn_rate=monthly_churn_rate,
            cac=tier.get('cac', 0)
        )
        
        tier_results.append(tier_metrics)
        
        # Accumulate for blended metrics
        customers = tier['expected_customers']
        total_customers += customers
        total_mrr += tier_metrics['monthly_mrr']
        total_arr += tier_metrics['annual_arr']
        
        # Weighted sums
        if tier_metrics['ltv'] != "∞":
            weighted_ltv_sum += tier_metrics['ltv'] * customers
        if tier_metrics['cac'] != "∞":
            weighted_cac_sum += tier_metrics['cac'] * customers
    
    # Calculate blended metrics
    blended_arpa = total_mrr / total_customers if total_customers > 0 else 0
    blended_ltv = weighted_ltv_sum / total_customers if total_customers > 0 else 0
    blended_cac = weighted_cac_sum / total_customers if total_customers > 0 else 0
    blended_ltv_cac_ratio = blended_ltv / blended_cac if blended_cac > 0 else 0
    
    # Find optimal tier (highest revenue)
    optimal_tier = max(tier_results, key=lambda x: x['monthly_mrr']) if tier_results else None
    
    # Revenue distribution
    revenue_distribution = [
        {
            "tier": t['tier_name'],
            "revenue": t['monthly_mrr'],
            "percentage": round((t['monthly_mrr'] / total_mrr * 100), 1) if total_mrr > 0 else 0
        }
        for t in tier_results
    ]
    
    return {
        "tiers": tier_results,
        "blended_metrics": {
            "total_customers": total_customers,
            "total_monthly_mrr": round(total_mrr, 2),
            "total_annual_arr": round(total_arr, 2),
            "blended_arpa": round(blended_arpa, 2),
            "blended_ltv": round(blended_ltv, 2),
            "blended_cac": round(blended_cac, 2),
            "blended_ltv_cac_ratio": round(blended_ltv_cac_ratio, 2),
            "gross_margin_percent": round(gross_margin_percent, 1),
            "monthly_churn_rate": round(monthly_churn_rate, 1)
        },
        "analysis": {
            "optimal_tier": optimal_tier['tier_name'] if optimal_tier else None,
            "optimal_tier_revenue": optimal_tier['monthly_mrr'] if optimal_tier else 0,
            "revenue_distribution": revenue_distribution
        }
    }


def validate_tier_inputs(tiers: List[Dict[str, Any]]) -> tuple[bool, str]:
    """Validate pricing tier inputs"""
    
    if not tiers or len(tiers) == 0:
        return False, "At least one tier is required"
    
    if len(tiers) > 10:
        return False, "Maximum 10 tiers allowed"
    
    for i, tier in enumerate(tiers):
        # Check required fields
        if 'name' not in tier:
            return False, f"Tier {i+1}: 'name' is required"
        if 'price' not in tier:
            return False, f"Tier {i+1}: 'price' is required"
        if 'expected_customers' not in tier:
            return False, f"Tier {i+1}: 'expected_customers' is required"
        
        # Validate values
        if tier['price'] < 0:
            return False, f"Tier '{tier['name']}': price must be non-negative"
        
        if tier['expected_customers'] < 0:
            return False, f"Tier '{tier['name']}': expected_customers must be non-negative"
        
        if 'conversion_rate' in tier and (tier['conversion_rate'] < 0 or tier['conversion_rate'] > 100):
            return False, f"Tier '{tier['name']}': conversion_rate must be 0-100%"
    
    return True, ""
