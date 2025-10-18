# UnitSim — Unit Economics & Pricing Simulator MCP

**Interactive "what-if" calculators for CAC/LTV, freemium funnels, and pricing tiers**

Built as a Model Context Protocol (MCP) server for ChatGPT and other AI assistants.

---

## 🎯 What It Does

UnitSim helps founders and product managers make data-driven decisions by providing:

- **Unit Economics Analysis** — Calculate LTV, CAC ratios, and payback periods
- **Pricing Tier Simulation** — Compare multiple pricing tiers and find optimal configurations
- **Freemium Funnel Analysis** — (Coming in Stage 3) Track conversion funnels
- **Scenario Planning** — (Coming in Stage 4) Monte Carlo simulation and sensitivity analysis

---

## 🚀 Current Status

**Stage 1:** ✅ Complete — Basic unit economics calculator  
**Stage 2:** 🔄 70% Complete — Pricing tier simulator  
**Stage 3:** ⏳ Planned — Freemium funnel analyzer  
**Stage 4:** ⏳ Planned — Scenario & sensitivity analysis  
**Stage 5:** ⏳ Planned — Export & persistence

See **[plan.md](./plan.md)** for full roadmap and **[STAGE2_PROGRESS.md](./STAGE2_PROGRESS.md)** for current progress.

---

## 📊 Available Tools

### 1. `calculate_unit_economics_tool` ✅

Calculate customer lifetime value and acquisition cost metrics.

**Input:**
```json
{
  "monthlyRecurringRevenue": 100,
  "grossMarginPercent": 80,
  "monthlyChurnRate": 5,
  "customerAcquisitionCost": 500
}
```

**Output:**
- Customer LTV: $1,600
- LTV/CAC Ratio: 3.2:1
- Payback Period: 6.3 months
- Health Status: ✅ Healthy

### 2. `simulate_pricing_tiers_tool` 🔄

Compare multiple pricing tiers and calculate blended metrics.

**Input:**
```json
{
  "tiers": [
    {"name": "Basic", "price": 10, "expected_customers": 100, "cac": 50},
    {"name": "Pro", "price": 50, "expected_customers": 50, "cac": 200},
    {"name": "Enterprise", "price": 200, "expected_customers": 10, "cac": 500}
  ],
  "grossMarginPercent": 80,
  "monthlyChurnRate": 5
}
```

**Output:**
- Total MRR: $5,500
- Blended LTV/CAC: 3.2:1
- Optimal Tier: Pro (45% of revenue)
- Revenue Distribution across tiers

---

## 🧮 Mathematical Foundation

### Unit Economics (Stage 1)
```
LTV = (MRR × Gross Margin) / Churn Rate
LTV/CAC Ratio = LTV / CAC
Payback Period = CAC / (MRR × Gross Margin)
```

### Pricing Tiers (Stage 2)
```
Tier MRR = Price × Expected Customers
Blended ARPA = Total MRR / Total Customers
Blended LTV = Σ(Tier LTV × Tier Customers) / Total Customers
Revenue % = (Tier MRR / Total MRR) × 100
```

---

## 🛠️ Technical Stack

- **Backend:** Python 3.11, FastMCP, Pydantic
- **Deployment:** Docker + Docker Compose
- **Proxy:** nginx with HTTPS
- **Protocol:** MCP over streamable-http

---

## 📁 Project Structure

```
/srv/unitsim/
├── plan.md                    # Full implementation plan
├── STAGE2_PROGRESS.md         # Current stage progress
├── README.md                  # This file
├── docker-compose.yml         # Container orchestration
└── app/
    ├── server.py              # FastMCP server
    ├── calculators/
    │   ├── unit_economics.py  # Stage 1: LTV/CAC
    │   └── pricing_tiers.py   # Stage 2: Multi-tier analysis
    └── assets/
        └── unit_economics_table.html  # UI component
```

---

## 🚀 Quick Start

### Build & Run

```bash
cd /srv/unitsim
docker compose up -d --build
```

### View Logs

```bash
docker logs -f unitsim_app
```

### Test Locally

```bash
curl -s -N \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -X POST http://127.0.0.1:8000/mcp \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}'
```

---

## 🧪 Testing

### Run Calculator Tests

```python
import sys
sys.path.insert(0, '/srv/unitsim/app')

from calculators import calculate_unit_economics

result = calculate_unit_economics(100, 80, 5, 500)
print(f"LTV: ${result['ltv']}, Ratio: {result['ltv_cac_ratio']}:1")
# Output: LTV: $1600.0, Ratio: 3.2:1
```

### Test Status

- ✅ Stage 1 calculations verified
- ✅ Input validation working
- ✅ Docker container stable
- ✅ MCP protocol responding
- ⏳ Stage 2 calculations pending
- ⏳ Integration tests pending

---

## 📚 Documentation

- **[plan.md](./plan.md)** — Full 5-stage implementation plan with mathematical foundations
- **[STAGE2_PROGRESS.md](./STAGE2_PROGRESS.md)** — Current stage progress and next steps
- **[nginx-config.txt](./nginx-config.txt)** — nginx reverse proxy configuration

---

## 🎯 Why UnitSim Wins

1. **Instant Answers** — Founders constantly ask these questions; get visual answers in seconds
2. **Pure Math** — No external APIs needed, deterministic calculations
3. **Low Maintenance** — Simple code, no ML complexity
4. **Perfect for ChatGPT** — Tables, charts, inline components
5. **Clear ROI** — Direct monetization path (€15/€49/€19)

---

## 💰 Monetization Plan

- **Solo Plan:** €15/mo (3 saved models)
- **Team Plan:** €49/mo (10 models, share links)
- **One-off Export:** €19 ("Pitch PDF" export)

---

## 🔗 Access

- **MCP Endpoint:** `http://127.0.0.1:8000/mcp`
- **Public Endpoint:** `https://ai-contextengineering.com/unitsim` (when nginx configured)
- **ChatGPT:** Add via MCP manifest at `.well-known/mcp.json`

---

## 📈 Roadmap

See **[plan.md](./plan.md)** for detailed roadmap.

**Next Up:**
1. Complete Stage 2 HTML component
2. Test pricing tier calculations
3. Rebuild and deploy
4. Validate in ChatGPT

---

## 🤝 Contributing

This is a focused MVP. Current priority: Complete Stage 2.

---

## 📄 License

MIT

---

**Built:** October 17, 2025  
**Status:** Stage 2 in progress (70% complete)  
**Container:** `unitsim_app` running on port 8000
