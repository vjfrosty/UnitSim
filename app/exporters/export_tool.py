"""
MCP Export Analysis Tool
========================

Provides export functionality as an MCP tool for downloading analysis results
in multiple formats (PDF, CSV, Excel, JSON) with persistence integration.
"""

from typing import Dict, Any, List, Optional
import base64
from datetime import datetime

from .pdf_generator import generate_pdf_report
from .csv_exporter import export_to_csv, export_to_excel
from .json_serializer import serialize_analysis, export_configuration_only
from persistence.database import get_database


def export_analysis_tool(
    analysis_type: str,
    input_parameters: Dict[str, Any],
    results: Dict[str, Any],
    export_format: str = "pdf",
    title: Optional[str] = None,
    description: Optional[str] = None,
    include_charts: bool = True,
    save_to_database: bool = True,
    configuration_only: bool = False
) -> Dict[str, Any]:
    """
    Export analysis results in specified format
    
    Args:
        analysis_type: Type of analysis ('unit_economics', 'pricing_tiers', etc.)
        input_parameters: Original analysis input parameters
        results: Calculated analysis results
        export_format: Output format ('pdf', 'csv', 'excel', 'json')
        title: Optional custom title for export
        description: Optional description
        include_charts: Whether to include visualizations (PDF only)
        save_to_database: Whether to save analysis to database
        configuration_only: For JSON, export only input configuration
    
    Returns:
        Dictionary with export data and metadata
    """
    
    # Validate inputs
    if not analysis_type:
        raise ValueError("analysis_type is required")
    
    if not input_parameters:
        raise ValueError("input_parameters is required")
    
    valid_formats = ["pdf", "csv", "excel", "json"]
    if export_format not in valid_formats:
        raise ValueError(f"export_format must be one of: {', '.join(valid_formats)}")
    
    valid_analysis_types = ["unit_economics", "pricing_tiers", "freemium_funnel", "scenario_analysis"]
    if analysis_type not in valid_analysis_types:
        raise ValueError(f"analysis_type must be one of: {', '.join(valid_analysis_types)}")
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    title_safe = (title or f"{analysis_type}_analysis").replace(' ', '_').lower()
    filename = f"unitsim_{title_safe}_{timestamp}"
    
    try:
        # Generate export based on format
        if export_format == "pdf":
            export_data = generate_pdf_report(
                analysis_type=analysis_type,
                input_params=input_parameters,
                results=results,
                title=title,
                description=description,
                include_charts=include_charts
            )
            filename += ".pdf"
            content_type = "application/pdf"
            
        elif export_format == "csv":
            export_data = export_to_csv(
                analysis_type=analysis_type,
                input_params=input_parameters,
                results=results,
                include_summary=True
            ).encode('utf-8')
            filename += ".csv"
            content_type = "text/csv"
            
        elif export_format == "excel":
            export_data = export_to_excel(
                analysis_type=analysis_type,
                input_params=input_parameters,
                results=results
            )
            filename += ".xlsx"
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        elif export_format == "json":
            if configuration_only:
                export_text = export_configuration_only(
                    analysis_type=analysis_type,
                    input_params=input_parameters,
                    title=title
                )
                filename += "_config.json"
            else:
                export_text = serialize_analysis(
                    analysis_type=analysis_type,
                    input_params=input_parameters,
                    results=results,
                    title=title,
                    description=description,
                    include_results=True
                )
                filename += ".json"
            
            export_data = export_text.encode('utf-8')
            content_type = "application/json"
        
        # Save to database if requested
        analysis_id = None
        if save_to_database and not configuration_only:
            try:
                db = get_database()
                analysis_id = db.save_analysis(
                    analysis_type=analysis_type,
                    input_params=input_parameters,
                    results=results,
                    title=title,
                    description=description,
                    tags=[analysis_type, export_format]
                )
                
                # Record export activity
                db.record_export(
                    analysis_id=analysis_id,
                    export_format=export_format,
                    file_size=len(export_data),
                    export_options={
                        "include_charts": include_charts,
                        "configuration_only": configuration_only,
                        "title": title,
                        "description": description
                    }
                )
                
            except Exception as e:
                # Don't fail export if database save fails
                print(f"Warning: Could not save to database: {str(e)}")
        
        # Encode data for transport
        if isinstance(export_data, bytes):
            encoded_data = base64.b64encode(export_data).decode('utf-8')
        else:
            encoded_data = base64.b64encode(export_data.encode('utf-8')).decode('utf-8')
        
        # Prepare response
        response = {
            "success": True,
            "export_format": export_format,
            "filename": filename,
            "content_type": content_type,
            "file_size": len(export_data),
            "data": encoded_data,
            "encoding": "base64",
            "analysis_type": analysis_type,
            "created_at": datetime.now().isoformat(),
            "configuration_only": configuration_only
        }
        
        # Add analysis ID if saved to database
        if analysis_id:
            response["analysis_id"] = analysis_id
            response["database_saved"] = True
        else:
            response["database_saved"] = False
        
        # Add format-specific metadata
        if export_format == "pdf":
            response["metadata"] = {
                "pages_estimated": len(export_data) // 50000,  # Rough estimate
                "includes_charts": include_charts,
                "report_type": "comprehensive_analysis"
            }
        elif export_format == "excel":
            response["metadata"] = {
                "format": "multi_sheet_workbook",
                "sheets_included": ["Summary", "Details", "Calculations"]
            }
        elif export_format == "json":
            response["metadata"] = {
                "format_version": "1.0",
                "serialization": "complete_analysis",
                "configuration_only": configuration_only
            }
        elif export_format == "csv":
            response["metadata"] = {
                "format": "comma_separated_values",
                "encoding": "utf-8",
                "includes_summary": True
            }
        
        # Add usage instructions
        response["usage_instructions"] = _get_usage_instructions(export_format)
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "analysis_type": analysis_type,
            "export_format": export_format,
            "created_at": datetime.now().isoformat()
        }


def list_saved_analyses_tool(
    analysis_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List saved analyses from database
    
    Args:
        analysis_type: Optional filter by analysis type
        limit: Maximum results to return (max 100)
        offset: Number of results to skip for pagination
    
    Returns:
        Dictionary with analysis list and metadata
    """
    
    try:
        # Validate inputs
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 20
            
        if offset < 0:
            offset = 0
        
        db = get_database()
        
        # Get analyses
        analyses = db.list_analyses(
            analysis_type=analysis_type,
            limit=limit,
            offset=offset
        )
        
        # Get database stats
        stats = db.get_database_stats()
        
        return {
            "success": True,
            "analyses": analyses,
            "count": len(analyses),
            "offset": offset,
            "limit": limit,
            "filter_type": analysis_type,
            "database_stats": stats,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "retrieved_at": datetime.now().isoformat()
        }


def load_saved_analysis_tool(analysis_id: str) -> Dict[str, Any]:
    """
    Load saved analysis from database
    
    Args:
        analysis_id: Analysis identifier
    
    Returns:
        Dictionary with analysis data or error
    """
    
    try:
        if not analysis_id:
            raise ValueError("analysis_id is required")
        
        db = get_database()
        
        # Load analysis
        analysis = db.load_analysis(analysis_id)
        
        if analysis is None:
            return {
                "success": False,
                "error": "Analysis not found",
                "analysis_id": analysis_id,
                "retrieved_at": datetime.now().isoformat()
            }
        
        # Get version history
        versions = db.get_analysis_versions(analysis_id)
        
        # Get export history
        exports = db.get_export_history(analysis_id)
        
        return {
            "success": True,
            "analysis": analysis,
            "version_history": versions,
            "export_history": exports,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "analysis_id": analysis_id,
            "retrieved_at": datetime.now().isoformat()
        }


def delete_saved_analysis_tool(
    analysis_id: str,
    permanent: bool = False
) -> Dict[str, Any]:
    """
    Delete or archive saved analysis
    
    Args:
        analysis_id: Analysis identifier
        permanent: If True, permanently delete; otherwise archive
    
    Returns:
        Dictionary with deletion status
    """
    
    try:
        if not analysis_id:
            raise ValueError("analysis_id is required")
        
        db = get_database()
        
        # Delete analysis
        success = db.delete_analysis(analysis_id, permanent=permanent)
        
        if not success:
            return {
                "success": False,
                "error": "Analysis not found",
                "analysis_id": analysis_id,
                "action": "permanent_delete" if permanent else "archive"
            }
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "action": "permanent_delete" if permanent else "archive",
            "message": f"Analysis {'permanently deleted' if permanent else 'archived'} successfully",
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "analysis_id": analysis_id,
            "action": "permanent_delete" if permanent else "archive"
        }


def _get_usage_instructions(export_format: str) -> Dict[str, str]:
    """Get format-specific usage instructions"""
    
    instructions = {
        "pdf": {
            "description": "Professional report with comprehensive analysis and visualizations",
            "usage": "Download and open with any PDF viewer (Adobe Reader, browser, etc.)",
            "best_for": "Presentations, stakeholder reports, comprehensive documentation"
        },
        "csv": {
            "description": "Comma-separated values for data analysis and processing",
            "usage": "Open with Excel, Google Sheets, or import into data analysis tools",
            "best_for": "Data processing, further analysis, integration with other tools"
        },
        "excel": {
            "description": "Multi-sheet Excel workbook with organized data and summaries",
            "usage": "Open with Microsoft Excel, LibreOffice Calc, or Google Sheets",
            "best_for": "Detailed analysis, data manipulation, financial modeling"
        },
        "json": {
            "description": "Structured data format for programmatic access and sharing",
            "usage": "Load into applications, APIs, or configuration management systems",
            "best_for": "Integration with other systems, configuration sharing, data exchange"
        }
    }
    
    return instructions.get(export_format, {
        "description": "Exported analysis data",
        "usage": "Use appropriate application for the file format",
        "best_for": "Data sharing and analysis"
    })


# Export the tool functions for MCP server integration
__all__ = [
    'export_analysis_tool',
    'list_saved_analyses_tool', 
    'load_saved_analysis_tool',
    'delete_saved_analysis_tool'
]