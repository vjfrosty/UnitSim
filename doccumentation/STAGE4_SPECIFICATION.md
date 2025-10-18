# Stage 4: Scenario & Sensitivity Analysis - Technical Specification

**Project:** UnitSim - Unit Economics & Pricing Simulator MCP  
**Stage:** 4 - Scenario & Sensitivity Analysis  
**Start Date:** October 18, 2025  
**Target Completion:** 7-10 days  
**Complexity:** High

---

## 🎯 Overview

Stage 4 adds advanced statistical analysis to UnitSim through Monte Carlo simulation and sensitivity analysis. This enables users to:
- Model uncertainty in key business metrics
- Quantify risk and probability distributions  
- Identify most sensitive input parameters
- Generate confidence intervals and percentile forecasts
- Compare multiple scenarios with statistical rigor

---

## 🧮 Mathematical Foundation

### Monte Carlo Simulation Framework
```python
# Basic Monte Carlo loop
results = []
for i in range(n_simulations):
    # Sample from input distributions
    mrr = sample_normal(mrr_mean, mrr_std)
    churn = sample_lognormal(churn_mean, churn_std)
    
    # Calculate output metric
    ltv = (mrr * gross_margin) / churn
    results.append(ltv)

# Statistical analysis
confidence_intervals = percentile(results, [10, 50, 90])
```

### Sensitivity Analysis (Tornado Diagrams)
```python
# Sensitivity coefficient calculation
sensitivity = (ΔOutput / Output) / (ΔInput / Input)

# Where:
# ΔOutput = change in output metric
# ΔInput = change in input parameter  
# Higher |sensitivity| = more important parameter
```

### Statistical Distributions

#### Normal Distribution
```python
# For symmetric parameters (e.g., growth rates)
X ~ N(μ, σ²)
pdf(x) = (1/σ√2π) × e^(-½((x-μ)/σ)²)
```

#### Log-Normal Distribution  
```python
# For positive-only parameters (e.g., prices, costs)
X ~ LogNormal(μ, σ²)
pdf(x) = (1/xσ√2π) × e^(-½((ln(x)-μ)/σ)²)
```

#### Triangular Distribution
```python
# For bounded parameters with known min/max/mode
X ~ Triangular(a, b, c) where a ≤ c ≤ b
pdf(x) = 2(x-a)/((b-a)(c-a)) for a ≤ x ≤ c
```

---

## 📊 Input Parameter Specifications

### Parameter Configuration Structure
```json
{
  "parameter_name": "monthly_recurring_revenue",
  "display_name": "Monthly Recurring Revenue",
  "base_value": 100.0,
  "distribution": {
    "type": "normal",  // "normal", "lognormal", "triangular"
    "parameters": {
      "mean": 100.0,
      "std": 15.0
    }
  },
  "range": {
    "min": 50.0,
    "max": 200.0
  },
  "sensitivity_range": 0.20  // ±20% for sensitivity analysis
}
```

### Standard Business Parameter Distributions

#### Unit Economics Parameters
```json
{
  "mrr": {
    "distribution": "normal",
    "sensitivity_range": 0.15
  },
  "gross_margin_percent": {
    "distribution": "triangular", 
    "min": 60, "mode": 80, "max": 95
  },
  "monthly_churn_rate": {
    "distribution": "lognormal",
    "sensitivity_range": 0.25
  },
  "customer_acquisition_cost": {
    "distribution": "lognormal",
    "sensitivity_range": 0.30
  }
}
```

#### Pricing Tier Parameters
```json
{
  "tier_prices": {
    "distribution": "normal",
    "sensitivity_range": 0.20
  },
  "conversion_rates": {
    "distribution": "triangular",
    "sensitivity_range": 0.25
  },
  "customer_counts": {
    "distribution": "normal", 
    "sensitivity_range": 0.15
  }
}
```

#### Funnel Parameters
```json
{
  "funnel_conversion_rates": {
    "distribution": "triangular",
    "sensitivity_range": 0.30
  },
  "traffic_volume": {
    "distribution": "lognormal",
    "sensitivity_range": 0.25
  },
  "arpu": {
    "distribution": "normal",
    "sensitivity_range": 0.20
  }
}
```

---

## 🔧 Function Specifications

### 1. `run_monte_carlo_simulation(base_params, param_distributions, n_iterations)`
**Purpose:** Execute Monte Carlo simulation with statistical sampling

**Input:**
```python
base_params = {
    "mrr": 100,
    "gross_margin": 80, 
    "churn_rate": 5,
    "cac": 500
}

param_distributions = {
    "mrr": {"type": "normal", "mean": 100, "std": 15},
    "churn_rate": {"type": "lognormal", "mean": 5, "std": 1.2}
}

n_iterations = 10000
```

**Output:**
```python
{
  "simulation_results": [
    {"iteration": 1, "inputs": {...}, "outputs": {"ltv": 1580, "ratio": 3.16}},
    # ... n_iterations
  ],
  "summary_statistics": {
    "ltv": {
      "mean": 1600.0,
      "median": 1580.0, 
      "std": 245.0,
      "min": 980.0,
      "max": 2350.0,
      "percentiles": {
        "p10": 1280.0,
        "p25": 1450.0,
        "p50": 1580.0,
        "p75": 1750.0,
        "p90": 1920.0
      }
    },
    "ltv_cac_ratio": {
      "mean": 3.20,
      "median": 3.16,
      "std": 0.49,
      "percentiles": {...}
    }
  },
  "risk_metrics": {
    "probability_ltv_cac_below_3": 0.15,
    "probability_positive_unit_economics": 0.95,
    "value_at_risk_5pct": 1180.0  // 5% chance LTV below this
  }
}
```

### 2. `calculate_sensitivity_analysis(base_params, param_ranges, output_metrics)`
**Purpose:** Identify most sensitive input parameters using tornado diagram analysis

**Input:**
```python
base_params = {"mrr": 100, "churn_rate": 5, "cac": 500}
param_ranges = {
    "mrr": {"min": 85, "max": 115},           # ±15%
    "churn_rate": {"min": 4, "max": 6},       # ±20%
    "cac": {"min": 400, "max": 600}           # ±20%
}
output_metrics = ["ltv", "ltv_cac_ratio", "payback_months"]
```

**Output:**
```python
{
  "sensitivity_rankings": [
    {
      "parameter": "churn_rate",
      "sensitivity_coefficient": -2.8,  // negative = inverse relationship
      "impact_range": {"low": 1200, "high": 2100},
      "rank": 1
    },
    {
      "parameter": "cac", 
      "sensitivity_coefficient": -0.6,
      "impact_range": {"low": 2.67, "high": 4.0},
      "rank": 2
    },
    {
      "parameter": "mrr",
      "sensitivity_coefficient": 1.0,
      "impact_range": {"low": 1360, "high": 1840},
      "rank": 3
    }
  ],
  "tornado_chart_data": {
    "parameter_names": ["churn_rate", "cac", "mrr"],
    "low_values": [1200, 1467, 1360],
    "high_values": [2100, 1733, 1840],
    "base_value": 1600
  }
}
```

### 3. `generate_scenario_analysis(scenarios, base_model)`
**Purpose:** Compare multiple predefined scenarios (optimistic, realistic, pessimistic)

**Input:**
```python
scenarios = {
  "pessimistic": {
    "mrr": 80, "churn_rate": 8, "cac": 600,
    "probability": 0.2
  },
  "realistic": {
    "mrr": 100, "churn_rate": 5, "cac": 500,
    "probability": 0.6  
  },
  "optimistic": {
    "mrr": 130, "churn_rate": 3, "cac": 400,
    "probability": 0.2
  }
}
```

**Output:**
```python
{
  "scenario_results": {
    "pessimistic": {
      "ltv": 800, "ltv_cac_ratio": 1.33, "payback_months": 18.8,
      "status": "Critical", "probability": 0.2
    },
    "realistic": {
      "ltv": 1600, "ltv_cac_ratio": 3.20, "payback_months": 6.3,
      "status": "Healthy", "probability": 0.6
    },
    "optimistic": {
      "ltv": 3467, "ltv_cac_ratio": 8.67, "payback_months": 2.9,
      "status": "Excellent", "probability": 0.2
    }
  },
  "weighted_expected_values": {
    "expected_ltv": 1840.0,  // probability-weighted average
    "expected_ratio": 3.95,
    "risk_adjusted_ltv": 1600.0  // conservative estimate
  }
}
```

### 4. `calculate_confidence_intervals(simulation_results, confidence_levels)`
**Purpose:** Generate statistical confidence intervals for forecasting

**Input:**
```python
simulation_results = [1200, 1580, 1750, ...]  # Monte Carlo results
confidence_levels = [0.80, 0.90, 0.95]
```

**Output:**
```python
{
  "confidence_intervals": {
    "80%": {"lower": 1420, "upper": 1780},
    "90%": {"lower": 1350, "upper": 1850}, 
    "95%": {"lower": 1280, "upper": 1920}
  },
  "prediction_intervals": {
    "next_month": {"80%": [1400, 1800], "90%": [1320, 1880]},
    "next_quarter": {"80%": [1380, 1820], "90%": [1300, 1900]}
  }
}
```

---

## 🎨 HTML Component Features

### Monte Carlo Results Dashboard
- **Distribution Histograms:** Visual probability distributions for key metrics
- **Summary Statistics Table:** Mean, median, std dev, percentiles
- **Risk Metrics:** Probability of different outcomes
- **Confidence Intervals:** Visual bands for forecasting

### Tornado Diagram Visualization
- **Sensitivity Chart:** Horizontal bar chart showing parameter impact
- **Parameter Rankings:** Ordered list of most sensitive variables
- **Impact Quantification:** Numeric ranges for each parameter
- **Interactive Controls:** Adjust parameter ranges and see live updates

### Scenario Comparison
- **Side-by-side Comparison:** Pessimistic/Realistic/Optimistic scenarios
- **Probability Weighting:** Expected value calculations
- **Risk Assessment:** Color-coded status indicators
- **Decision Support:** Recommendations based on scenario analysis

### Statistical Outputs
- **Percentile Charts:** P10, P25, P50, P75, P90 visualizations
- **Value at Risk:** Downside risk quantification
- **Probability Tables:** Likelihood of achieving targets
- **Export Options:** Download results as CSV/JSON

---

## 📚 Implementation Plan

### Phase 4.1: Statistical Foundation (3 days)
- [x] Plan architecture and mathematical models
- [ ] Implement random number generation and distributions
- [ ] Create Monte Carlo simulation engine
- [ ] Add statistical summary functions

### Phase 4.2: Sensitivity Analysis (2 days)
- [ ] Implement tornado diagram calculations
- [ ] Add parameter sensitivity ranking
- [ ] Create scenario comparison logic
- [ ] Add confidence interval calculations

### Phase 4.3: MCP Integration (2 days)
- [ ] Create `scenario_analysis_tool()`
- [ ] Add tool to server.py with validation
- [ ] Format statistical outputs for readability
- [ ] Update module exports

### Phase 4.4: Visualization (2 days)
- [ ] Design interactive HTML component
- [ ] Create distribution charts and histograms
- [ ] Add tornado diagram visualization
- [ ] Implement scenario comparison interface

### Phase 4.5: Testing & Deployment (1 day)
- [ ] Validate statistical accuracy
- [ ] Test edge cases and performance
- [ ] Integration test with existing tools
- [ ] Deploy and verify functionality

---

## 🎯 Success Criteria

- [ ] **Monte Carlo Accuracy:** 10,000+ iteration simulations with proper convergence
- [ ] **Statistical Validity:** Correct confidence intervals and percentile calculations
- [ ] **Sensitivity Analysis:** Accurate tornado diagrams with parameter rankings
- [ ] **Performance:** Sub-10 second execution for typical simulations
- [ ] **Risk Metrics:** Probability calculations and value-at-risk quantification
- [ ] **Visualization:** Interactive charts and statistical summaries
- [ ] **Integration:** Seamless operation with Stages 1-3
- [ ] **Business Value:** Actionable insights for decision-making under uncertainty

---

This specification provides the foundation for implementing sophisticated scenario and sensitivity analysis capabilities that will help businesses make data-driven decisions under uncertainty.