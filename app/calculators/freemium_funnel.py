"""
Freemium Funnel Analyzer
Analyze conversion funnels, cohort survival, and A/B test planning
"""

from typing import List, Dict, Any, Optional
import math


def calculate_funnel_metrics(
    stages: List[Dict[str, Any]], 
    initial_users: int
) -> Dict[str, Any]:
    """
    Calculate users and conversion rates through each funnel stage
    
    Args:
        stages: List of funnel stages with conversion rates
        initial_users: Number of users entering the funnel
        
    Returns:
        Dictionary with stage metrics and summary
    """
    
    funnel_results = []
    current_users = initial_users
    total_revenue = 0
    
    for i, stage in enumerate(stages):
        # Users entering this stage
        users_entering = current_users
        
        # Get conversion rate for this stage (last stage has no conversion)
        if i < len(stages) - 1:  # Not the last stage
            conversion_rate = stage.get('conversion_rate', 1.0)  # Default to 100% if not specified
        else:
            conversion_rate = 0  # Last stage doesn't convert anywhere
        
        # Calculate users converting to next stage
        users_converting = int(users_entering * conversion_rate)
        
        # Drop-off calculation
        drop_off_rate = (1 - conversion_rate) * 100 if conversion_rate > 0 else 0
        users_dropping_off = users_entering - users_converting
        
        # Cumulative conversion from start
        cumulative_conversion = (users_entering / initial_users) * 100 if initial_users > 0 else 0
        
        # Revenue calculation (if this is a paid stage)
        stage_revenue = 0
        if stage.get('generates_revenue', False) and 'arpu_monthly' in stage:
            stage_revenue = users_entering * stage['arpu_monthly']
            total_revenue += stage_revenue
        
        stage_result = {
            "stage_name": stage['name'],
            "stage_description": stage.get('description', ''),
            "users_entering": users_entering,
            "users_converting": users_converting,
            "users_dropping_off": users_dropping_off,
            "conversion_rate": conversion_rate * 100 if conversion_rate > 0 else 0,
            "drop_off_rate": drop_off_rate,
            "cumulative_conversion": cumulative_conversion,
            "stage_revenue": stage_revenue,
            "generates_revenue": stage.get('generates_revenue', False)
        }
        
        funnel_results.append(stage_result)
        current_users = users_converting
    
    # Calculate overall funnel metrics
    final_users = funnel_results[-1]['users_entering'] if funnel_results else 0
    overall_conversion = (final_users / initial_users) * 100 if initial_users > 0 else 0
    revenue_per_visitor = total_revenue / initial_users if initial_users > 0 else 0
    
    return {
        "stages": funnel_results,
        "summary": {
            "total_stages": len(stages),
            "initial_users": initial_users,
            "final_users": final_users,
            "overall_conversion": round(overall_conversion, 2),
            "total_revenue": round(total_revenue, 2),
            "revenue_per_visitor": round(revenue_per_visitor, 2),
            "biggest_drop_off": _find_biggest_drop_off(funnel_results)
        }
    }


def analyze_cohort_survival(
    retention_rates: List[float], 
    initial_cohort: int,
    arpu_monthly: float = 0
) -> Dict[str, Any]:
    """
    Model customer lifetime and churn patterns using retention rates
    
    Args:
        retention_rates: Monthly retention percentages (0-100)
        initial_cohort: Starting cohort size
        arpu_monthly: Average revenue per user per month
        
    Returns:
        Dictionary with cohort data and lifetime metrics
    """
    
    cohort_data = []
    total_revenue = 0
    user_months = 0  # For calculating average lifetime
    
    current_users = initial_cohort
    
    for month, retention_pct in enumerate(retention_rates):
        # Calculate users retained this month
        if month == 0:
            # First month is always 100% retention
            users_retained = current_users
            churn_rate = 0.0
        else:
            # Apply retention rate
            retention_decimal = retention_pct / 100.0
            users_retained = int(current_users * retention_decimal)
            churn_rate = 100.0 - retention_pct
        
        # Calculate revenue for this month
        monthly_revenue = users_retained * arpu_monthly
        total_revenue += monthly_revenue
        
        # Track user-months for lifetime calculation
        user_months += users_retained
        
        cohort_data.append({
            "month": month,
            "users_active": users_retained,
            "retention_rate": retention_pct,
            "churn_rate": churn_rate,
            "monthly_revenue": round(monthly_revenue, 2),
            "cumulative_revenue": round(total_revenue, 2)
        })
        
        current_users = users_retained
        
        # Stop if no users left
        if users_retained == 0:
            break
    
    # Calculate lifetime metrics
    average_lifetime_months = user_months / initial_cohort if initial_cohort > 0 else 0
    ltv = total_revenue / initial_cohort if initial_cohort > 0 else 0
    
    # Find median lifetime (50% retention point)
    median_lifetime = _calculate_median_lifetime(retention_rates)
    
    return {
        "cohort_data": cohort_data,
        "lifetime_metrics": {
            "initial_cohort_size": initial_cohort,
            "average_lifetime_months": round(average_lifetime_months, 1),
            "median_lifetime_months": round(median_lifetime, 1),
            "customer_ltv": round(ltv, 2),
            "total_cohort_revenue": round(total_revenue, 2),
            "months_tracked": len(cohort_data)
        }
    }


def calculate_ab_test_size(
    baseline_rate: float,
    target_rate: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> Dict[str, Any]:
    """
    Calculate required sample size for conversion rate A/B test
    
    Args:
        baseline_rate: Current conversion rate (0-1)
        target_rate: Target conversion rate (0-1)
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.80)
        
    Returns:
        Dictionary with sample size and test parameters
    """
    
    # Z-scores for significance and power
    z_alpha = 1.96 if alpha == 0.05 else 2.58  # 95% or 99% confidence
    z_beta = 0.84 if power == 0.80 else 1.28   # 80% or 90% power
    
    # Pooled probability
    p_pooled = (baseline_rate + target_rate) / 2
    
    # Effect size
    effect_size = abs(target_rate - baseline_rate)
    
    # Sample size calculation (per variant)
    numerator = 2 * (z_alpha + z_beta) ** 2 * p_pooled * (1 - p_pooled)
    denominator = effect_size ** 2
    
    sample_size_per_variant = math.ceil(numerator / denominator)
    total_sample_size = sample_size_per_variant * 2
    
    # Relative improvement
    relative_improvement = (target_rate - baseline_rate) / baseline_rate * 100
    
    # Confidence interval (approximate)
    margin_of_error = z_alpha * math.sqrt(target_rate * (1 - target_rate) / sample_size_per_variant)
    ci_lower = target_rate - margin_of_error
    ci_upper = target_rate + margin_of_error
    
    return {
        "sample_size_per_variant": sample_size_per_variant,
        "total_sample_size": total_sample_size,
        "baseline_conversion": round(baseline_rate * 100, 1),
        "target_conversion": round(target_rate * 100, 1),
        "effect_size": round(effect_size * 100, 2),
        "relative_improvement": round(relative_improvement, 1),
        "significance_level": alpha,
        "statistical_power": power,
        "confidence_interval": [round(ci_lower * 100, 1), round(ci_upper * 100, 1)]
    }


def identify_funnel_bottlenecks(
    funnel_data: Dict[str, Any],
    revenue_per_conversion: float = 50
) -> Dict[str, Any]:
    """
    Identify stages with highest optimization potential
    
    Args:
        funnel_data: Output from calculate_funnel_metrics
        revenue_per_conversion: Revenue gained per additional conversion
        
    Returns:
        Dictionary with bottleneck analysis and recommendations
    """
    
    stages = funnel_data['stages']
    bottlenecks = []
    
    for i, stage in enumerate(stages[:-1]):  # Exclude final stage
        # Calculate revenue impact of 1% improvement
        users_entering = stage['users_entering']
        improvement_users = users_entering * 0.01  # 1% improvement
        revenue_impact = improvement_users * revenue_per_conversion
        
        # Drop-off severity score (higher = worse)
        drop_off_rate = stage['drop_off_rate']
        severity_score = min(drop_off_rate / 10, 10)  # Scale 0-10
        
        # Priority score combines impact and severity
        priority_score = (revenue_impact / 1000) + severity_score  # Normalize revenue to thousands
        
        bottleneck = {
            "stage_name": stage['stage_name'],
            "current_conversion": stage['conversion_rate'],
            "drop_off_rate": drop_off_rate,
            "users_entering": users_entering,
            "revenue_impact_per_1pct": round(revenue_impact, 0),
            "severity_score": round(severity_score, 1),
            "priority_score": round(priority_score, 1)
        }
        
        bottlenecks.append(bottleneck)
    
    # Sort by priority score (highest first)
    bottlenecks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Generate recommendations for top bottlenecks
    recommendations = _generate_recommendations(bottlenecks[:3])
    
    return {
        "bottlenecks": bottlenecks,
        "top_bottleneck": bottlenecks[0] if bottlenecks else None,
        "total_optimization_potential": sum(b['revenue_impact_per_1pct'] for b in bottlenecks),
        "recommendations": recommendations
    }


def validate_funnel_inputs(stages: List[Dict[str, Any]], initial_users: int) -> tuple[bool, str]:
    """Validate freemium funnel inputs"""
    
    if not stages or len(stages) < 2:
        return False, "At least 2 funnel stages are required"
    
    if len(stages) > 10:
        return False, "Maximum 10 funnel stages allowed"
    
    if initial_users <= 0:
        return False, "Initial users must be positive"
    
    for i, stage in enumerate(stages):
        # Check required fields
        if 'name' not in stage:
            return False, f"Stage {i+1}: 'name' is required"
        
        # Check conversion rates (required for all stages except final)
        if i < len(stages) - 1:  # Not the final stage
            if 'conversion_rate' in stage:
                conversion_rate = stage['conversion_rate']
                if not 0 <= conversion_rate <= 1:
                    return False, f"Stage '{stage['name']}': conversion_rate must be between 0 and 1"
            # If no conversion_rate specified, that's OK - will be calculated or defaults to 0
    
    return True, ""


def _find_biggest_drop_off(stages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find the stage with the biggest drop-off rate"""
    if not stages:
        return {}
    
    biggest_drop_off = max(stages, key=lambda x: x['drop_off_rate'])
    return {
        "stage_name": biggest_drop_off['stage_name'],
        "drop_off_rate": biggest_drop_off['drop_off_rate'],
        "users_lost": biggest_drop_off['users_dropping_off']
    }


def _calculate_median_lifetime(retention_rates: List[float]) -> float:
    """Calculate median customer lifetime (50% retention point)"""
    for i, retention in enumerate(retention_rates):
        if retention <= 50:
            return i + (50 - retention) / (retention_rates[i-1] - retention) if i > 0 else 0
    return len(retention_rates)  # If never reaches 50%


def _generate_recommendations(top_bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate optimization recommendations for top bottlenecks"""
    
    recommendations = []
    
    stage_recommendations = {
        "visitor": "Improve landing page design and value proposition clarity",
        "signup": "Reduce friction in registration process, offer social login",
        "activation": "Streamline onboarding, show quick wins",
        "engagement": "Improve feature discovery and user guidance", 
        "trial": "Better trial experience and clear upgrade prompts",
        "conversion": "Optimize pricing page and reduce payment friction"
    }
    
    for bottleneck in top_bottlenecks:
        stage_name_lower = bottleneck['stage_name'].lower()
        
        # Match stage name to recommendation
        recommendation_text = "Optimize user experience and reduce friction"
        for key, rec in stage_recommendations.items():
            if key in stage_name_lower:
                recommendation_text = rec
                break
        
        recommendations.append({
            "stage": bottleneck['stage_name'],
            "current_conversion": bottleneck['current_conversion'],
            "recommendation": recommendation_text,
            "potential_impact": f"${bottleneck['revenue_impact_per_1pct']:,.0f} per 1% improvement",
            "priority": "High" if bottleneck['priority_score'] > 15 else "Medium"
        })
    
    return recommendations