from fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any, Optional
from calculators.unit_economics import calculate_unit_economics, validate_inputs
from calculators.pricing_tiers import validate_tier_inputs, simulate_pricing_tiers
from calculators.freemium_funnel import (
    validate_funnel_inputs,
    calculate_funnel_metrics,
    identify_funnel_bottlenecks,
    analyze_cohort_survival
)
from calculators.scenario_analysis import (
    DistributionConfig,
    run_monte_carlo_simulation,
    get_default_sensitivity_ranges,
    calculate_sensitivity_analysis,
    generate_scenario_analysis
)
from exporters.export_tool import (
    export_analysis_tool,
    list_saved_analyses_tool,
    load_saved_analysis_tool,
    delete_saved_analysis_tool
)

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

@lru_cache(maxsize=None)
def _load_widget_html(name: str) -> str:
    path = ASSETS_DIR / f"{name}.html"
    if path.exists():
        return path.read_text(encoding="utf8")
    return ""

mcp = FastMCP(name="unitsim")

@mcp.tool()
async def calculate_unit_economics_tool(
    monthlyRecurringRevenue: float,
    grossMarginPercent: float,
    monthlyChurnRate: float,
    customerAcquisitionCost: float
) -> str:
    """Calculate unit economics: LTV, CAC, ratio, payback period"""
    try:
        is_valid, error_msg = validate_inputs(
            monthlyRecurringRevenue,
            grossMarginPercent,
            monthlyChurnRate,
            customerAcquisitionCost
        )
        
        if not is_valid:
            return f"❌ {error_msg}"
        
        results = calculate_unit_economics(
            monthlyRecurringRevenue,
            grossMarginPercent,
            monthlyChurnRate,
            customerAcquisitionCost
        )
        
        emoji = {"Healthy": "✅", "Warning": "⚠️", "Critical": "🚨"}
        response = f"{emoji.get(results['status'], '📊')} **{results['status']}**\n\n"
        response += f"{results['status_message']}\n\n"
        response += f"**Metrics:**\n"
        response += f"• LTV: ${results['ltv']:,.0f}\n"
        response += f"• CAC: ${results['cac']:,.0f}\n"
        response += f"• Ratio: {results['ltv_cac_ratio']:.1f}:1\n"
        response += f"• Payback: {results['payback_months']:.1f} mo\n"
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def simulate_pricing_tiers_tool(
    tiers: List[Dict[str, Any]],
    grossMarginPercent: float,
    monthlyChurnRate: float
) -> str:
    """Compare multiple pricing tiers and calculate blended metrics. 
    
    Takes a list of pricing tiers with their expected customers and calculates:
    - Individual tier metrics (MRR, ARR, LTV, LTV/CAC ratios)  
    - Blended metrics across all tiers (weighted averages)
    - Revenue distribution and optimal tier identification
    
    Each tier should have: name, price, expected_customers, and optionally cac and conversion_rate
    """
    try:
        # Debug: Check input data structure
        if not isinstance(tiers, list):
            return f"❌ Tiers must be a list, got {type(tiers)}"
        
        if len(tiers) == 0:
            return f"❌ Tiers list cannot be empty"
            
        # Debug: Check each tier structure
        for i, tier in enumerate(tiers):
            if not isinstance(tier, dict):
                return f"❌ Tier {i} must be a dictionary, got {type(tier)}"
            
            required_fields = ["name", "price", "expected_customers"]
            missing_fields = [field for field in required_fields if field not in tier]
            if missing_fields:
                return f"❌ Tier {i} missing required fields: {', '.join(missing_fields)}"
        
        # Validate tier inputs
        is_valid, error_msg = validate_tier_inputs(tiers)
        if not is_valid:
            return f"❌ {error_msg}"
        
        # Validate global parameters
        if grossMarginPercent < 0 or grossMarginPercent > 100:
            return f"❌ Gross Margin must be 0-100%"
        if monthlyChurnRate < 0 or monthlyChurnRate > 50:
            return f"❌ Monthly Churn Rate must be 0-50%"
        
        # Calculate pricing tier metrics
        results = simulate_pricing_tiers(tiers, grossMarginPercent, monthlyChurnRate)
        
        # Format response
        response = "📊 **Pricing Tier Analysis**\n\n"
        
        # Blended metrics summary
        blended = results['blended_metrics']
        response += "**Blended Metrics Across All Tiers:**\n"
        response += f"• Total Customers: {blended['total_customers']:,}\n"
        response += f"• Total MRR: ${blended['total_monthly_mrr']:,.0f}\n"
        response += f"• Total ARR: ${blended['total_annual_arr']:,.0f}\n"
        response += f"• Blended ARPA: ${blended['blended_arpa']:.2f}\n"
        response += f"• Blended LTV: ${blended['blended_ltv']:,.0f}\n"
        response += f"• Blended LTV/CAC: {blended['blended_ltv_cac_ratio']:.1f}:1\n\n"
        
        # Individual tier performance
        response += "**Individual Tier Performance:**\n\n"
        try:
            for i, tier in enumerate(results['tiers']):
                # Debug: Check tier structure
                if not isinstance(tier, dict):
                    return f"❌ Tier {i} result is not a dictionary: {type(tier)}"
                
                # Safe access with error handling
                try:
                    ltv_val = tier.get('ltv', 0)
                    ltv_display = f"${ltv_val:,.0f}" if ltv_val != "∞" else "∞"
                except Exception as e:
                    return f"❌ Error formatting LTV for tier {i}: {str(e)}"
                
                try:
                    ratio_val = tier.get('ltv_cac_ratio', 0)
                    ratio_display = f"{ratio_val:.1f}:1" if ratio_val != "∞" else "∞"
                except Exception as e:
                    return f"❌ Error formatting ratio for tier {i}: {str(e)}"
                
                # Build response with safe access
                tier_name = tier.get('tier_name', f'Tier {i+1}')
                price = tier.get('price', 0)
                customers = tier.get('expected_customers', 0)
                mrr = tier.get('monthly_mrr', 0)
                
                response += f"**{tier_name}** (${price:.0f}/mo)\n"
                response += f"  • Customers: {customers:,}\n"
                response += f"  • MRR: ${mrr:,.0f}\n"
                response += f"  • LTV: {ltv_display}\n"
                response += f"  • LTV/CAC: {ratio_display}\n\n"
                
        except Exception as tier_error:
            return f"❌ Error processing tier data: {str(tier_error)}"
        
        # Insights
        analysis = results['analysis']
        response += "💡 **Insights:**\n"
        if analysis['optimal_tier']:
            response += f"• Highest revenue tier: **{analysis['optimal_tier']}** "
            response += f"(${analysis['optimal_tier_revenue']:,.0f}/mo)\n"
        
        response += "• Revenue distribution:\n"
        for dist in analysis['revenue_distribution']:
            response += f"  - {dist['tier']}: {dist['percentage']:.0f}%\n"
        
        return response
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def analyze_freemium_funnel_tool(
    stages: List[Dict[str, Any]],
    initial_users: int,
    include_cohort_analysis: bool = False,
    retention_rates: Optional[List[float]] = None,
    arpu_monthly: float = 50.0
) -> str:
    """Analyze freemium conversion funnel with stage-by-stage metrics and bottleneck identification.
    
    Takes a list of funnel stages and calculates conversion rates, drop-offs, revenue impact, 
    and optimization recommendations. Optionally includes cohort survival analysis.
    
    Each stage should have: name, description, and conversion_rate (except first and last stages).
    Conversion rates should be decimals (0-1), e.g., 0.15 for 15%.
    """
    try:
        # Debug: Check input data structure
        if not isinstance(stages, list):
            return f"❌ 'stages' must be a list of funnel stages, got {type(stages)}"
        
        if len(stages) == 0:
            return f"❌ 'stages' list cannot be empty. Please provide funnel stages."
            
        # Debug: Check each stage structure
        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                return f"❌ Stage {i} must be a dictionary, got {type(stage)}"
            
            if i == 0:  # First stage
                required_fields = ["name", "description"]
            elif i == len(stages) - 1:  # Last stage
                required_fields = ["name", "description"] 
            else:  # Middle stages
                required_fields = ["name", "description", "conversion_rate"]
                
            missing_fields = [field for field in required_fields if field not in stage]
            if missing_fields:
                return f"❌ Stage {i} ('{stage.get('name', 'unnamed')}') missing required fields: {', '.join(missing_fields)}"
        
        # Validate funnel inputs
        is_valid, error_msg = validate_funnel_inputs(stages, initial_users)
        if not is_valid:
            return f"❌ {error_msg}"
        
        # Validate optional parameters
        if arpu_monthly < 0:
            return f"❌ ARPU must be non-negative"
        
        if include_cohort_analysis and retention_rates:
            if len(retention_rates) < 2 or any(r < 0 or r > 100 for r in retention_rates):
                return f"❌ Retention rates must be between 0-100% with at least 2 periods"
        
        # Calculate funnel metrics
        funnel_results = calculate_funnel_metrics(stages, initial_users)
        
        # Format response
        response = "🔄 **Freemium Funnel Analysis**\n\n"
        
        # Funnel flow summary
        response += "**Conversion Funnel:**\n"
        for stage in funnel_results['stages']:
            entering = stage['users_entering']
            converting = stage['users_converting']
            rate = stage['conversion_rate']
            
            if rate > 0:
                response += f"• **{stage['stage_name']}**: {entering:,} → {converting:,} ({rate:.1f}%)\n"
            else:
                response += f"• **{stage['stage_name']}**: {entering:,} users (final stage)\n"
        
        # Overall metrics
        summary = funnel_results['summary']
        response += f"\n**Overall Metrics:**\n"
        response += f"• Initial Users: {summary['initial_users']:,}\n"
        response += f"• Final Users: {summary['final_users']:,}\n"
        response += f"• Overall Conversion: {summary['overall_conversion']:.2f}%\n"
        
        # Bottleneck analysis
        bottleneck_results = identify_funnel_bottlenecks(funnel_results, arpu_monthly)
        
        response += f"\n🚨 **Bottleneck Analysis:**\n"
        top_bottleneck = bottleneck_results['top_bottleneck']
        if top_bottleneck:
            response += f"• **Biggest Drop-off**: {top_bottleneck['stage_name']} "
            response += f"({top_bottleneck['drop_off_rate']:.1f}% drop-off)\n"
        
        response += f"• **Top 3 Optimization Opportunities:**\n"
        for bottleneck in bottleneck_results['bottlenecks'][:3]:
            response += f"  - {bottleneck['stage_name']}: "
            response += f"${bottleneck['revenue_impact_per_1pct']:,.0f} per 1% improvement\n"
        
        # Recommendations
        recommendations = bottleneck_results['recommendations'][:2]
        if recommendations:
            response += f"\n💡 **Optimization Recommendations:**\n"
            for rec in recommendations:
                response += f"• **{rec['stage']}**: {rec['recommendation']}\n"
                response += f"  *Impact*: {rec['potential_impact']}\n"
        
        # Cohort analysis (if requested)
        if include_cohort_analysis and retention_rates:
            cohort_results = analyze_cohort_survival(retention_rates, summary['final_users'], arpu_monthly)
            
            response += f"\n📊 **Cohort Survival Analysis:**\n"
            metrics = cohort_results['lifetime_metrics']
            response += f"• Average Customer Lifetime: {metrics['average_lifetime_months']} months\n"
            response += f"• Customer LTV: ${metrics['customer_ltv']:,.0f}\n"
            response += f"• Total Cohort Value: ${metrics['total_cohort_revenue']:,.0f}\n"
            
            # Show first few months of retention
            response += f"\n**Retention Curve (first 6 months):**\n"
            for month_data in cohort_results['cohort_data'][:6]:
                response += f"• Month {month_data['month']}: {month_data['retention_rate']:.0f}% retention\n"
        
        return response
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def scenario_analysis_tool(
    base_params: Dict[str, float],
    analysis_type: str = "monte_carlo",
    n_iterations: int = 10000,
    param_distributions: Optional[Dict[str, Dict[str, Any]]] = None,
    sensitivity_range_percent: float = 20.0,
    scenarios: Optional[Dict[str, Dict[str, Any]]] = None,
    confidence_levels: Optional[List[float]] = None
) -> str:
    """Perform advanced scenario and sensitivity analysis with Monte Carlo simulation.
    
    Supports three analysis types:
    1. 'monte_carlo': Statistical simulation with uncertainty quantification
    2. 'sensitivity': Tornado diagram analysis identifying most impactful parameters  
    3. 'scenarios': Compare optimistic/realistic/pessimistic scenarios
    
    Base parameters should include: mrr, gross_margin_percent, monthly_churn_rate, customer_acquisition_cost
    
    For Monte Carlo: optionally specify param_distributions with distribution configs
    For Sensitivity: optionally specify sensitivity_range_percent (default 20%)
    For Scenarios: provide scenarios dict with scenario configurations
    """
    try:
        # Validate base parameters
        required_params = ["mrr", "gross_margin_percent", "monthly_churn_rate", "customer_acquisition_cost"]
        missing_params = [p for p in required_params if p not in base_params]
        if missing_params:
            return f"❌ Missing required parameters: {', '.join(missing_params)}"
        
        # Validate parameter values
        mrr = base_params.get("mrr", 0)
        gross_margin = base_params.get("gross_margin_percent", 0)
        churn_rate = base_params.get("monthly_churn_rate", 0)
        cac = base_params.get("customer_acquisition_cost", 0)
        
        if mrr <= 0:
            return "❌ MRR must be positive"
        if gross_margin <= 0 or gross_margin > 100:
            return "❌ Gross Margin must be between 0-100%"
        if churn_rate <= 0 or churn_rate > 50:
            return "❌ Monthly Churn Rate must be between 0-50%"
        if cac <= 0:
            return "❌ CAC must be positive"
        
        response = ""
        
        if analysis_type == "monte_carlo":
            # Monte Carlo Simulation
            response += "🎲 **Monte Carlo Simulation Analysis**\n\n"
            
            # Use provided distributions or create defaults
            if param_distributions is None:
                param_distributions = {
                    "mrr": {"type": "normal", "parameters": {"mean": mrr, "std": mrr * 0.15}},
                    "monthly_churn_rate": {"type": "normal", "parameters": {"mean": churn_rate, "std": churn_rate * 0.20}}
                }
            
            # Convert to DistributionConfig objects
            distributions = {}
            for param, config in param_distributions.items():
                distributions[param] = DistributionConfig(
                    type=config["type"],
                    parameters=config["parameters"],
                    min_value=config.get("min_value"),
                    max_value=config.get("max_value")
                )
            
            # Run simulation
            results = run_monte_carlo_simulation(base_params, distributions, n_iterations)
            
            # Format results
            response += f"**Simulation Summary:**\n"
            response += f"• Iterations: {results['simulation_summary']['n_iterations']:,}\n"
            response += f"• Convergence: {'✅' if results['simulation_summary']['convergence_achieved'] else '⚠️'}\n\n"
            
            # Statistical summaries for key metrics
            ltv_stats = results['summary_statistics']['ltv']
            ratio_stats = results['summary_statistics']['ltv_cac_ratio']
            
            response += f"**Lifetime Value (LTV) Distribution:**\n"
            response += f"• Mean: ${ltv_stats['mean']:,.0f}\n"
            response += f"• Median: ${ltv_stats['median']:,.0f}\n"
            response += f"• Std Dev: ${ltv_stats['std']:,.0f}\n"
            response += f"• Range: ${ltv_stats['min']:,.0f} - ${ltv_stats['max']:,.0f}\n\n"
            
            response += f"**Confidence Intervals (LTV):**\n"
            percentiles = ltv_stats['percentiles']
            response += f"• 10th-90th percentile: ${percentiles['p10']:,.0f} - ${percentiles['p90']:,.0f}\n"
            response += f"• 25th-75th percentile: ${percentiles['p25']:,.0f} - ${percentiles['p75']:,.0f}\n\n"
            
            response += f"**LTV/CAC Ratio Distribution:**\n"
            response += f"• Mean: {ratio_stats['mean']:.1f}:1\n"
            response += f"• Median: {ratio_stats['median']:.1f}:1\n"
            response += f"• Range: {ratio_stats['min']:.1f}:1 - {ratio_stats['max']:.1f}:1\n\n"
            
            # Risk metrics
            if 'risk_metrics' in results:
                risk = results['risk_metrics']
                response += f"📊 **Risk Assessment:**\n"
                response += f"• Probability of LTV/CAC < 3:1: {risk['probability_ltv_cac_below_3']:.1%}\n"
                response += f"• Probability of positive economics: {risk['probability_positive_unit_economics']:.1%}\n"
                response += f"• Value at Risk (5%): ${risk['value_at_risk_5pct']:,.0f}\n"
        
        elif analysis_type == "sensitivity":
            # Sensitivity Analysis (Tornado Diagram)
            response += "🌪️ **Sensitivity Analysis (Tornado Diagram)**\n\n"
            
            # Generate parameter ranges
            ranges = get_default_sensitivity_ranges(base_params, sensitivity_range_percent / 100)
            
            # Run sensitivity analysis
            results = calculate_sensitivity_analysis(base_params, ranges)
            
            response += f"**Base Case:**\n"
            base_case = results['base_case_outputs']
            response += f"• LTV: ${base_case['ltv']:,.0f}\n"
            response += f"• LTV/CAC Ratio: {base_case['ltv_cac_ratio']:.1f}:1\n"
            response += f"• Payback: {base_case['payback_months']:.1f} months\n\n"
            
            response += f"**Parameter Sensitivity Rankings:**\n"
            rankings = results['sensitivity_rankings'][:5]  # Top 5
            
            for rank, item in enumerate(rankings, 1):
                param_name = item['parameter'].replace('_', ' ').title()
                coefficient = item['sensitivity_coefficient']
                direction = "increases" if coefficient > 0 else "decreases"
                
                response += f"{rank}. **{param_name}** (coeff: {coefficient:.2f})\n"
                response += f"   • LTV range: ${item['low_value']:,.0f} - ${item['high_value']:,.0f}\n"
                response += f"   • Impact: {direction} LTV by {abs(coefficient):.1f}x parameter change\n\n"
            
            response += f"💡 **Key Insights:**\n"
            most_sensitive = rankings[0] if rankings else None
            if most_sensitive:
                response += f"• Most critical parameter: **{most_sensitive['parameter'].replace('_', ' ').title()}**\n"
                response += f"• Focus optimization efforts on this parameter for maximum impact\n"
                
                if most_sensitive['parameter'] == 'monthly_churn_rate':
                    response += f"• Reducing churn rate is your highest leverage improvement\n"
                elif most_sensitive['parameter'] == 'customer_acquisition_cost':
                    response += f"• Improving CAC efficiency offers significant upside\n"
        
        elif analysis_type == "scenarios":
            # Scenario Analysis
            response += "📈 **Scenario Analysis Comparison**\n\n"
            
            # Use provided scenarios or create defaults
            if scenarios is None:
                scenarios = {
                    "pessimistic": {
                        "mrr": mrr * 0.8,
                        "gross_margin_percent": gross_margin * 0.9, 
                        "monthly_churn_rate": churn_rate * 1.5,
                        "customer_acquisition_cost": cac * 1.3,
                        "probability": 0.2
                    },
                    "realistic": {
                        **base_params,
                        "probability": 0.6
                    },
                    "optimistic": {
                        "mrr": mrr * 1.3,
                        "gross_margin_percent": min(95, gross_margin * 1.1),
                        "monthly_churn_rate": churn_rate * 0.7,
                        "customer_acquisition_cost": cac * 0.8,
                        "probability": 0.2
                    }
                }
            
            # Run scenario analysis
            results = generate_scenario_analysis(scenarios)
            
            # Format results
            scenario_results = results['scenario_results']
            
            for scenario_name, scenario_data in scenario_results.items():
                status_emoji = {"Critical": "🚨", "Concerning": "⚠️", "Healthy": "✅", "Excellent": "🌟"}
                emoji = status_emoji.get(scenario_data['status'], "📊")
                
                response += f"**{scenario_name.title()} Scenario** {emoji}\n"
                response += f"• LTV: ${scenario_data['ltv']:,.0f}\n"
                response += f"• LTV/CAC Ratio: {scenario_data['ltv_cac_ratio']:.1f}:1\n"
                response += f"• Payback: {scenario_data['payback_months']:.1f} months\n"
                response += f"• Status: {scenario_data['status']}\n"
                response += f"• Probability: {scenario_data['probability']:.0%}\n\n"
            
            # Expected values
            expected = results['weighted_expected_values']
            response += f"📊 **Probability-Weighted Expectations:**\n"
            response += f"• Expected LTV: ${expected['expected_ltv']:,.0f}\n"
            response += f"• Expected Ratio: {expected['expected_ratio']:.1f}:1\n"
            response += f"• Risk-Adjusted LTV: ${expected['risk_adjusted_ltv']:,.0f}\n\n"
            
            response += f"💡 **Strategic Recommendations:**\n"
            if expected['expected_ratio'] < 3.0:
                response += f"• Expected ratio below 3:1 - focus on unit economics improvement\n"
            if expected['risk_adjusted_ltv'] < expected['expected_ltv'] * 0.8:
                response += f"• High downside risk - develop contingency plans\n"
            response += f"• Plan for scenario range: ${min(s['ltv'] for s in scenario_results.values()):,.0f} - ${max(s['ltv'] for s in scenario_results.values()):,.0f} LTV\n"
        
        else:
            return f"❌ Unsupported analysis type. Use: monte_carlo, sensitivity, or scenarios"
        
        # Add widget HTML for visualization
        widget_html = _load_widget_html("scenario_analysis_table") 
        if widget_html:
            response += f"\n{widget_html}"
        
        return response
        
    except Exception as e:
        return f"❌ Error in scenario analysis: {str(e)}"


@mcp.tool()
async def export_analysis(
    analysis_type: str,
    input_parameters: Dict[str, Any],
    results: Dict[str, Any],
    export_format: str = "pdf",
    title: Optional[str] = None,
    description: Optional[str] = None,
    include_charts: bool = True,
    save_to_database: bool = True,
    configuration_only: bool = False
) -> str:
    """
    Export analysis results in specified format (PDF, CSV, Excel, JSON)
    
    Args:
        analysis_type: Type of analysis ('unit_economics', 'pricing_tiers', 'freemium_funnel', 'scenario_analysis')
        input_parameters: Original analysis input parameters
        results: Calculated analysis results  
        export_format: Output format ('pdf', 'csv', 'excel', 'json')
        title: Optional custom title for export
        description: Optional description
        include_charts: Whether to include visualizations (PDF only)
        save_to_database: Whether to save analysis to database
        configuration_only: For JSON, export only input configuration
    
    Returns:
        Export result with download information
    """
    try:
        result = export_analysis_tool(
            analysis_type=analysis_type,
            input_parameters=input_parameters,
            results=results,
            export_format=export_format,
            title=title,
            description=description,
            include_charts=include_charts,
            save_to_database=save_to_database,
            configuration_only=configuration_only
        )
        
        if result["success"]:
            # Format success response
            response = f"✅ **Export Successful**\n\n"
            response += f"📄 **File:** {result['filename']}\n"
            response += f"📊 **Format:** {result['export_format'].upper()}\n"
            response += f"📏 **Size:** {result['file_size']:,} bytes\n"
            
            if result.get("analysis_id"):
                response += f"💾 **Saved to Database:** {result['analysis_id']}\n"
            
            response += f"\n**Usage Instructions:**\n"
            instructions = result.get("usage_instructions", {})
            response += f"• **Description:** {instructions.get('description', 'Exported analysis data')}\n"
            response += f"• **Usage:** {instructions.get('usage', 'Use appropriate application for the file format')}\n"
            response += f"• **Best For:** {instructions.get('best_for', 'Data sharing and analysis')}\n"
            
            # Include base64 data for download
            response += f"\n**Download Data (Base64):**\n```\n{result['data'][:100]}...\n```"
            response += f"\n*Note: Complete file data available in result.data field*"
            
            return response
        else:
            return f"❌ Export failed: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Export error: {str(e)}"


@mcp.tool()
async def list_saved_analyses(
    analysis_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> str:
    """
    List saved analyses from database with optional filtering
    
    Args:
        analysis_type: Optional filter by analysis type ('unit_economics', 'pricing_tiers', etc.)
        limit: Maximum results to return (max 100)
        offset: Number of results to skip for pagination
    
    Returns:
        Formatted list of saved analyses
    """
    try:
        result = list_saved_analyses_tool(
            analysis_type=analysis_type,
            limit=limit,
            offset=offset
        )
        
        if result["success"]:
            analyses = result["analyses"]
            stats = result["database_stats"]
            
            response = f"📊 **Saved Analyses** ({len(analyses)} of {stats['total_analyses']} total)\n\n"
            
            if result.get("filter_type"):
                response += f"🔍 **Filter:** {result['filter_type']}\n\n"
            
            if not analyses:
                response += "No analyses found matching criteria.\n"
                return response
            
            # List analyses
            for i, analysis in enumerate(analyses, 1):
                response += f"**{i}.** `{analysis['id'][:20]}...`\n"
                response += f"   📈 **Type:** {analysis['analysis_type'].replace('_', ' ').title()}\n"
                
                if analysis.get('title'):
                    response += f"   📝 **Title:** {analysis['title']}\n"
                
                response += f"   📅 **Created:** {analysis['created_at'][:16].replace('T', ' ')}\n"
                response += f"   🔄 **Version:** {analysis['version']}\n"
                
                if analysis.get('tags'):
                    response += f"   🏷️ **Tags:** {', '.join(analysis['tags'])}\n"
                
                response += "\n"
            
            # Database statistics
            response += f"\n**📈 Database Statistics:**\n"
            response += f"• Total Analyses: {stats['total_analyses']}\n"
            response += f"• Total Exports: {stats['total_exports']}\n"
            
            if stats.get('analyses_by_type'):
                response += "• By Type:\n"
                for atype, count in stats['analyses_by_type'].items():
                    response += f"  - {atype.replace('_', ' ').title()}: {count}\n"
            
            return response
        else:
            return f"❌ Failed to list analyses: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error listing analyses: {str(e)}"


@mcp.tool()
async def load_saved_analysis(analysis_id: str) -> str:
    """
    Load saved analysis from database by ID
    
    Args:
        analysis_id: Analysis identifier
    
    Returns:
        Complete analysis data with version history
    """
    try:
        result = load_saved_analysis_tool(analysis_id)
        
        if result["success"]:
            analysis = result["analysis"]
            
            response = f"📊 **Analysis Loaded:** `{analysis['id']}`\n\n"
            response += f"📈 **Type:** {analysis['analysis_type'].replace('_', ' ').title()}\n"
            
            if analysis.get('title'):
                response += f"📝 **Title:** {analysis['title']}\n"
            
            if analysis.get('description'):
                response += f"📄 **Description:** {analysis['description']}\n"
            
            response += f"📅 **Created:** {analysis['created_at'][:16].replace('T', ' ')}\n"
            response += f"📅 **Updated:** {analysis['updated_at'][:16].replace('T', ' ')}\n"
            response += f"🔄 **Version:** {analysis['version']}\n"
            
            if analysis.get('tags'):
                response += f"🏷️ **Tags:** {', '.join(analysis['tags'])}\n"
            
            # Input parameters summary
            response += f"\n**📝 Input Parameters:**\n"
            for key, value in analysis['input_parameters'].items():
                if isinstance(value, (int, float)):
                    response += f"• {key.replace('_', ' ').title()}: {value:,.2f}\n"
                else:
                    response += f"• {key.replace('_', ' ').title()}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}\n"
            
            # Key results summary
            if analysis.get('results'):
                response += f"\n**📊 Key Results:**\n"
                results = analysis['results']
                
                # Type-specific result highlights
                if analysis['analysis_type'] == 'unit_economics':
                    response += f"• LTV: ${results.get('ltv', 0):,.2f}\n"
                    response += f"• LTV:CAC Ratio: {results.get('ltv_cac_ratio', 0):.2f}\n"
                    response += f"• Payback Months: {results.get('payback_months', 0):.1f}\n"
                    response += f"• Status: {results.get('status', 'Unknown')}\n"
                    
                elif analysis['analysis_type'] == 'pricing_tiers':
                    blended = results.get('blended_metrics', {})
                    response += f"• Total Customers: {blended.get('total_customers', 0):,}\n"
                    response += f"• Total ARR: ${blended.get('total_annual_arr', 0):,.2f}\n"
                    response += f"• Blended LTV: ${blended.get('blended_ltv', 0):,.2f}\n"
                    response += f"• Number of Tiers: {len(results.get('tiers', []))}\n"
                    
                elif analysis['analysis_type'] == 'freemium_funnel':
                    summary = results.get('summary', {})
                    response += f"• Initial Users: {summary.get('initial_users', 0):,}\n"
                    response += f"• Final Users: {summary.get('final_users', 0):,}\n"
                    response += f"• Overall Conversion: {summary.get('overall_conversion', 0):.2f}%\n"
                    response += f"• Stages: {len(results.get('stages', []))}\n"
                    
                elif analysis['analysis_type'] == 'scenario_analysis':
                    stats = results.get('summary_statistics', {})
                    ltv_stats = stats.get('ltv', {})
                    response += f"• Mean LTV: ${ltv_stats.get('mean', 0):,.2f}\n"
                    response += f"• Median LTV: ${ltv_stats.get('median', 0):,.2f}\n"
                    response += f"• Iterations: {results.get('simulation_summary', {}).get('n_iterations', 0):,}\n"
            
            # Version history
            versions = result.get("version_history", [])
            if len(versions) > 1:
                response += f"\n**🔄 Version History:** ({len(versions)} versions)\n"
                for version in versions[:3]:  # Show latest 3 versions
                    response += f"• v{version['version']}: {version['created_at'][:16].replace('T', ' ')} - {version['change_summary']}\n"
            
            # Export history
            exports = result.get("export_history", [])
            if exports:
                response += f"\n**📤 Recent Exports:** ({len(exports)} total)\n"
                for export in exports[:3]:  # Show latest 3 exports
                    response += f"• {export['export_format'].upper()}: {export['exported_at'][:16].replace('T', ' ')} ({export['file_size']:,} bytes)\n"
            
            return response
        else:
            return f"❌ Failed to load analysis: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error loading analysis: {str(e)}"


@mcp.tool()
async def delete_saved_analysis(
    analysis_id: str,
    permanent: bool = False
) -> str:
    """
    Delete or archive saved analysis
    
    Args:
        analysis_id: Analysis identifier
        permanent: If True, permanently delete; otherwise archive (soft delete)
    
    Returns:
        Deletion status message
    """
    try:
        result = delete_saved_analysis_tool(analysis_id, permanent=permanent)
        
        if result["success"]:
            action = "permanently deleted" if permanent else "archived"
            return f"✅ Analysis `{analysis_id}` has been {action} successfully."
        else:
            return f"❌ Failed to delete analysis: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error deleting analysis: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
