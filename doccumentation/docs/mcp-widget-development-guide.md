# MCP Widget Development Guide

Complete guide to building Model Context Protocol (MCP) servers with interactive widgets for ChatGPT and other MCP clients.

## Table of Contents

1. [Understanding MCP Widgets](#understanding-mcp-widgets)
2. [Core Architecture](#core-architecture)
3. [Widget Data Structure](#widget-data-structure)
4. [Tool Implementation Patterns](#tool-implementation-patterns)
5. [Resource Management](#resource-management)
6. [Metadata Configuration](#metadata-configuration)
7. [Input Validation](#input-validation)
8. [Structured Content](#structured-content)
9. [Error Handling](#error-handling)
10. [Complete Examples](#complete-examples)

---

## Understanding MCP Widgets

### What Are MCP Widgets?

MCP widgets are interactive HTML components that render inside ChatGPT when a tool is invoked. They provide rich, visual experiences beyond plain text responses.

**Key Features:**
- **Visual representation** of data (maps, carousels, 3D scenes, lists)
- **Interactive elements** that respond to user input
- **Structured data** passed from server to widget
- **Embedded resources** containing HTML/CSS/JS

**Use Cases:**
- Data visualization (charts, graphs, maps)
- Interactive galleries (images, albums, carousels)
- 3D scenes (solar system, molecular structures)
- Lists and tables with rich formatting
- Forms and interactive controls

---

## Core Architecture

### MCP Server Components

```
┌─────────────────────────────────────────────────┐
│                 MCP Server                       │
├─────────────────────────────────────────────────┤
│  1. Widget Definitions (data structures)        │
│  2. Tools (callable functions)                   │
│  3. Resources (HTML/CSS/JS assets)              │
│  4. Request Handlers (tool calls, resources)    │
│  5. Transport Layer (SSE, streamable-http)      │
└─────────────────────────────────────────────────┘
         ↓
    HTTP/HTTPS
         ↓
┌─────────────────────────────────────────────────┐
│              MCP Client (ChatGPT)               │
├─────────────────────────────────────────────────┤
│  1. Discovers tools via tools/list              │
│  2. Calls tools with parameters                 │
│  3. Receives structured content + widget HTML   │
│  4. Renders widget in UI                        │
└─────────────────────────────────────────────────┘
```

### Flow of Execution

```
1. Client connects → Server announces capabilities
2. Client requests tools/list → Server returns tool definitions
3. User invokes tool → Client sends tools/call with arguments
4. Server validates input → Processes request
5. Server returns result → Includes:
   - Text content (visible to user)
   - Structured content (data for widget)
   - Embedded resource (HTML/CSS/JS)
   - Metadata (widget configuration)
6. Client renders widget → Hydrates with structured content
```

---

## Widget Data Structure

### Core Widget Definition

```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Widget:
    """Immutable widget definition."""
    
    # Unique identifier for the tool
    identifier: str
    
    # Human-readable title
    title: str
    
    # URI where the widget HTML is stored
    template_uri: str
    
    # Status message while tool is running
    invoking: str
    
    # Status message when tool completes
    invoked: str
    
    # The actual HTML content
    html: str
    
    # Text response to show user
    response_text: str
```

### Example Widget Definitions

```python
# Map Widget
map_widget = Widget(
    identifier="pizza-map",
    title="Show Pizza Map",
    template_uri="ui://widget/pizza-map.html",
    invoking="Hand-tossing a map",
    invoked="Served a fresh map",
    html=load_html("pizzaz-map.html"),
    response_text="Rendered a pizza map with your selected topping!"
)

# Carousel Widget
carousel_widget = Widget(
    identifier="pizza-carousel",
    title="Show Pizza Carousel",
    template_uri="ui://widget/pizza-carousel.html",
    invoking="Spinning up a carousel",
    invoked="Carousel ready",
    html=load_html("pizzaz-carousel.html"),
    response_text="Rendered a carousel of pizza places!"
)

# 3D Scene Widget
solar_widget = Widget(
    identifier="solar-system",
    title="Explore Solar System",
    template_uri="ui://widget/solar-system.html",
    invoking="Charting the solar system",
    invoked="Solar system ready",
    html=load_html("solar-system.html"),
    response_text="Centered view on the requested planet"
)
```

### Widget Collections

```python
# Create a registry of widgets
widgets: List[Widget] = [
    map_widget,
    carousel_widget,
    list_widget,
    album_widget
]

# Index by identifier for fast tool lookup
WIDGETS_BY_ID = {w.identifier: w for w in widgets}

# Index by URI for resource requests
WIDGETS_BY_URI = {w.template_uri: w for w in widgets}
```

---

## Tool Implementation Patterns

### Pattern 1: Simple Single-Widget Tool

Use when you have one widget with straightforward input/output.

```python
from pydantic import BaseModel, Field, ConfigDict

# Define input schema
class ToolInput(BaseModel):
    parameter: str = Field(
        ...,
        description="Description of what this parameter does"
    )
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid"
    )

# Register tool
@mcp._mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="my-tool",
            title="My Tool Title",
            description="What this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "parameter": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["parameter"]
            },
            _meta=tool_meta(widget)
        )
    ]

# Handle tool call
async def call_tool(req: types.CallToolRequest) -> types.ServerResult:
    # Validate input
    try:
        payload = ToolInput.model_validate(req.params.arguments)
    except ValidationError as exc:
        return error_result(f"Invalid input: {exc}")
    
    # Process request
    result_data = process(payload.parameter)
    
    # Return with widget
    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text="Operation successful"
                )
            ],
            structuredContent=result_data,
            _meta={
                "openai.com/widget": embedded_resource(widget),
                **widget_metadata(widget)
            }
        )
    )
```

### Pattern 2: Multi-Widget Tool Registry

Use when you have multiple similar widgets (like pizza examples).

```python
# Define shared input schema
class SharedInput(BaseModel):
    topping: str = Field(..., alias="pizzaTopping")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

# Register all widgets as tools
@mcp._mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name=widget.identifier,
            title=widget.title,
            description=widget.title,
            inputSchema=SHARED_INPUT_SCHEMA,
            _meta=tool_meta(widget)
        )
        for widget in widgets
    ]

# Single handler for all tools
async def call_tool(req: types.CallToolRequest) -> types.ServerResult:
    # Look up which widget was called
    widget = WIDGETS_BY_ID.get(req.params.name)
    if not widget:
        return error_result(f"Unknown tool: {req.params.name}")
    
    # Validate input
    try:
        payload = SharedInput.model_validate(req.params.arguments)
    except ValidationError as exc:
        return error_result(f"Invalid input: {exc}")
    
    # Return widget with data
    return success_result(
        widget=widget,
        text=widget.response_text,
        structured_data={"pizzaTopping": payload.topping}
    )
```

### Pattern 3: Complex Tool with Normalization

Use when input needs validation, normalization, or mapping.

```python
# Define input with defaults and aliases
class SolarInput(BaseModel):
    planet_name: str = Field(
        "Earth",
        alias="planetName",
        description="Planet name (case insensitive)"
    )
    auto_orbit: bool = Field(
        True,
        alias="autoOrbit",
        description="Keep camera orbiting"
    )
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

# Normalization logic
VALID_PLANETS = ["Mercury", "Venus", "Earth", "Mars", ...]
PLANET_ALIASES = {"terra": "Earth", "ares": "Mars", ...}

def normalize_planet(name: str) -> str | None:
    """Normalize planet name to canonical form."""
    if not name:
        return "Earth"
    
    key = name.strip().lower()
    
    # Exact match
    for planet in VALID_PLANETS:
        if key == planet.lower():
            return planet
    
    # Alias match
    if key in PLANET_ALIASES:
        return PLANET_ALIASES[key]
    
    # Prefix match
    for planet in VALID_PLANETS:
        if planet.lower().startswith(key):
            return planet
    
    return None

# Tool handler with normalization
async def call_tool(req: types.CallToolRequest) -> types.ServerResult:
    try:
        payload = SolarInput.model_validate(req.params.arguments)
    except ValidationError as exc:
        return error_result(f"Invalid input: {exc}")
    
    # Normalize and validate
    planet = normalize_planet(payload.planet_name)
    if not planet:
        return error_result(
            f"Unknown planet. Valid: {', '.join(VALID_PLANETS)}"
        )
    
    # Enrich with additional data
    description = PLANET_DESCRIPTIONS[planet]
    
    return success_result(
        widget=widget,
        text=f"Centered on {planet}",
        structured_data={
            "planet_name": planet,
            "planet_description": description,
            "autoOrbit": payload.auto_orbit
        }
    )
```

---

## Resource Management

### Loading Widget HTML

```python
from pathlib import Path
from functools import lru_cache

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

@lru_cache(maxsize=None)
def load_widget_html(component_name: str) -> str:
    """Load widget HTML with caching and fallback."""
    
    # Try exact match
    html_path = ASSETS_DIR / f"{component_name}.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf8")
    
    # Try versioned fallback (e.g., pizzaz-v1.2.3.html)
    fallback_candidates = sorted(
        ASSETS_DIR.glob(f"{component_name}-*.html")
    )
    if fallback_candidates:
        return fallback_candidates[-1].read_text(encoding="utf8")
    
    # Not found
    raise FileNotFoundError(
        f'Widget HTML "{component_name}" not found in {ASSETS_DIR}'
    )
```

### Resource Listing

```python
@mcp._mcp_server.list_resources()
async def list_resources() -> List[types.Resource]:
    """List all available widget resources."""
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType="text/html+skybridge",
            _meta=tool_meta(widget)
        )
        for widget in widgets
    ]

@mcp._mcp_server.list_resource_templates()
async def list_resource_templates() -> List[types.ResourceTemplate]:
    """List resource URI templates."""
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType="text/html+skybridge",
            _meta=tool_meta(widget)
        )
        for widget in widgets
    ]
```

### Resource Reading

```python
async def handle_read_resource(
    req: types.ReadResourceRequest
) -> types.ServerResult:
    """Handle resource read requests."""
    
    # Look up widget by URI
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if not widget:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"}
            )
        )
    
    # Return widget HTML
    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=widget.template_uri,
                    mimeType="text/html+skybridge",
                    text=widget.html,
                    _meta=tool_meta(widget)
                )
            ]
        )
    )
```

---

## Metadata Configuration

### Tool Metadata Structure

```python
def tool_meta(widget: Widget) -> Dict[str, Any]:
    """Generate tool metadata for OpenAI integration."""
    return {
        # Widget template URI
        "openai/outputTemplate": widget.template_uri,
        
        # Status messages
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        
        # Widget capabilities
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        
        # Tool behavior hints
        "annotations": {
            "destructiveHint": False,      # Tool doesn't modify data
            "openWorldHint": False,         # Tool doesn't access internet
            "readOnlyHint": True,           # Tool only reads data
        }
    }
```

### Embedded Resource Metadata

```python
def embedded_widget_resource(widget: Widget) -> types.EmbeddedResource:
    """Create embedded resource for widget HTML."""
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType="text/html+skybridge",
            text=widget.html,
            title=widget.title
        )
    )
```

### Result Metadata

```python
def result_metadata(widget: Widget) -> Dict[str, Any]:
    """Complete metadata for tool call result."""
    widget_resource = embedded_widget_resource(widget)
    
    return {
        # Embedded widget HTML
        "openai.com/widget": widget_resource.model_dump(mode="json"),
        
        # Widget configuration
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }
```

---

## Input Validation

### Basic Validation Pattern

```python
from pydantic import BaseModel, Field, ConfigDict, ValidationError

class ToolInput(BaseModel):
    """Input schema with validation."""
    
    # Required field
    name: str = Field(
        ...,
        description="Required parameter"
    )
    
    # Optional with default
    count: int = Field(
        10,
        ge=1,
        le=100,
        description="Count between 1 and 100"
    )
    
    # String with pattern
    code: str = Field(
        ...,
        pattern=r"^[A-Z]{3}$",
        description="Three uppercase letters"
    )
    
    # Enum constraint
    category: str = Field(
        ...,
        description="Category name"
    )
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allow aliases
        extra="forbid"           # Reject unknown fields
    )

# Usage in handler
async def call_tool(req: types.CallToolRequest) -> types.ServerResult:
    try:
        payload = ToolInput.model_validate(req.params.arguments)
    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Validation error: {exc.errors()}"
                    )
                ],
                isError=True
            )
        )
    
    # Use validated data
    result = process(payload)
    return success_result(result)
```

### Field Aliases

```python
class PizzaInput(BaseModel):
    """Support both camelCase (API) and snake_case (Python)."""
    
    pizza_topping: str = Field(
        ...,
        alias="pizzaTopping",  # Accept "pizzaTopping" in JSON
        description="Topping name"
    )
    
    extra_cheese: bool = Field(
        False,
        alias="extraCheese",
        description="Add extra cheese"
    )
    
    model_config = ConfigDict(
        populate_by_name=True  # Accept both names
    )

# Input JSON can use either:
# {"pizzaTopping": "pepperoni", "extraCheese": true}
# or
# {"pizza_topping": "pepperoni", "extra_cheese": true}
```

### Custom Validators

```python
from pydantic import field_validator

class SolarInput(BaseModel):
    planet_name: str = Field(..., alias="planetName")
    
    @field_validator('planet_name')
    @classmethod
    def validate_planet(cls, v: str) -> str:
        """Custom validation logic."""
        normalized = normalize_planet(v)
        if normalized is None:
            raise ValueError(
                f"Unknown planet '{v}'. "
                f"Valid: {', '.join(VALID_PLANETS)}"
            )
        return normalized
```

---

## Structured Content

### What is Structured Content?

Structured content is JSON data passed from the server to the widget's JavaScript. The widget reads this data and renders accordingly.

### Simple Example

```python
# Server returns
return types.ServerResult(
    types.CallToolResult(
        content=[...],
        structuredContent={
            "pizzaTopping": "pepperoni",
            "size": "large",
            "timestamp": "2025-10-17T12:00:00Z"
        },
        _meta={...}
    )
)

# Widget JavaScript reads
const data = getStructuredContent();
console.log(data.pizzaTopping);  // "pepperoni"
```

### Complex Example

```python
# Solar system with rich data
structured_content = {
    "planet_name": "Mars",
    "planet_description": "The Red Planet...",
    "autoOrbit": True,
    "camera": {
        "distance": 1500000,
        "elevation": 30,
        "rotation_speed": 0.001
    },
    "orbital_data": {
        "period_days": 687,
        "distance_au": 1.524,
        "moons": ["Phobos", "Deimos"]
    },
    "facts": [
        "Mars has the tallest volcano in the solar system",
        "A day on Mars is 24.6 hours",
        "Mars has seasons like Earth"
    ]
}

return types.ServerResult(
    types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=f"Focused on {structured_content['planet_name']}"
            )
        ],
        structuredContent=structured_content,
        _meta=result_metadata(widget)
    )
)
```

### Data Types

```python
# Supported types in structured content
structured_content = {
    # Primitives
    "string": "hello",
    "number": 42,
    "float": 3.14,
    "boolean": True,
    "null": None,
    
    # Collections
    "array": [1, 2, 3],
    "object": {"key": "value"},
    
    # Nested
    "nested": {
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ],
        "metadata": {
            "count": 2,
            "timestamp": "2025-10-17T12:00:00Z"
        }
    }
}
```

---

## Error Handling

### Error Response Pattern

```python
def error_result(message: str) -> types.ServerResult:
    """Create standardized error response."""
    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=message
                )
            ],
            isError=True
        )
    )

# Usage
if not valid_input:
    return error_result("Invalid input: expected positive number")
```

### Validation Errors

```python
try:
    payload = InputSchema.model_validate(req.params.arguments)
except ValidationError as exc:
    errors = exc.errors()
    message = "Validation errors:\n" + "\n".join(
        f"- {e['loc'][0]}: {e['msg']}" for e in errors
    )
    return error_result(message)
```

### Not Found Errors

```python
# Tool not found
widget = WIDGETS_BY_ID.get(req.params.name)
if not widget:
    return error_result(f"Unknown tool: {req.params.name}")

# Resource not found
resource = RESOURCES.get(uri)
if not resource:
    return types.ServerResult(
        types.ReadResourceResult(
            contents=[],
            _meta={"error": f"Resource not found: {uri}"}
        )
    )
```

### Processing Errors

```python
try:
    result = expensive_operation(payload)
except ProcessingError as exc:
    return error_result(f"Processing failed: {str(exc)}")
except Exception as exc:
    # Log unexpected errors
    logger.exception("Unexpected error in tool handler")
    return error_result("An unexpected error occurred")
```

---

## Complete Examples

### Example 1: Simple Map Widget

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict, ValidationError

# Widget definition
@dataclass(frozen=True)
class MapWidget:
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: str

# Load HTML
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
widget = MapWidget(
    identifier="show-map",
    title="Show Map",
    template_uri="ui://widget/map.html",
    invoking="Loading map",
    invoked="Map ready",
    html=(ASSETS_DIR / "map.html").read_text(),
    response_text="Map loaded successfully"
)

# Input schema
class MapInput(BaseModel):
    location: str = Field(..., description="Location to show")
    zoom: int = Field(12, ge=1, le=20, description="Zoom level")
    model_config = ConfigDict(extra="forbid")

# Initialize MCP
mcp = FastMCP(name="map-server", stateless_http=True)

# Register tool
@mcp._mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name=widget.identifier,
            title=widget.title,
            description="Show a map of the specified location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "zoom": {"type": "integer", "minimum": 1, "maximum": 20}
                },
                "required": ["location"]
            },
            _meta={
                "openai/outputTemplate": widget.template_uri,
                "openai/toolInvocation/invoking": widget.invoking,
                "openai/toolInvocation/invoked": widget.invoked,
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True
            }
        )
    ]

# Handle tool call
async def call_tool(req: types.CallToolRequest) -> types.ServerResult:
    try:
        payload = MapInput.model_validate(req.params.arguments)
    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=str(exc))],
                isError=True
            )
        )
    
    # Create widget resource
    widget_resource = types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType="text/html+skybridge",
            text=widget.html,
            title=widget.title
        )
    )
    
    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Showing map of {payload.location}"
                )
            ],
            structuredContent={
                "location": payload.location,
                "zoom": payload.zoom
            },
            _meta={
                "openai.com/widget": widget_resource.model_dump(mode="json"),
                "openai/outputTemplate": widget.template_uri,
                "openai/widgetAccessible": True
            }
        )
    )

# Register handler
mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

# Create app
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

### Example 2: Multi-Widget Gallery

```python
# Multiple related widgets
widgets = [
    GalleryWidget(
        identifier="gallery-grid",
        title="Grid Gallery",
        template_uri="ui://widget/gallery-grid.html",
        invoking="Loading grid",
        invoked="Grid ready",
        html=load_html("gallery-grid"),
        response_text="Showing images in grid layout"
    ),
    GalleryWidget(
        identifier="gallery-slideshow",
        title="Slideshow Gallery",
        template_uri="ui://widget/gallery-slideshow.html",
        invoking="Loading slideshow",
        invoked="Slideshow ready",
        html=load_html("gallery-slideshow"),
        response_text="Showing images as slideshow"
    ),
    GalleryWidget(
        identifier="gallery-masonry",
        title="Masonry Gallery",
        template_uri="ui://widget/gallery-masonry.html",
        invoking="Loading masonry",
        invoked="Masonry ready",
        html=load_html("gallery-masonry"),
        response_text="Showing images in masonry layout"
    )
]

WIDGETS_BY_ID = {w.identifier: w for w in widgets}

# Shared input schema
class GalleryInput(BaseModel):
    query: str = Field(..., description="Image search query")
    count: int = Field(9, ge=1, le=50, description="Number of images")
    model_config = ConfigDict(extra="forbid")

# Register all widgets as tools
@mcp._mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name=widget.identifier,
            title=widget.title,
            description=f"Show images in {widget.title.lower()} format",
            inputSchema=GalleryInput.model_json_schema(),
            _meta=tool_meta(widget)
        )
        for widget in widgets
    ]

# Single handler for all widgets
async def call_tool(req: types.CallToolRequest) -> types.ServerResult:
    widget = WIDGETS_BY_ID.get(req.params.name)
    if not widget:
        return error_result(f"Unknown tool: {req.params.name}")
    
    try:
        payload = GalleryInput.model_validate(req.params.arguments)
    except ValidationError as exc:
        return error_result(str(exc))
    
    # Fetch images (mock)
    images = fetch_images(payload.query, payload.count)
    
    return success_result(
        widget=widget,
        text=widget.response_text,
        structured_data={
            "query": payload.query,
            "images": images,
            "layout": widget.identifier.split("-")[1]  # grid, slideshow, masonry
        }
    )
```

### Example 3: Data Visualization

```python
# Chart widget with multiple chart types
class ChartInput(BaseModel):
    data_source: str = Field(..., alias="dataSource")
    chart_type: str = Field("bar", alias="chartType")
    title: str = Field("Chart", description="Chart title")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    
    @field_validator('chart_type')
    @classmethod
    def validate_chart_type(cls, v: str) -> str:
        valid_types = ["bar", "line", "pie", "scatter", "area"]
        if v not in valid_types:
            raise ValueError(f"Invalid chart type. Valid: {valid_types}")
        return v

async def call_tool(req: types.CallToolRequest) -> types.ServerResult:
    try:
        payload = ChartInput.model_validate(req.params.arguments)
    except ValidationError as exc:
        return error_result(str(exc))
    
    # Fetch and process data
    raw_data = fetch_data(payload.data_source)
    chart_data = process_for_chart(raw_data, payload.chart_type)
    
    # Calculate statistics
    stats = calculate_stats(chart_data)
    
    return success_result(
        widget=chart_widget,
        text=f"Rendered {payload.chart_type} chart: {payload.title}",
        structured_data={
            "chartType": payload.chart_type,
            "title": payload.title,
            "data": chart_data,
            "statistics": {
                "mean": stats.mean,
                "median": stats.median,
                "min": stats.min,
                "max": stats.max
            },
            "metadata": {
                "source": payload.data_source,
                "timestamp": datetime.now().isoformat(),
                "point_count": len(chart_data)
            }
        }
    )
```

---

## Best Practices

### 1. Widget Design

- **Keep widgets focused**: One widget = one purpose
- **Make widgets reusable**: Pass data via structured content
- **Optimize HTML size**: Minify and compress widget assets
- **Handle missing data**: Widget should degrade gracefully

### 2. Input Validation

- **Always validate**: Use Pydantic for type safety
- **Provide clear errors**: Help users fix invalid input
- **Set sensible defaults**: Make optional parameters actually optional
- **Document constraints**: Use Field descriptions

### 3. Error Handling

- **Return proper error flags**: Set `isError=True`
- **Give actionable messages**: Tell users how to fix the problem
- **Log unexpected errors**: But don't expose internals to user
- **Handle edge cases**: Null, empty, malformed input

### 4. Performance

- **Cache widget HTML**: Use `@lru_cache` for file loading
- **Minimize processing**: Do heavy work asynchronously if possible
- **Stream large responses**: Use SSE for real-time updates
- **Limit data size**: Don't send megabytes of structured content

### 5. Security

- **Validate all input**: Never trust client data
- **Sanitize output**: Escape HTML if generating dynamic content
- **Limit resource access**: Don't expose file system or credentials
- **Rate limit**: Protect against abuse

---

## Testing Your MCP Server

### Manual Testing

```bash
# Test initialize
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0"}
    },
    "id": 1
  }'

# Test tools/list
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 2
  }'

# Test tool call
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "pizza-map",
      "arguments": {"pizzaTopping": "pepperoni"}
    },
    "id": 3
  }'
```

### Unit Testing

```python
import pytest
from server import normalize_planet, PizzaInput

def test_normalize_planet():
    assert normalize_planet("earth") == "Earth"
    assert normalize_planet("MARS") == "Mars"
    assert normalize_planet("terra") == "Earth"
    assert normalize_planet("unknown") is None

def test_pizza_input_validation():
    # Valid
    valid = PizzaInput(pizza_topping="pepperoni")
    assert valid.pizza_topping == "pepperoni"
    
    # Valid with alias
    valid_alias = PizzaInput.model_validate({"pizzaTopping": "mushroom"})
    assert valid_alias.pizza_topping == "mushroom"
    
    # Invalid - missing required field
    with pytest.raises(ValidationError):
        PizzaInput.model_validate({})
    
    # Invalid - extra field
    with pytest.raises(ValidationError):
        PizzaInput.model_validate({
            "pizzaTopping": "pepperoni",
            "extraField": "not allowed"
        })
```

---

## Deployment Checklist

- [ ] Widget HTML assets built and minified
- [ ] All tools registered and tested
- [ ] Input validation working correctly
- [ ] Error handling covers edge cases
- [ ] Resources loading correctly
- [ ] Metadata properly configured
- [ ] Docker container builds successfully
- [ ] nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] MCP manifest created at `/.well-known/mcp.json`
- [ ] Manual curl tests passing
- [ ] Server registered with OpenAI
- [ ] Tools appear in ChatGPT
- [ ] Widgets render correctly

---

## Additional Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **FastMCP Documentation**: https://gofastmcp.com
- **OpenAI MCP Integration**: https://platform.openai.com/docs/guides/model-context-protocol
- **Example Repositories**:
  - Pizza Demo: https://github.com/openai/mcp-examples/tree/main/pizzaz
  - Solar System: https://github.com/openai/mcp-examples/tree/main/solar-system

---

**Guide Version**: 1.0  
**Last Updated**: October 17, 2025  
**Frameworks**: FastMCP 2.12.4, MCP SDK 1.18.0
