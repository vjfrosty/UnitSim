"""
Data Persistence Layer for UnitSim Analysis
==========================================

SQLite-based persistence for saving, loading, and managing analysis results
with versioning and metadata support.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


class AnalysisDatabase:
    """SQLite database manager for UnitSim analysis persistence"""
    
    def __init__(self, db_path: str = "/srv/unitsim/data/unitsim.db"):
        """
        Initialize database connection and create tables
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    analysis_type TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    input_parameters TEXT NOT NULL,
                    results TEXT,
                    metadata TEXT,
                    tags TEXT,
                    version INTEGER DEFAULT 1,
                    is_archived BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    input_parameters TEXT NOT NULL,
                    results TEXT,
                    change_summary TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS export_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    export_format TEXT NOT NULL,
                    exported_at TIMESTAMP NOT NULL,
                    file_size INTEGER,
                    export_options TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses (id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses (analysis_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses (created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_versions_analysis ON analysis_versions (analysis_id)")
            
            conn.commit()
    
    def save_analysis(
        self,
        analysis_type: str,
        input_params: Dict[str, Any],
        results: Dict[str, Any],
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        analysis_id: Optional[str] = None
    ) -> str:
        """
        Save analysis to database
        
        Args:
            analysis_type: Type of analysis
            input_params: Input parameters
            results: Analysis results
            title: Optional title
            description: Optional description
            tags: Optional tags list
            analysis_id: Optional existing ID (for updates)
        
        Returns:
            Analysis ID
        """
        
        if analysis_id is None:
            # Create new analysis
            analysis_id = f"unitsim_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            is_new = True
        else:
            # Update existing analysis
            is_new = False
        
        now = datetime.now()
        
        # Prepare data for storage
        input_json = json.dumps(input_params)
        results_json = json.dumps(results)
        tags_json = json.dumps(tags or [])
        metadata_json = json.dumps({
            "created_with": "UnitSim 2.0",
            "analysis_engine_version": "2.0.0",
            "calculation_timestamp": now.isoformat()
        })
        
        with sqlite3.connect(self.db_path) as conn:
            if is_new:
                # Insert new analysis
                conn.execute("""
                    INSERT INTO analyses (
                        id, analysis_type, title, description, created_at, updated_at,
                        input_parameters, results, metadata, tags, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    analysis_id, analysis_type, title, description, now, now,
                    input_json, results_json, metadata_json, tags_json
                ))
                
                # Save initial version
                conn.execute("""
                    INSERT INTO analysis_versions (
                        analysis_id, version, created_at, input_parameters, results, change_summary
                    ) VALUES (?, 1, ?, ?, ?, 'Initial version')
                """, (analysis_id, now, input_json, results_json))
                
            else:
                # Update existing analysis
                # Get current version
                cursor = conn.execute("SELECT version FROM analyses WHERE id = ?", (analysis_id,))
                current_version = cursor.fetchone()
                if current_version is None:
                    raise ValueError(f"Analysis {analysis_id} not found")
                
                new_version = current_version[0] + 1
                
                # Update main record
                conn.execute("""
                    UPDATE analyses SET
                        title = ?, description = ?, updated_at = ?,
                        input_parameters = ?, results = ?, metadata = ?, tags = ?, version = ?
                    WHERE id = ?
                """, (
                    title, description, now, input_json, results_json,
                    metadata_json, tags_json, new_version, analysis_id
                ))
                
                # Save new version
                conn.execute("""
                    INSERT INTO analysis_versions (
                        analysis_id, version, created_at, input_parameters, results, change_summary
                    ) VALUES (?, ?, ?, ?, ?, 'Updated analysis')
                """, (analysis_id, new_version, now, input_json, results_json))
            
            conn.commit()
        
        return analysis_id
    
    def load_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Load analysis by ID
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            Analysis data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            
            cursor = conn.execute("""
                SELECT * FROM analyses WHERE id = ? AND is_archived = FALSE
            """, (analysis_id,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return {
                "id": row["id"],
                "analysis_type": row["analysis_type"],
                "title": row["title"],
                "description": row["description"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "input_parameters": json.loads(row["input_parameters"]),
                "results": json.loads(row["results"]) if row["results"] else {},
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                "tags": json.loads(row["tags"]) if row["tags"] else [],
                "version": row["version"]
            }
    
    def list_analyses(
        self,
        analysis_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List saved analyses with optional filtering
        
        Args:
            analysis_type: Filter by analysis type
            tags: Filter by tags (any match)
            limit: Maximum results to return
            offset: Number of results to skip
        
        Returns:
            List of analysis summaries
        """
        query = """
            SELECT id, analysis_type, title, description, created_at, updated_at, tags, version
            FROM analyses 
            WHERE is_archived = FALSE
        """
        params = []
        
        if analysis_type:
            query += " AND analysis_type = ?"
            params.append(analysis_type)
        
        if tags:
            # Filter by tags (simplified - check if any tag matches)
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            if tag_conditions:
                query += f" AND ({' OR '.join(tag_conditions)})"
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "analysis_type": row["analysis_type"],
                    "title": row["title"],
                    "description": row["description"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "tags": json.loads(row["tags"]) if row["tags"] else [],
                    "version": row["version"]
                })
            
            return results
    
    def delete_analysis(self, analysis_id: str, permanent: bool = False) -> bool:
        """
        Delete or archive analysis
        
        Args:
            analysis_id: Analysis to delete
            permanent: If True, permanently delete; otherwise archive
        
        Returns:
            True if successful, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            if permanent:
                # Permanent deletion
                cursor = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
                conn.execute("DELETE FROM analysis_versions WHERE analysis_id = ?", (analysis_id,))
                conn.execute("DELETE FROM export_history WHERE analysis_id = ?", (analysis_id,))
            else:
                # Archive (soft delete)
                cursor = conn.execute(
                    "UPDATE analyses SET is_archived = TRUE WHERE id = ?",
                    (analysis_id,)
                )
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_analysis_versions(self, analysis_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for analysis
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            List of version records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT version, created_at, change_summary
                FROM analysis_versions
                WHERE analysis_id = ?
                ORDER BY version DESC
            """, (analysis_id,))
            
            return [
                {
                    "version": row["version"],
                    "created_at": row["created_at"],
                    "change_summary": row["change_summary"]
                }
                for row in cursor.fetchall()
            ]
    
    def load_analysis_version(self, analysis_id: str, version: int) -> Optional[Dict[str, Any]]:
        """
        Load specific version of analysis
        
        Args:
            analysis_id: Analysis identifier
            version: Version number
        
        Returns:
            Analysis data for specific version or None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT av.input_parameters, av.results, av.created_at, a.analysis_type, a.title
                FROM analysis_versions av
                JOIN analyses a ON av.analysis_id = a.id
                WHERE av.analysis_id = ? AND av.version = ?
            """, (analysis_id, version))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return {
                "id": analysis_id,
                "version": version,
                "analysis_type": row["analysis_type"],
                "title": row["title"],
                "created_at": row["created_at"],
                "input_parameters": json.loads(row["input_parameters"]),
                "results": json.loads(row["results"]) if row["results"] else {}
            }
    
    def record_export(
        self,
        analysis_id: str,
        export_format: str,
        file_size: int,
        export_options: Optional[Dict[str, Any]] = None
    ):
        """
        Record export activity for tracking
        
        Args:
            analysis_id: Analysis that was exported
            export_format: Format used (pdf, csv, excel, json)
            file_size: Size of exported file in bytes
            export_options: Optional export configuration
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO export_history (
                    analysis_id, export_format, exported_at, file_size, export_options
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                analysis_id,
                export_format,
                datetime.now(),
                file_size,
                json.dumps(export_options or {})
            ))
            conn.commit()
    
    def get_export_history(self, analysis_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get export history
        
        Args:
            analysis_id: Optional filter by analysis ID
        
        Returns:
            List of export records
        """
        query = """
            SELECT eh.*, a.title, a.analysis_type
            FROM export_history eh
            JOIN analyses a ON eh.analysis_id = a.id
        """
        params = []
        
        if analysis_id:
            query += " WHERE eh.analysis_id = ?"
            params.append(analysis_id)
        
        query += " ORDER BY eh.exported_at DESC LIMIT 100"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            return [
                {
                    "analysis_id": row["analysis_id"],
                    "analysis_title": row["title"],
                    "analysis_type": row["analysis_type"],
                    "export_format": row["export_format"],
                    "exported_at": row["exported_at"],
                    "file_size": row["file_size"],
                    "export_options": json.loads(row["export_options"]) if row["export_options"] else {}
                }
                for row in cursor.fetchall()
            ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Count analyses by type
            type_counts = {}
            cursor = conn.execute("""
                SELECT analysis_type, COUNT(*) as count
                FROM analyses
                WHERE is_archived = FALSE
                GROUP BY analysis_type
            """)
            for row in cursor.fetchall():
                type_counts[row[0]] = row[1]
            
            # Total analyses
            cursor = conn.execute("SELECT COUNT(*) FROM analyses WHERE is_archived = FALSE")
            total_analyses = cursor.fetchone()[0]
            
            # Total exports
            cursor = conn.execute("SELECT COUNT(*) FROM export_history")
            total_exports = cursor.fetchone()[0]
            
            # Database file size
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            
            return {
                "total_analyses": total_analyses,
                "analyses_by_type": type_counts,
                "total_exports": total_exports,
                "database_size_bytes": db_size,
                "database_path": self.db_path
            }


# Global database instance
_db_instance = None

def get_database() -> AnalysisDatabase:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = AnalysisDatabase()
    return _db_instance


# Convenience functions for common operations

def save_analysis_quick(
    analysis_type: str,
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    title: Optional[str] = None
) -> str:
    """Quick save without full parameter control"""
    db = get_database()
    return db.save_analysis(analysis_type, input_params, results, title=title)


def load_analysis_quick(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Quick load by ID"""
    db = get_database()
    return db.load_analysis(analysis_id)


def list_recent_analyses(limit: int = 10) -> List[Dict[str, Any]]:
    """List most recent analyses"""
    db = get_database()
    return db.list_analyses(limit=limit)


def search_analyses_by_type(analysis_type: str) -> List[Dict[str, Any]]:
    """Search analyses by type"""
    db = get_database()
    return db.list_analyses(analysis_type=analysis_type)


# Example usage and testing
if __name__ == "__main__":
    # Test database operations
    db = AnalysisDatabase("/tmp/test_unitsim.db")
    
    # Test save
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
        "payback_months": 6.25
    }
    
    # Save analysis
    analysis_id = db.save_analysis(
        "unit_economics",
        test_params,
        test_results,
        title="Test Unit Economics Analysis",
        description="Test analysis for persistence layer",
        tags=["test", "unit_economics"]
    )
    
    print(f"Saved analysis: {analysis_id}")
    
    # Load analysis
    loaded = db.load_analysis(analysis_id)
    if loaded:
        print(f"Loaded analysis: {loaded['title']}")
        print(f"LTV: {loaded['results']['ltv']}")
    
    # List analyses
    analyses = db.list_analyses()
    print(f"Found {len(analyses)} analyses")
    
    # Database stats
    stats = db.get_database_stats()
    print(f"Database stats: {stats}")
    
    # Clean up test database
    import os
    os.unlink("/tmp/test_unitsim.db")