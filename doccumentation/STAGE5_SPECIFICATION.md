# Stage 5: Export & Persistence - Technical Specification

**Project:** UnitSim - Unit Economics & Pricing Simulator MCP  
**Stage:** 5 - Export & Persistence  
**Start Date:** October 18, 2025  
**Target Completion:** 3-5 days  
**Complexity:** Medium

---

## 🎯 Overview

Stage 5 adds comprehensive export and data persistence capabilities to UnitSim, enabling users to:
- Generate professional PDF reports with charts and analysis
- Export data in multiple formats (CSV, Excel, JSON)
- Save and load analysis configurations
- Share analysis results with team members
- Track historical analysis over time

---

## 📋 Export Formats Supported

### 1. PDF Reports
```python
# Professional analysis reports with:
- Executive summary with key metrics
- Detailed calculations and assumptions  
- Charts and visualizations
- Recommendations and insights
- Company branding options
```

### 2. CSV/Excel Data Export
```python
# Structured data tables including:
- Raw calculation results
- Input parameters and assumptions
- Statistical summaries (Stage 4)
- Time-series data for tracking
- Import-ready format for other tools
```

### 3. JSON Configuration Export
```python
# Complete analysis state including:
- All input parameters
- Calculator settings
- Analysis results
- Metadata and timestamps
- Shareable configuration files
```

---

## 🏗️ Architecture Design

### Export Engine Structure
```python
/app/exporters/
├── __init__.py              # Export module initialization
├── pdf_generator.py         # PDF report generation (reportlab)
├── csv_exporter.py          # CSV/Excel export functions 
├── json_serializer.py       # JSON configuration handling
├── chart_generator.py       # Chart/graph generation for PDFs
└── templates/
    ├── unit_economics.html  # HTML template for PDF conversion
    ├── pricing_tiers.html   # Pricing analysis template
    ├── funnel_analysis.html # Funnel analysis template
    └── scenario_analysis.html # Monte Carlo/sensitivity template
```

### Persistence Layer
```python
/app/persistence/
├── __init__.py              # Persistence module
├── database.py              # SQLite database operations
├── models.py                # Data models and schemas
└── migrations/              # Database schema updates
    └── 001_initial.sql      # Initial database schema
```

---

## 📊 Database Schema

### Analysis Results Table
```sql
CREATE TABLE analysis_results (
    id TEXT PRIMARY KEY,
    analysis_type TEXT NOT NULL,  -- 'unit_economics', 'pricing_tiers', etc.
    input_params TEXT NOT NULL,   -- JSON of input parameters
    results TEXT NOT NULL,        -- JSON of calculation results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title TEXT,
    description TEXT,
    tags TEXT                     -- Comma-separated tags
);
```

### Export History Table
```sql
CREATE TABLE export_history (
    id TEXT PRIMARY KEY,
    analysis_id TEXT REFERENCES analysis_results(id),
    export_format TEXT NOT NULL, -- 'pdf', 'csv', 'json'
    export_params TEXT,          -- JSON of export settings
    file_path TEXT,              -- Local file path (if saved)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🛠️ Implementation Functions

### 1. PDF Report Generator (`pdf_generator.py`)

```python
def generate_pdf_report(
    analysis_data: Dict[str, Any],
    analysis_type: str,
    template_options: Dict[str, Any] = None
) -> bytes:
    """
    Generate professional PDF report from analysis data
    
    Args:
        analysis_data: Complete analysis results
        analysis_type: Type of analysis ('unit_economics', 'pricing_tiers', etc.)
        template_options: PDF formatting options
    
    Returns:
        PDF content as bytes
    """
```

**PDF Features:**
- **Executive Summary**: Key metrics and recommendations
- **Methodology Section**: Assumptions and calculations used
- **Charts and Graphs**: Visual representation of data
- **Data Tables**: Detailed numerical results
- **Appendix**: Raw data and technical details
- **Branding**: Company logo and color scheme options

### 2. CSV/Excel Exporter (`csv_exporter.py`)

```python
def export_to_csv(
    analysis_data: Dict[str, Any],
    include_metadata: bool = True
) -> str:
    """Export analysis results to CSV format"""

def export_to_excel(
    analysis_data: Dict[str, Any],
    multi_sheet: bool = True
) -> bytes:
    """Export analysis results to Excel with multiple sheets"""
```

**Excel Features:**
- **Multiple Sheets**: Separate sheets for inputs, outputs, charts
- **Formatted Tables**: Professional styling with headers
- **Embedded Charts**: Excel charts for visualization
- **Data Validation**: Input ranges and constraints
- **Formulas**: Calculation transparency

### 3. JSON Serializer (`json_serializer.py`)

```python
def serialize_analysis(
    analysis_data: Dict[str, Any],
    include_results: bool = True
) -> str:
    """Serialize analysis to shareable JSON format"""

def deserialize_analysis(
    json_data: str
) -> Dict[str, Any]:
    """Load analysis from JSON configuration"""
```

### 4. Chart Generator (`chart_generator.py`)

```python
def generate_charts(
    analysis_type: str,
    data: Dict[str, Any]
) -> List[bytes]:
    """
    Generate charts for PDF inclusion
    
    Supported chart types:
    - Unit Economics: LTV/CAC ratio trends
    - Pricing Tiers: Revenue distribution bar chart
    - Funnel Analysis: Conversion flow diagrams
    - Scenario Analysis: Monte Carlo histograms, tornado diagrams
    """
```

---

## 🔧 MCP Tool Specification

### `export_analysis_tool()`

```python
@mcp.tool()
async def export_analysis_tool(
    analysis_data: Dict[str, Any],
    export_format: str = "pdf",           # "pdf", "csv", "excel", "json"
    template_name: str = "standard",      # "standard", "executive", "technical"
    include_charts: bool = True,
    include_raw_data: bool = False,
    save_to_history: bool = True
) -> str:
    """
    Export analysis results in specified format
    
    Formats:
    - pdf: Professional report with charts and analysis
    - csv: Comma-separated values for data analysis
    - excel: Multi-sheet Excel workbook with charts
    - json: Configuration file for sharing/loading
    
    Templates (PDF only):
    - standard: Balanced report with summary and details
    - executive: High-level summary for leadership
    - technical: Detailed calculations and methodology
    """
```

**Input Validation:**
```python
# Validate export format
if export_format not in ["pdf", "csv", "excel", "json"]:
    return "❌ Invalid export format. Use: pdf, csv, excel, or json"

# Validate template name  
if template_name not in ["standard", "executive", "technical"]:
    return "❌ Invalid template. Use: standard, executive, or technical"

# Check analysis data completeness
required_fields = ["analysis_type", "input_params", "results"]
if not all(field in analysis_data for field in required_fields):
    return "❌ Analysis data missing required fields"
```

**Output Format:**
```python
{
    "export_successful": True,
    "export_id": "exp_20251018_143022",
    "format": "pdf",
    "file_size": "2.3 MB",
    "download_ready": True,
    "export_summary": {
        "pages": 8,
        "charts_included": 5,
        "data_points": 247
    }
}
```

---

## 💾 Persistence Functions

### Save Analysis
```python
def save_analysis(
    analysis_type: str,
    input_params: Dict[str, Any],
    results: Dict[str, Any],
    title: str = None,
    description: str = None,
    tags: List[str] = None
) -> str:
    """Save analysis to database and return unique ID"""
```

### Load Analysis
```python
def load_analysis(analysis_id: str) -> Dict[str, Any]:
    """Load saved analysis by ID"""

def list_saved_analyses(
    analysis_type: str = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """List saved analyses with optional filtering"""
```

### Analysis History
```python
def get_analysis_history(
    analysis_type: str = None,
    days_back: int = 30
) -> List[Dict[str, Any]]:
    """Get historical analysis results for tracking trends"""
```

---

## 🎨 HTML Export Interface

### Export Control Panel (`assets/export_controls.html`)

```html
<!-- Export Format Selection -->
<div class="export-format-selector">
    <label>Export Format:</label>
    <select id="export-format">
        <option value="pdf">PDF Report</option>
        <option value="excel">Excel Workbook</option>
        <option value="csv">CSV Data</option>
        <option value="json">JSON Configuration</option>
    </select>
</div>

<!-- PDF Template Options -->
<div class="pdf-template-options" id="pdf-options">
    <label>Report Template:</label>
    <select id="pdf-template">
        <option value="standard">Standard Report</option>
        <option value="executive">Executive Summary</option>
        <option value="technical">Technical Details</option>
    </select>
</div>

<!-- Export Options -->
<div class="export-options">
    <label>
        <input type="checkbox" id="include-charts" checked>
        Include Charts and Visualizations
    </label>
    <label>
        <input type="checkbox" id="include-raw-data">
        Include Raw Data Tables
    </label>
</div>

<!-- Download Controls -->
<div class="download-controls">
    <button id="generate-export" class="export-btn">
        📄 Generate Export
    </button>
    <button id="save-analysis" class="save-btn">
        💾 Save Analysis
    </button>
</div>
```

---

## 📈 PDF Templates

### Standard Template Structure
```
1. Cover Page
   - Analysis Title
   - Date and Parameters
   - Company Branding

2. Executive Summary (1 page)
   - Key Findings
   - Critical Metrics
   - Recommendations

3. Methodology (1 page)
   - Input Assumptions
   - Calculation Methods
   - Data Sources

4. Detailed Analysis (3-5 pages)
   - Charts and Visualizations
   - Data Tables
   - Scenario Comparisons

5. Appendix (1-2 pages)
   - Raw Data
   - Technical Notes
   - Definitions
```

### Executive Template (Condensed)
```
1. Executive Summary (2 pages)
   - Key Metrics Dashboard
   - Strategic Recommendations
   - Risk Assessment

2. Supporting Data (1 page)
   - Critical Charts Only
   - Summary Tables
```

### Technical Template (Detailed)
```
1. Methodology Deep-Dive (2 pages)
2. Complete Data Analysis (4-6 pages)  
3. Statistical Appendix (2-3 pages)
4. Raw Data Tables (2-4 pages)
```

---

## 🚀 Implementation Timeline

### Phase 5.1: Export Foundation (1 day)
- [x] Plan architecture and dependencies
- [ ] Set up export module structure
- [ ] Install required packages (reportlab, pandas, openpyxl)
- [ ] Create basic PDF generator

### Phase 5.2: Data Export (1 day)
- [ ] Implement CSV/Excel export functions
- [ ] Create JSON serialization
- [ ] Build chart generation for PDFs
- [ ] Test export formats

### Phase 5.3: Persistence Layer (1 day)
- [ ] Design database schema
- [ ] Implement SQLite operations
- [ ] Create save/load functions
- [ ] Add analysis history tracking

### Phase 5.4: MCP Integration (1 day)
- [ ] Create `export_analysis_tool()`
- [ ] Add tool to server.py
- [ ] Implement format validation
- [ ] Test tool integration

### Phase 5.5: UI & Testing (1 day)
- [ ] Design export controls interface
- [ ] Create HTML component
- [ ] Test all export formats
- [ ] Validate PDF generation

---

## 📋 Dependencies to Add

### requirements.txt Updates
```python
# Existing dependencies
fastmcp==2.12.5
fastapi
pydantic

# New Stage 5 dependencies
reportlab>=4.0.0        # PDF generation
pandas>=2.0.0           # Data manipulation and CSV/Excel
openpyxl>=3.1.0         # Excel file creation
matplotlib>=3.7.0       # Chart generation for PDFs
Pillow>=10.0.0          # Image processing for charts
sqlite3                 # Built into Python (persistence)
```

---

## 🎯 Success Criteria

- [ ] **PDF Generation**: Professional reports with charts and tables
- [ ] **Multiple Formats**: CSV, Excel, JSON export working
- [ ] **Data Persistence**: Save/load analysis configurations
- [ ] **Chart Integration**: Visual elements in PDF reports
- [ ] **Performance**: Export generation under 10 seconds
- [ ] **File Size**: PDF reports under 5MB
- [ ] **Template Quality**: Professional appearance suitable for presentations
- [ ] **Data Integrity**: Exported data matches analysis results exactly

---

This specification provides the foundation for implementing comprehensive export and persistence capabilities that will complete the UnitSim platform with professional-grade reporting and data management features.