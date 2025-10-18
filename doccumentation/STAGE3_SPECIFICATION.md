# Stage 3: Freemium Funnel Analyzer - Technical Specification

**Project:** UnitSim - Unit Economics & Pricing Simulator MCP  
**Stage:** 3 - Freemium Funnel Analyzer  
**Start Date:** October 17, 2025  
**Target Completion:** 5-7 days

---

## 🎯 Overview

The Freemium Funnel Analyzer will track users through multiple conversion stages, from initial signup to paid conversion, providing insights into:
- Stage-by-stage conversion rates
- Drop-off analysis and bottleneck identification  
- Cohort survival modeling
- A/B test sample size calculations
- Revenue impact of funnel optimizations

---

## 🧮 Mathematical Foundation

### Core Conversion Chain Formula
```
Final Revenue = Visitors × C₁ × C₂ × C₃ × ... × Cₙ × ARPU
```

Where:
- `Visitors` = Initial funnel entry point
- `C₁, C₂, ... Cₙ` = Conversion rates between stages (0-1)
- `ARPU` = Average Revenue Per User (paid users)

### Funnel Stages (Configurable)
```
1. Visitor → Signup (Landing Page)
2. Signup → Activation (Onboarding)  
3. Activation → Engagement (Feature Usage)
4. Engagement → Trial (Premium Trial)
5. Trial → Conversion (Paid Subscription)
```

### Key Metrics Calculated

#### 1. Stage-by-Stage Analysis
```python
# Conversion rate between stages
stage_conversion_rate = users_next_stage / users_current_stage

# Cumulative conversion rate
cumulative_conversion = users_final_stage / users_initial_stage

# Drop-off rate
drop_off_rate = 1 - stage_conversion_rate

# Users lost at each stage
users_lost = users_current_stage - users_next_stage
```

#### 2. Cohort Survival Analysis
```python
# Cohort survival function
S(t) = customers_active_at_time_t / initial_cohort_size

# Hazard rate (instantaneous churn probability)
h(t) = -dS(t)/dt / S(t)

# Expected customer lifetime
E[Lifetime] = ∫₀^∞ S(t) dt
```

#### 3. Revenue Impact Analysis
```python
# Revenue per funnel stage
stage_revenue = users_at_stage × conversion_rate × arpu

# Total funnel revenue
total_revenue = Σ(stage_revenue)

# Revenue impact of optimization
revenue_delta = (new_conversion_rate - old_conversion_rate) × users × arpu
```

#### 4. A/B Test Sample Size
```python
# Sample size for conversion rate test
n = 2 × (z_α/2 + z_β)² × p(1-p) / (p₁ - p₂)²

Where:
- z_α/2 = critical value for significance level
- z_β = critical value for power
- p = baseline conversion rate
- p₁, p₂ = conversion rates for variants
```

---

## 📊 Input Parameters

### Funnel Configuration
```json
{
  "funnel_name": "SaaS Freemium",
  "stages": [
    {
      "name": "Visitor",
      "description": "Landing page visitors"
    },
    {
      "name": "Signup", 
      "description": "Account registration",
      "conversion_rate": 0.15,
      "users": null  // calculated
    },
    {
      "name": "Activation",
      "description": "Completed onboarding", 
      "conversion_rate": 0.65,
      "users": null
    },
    {
      "name": "Engagement",
      "description": "Used core features",
      "conversion_rate": 0.45, 
      "users": null
    },
    {
      "name": "Trial",
      "description": "Started premium trial",
      "conversion_rate": 0.25,
      "users": null
    },
    {
      "name": "Conversion",
      "description": "Paid subscription",
      "conversion_rate": 0.18,
      "users": null
    }
  ],
  "initial_users": 10000,
  "arpu_monthly": 50,
  "time_period": "monthly"
}
```

### Analysis Parameters
```json
{
  "cohort_analysis": {
    "enabled": true,
    "time_periods": 12,  // months to track
    "retention_rates": [100, 85, 72, 63, 56, 50, 45, 42, 39, 37, 35, 33]
  },
  "ab_test": {
    "enabled": true,
    "baseline_conversion": 0.15,
    "target_conversion": 0.18, 
    "significance_level": 0.05,
    "statistical_power": 0.80
  }
}
```

---

## 🔧 Function Specifications

### 1. `calculate_funnel_metrics(stages, initial_users)`
**Purpose:** Calculate users and conversion rates through each funnel stage

**Input:**
- `stages`: List of funnel stages with conversion rates
- `initial_users`: Number of users entering the funnel

**Output:**
```python
{
  "stages": [
    {
      "name": "Visitor",
      "users_entering": 10000,
      "users_converting": 1500,
      "conversion_rate": 15.0,
      "drop_off_rate": 85.0,
      "cumulative_conversion": 15.0
    },
    # ... more stages
  ],
  "summary": {
    "total_stages": 5,
    "overall_conversion": 2.6,  // visitor to paid
    "total_revenue": 65000,
    "revenue_per_visitor": 6.50
  }
}
```

### 2. `analyze_cohort_survival(retention_rates, initial_cohort)`
**Purpose:** Model customer lifetime and churn patterns

**Input:**
- `retention_rates`: Monthly retention percentages
- `initial_cohort`: Starting cohort size

**Output:**
```python
{
  "cohort_data": [
    {"month": 0, "users": 1000, "retention": 100.0, "churn": 0.0},
    {"month": 1, "users": 850, "retention": 85.0, "churn": 15.0},
    # ... more months
  ],
  "lifetime_metrics": {
    "average_lifetime_months": 8.5,
    "median_lifetime_months": 6.2,
    "ltv": 425.0,
    "total_revenue": 425000
  }
}
```

### 3. `calculate_ab_test_size(baseline_rate, target_rate, alpha, power)`
**Purpose:** Determine required sample size for conversion rate tests

**Input:**
- `baseline_rate`: Current conversion rate (0-1)
- `target_rate`: Target conversion rate (0-1) 
- `alpha`: Significance level (default 0.05)
- `power`: Statistical power (default 0.80)

**Output:**
```python
{
  "sample_size_per_variant": 3841,
  "total_sample_size": 7682,
  "effect_size": 0.03,
  "relative_improvement": 20.0,
  "test_duration_days": 28,  // based on traffic
  "confidence_interval": [0.12, 0.21]
}
```

### 4. `optimize_funnel_bottlenecks(funnel_data, optimization_budget)`
**Purpose:** Identify highest-impact optimization opportunities

**Input:**
- `funnel_data`: Current funnel performance
- `optimization_budget`: Available resources/budget

**Output:**
```python
{
  "bottlenecks": [
    {
      "stage": "Signup",
      "current_conversion": 15.0,
      "revenue_impact_per_1pct": 5000,
      "optimization_difficulty": "Medium",
      "priority_score": 8.5
    },
    # ... more bottlenecks
  ],
  "recommendations": [
    {
      "stage": "Signup", 
      "improvement": "Reduce form fields",
      "expected_lift": "2-3%",
      "effort": "Low",
      "revenue_impact": 12500
    }
  ]
}
```

---

## 🎨 HTML Component Features

### Interactive Funnel Visualization
- **Sankey Diagram:** Visual flow of users through stages
- **Conversion Table:** Stage-by-stage breakdown with percentages
- **Revenue Waterfall:** Revenue contribution by stage
- **Bottleneck Highlighting:** Visual identification of drop-off points

### Cohort Analysis Dashboard  
- **Retention Curve:** Survival function over time
- **Cohort Heatmap:** Retention rates by month/cohort
- **LTV Distribution:** Customer lifetime value analysis
- **Churn Prediction:** Time-to-churn modeling

### A/B Test Calculator
- **Sample Size Calculator:** Interactive parameter adjustment
- **Statistical Power Analysis:** Power curves and effect sizes
- **Test Duration Estimator:** Based on traffic and conversions
- **Significance Testing:** Real-time results interpretation

---

## 📚 Implementation Plan

### Phase 3.1: Core Calculator (2 days)
- [x] Plan architecture and mathematical models
- [ ] Implement `calculators/freemium_funnel.py`
- [ ] Create funnel calculation functions
- [ ] Add input validation and error handling

### Phase 3.2: Advanced Analytics (2 days)
- [ ] Implement cohort survival analysis
- [ ] Add A/B test sample size calculations
- [ ] Create bottleneck identification logic
- [ ] Add revenue impact modeling

### Phase 3.3: MCP Integration (1 day)
- [ ] Create `analyze_freemium_funnel_tool()`
- [ ] Add tool to server.py with proper validation
- [ ] Format output with insights and recommendations
- [ ] Update module exports

### Phase 3.4: Visualization (2 days)
- [ ] Design interactive HTML component
- [ ] Create funnel flow visualization
- [ ] Add cohort analysis charts
- [ ] Implement A/B test calculator

### Phase 3.5: Testing & Deployment (1 day)
- [ ] Unit test all calculations
- [ ] Validate edge cases and error handling
- [ ] Integration test with MCP server
- [ ] Deploy and verify functionality

---

## 🎯 Success Criteria

- [ ] **Mathematical Accuracy:** All funnel formulas correct
- [ ] **Flexible Configuration:** Support 3-10 funnel stages  
- [ ] **Cohort Analysis:** Proper lifetime value calculations
- [ ] **A/B Testing:** Statistically valid sample sizes
- [ ] **Bottleneck Identification:** Actionable optimization insights
- [ ] **Interactive UI:** Visual funnel flow and analytics
- [ ] **MCP Integration:** Clean tool interface with validation
- [ ] **Performance:** Sub-second calculations for typical funnels

---

This specification provides the foundation for implementing a comprehensive freemium funnel analyzer that will help product managers optimize their conversion funnels and maximize revenue from freemium users.