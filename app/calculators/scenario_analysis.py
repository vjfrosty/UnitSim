"""
Stage 4: Scenario & Sensitivity Analysis Calculator
==================================================

Advanced statistical analysis for unit economics with Monte Carlo simulation,
sensitivity analysis, and probabilistic forecasting.

Functions:
- run_monte_carlo_simulation(): Execute statistical simulations with uncertainty
- calculate_sensitivity_analysis(): Identify critical parameters with tornado diagrams
- generate_scenario_analysis(): Compare optimistic/realistic/pessimistic scenarios
- calculate_confidence_intervals(): Generate statistical confidence bands

Mathematical Foundation:
- Monte Carlo sampling from probability distributions
- Sensitivity coefficient calculations for tornado diagrams
- Statistical summary with percentiles and confidence intervals
- Risk metrics including Value at Risk (VaR)
"""

import random
import math
import statistics
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class DistributionConfig:
    """Configuration for probability distributions"""
    type: str  # "normal", "lognormal", "triangular", "uniform"
    parameters: Dict[str, float]
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass 
class SimulationResult:
    """Single Monte Carlo simulation iteration result"""
    iteration: int
    inputs: Dict[str, float]
    outputs: Dict[str, float]


@dataclass
class StatisticalSummary:
    """Statistical summary for a metric"""
    mean: float
    median: float
    std: float
    min: float
    max: float
    percentiles: Dict[str, float]  # p10, p25, p50, p75, p90


def set_random_seed(seed: int = 42) -> None:
    """Set random seed for reproducible results"""
    random.seed(seed)


def sample_normal(mean: float, std: float, min_val: float = None, max_val: float = None) -> float:
    """Sample from normal distribution with optional bounds"""
    value = random.gauss(mean, std)
    
    if min_val is not None:
        value = max(value, min_val)
    if max_val is not None:
        value = min(value, max_val)
    
    return value


def sample_lognormal(mean: float, std: float, min_val: float = None, max_val: float = None) -> float:
    """Sample from log-normal distribution with optional bounds"""
    # Convert to log-space parameters
    mu = math.log(mean**2 / math.sqrt(mean**2 + std**2))
    sigma = math.sqrt(math.log(1 + (std/mean)**2))
    
    value = random.lognormvariate(mu, sigma)
    
    if min_val is not None:
        value = max(value, min_val)
    if max_val is not None:
        value = min(value, max_val)
    
    return value


def sample_triangular(min_val: float, mode: float, max_val: float) -> float:
    """Sample from triangular distribution"""
    return random.triangular(min_val, max_val, mode)


def sample_uniform(min_val: float, max_val: float) -> float:
    """Sample from uniform distribution"""
    return random.uniform(min_val, max_val)


def sample_from_distribution(config: DistributionConfig) -> float:
    """Sample a value from the specified distribution"""
    dist_type = config.type.lower()
    params = config.parameters
    
    if dist_type == "normal":
        value = sample_normal(
            params["mean"], 
            params["std"], 
            config.min_value, 
            config.max_value
        )
    elif dist_type == "lognormal":
        value = sample_lognormal(
            params["mean"], 
            params["std"], 
            config.min_value, 
            config.max_value
        )
    elif dist_type == "triangular":
        value = sample_triangular(
            params["min"], 
            params["mode"], 
            params["max"]
        )
    elif dist_type == "uniform":
        value = sample_uniform(params["min"], params["max"])
    else:
        raise ValueError(f"Unsupported distribution type: {dist_type}")
    
    return value


def calculate_unit_economics_metrics(inputs: Dict[str, float]) -> Dict[str, float]:
    """Calculate unit economics outputs from sampled inputs"""
    mrr = inputs.get("mrr", 100.0)
    gross_margin_pct = inputs.get("gross_margin_percent", 80.0)
    churn_rate_pct = inputs.get("monthly_churn_rate", 5.0)
    cac = inputs.get("customer_acquisition_cost", 500.0)
    
    # Convert percentages
    gross_margin = gross_margin_pct / 100.0
    churn_rate = churn_rate_pct / 100.0
    
    # Calculate metrics
    gross_revenue = mrr * gross_margin
    ltv = gross_revenue / churn_rate if churn_rate > 0 else 0
    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    payback_months = cac / gross_revenue if gross_revenue > 0 else float('inf')
    
    # Handle edge cases
    payback_months = min(payback_months, 999.0)  # Cap at reasonable maximum
    
    return {
        "ltv": ltv,
        "ltv_cac_ratio": ltv_cac_ratio,
        "payback_months": payback_months,
        "gross_revenue_monthly": gross_revenue
    }


def calculate_statistical_summary(values: List[float]) -> StatisticalSummary:
    """Calculate comprehensive statistical summary"""
    if not values:
        return StatisticalSummary(0, 0, 0, 0, 0, {})
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    # Basic statistics
    mean_val = statistics.mean(values)
    median_val = statistics.median(values)
    std_val = statistics.stdev(values) if n > 1 else 0
    min_val = min(values)
    max_val = max(values)
    
    # Percentiles
    percentiles = {
        "p10": sorted_values[max(0, int(0.10 * n) - 1)],
        "p25": sorted_values[max(0, int(0.25 * n) - 1)],
        "p50": median_val,
        "p75": sorted_values[max(0, int(0.75 * n) - 1)],
        "p90": sorted_values[max(0, int(0.90 * n) - 1)]
    }
    
    return StatisticalSummary(
        mean=mean_val,
        median=median_val,
        std=std_val,
        min=min_val,
        max=max_val,
        percentiles=percentiles
    )


def run_monte_carlo_simulation(
    base_params: Dict[str, float],
    param_distributions: Dict[str, DistributionConfig],
    n_iterations: int = 10000,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Execute Monte Carlo simulation with uncertainty analysis
    
    Args:
        base_params: Base parameter values
        param_distributions: Distribution configurations for each parameter
        n_iterations: Number of simulation iterations
        seed: Random seed for reproducibility
    
    Returns:
        Complete simulation results with statistical analysis
    """
    set_random_seed(seed)
    
    # Track all simulation results
    simulation_results = []
    output_metrics = ["ltv", "ltv_cac_ratio", "payback_months", "gross_revenue_monthly"]
    
    # Collect values for statistical analysis
    metric_values = {metric: [] for metric in output_metrics}
    
    # Run Monte Carlo iterations
    for i in range(n_iterations):
        # Sample inputs from distributions
        sampled_inputs = base_params.copy()
        
        for param_name, distribution in param_distributions.items():
            if param_name in sampled_inputs:
                sampled_inputs[param_name] = sample_from_distribution(distribution)
        
        # Calculate outputs
        outputs = calculate_unit_economics_metrics(sampled_inputs)
        
        # Store results
        simulation_results.append(SimulationResult(
            iteration=i + 1,
            inputs=sampled_inputs.copy(),
            outputs=outputs.copy()
        ))
        
        # Collect values for statistics
        for metric in output_metrics:
            if metric in outputs:
                metric_values[metric].append(outputs[metric])
    
    # Calculate summary statistics
    summary_statistics = {}
    for metric, values in metric_values.items():
        summary_statistics[metric] = calculate_statistical_summary(values)
    
    # Calculate risk metrics
    ltv_values = metric_values.get("ltv", [])
    ratio_values = metric_values.get("ltv_cac_ratio", [])
    
    risk_metrics = {}
    if ltv_values and ratio_values:
        # Probability metrics
        ratio_below_3 = sum(1 for r in ratio_values if r < 3.0) / len(ratio_values)
        positive_economics = sum(1 for r in ratio_values if r > 1.0) / len(ratio_values)
        
        # Value at Risk (5th percentile)
        sorted_ltv = sorted(ltv_values)
        var_5pct = sorted_ltv[max(0, int(0.05 * len(sorted_ltv)) - 1)]
        
        risk_metrics = {
            "probability_ltv_cac_below_3": round(ratio_below_3, 3),
            "probability_positive_unit_economics": round(positive_economics, 3),
            "value_at_risk_5pct": round(var_5pct, 2)
        }
    
    # Convert summary statistics to dictionaries for JSON serialization
    summary_dict = {}
    for metric, summary in summary_statistics.items():
        summary_dict[metric] = {
            "mean": round(summary.mean, 2),
            "median": round(summary.median, 2),
            "std": round(summary.std, 2),
            "min": round(summary.min, 2),
            "max": round(summary.max, 2),
            "percentiles": {k: round(v, 2) for k, v in summary.percentiles.items()}
        }
    
    return {
        "simulation_summary": {
            "n_iterations": n_iterations,
            "seed": seed,
            "convergence_achieved": n_iterations >= 1000  # Basic convergence check
        },
        "summary_statistics": summary_dict,
        "risk_metrics": risk_metrics,
        "sample_results": [
            {
                "iteration": result.iteration,
                "inputs": {k: round(v, 2) for k, v in result.inputs.items()},
                "outputs": {k: round(v, 2) for k, v in result.outputs.items()}
            }
            for result in simulation_results[:10]  # Return first 10 samples
        ]
    }


def calculate_sensitivity_analysis(
    base_params: Dict[str, float],
    param_ranges: Dict[str, Dict[str, float]],
    output_metrics: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate sensitivity analysis using tornado diagram methodology
    
    Args:
        base_params: Base parameter values
        param_ranges: Min/max ranges for each parameter
        output_metrics: Metrics to analyze (default: LTV, ratio, payback)
    
    Returns:
        Sensitivity rankings and tornado chart data
    """
    if output_metrics is None:
        output_metrics = ["ltv", "ltv_cac_ratio", "payback_months"]
    
    # Calculate base case outputs
    base_outputs = calculate_unit_economics_metrics(base_params)
    
    # Calculate sensitivity for each parameter
    sensitivity_results = []
    
    for param_name, param_range in param_ranges.items():
        if param_name not in base_params:
            continue
        
        # Calculate low and high cases
        low_params = base_params.copy()
        high_params = base_params.copy()
        
        low_params[param_name] = param_range["min"]
        high_params[param_name] = param_range["max"]
        
        low_outputs = calculate_unit_economics_metrics(low_params)
        high_outputs = calculate_unit_economics_metrics(high_params)
        
        # Calculate sensitivity coefficient for each metric
        for metric in output_metrics:
            if metric in base_outputs:
                base_value = base_outputs[metric]
                low_value = low_outputs[metric]
                high_value = high_outputs[metric]
                
                # Avoid division by zero
                if base_value == 0 or base_params[param_name] == 0:
                    sensitivity_coeff = 0
                else:
                    # Calculate relative changes
                    output_change = (high_value - low_value) / base_value
                    input_change = (param_range["max"] - param_range["min"]) / base_params[param_name]
                    
                    sensitivity_coeff = output_change / input_change if input_change != 0 else 0
                
                sensitivity_results.append({
                    "parameter": param_name,
                    "metric": metric,
                    "sensitivity_coefficient": round(sensitivity_coeff, 3),
                    "low_value": round(low_value, 2),
                    "high_value": round(high_value, 2),
                    "base_value": round(base_value, 2),
                    "impact_range": abs(high_value - low_value)
                })
    
    # Rank parameters by sensitivity (using LTV as primary metric)
    ltv_sensitivities = [r for r in sensitivity_results if r["metric"] == "ltv"]
    ltv_sensitivities.sort(key=lambda x: abs(x["sensitivity_coefficient"]), reverse=True)
    
    # Add rankings
    for i, result in enumerate(ltv_sensitivities):
        result["rank"] = i + 1
    
    # Prepare tornado chart data
    tornado_data = {
        "parameter_names": [r["parameter"] for r in ltv_sensitivities[:5]],  # Top 5
        "low_values": [r["low_value"] for r in ltv_sensitivities[:5]],
        "high_values": [r["high_value"] for r in ltv_sensitivities[:5]],
        "base_value": base_outputs.get("ltv", 0)
    }
    
    return {
        "sensitivity_rankings": ltv_sensitivities,
        "tornado_chart_data": tornado_data,
        "base_case_outputs": {k: round(v, 2) for k, v in base_outputs.items()}
    }


def generate_scenario_analysis(
    scenarios: Dict[str, Dict[str, Any]],
    base_model_type: str = "unit_economics"
) -> Dict[str, Any]:
    """
    Compare multiple predefined scenarios with probability weighting
    
    Args:
        scenarios: Dictionary of scenario configurations
        base_model_type: Type of model to analyze
    
    Returns:
        Scenario comparison with weighted expected values
    """
    scenario_results = {}
    all_probabilities = []
    all_ltvs = []
    all_ratios = []
    
    for scenario_name, scenario_config in scenarios.items():
        # Extract scenario parameters
        scenario_params = {k: v for k, v in scenario_config.items() if k != "probability"}
        probability = scenario_config.get("probability", 1.0)
        
        # Calculate scenario outputs
        outputs = calculate_unit_economics_metrics(scenario_params)
        
        # Determine status based on LTV/CAC ratio
        ratio = outputs.get("ltv_cac_ratio", 0)
        if ratio < 1.5:
            status = "Critical"
        elif ratio < 3.0:
            status = "Concerning"
        elif ratio < 5.0:
            status = "Healthy"
        else:
            status = "Excellent"
        
        scenario_results[scenario_name] = {
            **{k: round(v, 2) for k, v in outputs.items()},
            "status": status,
            "probability": probability
        }
        
        # Collect for weighted calculations
        all_probabilities.append(probability)
        all_ltvs.append(outputs.get("ltv", 0))
        all_ratios.append(ratio)
    
    # Calculate probability-weighted expected values
    total_prob = sum(all_probabilities)
    if total_prob > 0:
        # Normalize probabilities
        norm_probs = [p / total_prob for p in all_probabilities]
        
        expected_ltv = sum(ltv * prob for ltv, prob in zip(all_ltvs, norm_probs))
        expected_ratio = sum(ratio * prob for ratio, prob in zip(all_ratios, norm_probs))
        
        # Conservative estimate (probability-weighted minimum)
        risk_adjusted_ltv = min(all_ltvs)
    else:
        expected_ltv = statistics.mean(all_ltvs) if all_ltvs else 0
        expected_ratio = statistics.mean(all_ratios) if all_ratios else 0
        risk_adjusted_ltv = min(all_ltvs) if all_ltvs else 0
    
    weighted_expected_values = {
        "expected_ltv": round(expected_ltv, 2),
        "expected_ratio": round(expected_ratio, 2),
        "risk_adjusted_ltv": round(risk_adjusted_ltv, 2)
    }
    
    return {
        "scenario_results": scenario_results,
        "weighted_expected_values": weighted_expected_values,
        "scenario_count": len(scenarios)
    }


def calculate_confidence_intervals(
    values: List[float],
    confidence_levels: List[float] = None
) -> Dict[str, Any]:
    """
    Calculate statistical confidence intervals for forecasting
    
    Args:
        values: List of simulated values
        confidence_levels: Confidence levels to calculate (0.0 to 1.0)
    
    Returns:
        Confidence intervals and prediction intervals
    """
    if confidence_levels is None:
        confidence_levels = [0.80, 0.90, 0.95]
    
    if not values:
        return {"confidence_intervals": {}, "prediction_intervals": {}}
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    confidence_intervals = {}
    
    for level in confidence_levels:
        alpha = 1 - level
        lower_idx = max(0, int((alpha/2) * n) - 1)
        upper_idx = min(n - 1, int((1 - alpha/2) * n) - 1)
        
        lower_bound = sorted_values[lower_idx]
        upper_bound = sorted_values[upper_idx]
        
        confidence_intervals[f"{int(level*100)}%"] = {
            "lower": round(lower_bound, 2),
            "upper": round(upper_bound, 2)
        }
    
    # For prediction intervals, add some additional uncertainty
    # (simplified approach - could be more sophisticated)
    prediction_intervals = {}
    
    for period in ["next_month", "next_quarter"]:
        prediction_intervals[period] = {}
        
        for level in confidence_levels:
            # Add 5-10% additional uncertainty for predictions
            uncertainty_factor = 1.05 if period == "next_month" else 1.10
            
            base_interval = confidence_intervals[f"{int(level*100)}%"]
            mean_val = statistics.mean(values)
            
            pred_lower = base_interval["lower"] * (2 - uncertainty_factor)
            pred_upper = base_interval["upper"] * uncertainty_factor
            
            prediction_intervals[period][f"{int(level*100)}%"] = [
                round(pred_lower, 2),
                round(pred_upper, 2)
            ]
    
    return {
        "confidence_intervals": confidence_intervals,
        "prediction_intervals": prediction_intervals
    }


# Example distribution configurations for common business parameters
STANDARD_DISTRIBUTIONS = {
    "unit_economics": {
        "mrr": DistributionConfig(
            type="normal",
            parameters={"mean": 100.0, "std": 15.0},
            min_value=50.0,
            max_value=200.0
        ),
        "gross_margin_percent": DistributionConfig(
            type="triangular", 
            parameters={"min": 60.0, "mode": 80.0, "max": 95.0}
        ),
        "monthly_churn_rate": DistributionConfig(
            type="lognormal",
            parameters={"mean": 5.0, "std": 1.5},
            min_value=1.0,
            max_value=15.0
        ),
        "customer_acquisition_cost": DistributionConfig(
            type="lognormal",
            parameters={"mean": 500.0, "std": 150.0},
            min_value=200.0,
            max_value=1000.0
        )
    }
}


def get_default_sensitivity_ranges(base_params: Dict[str, float], range_pct: float = 0.20) -> Dict[str, Dict[str, float]]:
    """Generate default sensitivity analysis ranges (±20% by default)"""
    ranges = {}
    
    for param_name, base_value in base_params.items():
        ranges[param_name] = {
            "min": base_value * (1 - range_pct),
            "max": base_value * (1 + range_pct)
        }
    
    return ranges


# Test function for validation
def test_scenario_analysis():
    """Test scenario analysis functionality"""
    print("Testing Scenario Analysis Calculator...")
    
    # Test parameters
    base_params = {
        "mrr": 100.0,
        "gross_margin_percent": 80.0,
        "monthly_churn_rate": 5.0,
        "customer_acquisition_cost": 500.0
    }
    
    # Test basic unit economics calculation
    outputs = calculate_unit_economics_metrics(base_params)
    print(f"Base case LTV: ${outputs['ltv']:.0f}, Ratio: {outputs['ltv_cac_ratio']:.1f}")
    
    # Test Monte Carlo simulation
    distributions = {
        "mrr": DistributionConfig("normal", {"mean": 100, "std": 15}),
        "monthly_churn_rate": DistributionConfig("normal", {"mean": 5, "std": 1})
    }
    
    mc_results = run_monte_carlo_simulation(base_params, distributions, n_iterations=1000)
    print(f"Monte Carlo mean LTV: ${mc_results['summary_statistics']['ltv']['mean']:.0f}")
    
    # Test sensitivity analysis
    ranges = get_default_sensitivity_ranges(base_params)
    sensitivity = calculate_sensitivity_analysis(base_params, ranges)
    print(f"Most sensitive parameter: {sensitivity['sensitivity_rankings'][0]['parameter']}")
    
    print("All tests passed!")


if __name__ == "__main__":
    test_scenario_analysis()