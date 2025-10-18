# UnitSim Usage Examples

This document provides practical examples of using the UnitSim MCP server calculators.

## Example 1: SaaS Startup - CAC/LTV Analysis

**Scenario**: A SaaS company wants to validate their unit economics before scaling marketing spend.

**Assumptions**:
- It costs $100 to acquire a customer through paid ads
- Average customer pays $50/month
- Average customer stays for 24 months
- Gross margin is 70% (after hosting/support costs)
- Monthly churn rate is 5%

**Input**:
```json
{
  "customerAcquisitionCost": 100,
  "averageRevenuePerUser": 50,
  "customerLifetimeMonths": 24,
  "grossMargin": 70,
  "monthlyChurnRate": 5
}
```

**Expected Output**:
- LTV: $840
- CAC:LTV Ratio: 0.12 (Excellent - well below the 0.33 threshold)
- Break-even: 2.9 months
- Payback Period: ~3 months considering churn
- Health Check: Excellent ✅

**Insights**: This company has strong unit economics and can confidently scale customer acquisition.

---

## Example 2: Mobile App - Freemium Funnel

**Scenario**: A mobile app wants to optimize their freemium conversion funnel.

**Assumptions**:
- 10,000 monthly visitors to the app store/website
- 10% of visitors download and sign up (free)
- 5% of free users convert to paid ($29/month)
- Marketing costs $0.50 per visitor
- Gross margin is 80%

**Input**:
```json
{
  "monthlyVisitors": 10000,
  "signupRate": 10,
  "freeToPayConversion": 5,
  "averageMonthlyRevenue": 29,
  "costPerVisitor": 0.50,
  "grossMargin": 80
}
```

**Expected Output**:
- Funnel: 10,000 visitors → 1,000 signups → 50 paying customers
- Monthly Revenue: $1,450
- Acquisition Cost: $5,000
- Net Profit: -$3,840 (not yet profitable)
- Break-even: Need ~21,552 visitors at current conversion rates

**Insights**: The funnel needs optimization. Options include:
1. Improve free-to-paid conversion (current 5% is low)
2. Reduce cost per visitor
3. Increase price or add premium tiers
4. Scale to break-even visitor volume

---

## Example 3: SaaS Platform - Pricing Tiers

**Scenario**: A B2B SaaS platform with three pricing tiers wants to forecast revenue and margins.

**Assumptions**:
- Basic tier: $10/month, expect 1,000 customers, costs $2/customer
- Pro tier: $50/month, expect 200 customers, costs $8/customer  
- Enterprise tier: $200/month, expect 50 customers, costs $30/customer
- Fixed costs: $5,000/month (team, infrastructure, etc.)

**Input**:
```json
{
  "tiers": [
    {
      "name": "Basic",
      "price": 10,
      "expectedCustomers": 1000,
      "costPerCustomer": 2
    },
    {
      "name": "Pro",
      "price": 50,
      "expectedCustomers": 200,
      "costPerCustomer": 8
    },
    {
      "name": "Enterprise",
      "price": 200,
      "expectedCustomers": 50,
      "costPerCustomer": 30
    }
  ],
  "fixedCosts": 5000
}
```

**Expected Output**:
- Total Revenue: $30,000
- Total Variable Costs: $3,600
- Total Profit: $21,400
- Profit Margin: 71%
- Revenue Distribution:
  - Basic: 33% of revenue, 80% of customers
  - Pro: 33% of revenue, 16% of customers
  - Enterprise: 33% of revenue, 4% of customers

**Insights**: 
- Strong margins and profitability
- Revenue is well-balanced across tiers
- Enterprise customers (4% of base) generate 33% of revenue - high value segment
- Price sensitivity analysis helps determine if price increases are viable

---

## Example 4: E-commerce - CAC/LTV for Different Channels

**Scenario**: Testing customer acquisition from Instagram vs. Google Ads

### Instagram Ads
```json
{
  "customerAcquisitionCost": 45,
  "averageRevenuePerUser": 30,
  "customerLifetimeMonths": 18,
  "grossMargin": 60,
  "monthlyChurnRate": 8
}
```

**Result**: LTV $324, CAC:LTV 0.14 (Excellent)

### Google Ads
```json
{
  "customerAcquisitionCost": 85,
  "averageRevenuePerUser": 30,
  "customerLifetimeMonths": 18,
  "grossMargin": 60,
  "monthlyChurnRate": 8
}
```

**Result**: LTV $324, CAC:LTV 0.26 (Excellent)

**Decision**: Both channels are profitable, but Instagram has better unit economics. Allocate more budget there, but maintain Google presence for diversification.

---

## Tips for Using UnitSim

1. **Start Conservative**: Use pessimistic assumptions to stress-test your model
2. **Use Sensitivity Analysis**: The ±20% scenarios help understand risk
3. **Iterate**: Run multiple scenarios to find optimal pricing and conversion targets
4. **Compare**: Run the same calculator with different assumptions to compare strategies
5. **Track Reality**: Compare actual results vs. projections monthly and adjust

## Common Metrics Benchmarks

### CAC:LTV Ratio
- **< 0.33**: Excellent - highly profitable, can scale aggressively
- **0.33-0.50**: Good - sustainable growth
- **0.50-1.00**: Acceptable - profitable but tight margins
- **> 1.00**: Poor - losing money on each customer

### Freemium Conversion
- **< 1%**: Very low - improve onboarding/value prop
- **1-5%**: Typical for many apps
- **5-10%**: Good conversion
- **> 10%**: Excellent - strong product-market fit

### Payback Period
- **< 6 months**: Excellent - fast capital recovery
- **6-12 months**: Good - standard for SaaS
- **12-18 months**: Acceptable - requires patient capital
- **> 18 months**: Challenging - need strong retention

---

## Integration with AI Assistants

When using UnitSim with ChatGPT or Claude:

1. **Ask for Analysis**: "Use UnitSim to analyze my SaaS unit economics with these assumptions..."
2. **Compare Scenarios**: "Run the pricing tiers calculator with these two configurations and compare"
3. **Get Recommendations**: "What changes would improve my CAC:LTV ratio based on this analysis?"
4. **Create Reports**: "Generate a one-page summary of my freemium funnel for investors"

The formatted summaries are designed to be directly usable in presentations, investor updates, and strategic planning documents.
