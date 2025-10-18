"""
CSV/Excel Exporter for UnitSim Analysis
=======================================

Provides structured data export in CSV and Excel formats with multiple sheets
and comprehensive data organization.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import io


def export_to_csv(
    analysis_type: str,
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    include_summary: bool = True
) -> str:
    """
    Export analysis to CSV format
    
    Args:
        analysis_type: Type of analysis
        input_params: Input parameters
        results: Analysis results
        include_summary: Whether to include summary statistics
    
    Returns:
        CSV string ready for download
    """
    
    if analysis_type == "unit_economics":
        return _export_unit_economics_csv(input_params, results, include_summary)
    elif analysis_type == "pricing_tiers":
        return _export_pricing_tiers_csv(input_params, results, include_summary)
    elif analysis_type == "freemium_funnel":
        return _export_freemium_funnel_csv(input_params, results, include_summary)
    elif analysis_type == "scenario_analysis":
        return _export_scenario_analysis_csv(input_params, results, include_summary)
    else:
        raise ValueError(f"Unsupported analysis type: {analysis_type}")


def export_to_excel(
    analysis_type: str,
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    filename: Optional[str] = None
) -> bytes:
    """
    Export analysis to multi-sheet Excel workbook
    
    Args:
        analysis_type: Type of analysis
        input_params: Input parameters
        results: Analysis results
        filename: Optional filename (otherwise generated)
    
    Returns:
        Excel file as bytes
    """
    # Create Excel writer in memory
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        
        # Create summary sheet
        _create_summary_sheet(writer, analysis_type, input_params, results)
        
        # Create type-specific sheets
        if analysis_type == "unit_economics":
            _create_unit_economics_sheets(writer, input_params, results)
        elif analysis_type == "pricing_tiers":
            _create_pricing_tiers_sheets(writer, input_params, results)
        elif analysis_type == "freemium_funnel":
            _create_freemium_funnel_sheets(writer, input_params, results)
        elif analysis_type == "scenario_analysis":
            _create_scenario_analysis_sheets(writer, input_params, results)
    
    buffer.seek(0)
    return buffer.getvalue()


def _export_unit_economics_csv(
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    include_summary: bool
) -> str:
    """Export unit economics to CSV format"""
    
    # Create main data structure
    data = []
    
    # Add summary row if requested
    if include_summary:
        data.append({
            'Analysis Type': 'Unit Economics',
            'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'MRR': input_params.get('monthlyRecurringRevenue', 0),
            'Gross Margin %': input_params.get('grossMarginPercent', 0),
            'Churn Rate %': input_params.get('monthlyChurnRate', 0),
            'CAC': input_params.get('customerAcquisitionCost', 0),
            'LTV': results.get('ltv', 0),
            'LTV:CAC Ratio': results.get('ltv_cac_ratio', 0),
            'Payback Months': results.get('payback_months', 0),
            'Status': results.get('status', 'Unknown')
        })
    
    # Add detailed metrics if available
    metrics = results.get('detailed_metrics', {})
    for metric_name, value in metrics.items():
        data.append({
            'Metric': metric_name.replace('_', ' ').title(),
            'Value': value
        })
    
    # Convert to DataFrame and CSV
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def _export_pricing_tiers_csv(
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    include_summary: bool
) -> str:
    """Export pricing tiers to CSV format"""
    
    data = []
    
    # Add header info if summary requested
    if include_summary:
        blended = results.get('blended_metrics', {})
        data.append({
            'Analysis Type': 'Pricing Tiers',
            'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Total Customers': blended.get('total_customers', 0),
            'Total ARR': blended.get('total_annual_arr', 0),
            'Blended LTV': blended.get('blended_ltv', 0),
            'Blended LTV:CAC': blended.get('blended_ltv_cac_ratio', 0)
        })
        data.append({})  # Empty row for separation
    
    # Add tier details
    tiers = results.get('tiers', [])
    for i, tier in enumerate(tiers):
        data.append({
            'Tier': tier.get('name', f'Tier {i+1}'),
            'Price': tier.get('price', 0),
            'Customers': tier.get('customers', 0),
            'Churn Rate %': tier.get('churn_rate', 0),
            'CAC': tier.get('cac', 0),
            'LTV': tier.get('ltv', 0),
            'LTV:CAC Ratio': tier.get('ltv_cac_ratio', 0),
            'ARR': tier.get('annual_arr', 0),
            'Status': tier.get('status', 'Unknown')
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def _export_freemium_funnel_csv(
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    include_summary: bool
) -> str:
    """Export freemium funnel to CSV format"""
    
    data = []
    
    # Add summary if requested
    if include_summary:
        summary = results.get('summary', {})
        data.append({
            'Analysis Type': 'Freemium Funnel',
            'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Initial Users': summary.get('initial_users', 0),
            'Final Users': summary.get('final_users', 0),
            'Overall Conversion %': round(summary.get('overall_conversion', 0), 2),
            'Total Revenue': summary.get('total_revenue', 0)
        })
        data.append({})  # Separator
    
    # Add stage details
    stages = results.get('stages', [])
    for i, stage in enumerate(stages):
        data.append({
            'Stage': i + 1,
            'Name': stage.get('name', f'Stage {i+1}'),
            'Input Users': stage.get('input_users', 0),
            'Output Users': stage.get('output_users', 0),
            'Conversion Rate %': round(stage.get('conversion_rate', 0), 2),
            'Drop Off': stage.get('drop_off', 0),
            'Cumulative Conversion %': round(stage.get('cumulative_conversion', 0), 2)
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def _export_scenario_analysis_csv(
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    include_summary: bool
) -> str:
    """Export scenario analysis to CSV format"""
    
    data = []
    
    # Add simulation summary
    if include_summary:
        summary = results.get('simulation_summary', {})
        stats = results.get('summary_statistics', {})
        ltv_stats = stats.get('ltv', {})
        
        data.append({
            'Analysis Type': 'Scenario Analysis (Monte Carlo)',
            'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Iterations': summary.get('n_iterations', 0),
            'Mean LTV': round(ltv_stats.get('mean', 0), 2),
            'Median LTV': round(ltv_stats.get('median', 0), 2),
            'Std Dev LTV': round(ltv_stats.get('std', 0), 2),
            'Min LTV': round(ltv_stats.get('min', 0), 2),
            'Max LTV': round(ltv_stats.get('max', 0), 2)
        })
        data.append({})  # Separator
    
    # Add scenario results (first 1000 iterations for CSV)
    scenarios = results.get('scenarios', [])[:1000]  # Limit for CSV performance
    
    for i, scenario in enumerate(scenarios):
        data.append({
            'Iteration': i + 1,
            'MRR': scenario.get('mrr', 0),
            'Gross Margin %': scenario.get('gross_margin', 0),
            'Churn Rate %': scenario.get('churn_rate', 0),
            'CAC': scenario.get('cac', 0),
            'LTV': round(scenario.get('ltv', 0), 2),
            'LTV:CAC Ratio': round(scenario.get('ltv_cac_ratio', 0), 2),
            'Payback Months': round(scenario.get('payback_months', 0), 2)
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def _create_summary_sheet(
    writer: pd.ExcelWriter,
    analysis_type: str,
    input_params: Dict[str, Any],
    results: Dict[str, Any]
):
    """Create summary sheet for Excel export"""
    
    summary_data = []
    
    # Metadata
    summary_data.append(['Analysis Type', analysis_type.replace('_', ' ').title()])
    summary_data.append(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    summary_data.append(['UnitSim Version', '2.0'])
    summary_data.append([])  # Empty row
    
    # Key results based on analysis type
    if analysis_type == "unit_economics":
        summary_data.extend([
            ['Key Results', ''],
            ['LTV', results.get('ltv', 0)],
            ['LTV:CAC Ratio', results.get('ltv_cac_ratio', 0)],
            ['Payback Months', results.get('payback_months', 0)],
            ['Status', results.get('status', 'Unknown')]
        ])
    
    elif analysis_type == "pricing_tiers":
        blended = results.get('blended_metrics', {})
        summary_data.extend([
            ['Key Results', ''],
            ['Total Customers', blended.get('total_customers', 0)],
            ['Total ARR', blended.get('total_annual_arr', 0)],
            ['Blended LTV', blended.get('blended_ltv', 0)],
            ['Number of Tiers', len(results.get('tiers', []))]
        ])
    
    elif analysis_type == "freemium_funnel":
        summary = results.get('summary', {})
        summary_data.extend([
            ['Key Results', ''],
            ['Initial Users', summary.get('initial_users', 0)],
            ['Final Users', summary.get('final_users', 0)],
            ['Overall Conversion %', round(summary.get('overall_conversion', 0), 2)],
            ['Number of Stages', len(results.get('stages', []))]
        ])
    
    elif analysis_type == "scenario_analysis":
        stats = results.get('summary_statistics', {})
        ltv_stats = stats.get('ltv', {})
        summary_data.extend([
            ['Key Results', ''],
            ['Simulation Iterations', results.get('simulation_summary', {}).get('n_iterations', 0)],
            ['Mean LTV', round(ltv_stats.get('mean', 0), 2)],
            ['Median LTV', round(ltv_stats.get('median', 0), 2)],
            ['LTV Standard Deviation', round(ltv_stats.get('std', 0), 2)]
        ])
    
    # Convert to DataFrame and save
    df = pd.DataFrame(summary_data, columns=['Parameter', 'Value'])
    df.to_excel(writer, sheet_name='Summary', index=False)


def _create_unit_economics_sheets(
    writer: pd.ExcelWriter,
    input_params: Dict[str, Any],
    results: Dict[str, Any]
):
    """Create unit economics specific sheets"""
    
    # Input parameters sheet
    input_data = [
        ['Parameter', 'Value'],
        ['Monthly Recurring Revenue', input_params.get('monthlyRecurringRevenue', 0)],
        ['Gross Margin %', input_params.get('grossMarginPercent', 0)],
        ['Monthly Churn Rate %', input_params.get('monthlyChurnRate', 0)],
        ['Customer Acquisition Cost', input_params.get('customerAcquisitionCost', 0)]
    ]
    
    input_df = pd.DataFrame(input_data[1:], columns=input_data[0])
    input_df.to_excel(writer, sheet_name='Input Parameters', index=False)
    
    # Detailed calculations sheet
    calc_data = []
    metrics = results.get('detailed_metrics', {})
    for metric, value in metrics.items():
        calc_data.append([metric.replace('_', ' ').title(), value])
    
    if calc_data:
        calc_df = pd.DataFrame(calc_data, columns=['Metric', 'Value'])
        calc_df.to_excel(writer, sheet_name='Detailed Calculations', index=False)


def _create_pricing_tiers_sheets(
    writer: pd.ExcelWriter,
    input_params: Dict[str, Any],
    results: Dict[str, Any]
):
    """Create pricing tiers specific sheets"""
    
    # Tier details sheet
    tiers = results.get('tiers', [])
    tier_data = []
    
    for tier in tiers:
        tier_data.append([
            tier.get('name', ''),
            tier.get('price', 0),
            tier.get('customers', 0),
            tier.get('churn_rate', 0),
            tier.get('cac', 0),
            tier.get('ltv', 0),
            tier.get('ltv_cac_ratio', 0),
            tier.get('annual_arr', 0),
            tier.get('status', '')
        ])
    
    if tier_data:
        tier_df = pd.DataFrame(tier_data, columns=[
            'Tier Name', 'Price', 'Customers', 'Churn Rate %', 'CAC',
            'LTV', 'LTV:CAC Ratio', 'Annual ARR', 'Status'
        ])
        tier_df.to_excel(writer, sheet_name='Tier Details', index=False)
    
    # Blended metrics sheet
    blended = results.get('blended_metrics', {})
    blended_data = [[k.replace('_', ' ').title(), v] for k, v in blended.items()]
    
    if blended_data:
        blended_df = pd.DataFrame(blended_data, columns=['Metric', 'Value'])
        blended_df.to_excel(writer, sheet_name='Blended Metrics', index=False)


def _create_freemium_funnel_sheets(
    writer: pd.ExcelWriter,
    input_params: Dict[str, Any],
    results: Dict[str, Any]
):
    """Create freemium funnel specific sheets"""
    
    # Stage analysis sheet
    stages = results.get('stages', [])
    stage_data = []
    
    for i, stage in enumerate(stages):
        stage_data.append([
            i + 1,
            stage.get('name', f'Stage {i+1}'),
            stage.get('input_users', 0),
            stage.get('output_users', 0),
            round(stage.get('conversion_rate', 0), 2),
            stage.get('drop_off', 0),
            round(stage.get('cumulative_conversion', 0), 2)
        ])
    
    if stage_data:
        stage_df = pd.DataFrame(stage_data, columns=[
            'Stage #', 'Name', 'Input Users', 'Output Users',
            'Conversion Rate %', 'Drop Off', 'Cumulative Conversion %'
        ])
        stage_df.to_excel(writer, sheet_name='Stage Analysis', index=False)


def _create_scenario_analysis_sheets(
    writer: pd.ExcelWriter,
    input_params: Dict[str, Any],
    results: Dict[str, Any]
):
    """Create scenario analysis specific sheets"""
    
    # Statistics sheet
    stats = results.get('summary_statistics', {})
    stats_data = []
    
    for metric, values in stats.items():
        if isinstance(values, dict):
            for stat_name, stat_value in values.items():
                stats_data.append([
                    metric.replace('_', ' ').title(),
                    stat_name.title(),
                    round(stat_value, 4) if isinstance(stat_value, (int, float)) else stat_value
                ])
    
    if stats_data:
        stats_df = pd.DataFrame(stats_data, columns=['Metric', 'Statistic', 'Value'])
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
    
    # Sample scenarios (first 100)
    scenarios = results.get('scenarios', [])[:100]
    scenario_data = []
    
    for i, scenario in enumerate(scenarios):
        scenario_data.append([
            i + 1,
            round(scenario.get('mrr', 0), 2),
            round(scenario.get('gross_margin', 0), 2),
            round(scenario.get('churn_rate', 0), 2),
            round(scenario.get('cac', 0), 2),
            round(scenario.get('ltv', 0), 2),
            round(scenario.get('ltv_cac_ratio', 0), 2),
            round(scenario.get('payback_months', 0), 2)
        ])
    
    if scenario_data:
        scenario_df = pd.DataFrame(scenario_data, columns=[
            'Iteration', 'MRR', 'Gross Margin %', 'Churn Rate %',
            'CAC', 'LTV', 'LTV:CAC Ratio', 'Payback Months'
        ])
        scenario_df.to_excel(writer, sheet_name='Sample Scenarios', index=False)


# Example usage
if __name__ == "__main__":
    # Test unit economics export
    test_params = {
        "monthlyRecurringRevenue": 100,
        "grossMarginPercent": 80,
        "monthlyChurnRate": 5,
        "customerAcquisitionCost": 500
    }
    
    test_results = {
        "ltv": 1600,
        "ltv_cac_ratio": 3.2,
        "status": "Healthy",
        "payback_months": 6.25,
        "detailed_metrics": {
            "monthly_gross_margin": 80,
            "annual_churn_rate": 46.0,
            "customer_lifetime_months": 20
        }
    }
    
    # Test CSV export
    csv_output = export_to_csv("unit_economics", test_params, test_results)
    print("CSV Export Preview:")
    print(csv_output[:300] + "...")
    
    # Test Excel export
    excel_bytes = export_to_excel("unit_economics", test_params, test_results)
    print(f"\nExcel file size: {len(excel_bytes)} bytes")