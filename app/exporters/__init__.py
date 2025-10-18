"""
UnitSim Export Module
====================

Comprehensive export functionality for UnitSim analysis results.
Supports PDF reports, CSV/Excel data export, JSON serialization, and data persistence.
"""

# PDF Generation
from .pdf_generator import generate_pdf_report

# CSV/Excel Export  
from .csv_exporter import export_to_csv, export_to_excel

# JSON Serialization
from .json_serializer import serialize_analysis, deserialize_analysis, export_configuration_only

# Export Tool Integration
from .export_tool import (
    export_analysis_tool,
    list_saved_analyses_tool,
    load_saved_analysis_tool,
    delete_saved_analysis_tool
)

# Main exports
__all__ = [
    # PDF Generation
    'generate_pdf_report',
    
    # Data Export
    'export_to_csv',
    'export_to_excel', 
    
    # JSON Serialization
    'serialize_analysis',
    'deserialize_analysis',
    'export_configuration_only',
    
    # MCP Tool Functions
    'export_analysis_tool',
    'list_saved_analyses_tool',
    'load_saved_analysis_tool',
    'delete_saved_analysis_tool'
]

# Module metadata
__version__ = "2.0.0"
__author__ = "UnitSim Development Team"
__description__ = "Export and serialization tools for UnitSim analysis"

# These imports are already above, removing duplicates

__all__ = [
    # PDF Generation
    'generate_pdf_report',
    'PDFTemplate',
    
    # Data Export
    'export_to_csv',
    'export_to_excel',
    
    # JSON Serialization
    'serialize_analysis',
    'deserialize_analysis',
    
    # Chart Generation
    'generate_charts',
    'ChartType'
]