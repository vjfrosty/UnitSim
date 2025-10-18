# Freemium Funnel Tool - Correct Usage Guide

## ✅ Required Parameter: `stages`

The `analyze_freemium_funnel_tool` requires a **`stages`** parameter that you're missing in your request.

## 📋 Correct Request Format:

```json
{
  "stages": [
    {
      "name": "Visitors",
      "description": "Website traffic"
    },
    {
      "name": "Signups", 
      "description": "Free account registration",
      "conversion_rate": 0.05
    },
    {
      "name": "Trial Users",
      "description": "Started free trial", 
      "conversion_rate": 0.80
    },
    {
      "name": "Paid Customers",
      "description": "Converted to paid plan",
      "conversion_rate": 0.15
    }
  ],
  "initial_users": 50000,
  "include_cohort_analysis": true,
  "retention_rates": [0.85, 0.8, 0.75, 0.73, 0.7],
  "arpu_monthly": 18
}
```

## 🔧 Stage Requirements:

### First Stage (Entry Point):
- `name` (string): Stage name (e.g., "Visitors", "Traffic")
- `description` (string): What this stage represents

### Middle Stages:
- `name` (string): Stage name (e.g., "Signups", "Trial")  
- `description` (string): What this stage represents
- `conversion_rate` (decimal): Rate from previous stage (0.0 to 1.0)

### Last Stage (Final Conversion):
- `name` (string): Stage name (e.g., "Paid Customers")
- `description` (string): What this stage represents
- `conversion_rate` (decimal): Final conversion rate

## ❌ Your Current Request Issue:

Your request is missing the `stages` parameter entirely:

```json
// ❌ MISSING 'stages' parameter
{
  "initial_users": 50000,
  "include_cohort_analysis": true, 
  "retention_rates": [0.85, 0.8, 0.75, 0.73, 0.7],
  "arpu_monthly": 18
}
```

## ✅ Fixed Request:

Add the `stages` parameter to your request:

```json
{
  "stages": [
    {"name": "Visitors", "description": "Website visitors"},
    {"name": "Signups", "description": "Free registrations", "conversion_rate": 0.05},  
    {"name": "Trial", "description": "Active trial users", "conversion_rate": 0.80},
    {"name": "Paid", "description": "Paying customers", "conversion_rate": 0.15}
  ],
  "initial_users": 50000,
  "include_cohort_analysis": true,
  "retention_rates": [0.85, 0.8, 0.75, 0.73, 0.7],
  "arpu_monthly": 18
}
```

## 💡 Example Funnel Flows:

### SaaS Freemium:
1. **Website Visitors** → **Free Signups** (5%) → **Trial Users** (80%) → **Paid** (15%)

### Mobile App:
1. **App Downloads** → **Account Creation** (30%) → **Premium Trial** (20%) → **Subscription** (25%)

### Content Platform:
1. **Site Visitors** → **Free Members** (8%) → **Premium Trial** (15%) → **Subscribers** (40%)

The tool will analyze conversion rates, identify bottlenecks, and provide optimization recommendations for your funnel!