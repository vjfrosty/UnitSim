#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Type definitions for calculator inputs
interface CACLTVInput {
  customerAcquisitionCost: number;
  averageRevenuePerUser: number;
  customerLifetimeMonths: number;
  grossMargin: number; // percentage (0-100)
  monthlyChurnRate: number; // percentage (0-100)
}

interface FreemiumFunnelInput {
  monthlyVisitors: number;
  signupRate: number; // percentage (0-100)
  freeToPayConversion: number; // percentage (0-100)
  averageMonthlyRevenue: number;
  costPerVisitor: number;
  grossMargin: number; // percentage (0-100)
}

interface PricingTiersInput {
  tiers: Array<{
    name: string;
    price: number;
    expectedCustomers: number;
    costPerCustomer: number;
  }>;
  fixedCosts: number;
}

// Calculator functions
function calculateCACLTV(input: CACLTVInput) {
  const { customerAcquisitionCost, averageRevenuePerUser, customerLifetimeMonths, grossMargin, monthlyChurnRate } = input;
  
  // Calculate LTV
  const ltv = (averageRevenuePerUser * customerLifetimeMonths * grossMargin) / 100;
  
  // Calculate CAC:LTV ratio
  const cacLtvRatio = customerAcquisitionCost / ltv;
  
  // Calculate break-even months
  const monthlyProfit = (averageRevenuePerUser * grossMargin) / 100;
  const breakEvenMonths = customerAcquisitionCost / monthlyProfit;
  
  // Calculate payback period with churn
  const churnRate = monthlyChurnRate / 100;
  const retentionRate = 1 - churnRate;
  let paybackPeriod = 0;
  let cumulativeRevenue = 0;
  let remainingCustomers = 1;
  
  while (cumulativeRevenue < customerAcquisitionCost && paybackPeriod < 100) {
    cumulativeRevenue += remainingCustomers * monthlyProfit;
    remainingCustomers *= retentionRate;
    paybackPeriod++;
  }
  
  // Sensitivity analysis
  const sensitivity = {
    ltv: {
      pessimistic: (averageRevenuePerUser * customerLifetimeMonths * 0.8 * grossMargin) / 100,
      baseline: ltv,
      optimistic: (averageRevenuePerUser * customerLifetimeMonths * 1.2 * grossMargin) / 100
    },
    cacLtvRatio: {
      pessimistic: customerAcquisitionCost / ((averageRevenuePerUser * customerLifetimeMonths * 0.8 * grossMargin) / 100),
      baseline: cacLtvRatio,
      optimistic: customerAcquisitionCost / ((averageRevenuePerUser * customerLifetimeMonths * 1.2 * grossMargin) / 100)
    }
  };
  
  return {
    ltv: ltv.toFixed(2),
    cac: customerAcquisitionCost.toFixed(2),
    cacLtvRatio: cacLtvRatio.toFixed(2),
    breakEvenMonths: breakEvenMonths.toFixed(1),
    paybackPeriod: paybackPeriod.toFixed(1),
    monthlyProfit: monthlyProfit.toFixed(2),
    healthCheck: cacLtvRatio < 0.33 ? "Excellent" : cacLtvRatio < 0.5 ? "Good" : cacLtvRatio < 1 ? "Acceptable" : "Poor",
    sensitivity,
    summary: `
## CAC/LTV Analysis Summary

### Key Metrics
- **Customer Acquisition Cost (CAC)**: $${customerAcquisitionCost.toFixed(2)}
- **Lifetime Value (LTV)**: $${ltv.toFixed(2)}
- **CAC:LTV Ratio**: ${cacLtvRatio.toFixed(2)} (${cacLtvRatio < 0.33 ? "Excellent ✅" : cacLtvRatio < 0.5 ? "Good ✓" : cacLtvRatio < 1 ? "Acceptable ⚠️" : "Poor ❌"})

### Financial Health
- **Monthly Profit per Customer**: $${monthlyProfit.toFixed(2)}
- **Simple Break-Even**: ${breakEvenMonths.toFixed(1)} months
- **Payback Period (with ${monthlyChurnRate}% churn)**: ${paybackPeriod.toFixed(1)} months

### Sensitivity Analysis
**LTV Scenarios:**
- Pessimistic (-20%): $${sensitivity.ltv.pessimistic.toFixed(2)}
- Baseline: $${sensitivity.ltv.baseline.toFixed(2)}
- Optimistic (+20%): $${sensitivity.ltv.optimistic.toFixed(2)}

**CAC:LTV Ratio Scenarios:**
- Pessimistic: ${sensitivity.cacLtvRatio.pessimistic.toFixed(2)}
- Baseline: ${sensitivity.cacLtvRatio.baseline.toFixed(2)}
- Optimistic: ${sensitivity.cacLtvRatio.optimistic.toFixed(2)}

### Recommendations
${cacLtvRatio >= 1 ? "⚠️ CAC is too high relative to LTV. Consider reducing acquisition costs or increasing customer value." : ""}
${cacLtvRatio > 0.5 && cacLtvRatio < 1 ? "💡 Room for improvement. Focus on increasing LTV or reducing CAC." : ""}
${cacLtvRatio <= 0.33 ? "🎉 Excellent unit economics! You have a sustainable and profitable model." : ""}
${paybackPeriod > 12 ? "⏰ Long payback period detected. Consider strategies to accelerate customer value realization." : ""}
`
  };
}

function calculateFreemiumFunnel(input: FreemiumFunnelInput) {
  const { monthlyVisitors, signupRate, freeToPayConversion, averageMonthlyRevenue, costPerVisitor, grossMargin } = input;
  
  // Calculate funnel metrics
  const signups = monthlyVisitors * (signupRate / 100);
  const payingCustomers = signups * (freeToPayConversion / 100);
  
  // Calculate revenue and costs
  const monthlyRevenue = payingCustomers * averageMonthlyRevenue;
  const grossProfit = monthlyRevenue * (grossMargin / 100);
  const acquisitionCost = monthlyVisitors * costPerVisitor;
  const netProfit = grossProfit - acquisitionCost;
  
  // Calculate conversion rates and margins
  const visitorToCustomerRate = (payingCustomers / monthlyVisitors) * 100;
  const revenuePerVisitor = monthlyRevenue / monthlyVisitors;
  const profitMargin = (netProfit / monthlyRevenue) * 100;
  
  // Break-even analysis
  const breakEvenVisitors = acquisitionCost / (revenuePerVisitor * (grossMargin / 100));
  
  // Sensitivity analysis
  const sensitivity = {
    conversionRate: {
      pessimistic: { rate: freeToPayConversion * 0.8, revenue: signups * (freeToPayConversion * 0.8 / 100) * averageMonthlyRevenue },
      baseline: { rate: freeToPayConversion, revenue: monthlyRevenue },
      optimistic: { rate: freeToPayConversion * 1.2, revenue: signups * (freeToPayConversion * 1.2 / 100) * averageMonthlyRevenue }
    },
    signupRate: {
      pessimistic: { rate: signupRate * 0.8, signups: monthlyVisitors * (signupRate * 0.8 / 100) },
      baseline: { rate: signupRate, signups: signups },
      optimistic: { rate: signupRate * 1.2, signups: monthlyVisitors * (signupRate * 1.2 / 100) }
    }
  };
  
  return {
    funnel: {
      visitors: monthlyVisitors,
      signups: signups.toFixed(0),
      payingCustomers: payingCustomers.toFixed(0),
      signupRate: signupRate.toFixed(2) + "%",
      conversionRate: freeToPayConversion.toFixed(2) + "%",
      visitorToCustomerRate: visitorToCustomerRate.toFixed(2) + "%"
    },
    financials: {
      monthlyRevenue: monthlyRevenue.toFixed(2),
      grossProfit: grossProfit.toFixed(2),
      acquisitionCost: acquisitionCost.toFixed(2),
      netProfit: netProfit.toFixed(2),
      profitMargin: profitMargin.toFixed(2) + "%",
      revenuePerVisitor: revenuePerVisitor.toFixed(2)
    },
    breakEven: {
      visitorsNeeded: breakEvenVisitors.toFixed(0),
      currentStatus: monthlyVisitors >= breakEvenVisitors ? "Profitable ✅" : "Not yet profitable ⚠️"
    },
    sensitivity,
    summary: `
## Freemium Funnel Analysis Summary

### Conversion Funnel
- **Monthly Visitors**: ${monthlyVisitors.toLocaleString()}
- **Signups**: ${signups.toFixed(0)} (${signupRate}% conversion)
- **Paying Customers**: ${payingCustomers.toFixed(0)} (${freeToPayConversion}% of signups)
- **Overall Visitor→Customer**: ${visitorToCustomerRate.toFixed(2)}%

### Financial Performance
- **Monthly Revenue**: $${monthlyRevenue.toFixed(2)}
- **Gross Profit**: $${grossProfit.toFixed(2)}
- **Acquisition Cost**: $${acquisitionCost.toFixed(2)}
- **Net Profit**: $${netProfit.toFixed(2)}
- **Profit Margin**: ${profitMargin.toFixed(2)}%

### Revenue per Visitor
- **RPV**: $${revenuePerVisitor.toFixed(2)}
- **Cost per Visitor**: $${costPerVisitor.toFixed(2)}
- **Value/Cost Ratio**: ${(revenuePerVisitor / costPerVisitor).toFixed(2)}x

### Break-Even Analysis
- **Current Visitors**: ${monthlyVisitors.toLocaleString()}
- **Break-Even Visitors**: ${breakEvenVisitors.toFixed(0)}
- **Status**: ${monthlyVisitors >= breakEvenVisitors ? "Profitable ✅" : `Need ${(breakEvenVisitors - monthlyVisitors).toFixed(0)} more visitors ⚠️`}

### Sensitivity Analysis
**Conversion Rate Impact (Free→Paid):**
- Pessimistic (-20% → ${sensitivity.conversionRate.pessimistic.rate.toFixed(2)}%): $${sensitivity.conversionRate.pessimistic.revenue.toFixed(2)} revenue
- Baseline (${freeToPayConversion}%): $${monthlyRevenue.toFixed(2)} revenue
- Optimistic (+20% → ${sensitivity.conversionRate.optimistic.rate.toFixed(2)}%): $${sensitivity.conversionRate.optimistic.revenue.toFixed(2)} revenue

**Signup Rate Impact:**
- Pessimistic (-20% → ${sensitivity.signupRate.pessimistic.rate.toFixed(2)}%): ${sensitivity.signupRate.pessimistic.signups.toFixed(0)} signups
- Baseline (${signupRate}%): ${signups.toFixed(0)} signups
- Optimistic (+20% → ${sensitivity.signupRate.optimistic.rate.toFixed(2)}%): ${sensitivity.signupRate.optimistic.signups.toFixed(0)} signups

### Recommendations
${netProfit < 0 ? "⚠️ Current funnel is not profitable. Focus on improving conversion rates or reducing acquisition costs." : ""}
${visitorToCustomerRate < 1 ? "💡 Low overall conversion rate. Consider improving signup flow and free-to-paid conversion." : ""}
${profitMargin < 20 ? "📊 Thin margins. Look for opportunities to increase revenue per customer or reduce costs." : ""}
${revenuePerVisitor / costPerVisitor > 3 ? "🎉 Strong unit economics! Your funnel is efficient and scalable." : ""}
`
  };
}

function calculatePricingTiers(input: PricingTiersInput) {
  const { tiers, fixedCosts } = input;
  
  // Calculate metrics for each tier
  const tierAnalysis = tiers.map(tier => {
    const revenue = tier.price * tier.expectedCustomers;
    const variableCosts = tier.costPerCustomer * tier.expectedCustomers;
    const margin = revenue - variableCosts;
    const marginPercent = (margin / revenue) * 100;
    
    return {
      name: tier.name,
      price: tier.price,
      customers: tier.expectedCustomers,
      revenue: revenue,
      variableCosts: variableCosts,
      margin: margin,
      marginPercent: marginPercent,
      revenuePerCustomer: tier.price,
      profitPerCustomer: tier.price - tier.costPerCustomer
    };
  });
  
  // Calculate totals
  const totalRevenue = tierAnalysis.reduce((sum, t) => sum + t.revenue, 0);
  const totalVariableCosts = tierAnalysis.reduce((sum, t) => sum + t.variableCosts, 0);
  const totalMargin = totalRevenue - totalVariableCosts;
  const totalProfit = totalMargin - fixedCosts;
  const totalCustomers = tierAnalysis.reduce((sum, t) => sum + t.customers, 0);
  
  // Break-even analysis
  const avgMarginPerCustomer = totalMargin / totalCustomers;
  const breakEvenCustomers = fixedCosts / avgMarginPerCustomer;
  
  // Tier distribution
  const tierDistribution = tierAnalysis.map(t => ({
    name: t.name,
    percentOfCustomers: ((t.customers / totalCustomers) * 100).toFixed(1) + "%",
    percentOfRevenue: ((t.revenue / totalRevenue) * 100).toFixed(1) + "%"
  }));
  
  // Sensitivity analysis - price changes
  const sensitivity = tierAnalysis.map(tier => {
    const priceChangeImpact = (priceChange: number) => {
      const newPrice = tier.price * (1 + priceChange / 100);
      const elasticity = -0.5; // Assume moderate price elasticity
      const newCustomers = tier.customers * Math.pow(1 + priceChange / 100, elasticity);
      const newRevenue = newPrice * newCustomers;
      const newVariableCosts = tier.variableCosts / tier.customers * newCustomers;
      const newMargin = newRevenue - newVariableCosts;
      return {
        customers: newCustomers.toFixed(0),
        revenue: newRevenue.toFixed(2),
        margin: newMargin.toFixed(2)
      };
    };
    
    return {
      tier: tier.name,
      priceIncrease10: priceChangeImpact(10),
      baseline: {
        customers: tier.customers.toString(),
        revenue: tier.revenue.toFixed(2),
        margin: tier.margin.toFixed(2)
      },
      priceDecrease10: priceChangeImpact(-10)
    };
  });
  
  return {
    tiers: tierAnalysis.map(t => ({
      ...t,
      revenue: t.revenue.toFixed(2),
      variableCosts: t.variableCosts.toFixed(2),
      margin: t.margin.toFixed(2),
      marginPercent: t.marginPercent.toFixed(1) + "%",
      profitPerCustomer: t.profitPerCustomer.toFixed(2)
    })),
    totals: {
      customers: totalCustomers,
      revenue: totalRevenue.toFixed(2),
      variableCosts: totalVariableCosts.toFixed(2),
      margin: totalMargin.toFixed(2),
      fixedCosts: fixedCosts.toFixed(2),
      profit: totalProfit.toFixed(2),
      profitMargin: ((totalProfit / totalRevenue) * 100).toFixed(1) + "%"
    },
    breakEven: {
      customersNeeded: breakEvenCustomers.toFixed(0),
      currentCustomers: totalCustomers,
      status: totalCustomers >= breakEvenCustomers ? "Profitable ✅" : "Not yet profitable ⚠️"
    },
    distribution: tierDistribution,
    sensitivity,
    summary: `
## Pricing Tiers Analysis Summary

### Overall Performance
- **Total Customers**: ${totalCustomers.toLocaleString()}
- **Total Revenue**: $${totalRevenue.toFixed(2)}
- **Total Profit**: $${totalProfit.toFixed(2)}
- **Profit Margin**: ${((totalProfit / totalRevenue) * 100).toFixed(1)}%

### Tier Breakdown
${tierAnalysis.map(t => `
**${t.name}** ($${t.price}/mo)
- Customers: ${t.customers} (${((t.customers / totalCustomers) * 100).toFixed(1)}%)
- Revenue: $${t.revenue.toFixed(2)} (${((t.revenue / totalRevenue) * 100).toFixed(1)}%)
- Margin: $${t.margin.toFixed(2)} (${t.marginPercent.toFixed(1)}%)
- Profit/Customer: $${t.profitPerCustomer.toFixed(2)}
`).join('\n')}

### Financial Health
- **Variable Costs**: $${totalVariableCosts.toFixed(2)}
- **Fixed Costs**: $${fixedCosts.toFixed(2)}
- **Contribution Margin**: $${totalMargin.toFixed(2)}
- **Net Profit**: $${totalProfit.toFixed(2)}

### Break-Even Analysis
- **Current Customers**: ${totalCustomers.toLocaleString()}
- **Break-Even Customers**: ${breakEvenCustomers.toFixed(0)}
- **Status**: ${totalCustomers >= breakEvenCustomers ? "Profitable ✅" : `Need ${(breakEvenCustomers - totalCustomers).toFixed(0)} more customers ⚠️`}
- **Avg Margin per Customer**: $${avgMarginPerCustomer.toFixed(2)}

### Revenue Distribution
${tierDistribution.map(d => `- ${d.name}: ${d.percentOfRevenue} of revenue, ${d.percentOfCustomers} of customers`).join('\n')}

### Price Sensitivity Analysis
${sensitivity.map(s => `
**${s.tier}:**
- 10% Price Increase: ${s.priceIncrease10.customers} customers, $${s.priceIncrease10.revenue} revenue, $${s.priceIncrease10.margin} margin
- Baseline: ${s.baseline.customers} customers, $${s.baseline.revenue} revenue, $${s.baseline.margin} margin  
- 10% Price Decrease: ${s.priceDecrease10.customers} customers, $${s.priceDecrease10.revenue} revenue, $${s.priceDecrease10.margin} margin
`).join('\n')}

### Recommendations
${totalProfit < 0 ? "⚠️ Not yet profitable. Need to either increase prices, reduce costs, or acquire more customers." : ""}
${totalProfit > 0 && ((totalProfit / totalRevenue) * 100) < 20 ? "📊 Profitable but with thin margins. Consider optimizing pricing or reducing costs." : ""}
${((totalProfit / totalRevenue) * 100) >= 20 ? "🎉 Strong profitability! Your pricing tiers are working well." : ""}
${tierAnalysis.some(t => t.marginPercent < 0) ? "⚠️ Some tiers have negative margins. Review pricing or cost structure for those tiers." : ""}
`
  };
}

// Create server instance
const server = new Server(
  {
    name: "unitsim",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "calculate_cac_ltv",
        description: "Calculate Customer Acquisition Cost (CAC) and Lifetime Value (LTV) metrics with sensitivity analysis. Returns break-even periods, profit margins, and health check recommendations.",
        inputSchema: {
          type: "object",
          properties: {
            customerAcquisitionCost: {
              type: "number",
              description: "Cost to acquire a single customer (in dollars)"
            },
            averageRevenuePerUser: {
              type: "number",
              description: "Monthly revenue per customer (in dollars)"
            },
            customerLifetimeMonths: {
              type: "number",
              description: "Average number of months a customer stays"
            },
            grossMargin: {
              type: "number",
              description: "Gross profit margin as a percentage (0-100)"
            },
            monthlyChurnRate: {
              type: "number",
              description: "Percentage of customers who leave each month (0-100)"
            }
          },
          required: ["customerAcquisitionCost", "averageRevenuePerUser", "customerLifetimeMonths", "grossMargin", "monthlyChurnRate"]
        }
      },
      {
        name: "calculate_freemium_funnel",
        description: "Analyze freemium conversion funnel metrics including signup rates, free-to-paid conversion, revenue, and profitability. Includes sensitivity analysis for conversion rate variations.",
        inputSchema: {
          type: "object",
          properties: {
            monthlyVisitors: {
              type: "number",
              description: "Number of monthly website/app visitors"
            },
            signupRate: {
              type: "number",
              description: "Percentage of visitors who sign up for free (0-100)"
            },
            freeToPayConversion: {
              type: "number",
              description: "Percentage of free users who convert to paid (0-100)"
            },
            averageMonthlyRevenue: {
              type: "number",
              description: "Average monthly revenue per paying customer (in dollars)"
            },
            costPerVisitor: {
              type: "number",
              description: "Marketing/acquisition cost per visitor (in dollars)"
            },
            grossMargin: {
              type: "number",
              description: "Gross profit margin as a percentage (0-100)"
            }
          },
          required: ["monthlyVisitors", "signupRate", "freeToPayConversion", "averageMonthlyRevenue", "costPerVisitor", "grossMargin"]
        }
      },
      {
        name: "calculate_pricing_tiers",
        description: "Analyze multi-tier pricing strategy with revenue projections, margin analysis, and break-even calculations. Includes price sensitivity analysis showing impact of price changes.",
        inputSchema: {
          type: "object",
          properties: {
            tiers: {
              type: "array",
              description: "Array of pricing tiers with their details",
              items: {
                type: "object",
                properties: {
                  name: {
                    type: "string",
                    description: "Name of the pricing tier (e.g., 'Basic', 'Pro', 'Enterprise')"
                  },
                  price: {
                    type: "number",
                    description: "Monthly price for this tier (in dollars)"
                  },
                  expectedCustomers: {
                    type: "number",
                    description: "Expected number of customers in this tier"
                  },
                  costPerCustomer: {
                    type: "number",
                    description: "Variable cost per customer in this tier (in dollars)"
                  }
                },
                required: ["name", "price", "expectedCustomers", "costPerCustomer"]
              }
            },
            fixedCosts: {
              type: "number",
              description: "Monthly fixed costs for the business (in dollars)"
            }
          },
          required: ["tiers", "fixedCosts"]
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "calculate_cac_ltv") {
      const result = calculateCACLTV(args as unknown as CACLTVInput);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2)
          },
          {
            type: "text",
            text: result.summary
          }
        ]
      };
    } else if (name === "calculate_freemium_funnel") {
      const result = calculateFreemiumFunnel(args as unknown as FreemiumFunnelInput);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2)
          },
          {
            type: "text",
            text: result.summary
          }
        ]
      };
    } else if (name === "calculate_pricing_tiers") {
      const result = calculatePricingTiers(args as unknown as PricingTiersInput);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2)
          },
          {
            type: "text",
            text: result.summary
          }
        ]
      };
    } else {
      throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: `Error: ${errorMessage}`
        }
      ],
      isError: true
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("UnitSim MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
