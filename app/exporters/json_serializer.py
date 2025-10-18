"""
JSON Serializer for UnitSim Analysis
=====================================

Handles serialization and deserialization of analysis results for sharing
and persistence. Supports all analysis types from Stages 1-4.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional


def serialize_analysis(
    analysis_type: str,
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list] = None,
    include_results: bool = True
) -> str:
    """
    Serialize analysis to shareable JSON format
    
    Args:
        analysis_type: Type of analysis ('unit_economics', 'pricing_tiers', etc.)
        input_params: Original input parameters
        results: Calculated analysis results
        title: Optional analysis title
        description: Optional description
        tags: Optional tags for categorization
        include_results: Whether to include calculated results
    
    Returns:
        JSON string of serialized analysis
    """
    # Create unique analysis ID
    analysis_id = f"unitsim_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    # Build analysis object
    analysis_data = {
        "id": analysis_id,
        "metadata": {
            "analysis_type": analysis_type,
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "title": title or f"{analysis_type.replace('_', ' ').title()} Analysis",
            "description": description or f"UnitSim {analysis_type} analysis",
            "tags": tags or []
        },
        "input_parameters": input_params,
        "configuration": {
            "include_results": include_results,
            "export_format": "json"
        }
    }
    
    # Include results if requested
    if include_results:
        analysis_data["results"] = results
        analysis_data["summary"] = _generate_summary(analysis_type, results)
    
    return json.dumps(analysis_data, indent=2, ensure_ascii=False)


def deserialize_analysis(json_data: str) -> Dict[str, Any]:
    """
    Load analysis from JSON configuration
    
    Args:
        json_data: JSON string of serialized analysis
    
    Returns:
        Dictionary with analysis data
        
    Raises:
        ValueError: If JSON is invalid or missing required fields
    """
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    
    # Validate required fields
    required_fields = ["id", "metadata", "input_parameters"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate metadata
    metadata = data.get("metadata", {})
    if "analysis_type" not in metadata:
        raise ValueError("Missing analysis_type in metadata")
    
    # Validate analysis type
    valid_types = ["unit_economics", "pricing_tiers", "freemium_funnel", "scenario_analysis"]
    if metadata["analysis_type"] not in valid_types:
        raise ValueError(f"Invalid analysis_type. Must be one of: {', '.join(valid_types)}")
    
    return data


def export_configuration_only(
    analysis_type: str,
    input_params: Dict[str, Any],
    title: Optional[str] = None
) -> str:
    """
    Export only input configuration (no results) for sharing parameters
    
    Args:
        analysis_type: Type of analysis
        input_params: Input parameters to export
        title: Optional title
    
    Returns:
        JSON string with configuration only
    """
    return serialize_analysis(
        analysis_type=analysis_type,
        input_params=input_params,
        results={},  # Empty results
        title=title,
        description="Configuration template",
        include_results=False
    )


def _generate_summary(analysis_type: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary statistics for different analysis types"""
    
    if analysis_type == "unit_economics":
        return {
            "ltv": results.get("ltv", 0),
            "ltv_cac_ratio": results.get("ltv_cac_ratio", 0),
            "status": results.get("status", "Unknown"),
            "payback_months": results.get("payback_months", 0)
        }
    
    elif analysis_type == "pricing_tiers":
        blended = results.get("blended_metrics", {})
        return {
            "total_customers": blended.get("total_customers", 0),
            "total_arr": blended.get("total_annual_arr", 0),
            "blended_ltv": blended.get("blended_ltv", 0),
            "tier_count": len(results.get("tiers", []))
        }
    
    elif analysis_type == "freemium_funnel":
        summary = results.get("summary", {})
        return {
            "initial_users": summary.get("initial_users", 0),
            "final_users": summary.get("final_users", 0),
            "overall_conversion": summary.get("overall_conversion", 0),
            "stage_count": len(results.get("stages", []))
        }
    
    elif analysis_type == "scenario_analysis":
        stats = results.get("summary_statistics", {})
        ltv_stats = stats.get("ltv", {})
        return {
            "mean_ltv": ltv_stats.get("mean", 0),
            "median_ltv": ltv_stats.get("median", 0),
            "iterations": results.get("simulation_summary", {}).get("n_iterations", 0),
            "analysis_mode": "monte_carlo"  # Could be enhanced to detect mode
        }
    
    else:
        return {"analysis_type": analysis_type, "summary": "Generic analysis"}


def validate_analysis_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate analysis data structure
    
    Args:
        data: Analysis data dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check basic structure
        if not isinstance(data, dict):
            return False, "Analysis data must be a dictionary"
        
        # Check metadata
        metadata = data.get("metadata", {})
        if not metadata.get("analysis_type"):
            return False, "Missing analysis_type in metadata"
        
        # Check input parameters
        input_params = data.get("input_parameters", {})
        if not input_params:
            return False, "Missing input_parameters"
        
        # Type-specific validation
        analysis_type = metadata["analysis_type"]
        
        if analysis_type == "unit_economics":
            required = ["monthlyRecurringRevenue", "grossMarginPercent", "monthlyChurnRate", "customerAcquisitionCost"]
            missing = [field for field in required if field not in input_params]
            if missing:
                return False, f"Unit economics missing fields: {', '.join(missing)}"
        
        elif analysis_type == "pricing_tiers":
            if "tiers" not in input_params:
                return False, "Pricing tiers missing 'tiers' parameter"
            if not isinstance(input_params["tiers"], list):
                return False, "Tiers must be a list"
        
        elif analysis_type == "freemium_funnel":
            if "stages" not in input_params:
                return False, "Freemium funnel missing 'stages' parameter"
            if not isinstance(input_params["stages"], list):
                return False, "Stages must be a list"
        
        elif analysis_type == "scenario_analysis":
            if "base_params" not in input_params:
                return False, "Scenario analysis missing 'base_params' parameter"
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


# Example usage and test data
if __name__ == "__main__":
    # Test unit economics serialization
    test_input = {
        "monthlyRecurringRevenue": 100,
        "grossMarginPercent": 80,
        "monthlyChurnRate": 5,
        "customerAcquisitionCost": 500
    }
    
    test_results = {
        "ltv": 1600,
        "ltv_cac_ratio": 3.2,
        "status": "Healthy",
        "payback_months": 6.25
    }
    
    # Serialize
    json_output = serialize_analysis(
        analysis_type="unit_economics",
        input_params=test_input,
        results=test_results,
        title="Test Unit Economics",
        description="Example analysis for testing"
    )
    
    print("Serialized Analysis:")
    print(json_output[:200] + "...")
    
    # Deserialize
    loaded_data = deserialize_analysis(json_output)
    print(f"\nLoaded analysis ID: {loaded_data['id']}")
    print(f"Analysis type: {loaded_data['metadata']['analysis_type']}")
    print(f"LTV result: {loaded_data['results']['ltv']}")