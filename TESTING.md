# Testing UnitSim

This document explains how to test the UnitSim MCP server.

## Build and Start

```bash
# Install dependencies
npm install

# Build the TypeScript code
npm run build

# The server is now ready to use
```

## Testing with MCP Inspector

The easiest way to test the MCP server is using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
# Install MCP Inspector globally
npm install -g @modelcontextprotocol/inspector

# Run the inspector with UnitSim
npx @modelcontextprotocol/inspector node dist/index.js
```

This will open a web interface where you can:
1. See all available tools
2. Test each calculator with custom inputs
3. View the formatted responses

## Testing with Claude Desktop

Add UnitSim to your Claude Desktop configuration:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "unitsim": {
      "command": "node",
      "args": ["/absolute/path/to/UnitSim/dist/index.js"]
    }
  }
}
```

Restart Claude Desktop, and you can now ask:
- "Calculate CAC/LTV for a SaaS with $100 CAC and $50 monthly revenue..."
- "Analyze my freemium funnel with 10,000 monthly visitors..."
- "Compare these pricing tier scenarios..."

## Manual Testing

Run the test script to verify calculations:

```bash
node test-manual.js
```

This will test all three calculators with known inputs and verify the outputs match expected values.

## Integration Testing

### Test Tool Discovery

Send a `tools/list` request to see all available tools:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

Expected response includes three tools:
- `calculate_cac_ltv`
- `calculate_freemium_funnel`
- `calculate_pricing_tiers`

### Test CAC/LTV Calculator

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "calculate_cac_ltv",
    "arguments": {
      "customerAcquisitionCost": 100,
      "averageRevenuePerUser": 50,
      "customerLifetimeMonths": 24,
      "grossMargin": 70,
      "monthlyChurnRate": 5
    }
  }
}
```

Expected:
- LTV: ~$840
- CAC:LTV ratio: ~0.12 (Excellent)

### Test Freemium Funnel

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "calculate_freemium_funnel",
    "arguments": {
      "monthlyVisitors": 10000,
      "signupRate": 10,
      "freeToPayConversion": 5,
      "averageMonthlyRevenue": 29,
      "costPerVisitor": 0.50,
      "grossMargin": 80
    }
  }
}
```

Expected:
- 1,000 signups
- 50 paying customers
- $1,450 monthly revenue

### Test Pricing Tiers

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "calculate_pricing_tiers",
    "arguments": {
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
        }
      ],
      "fixedCosts": 5000
    }
  }
}
```

Expected:
- Total revenue: $20,000
- Total profit after fixed costs

## Verification Checklist

- [ ] Server starts without errors
- [ ] All three tools are listed in `tools/list`
- [ ] CAC/LTV calculator returns correct metrics
- [ ] Freemium funnel calculator computes conversions correctly
- [ ] Pricing tiers calculator handles multiple tiers
- [ ] Sensitivity analysis is included in responses
- [ ] Summaries are formatted and readable
- [ ] Health checks provide correct assessments
- [ ] Edge cases are handled (e.g., zero values, high churn)

## Common Issues

### Server won't start
- Ensure dependencies are installed: `npm install`
- Build the project: `npm run build`
- Check that Node.js version is 16+ 

### Calculations seem wrong
- Verify all inputs are numbers (not strings)
- Check percentage values are 0-100 (not 0-1)
- Review the EXAMPLES.md file for correct input formats

### Can't connect from MCP client
- Ensure the path to `dist/index.js` is absolute
- Check that the build succeeded
- Restart the MCP client after configuration changes

## Development Testing

When making changes to the calculators:

1. Edit `src/index.ts`
2. Run `npm run build`
3. Test with manual script or MCP Inspector
4. Verify outputs match expected business logic

Use `npm run watch` during development to automatically rebuild on file changes.
