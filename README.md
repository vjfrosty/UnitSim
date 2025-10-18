# UnitSim
Unit Economics & Pricing Simulator MCP Server

Interactive "what-if" calculators for business metrics and pricing analysis.

## Overview

UnitSim is a Model Context Protocol (MCP) server that provides interactive calculators for:
- **Customer Acquisition Cost (CAC) / Lifetime Value (LTV)** analysis
- **Freemium Funnel** conversion metrics
- **Pricing Tiers** revenue optimization

Each calculator computes margins, break-even points, and sensitivity tables, providing comprehensive one-page summaries with actionable recommendations.

## Installation

```bash
npm install
npm run build
```

## Usage

This is an MCP server designed to be used with MCP clients like Claude Desktop or other MCP-compatible applications.

### Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "unitsim": {
      "command": "node",
      "args": ["/path/to/UnitSim/dist/index.js"]
    }
  }
}
```

## Available Tools

### 1. calculate_cac_ltv

Calculate Customer Acquisition Cost and Lifetime Value metrics with sensitivity analysis.

**Parameters:**
- `customerAcquisitionCost` (number): Cost to acquire a single customer ($)
- `averageRevenuePerUser` (number): Monthly revenue per customer ($)
- `customerLifetimeMonths` (number): Average customer lifetime in months
- `grossMargin` (number): Gross profit margin percentage (0-100)
- `monthlyChurnRate` (number): Monthly customer churn rate percentage (0-100)

**Returns:**
- LTV and CAC metrics
- CAC:LTV ratio with health assessment
- Break-even and payback periods
- Sensitivity analysis (±20% scenarios)
- Actionable recommendations

**Example:**
```json
{
  "customerAcquisitionCost": 100,
  "averageRevenuePerUser": 50,
  "customerLifetimeMonths": 24,
  "grossMargin": 70,
  "monthlyChurnRate": 5
}
```

### 2. calculate_freemium_funnel

Analyze freemium conversion funnel with revenue and profitability metrics.

**Parameters:**
- `monthlyVisitors` (number): Monthly website/app visitors
- `signupRate` (number): Visitor to signup conversion rate % (0-100)
- `freeToPayConversion` (number): Free to paid conversion rate % (0-100)
- `averageMonthlyRevenue` (number): Average monthly revenue per paying customer ($)
- `costPerVisitor` (number): Marketing/acquisition cost per visitor ($)
- `grossMargin` (number): Gross profit margin percentage (0-100)

**Returns:**
- Complete funnel metrics (visitors → signups → customers)
- Revenue and profitability analysis
- Break-even analysis
- Sensitivity analysis for conversion rates
- Optimization recommendations

**Example:**
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

### 3. calculate_pricing_tiers

Analyze multi-tier pricing strategy with revenue projections and margin analysis.

**Parameters:**
- `tiers` (array): Array of pricing tier objects with:
  - `name` (string): Tier name (e.g., "Basic", "Pro", "Enterprise")
  - `price` (number): Monthly price ($)
  - `expectedCustomers` (number): Expected customer count
  - `costPerCustomer` (number): Variable cost per customer ($)
- `fixedCosts` (number): Monthly fixed costs ($)

**Returns:**
- Per-tier and total revenue analysis
- Margin and profitability breakdown
- Break-even analysis
- Revenue distribution across tiers
- Price sensitivity analysis (±10% scenarios)
- Strategic recommendations

**Example:**
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

## Features

- **Comprehensive Metrics**: All calculators provide detailed financial metrics including margins, break-even points, and profitability
- **Sensitivity Analysis**: Understand how changes in key variables affect outcomes
- **Health Assessments**: Automatic evaluation of metric health with visual indicators (✅ ⚠️ ❌)
- **Actionable Recommendations**: Each analysis includes specific, context-aware recommendations
- **Formatted Outputs**: Results include both structured JSON data and human-readable summaries

## Use Cases

- **Startup Planning**: Validate unit economics before scaling
- **Pricing Strategy**: Optimize multi-tier pricing for maximum revenue
- **Growth Modeling**: Understand break-even points and profitability timelines
- **Investment Analysis**: Demonstrate sustainable unit economics to investors
- **Product Decisions**: Evaluate freemium vs. paid conversion strategies

## License

MIT
