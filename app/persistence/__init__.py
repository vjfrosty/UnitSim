"""
UnitSim Persistence Module
=========================

Data persistence and management for UnitSim analysis results.
Provides SQLite-based storage with versioning, metadata, and export tracking.
"""

from .database import (
    AnalysisDatabase,
    get_database,
    save_analysis_quick,
    load_analysis_quick,
    list_recent_analyses,
    search_analyses_by_type
)

__all__ = [
    'AnalysisDatabase',
    'get_database',
    'save_analysis_quick',
    'load_analysis_quick',
    'list_recent_analyses',
    'search_analyses_by_type'
]

# Module metadata
__version__ = "2.0.0"
__author__ = "UnitSim Development Team"
__description__ = "Analysis persistence and data management for UnitSim"