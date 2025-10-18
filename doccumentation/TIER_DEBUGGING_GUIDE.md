# Tier Variable Error Debugging Guide

## ✅ Correct Tier Data Format

The `simulate_pricing_tiers_tool` expects tiers as a **list of dictionaries** with specific field names:

### Required Fields for Each Tier:
- `name` (string): Tier name (e.g., "Basic", "Pro", "Enterprise")
- `price` (number): Monthly price in dollars
- `expected_customers` (number): Number of customers expected for this tier

### Optional Fields:
- `cac` (number): Customer Acquisition Cost (defaults to 400 if not provided)
- `conversion_rate` (number): Conversion rate as decimal (defaults to 0.02 if not provided)

## ✅ Correct Usage Example:

```json
{
  "tiers": [
    {
      "name": "Basic", 
      "price": 29,
      "expected_customers": 100,
      "cac": 150
    },
    {
      "name": "Pro",
      "price": 99, 
      "expected_customers": 50,
      "cac": 300
    },
    {
      "name": "Enterprise",
      "price": 299,
      "expected_customers": 10, 
      "cac": 800
    }
  ],
  "grossMarginPercent": 80,
  "monthlyChurnRate": 5
}
```

## ❌ Common Errors That Cause "Tier Variable" Issues:

### 1. Wrong Field Names:
```json
// ❌ WRONG - uses 'title' instead of 'name'
{
  "title": "Basic",  // Should be "name"
  "price": 29,
  "expected_customers": 100
}
```

### 2. Missing Required Fields:
```json
// ❌ WRONG - missing 'expected_customers'
{
  "name": "Basic",
  "price": 29
  // Missing "expected_customers"
}
```

### 3. Wrong Data Types:
```json
// ❌ WRONG - price as string instead of number
{
  "name": "Basic",
  "price": "29",  // Should be 29 (number)
  "expected_customers": 100
}
```

### 4. Not Using List Format:
```json
// ❌ WRONG - single object instead of list
{
  "name": "Basic",
  "price": 29,
  "expected_customers": 100
}

// ✅ CORRECT - wrapped in array
[
  {
    "name": "Basic",
    "price": 29,
    "expected_customers": 100
  }
]
```

## 🔧 Debugging Steps:

1. **Check Data Structure**: Ensure you're passing a list of dictionaries
2. **Verify Field Names**: Must be exactly `name`, `price`, `expected_customers`
3. **Check Data Types**: Numbers should be numbers, not strings
4. **Validate Required Fields**: All three required fields must be present

## 🚀 Test Your Tier Data:

Use this MCP client call to test:

```json
{
  "method": "tools/call",
  "params": {
    "name": "simulate_pricing_tiers_tool",
    "arguments": {
      "tiers": [
        {"name": "Basic", "price": 29, "expected_customers": 100, "cac": 150},
        {"name": "Pro", "price": 99, "expected_customers": 50, "cac": 300}
      ],
      "grossMarginPercent": 80,
      "monthlyChurnRate": 5
    }
  }
}
```

## 💡 Recent Improvements:

The server now includes enhanced error messages that will tell you:
- If tiers is not a list
- If individual tiers are not dictionaries  
- Which required fields are missing
- Specific formatting errors for LTV/ratio calculations

Try your call again and the error message should now be much more specific about what's wrong with the tier data format!