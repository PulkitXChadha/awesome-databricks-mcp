"""Lakeview Dashboard MCP Tools

This module provides comprehensive MCP tools for Lakeview dashboard management
with native Lakeview implementation. Provides parameter validation, widget creation,
and encoding management for .lvdash.json file generation.

QueryLines Format (based on actual Lakeview dashboard JSON structure):
- Always uses 'queryLines' field (array format)
- Single-line queries: ["SELECT * FROM table"]
- Multi-line queries: ["SELECT \\n", "  col1,\\n", "FROM table"] (preserves line breaks)

"""

import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List

try:
  from .widget_specs import create_widget_spec
except ImportError:
  from widget_specs import create_widget_spec


def generate_id() -> str:
  """Generate 8-character hex ID for Lakeview objects."""
  return str(uuid.uuid4())[:8]


def query_to_querylines(query: str) -> List[str]:
  """Convert SQL query string to Lakeview queryLines format.

  Based on actual Lakeview dashboard JSON format analysis:
  - Always returns an array for the queryLines field
  - Short simple queries: ["SELECT * FROM table"]
  - Complex queries: Intelligently split into readable lines with proper formatting
  - Multi-line format: ["SELECT \n", "    col1,\n", "    col2\n", "FROM table"]
    Each line except typically the last has \n appended

  Args:
      query: SQL query as string (single or multiline)

  Returns:
      List of strings in proper Lakeview queryLines array format
  """
  query = query.strip()

  # If query already contains newlines, split and preserve formatting
  if '\n' in query:
    result = []
    lines = query.split('\n')

    for i in range(len(lines)):
      line = lines[i]
      if i < len(lines) - 1:
        # Add \n to all lines except the last
        result.append(line + '\n')
      else:
        # Last line: only add if it's not empty
        if line.strip():
          result.append(line)

    return result

  # For single-line queries, check if they should be formatted as multi-line
  # Threshold: queries longer than 120 characters or containing multiple clauses
  should_format_multiline = (
    len(query) > 120
    or query.upper().count(' FROM ') >= 1
    and (
      query.upper().count(' WHERE ') >= 1
      or query.upper().count(' GROUP BY ') >= 1
      or query.upper().count(' ORDER BY ') >= 1
      or query.upper().count(' HAVING ') >= 1
      or query.upper().count(' JOIN ') >= 1
      or query.upper().count(',') >= 3
    )
  )

  if not should_format_multiline:
    return [query]

  # Format complex single-line queries into readable multi-line format
  import re

  # Simplified approach: split on major SQL keywords and format columns
  result = []

  # Split on major SQL clauses while preserving them
  pattern = r'\b(SELECT|FROM|WHERE|GROUP BY|ORDER BY|HAVING|UNION)\b'
  parts = re.split(pattern, query, flags=re.IGNORECASE)
  parts = [p.strip() for p in parts if p.strip()]

  current_clause = ''

  for i, part in enumerate(parts):
    part_upper = part.upper()

    if part_upper in ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'UNION']:
      # Start new clause
      if current_clause.strip():
        result.extend(_format_clause_content(current_clause))
      current_clause = part + ' '
    else:
      current_clause += part

  # Add the final clause
  if current_clause.strip():
    result.extend(_format_clause_content(current_clause))

  return result if result else [query]


def _format_clause_content(clause: str) -> List[str]:
  """Format the content of a SQL clause into properly formatted lines."""
  clause = clause.strip()

  # Check if this is a SELECT clause with multiple columns
  if clause.upper().startswith('SELECT ') and ',' in clause:
    # Extract the SELECT keyword and column list
    select_part = clause[:6]  # "SELECT"
    columns_part = clause[6:].strip()

    # Split columns more carefully, respecting parentheses and CASE statements
    columns = _split_columns_safely(columns_part)

    if len(columns) > 1:
      # Format as multi-line
      lines = [select_part + ' \n']
      for j, col in enumerate(columns):
        col = col.strip()
        if j < len(columns) - 1:
          lines.append('    ' + col + ',\n')
        else:
          lines.append('    ' + col + '\n')
      return lines

  # For non-SELECT clauses or single-column SELECT, return as single line
  return [clause + '\n']


def _split_columns_safely(columns_text: str) -> List[str]:
  """Split column list while respecting parentheses, CASE statements, etc."""
  columns = []
  current_col = ''
  paren_depth = 0
  case_depth = 0

  i = 0
  while i < len(columns_text):
    char = columns_text[i]

    if char == '(':
      paren_depth += 1
      current_col += char
    elif char == ')':
      paren_depth -= 1
      current_col += char
    elif char == ',' and paren_depth == 0 and case_depth == 0:
      # This is a real column separator
      columns.append(current_col.strip())
      current_col = ''
    else:
      current_col += char

      # Check for CASE/END keywords
      if i >= 3:
        last_4 = columns_text[i - 3 : i + 1].upper()
        if last_4 == 'CASE':
          case_depth += 1
        elif last_4.endswith('END') and case_depth > 0:
          case_depth -= 1

    i += 1

  # Add the last column
  if current_col.strip():
    columns.append(current_col.strip())

  return columns


def create_dashboard_json(
  name: str, warehouse_id: str, datasets: List[Dict[str, Any]], widgets: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
  """Create complete Lakeview dashboard JSON with proper queryLines format.

  Generates Lakeview dashboard JSON with queryLines array format:
  - Input accepts 'query' as a string for convenience
  - Output uses 'queryLines' array as required by Lakeview format

  Args:
      name: Dashboard display name
      warehouse_id: SQL warehouse ID
      datasets: List of dataset configurations with structure:
          {
              "name": str,                    # Dataset display name
              "query": str,                   # SQL query string (converted to queryLines array)
              "parameters": List[Dict]        # Optional query parameters
          }
      widgets: List of widget configurations with advanced features

  Returns:
      Complete dashboard JSON ready for .lvdash.json file with proper queryLines array format
  """
  if widgets is None:
    widgets = []

  # Generate dashboard ID
  dashboard_id = (
    generate_id() + generate_id() + generate_id() + generate_id()
  )  # 32 character ID like real examples

  # Convert datasets to Lakeview format with parameter support
  lv_datasets = []
  for ds in datasets:
    # Convert query to proper Lakeview queryLines format using simplified function
    query_lines = query_to_querylines(ds['query'])

    dataset = {'name': generate_id(), 'displayName': ds['name'], 'queryLines': query_lines}

    # Add parameters if provided
    if 'parameters' in ds and ds['parameters']:
      dataset['parameters'] = ds['parameters']

    lv_datasets.append(dataset)

  # Convert widgets to layout items with custom positioning support
  layout = []
  for i, widget in enumerate(widgets):
    # Check if custom position is provided
    if 'position' in widget:
      position = widget['position']
    else:
      # Default grid layout: 2 columns, auto-flow vertically
      x = (i % 2) * 6
      y = (i // 2) * 4
      position = {'x': x, 'y': y, 'width': 6, 'height': 4}

    layout.append(
      {'position': position, 'widget': create_widget_spec(widget, lv_datasets, dashboard_id)}
    )

  return {
    'dashboard_id': dashboard_id,
    'displayName': name,
    'warehouseId': warehouse_id,
    'datasets': lv_datasets,
    'pages': [{'name': generate_id(), 'displayName': name, 'layout': layout}],
  }


def create_optimized_dashboard_json(
  name: str,
  warehouse_id: str,
  datasets: List[Dict[str, Any]],
  widgets: List[Dict[str, Any]] = None,
  enable_optimization: bool = True,
) -> Dict[str, Any]:
  """Create dashboard with automatic layout optimization.

  This function enhances the core dashboard creation with intelligent layout optimization.
  It analyzes widget data to determine optimal sizing and positioning automatically.

  Args:
      name: Dashboard display name
      warehouse_id: SQL warehouse ID
      datasets: List of datasets
      widgets: List of widget configurations
      enable_optimization: Whether to apply layout optimization (default: True)

  Returns:
      Optimized dashboard JSON with intelligent layout
  """
  if widgets is None:
    widgets = []

  if enable_optimization:
    try:
      # Import layout optimization functions
      from .layout_optimization import optimize_dashboard_layout

      # Optimize widget layout
      optimized_widgets = optimize_dashboard_layout(widgets, warehouse_id, datasets)

      # Use the core function with optimized widgets
      return create_dashboard_json(name, warehouse_id, datasets, optimized_widgets)

    except ImportError:
      # Fallback if optimization module not available
      print('Layout optimization module not found, using default layout')
      return create_dashboard_json(name, warehouse_id, datasets, widgets)
    except Exception as e:
      # Fallback on any error - use default layout
      print(f'Layout optimization failed, using default layout: {str(e)}')
      return create_dashboard_json(name, warehouse_id, datasets, widgets)
  else:
    # Optimization disabled, use default
    return create_dashboard_json(name, warehouse_id, datasets, widgets)


def prepare_dashboard_for_client(dashboard_json: Dict[str, Any], file_path: str) -> Dict[str, Any]:
  """Create dashboard JSON file on the filesystem.

  Saves the dashboard JSON to the specified file path and returns both
  the file path and content for verification.
  """
  import os

  try:
    # Ensure the directory exists
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Format JSON content with proper indentation
    json_content = json.dumps(dashboard_json, indent=2)

    # Write the file to the filesystem
    with open(file_path, 'w', encoding='utf-8') as f:
      f.write(json_content)

    # Verify file was created and get file size
    if os.path.exists(file_path):
      file_size = os.path.getsize(file_path)
      return {
        'success': True,
        'file_path': file_path,
        'content': json_content,
        'file_size': file_size,
        'message': f'Dashboard file successfully created at {file_path} ({file_size} bytes)',
      }
    else:
      return {
        'success': False,
        'error': f'File creation failed: {file_path} was not created',
        'file_path': file_path,
      }

  except PermissionError as e:
    return {
      'success': False,
      'error': f'Permission denied: Cannot write to {file_path}. {str(e)}',
      'file_path': file_path,
    }
  except OSError as e:
    return {'success': False, 'error': f'File system error: {str(e)}', 'file_path': file_path}
  except Exception as e:
    return {
      'success': False,
      'error': f'Unexpected error creating file: {str(e)}',
      'file_path': file_path,
    }


def find_dataset_id(dataset_name: str, datasets: List[Dict[str, Any]]) -> str:
  """Find dataset ID by display name."""
  for ds in datasets:
    if ds['displayName'] == dataset_name:
      return ds['name']

  # If not found, return the first dataset or generate new ID
  return datasets[0]['name'] if datasets else generate_id()


def validate_sql_query(
  query: str, warehouse_id: str, catalog: str = None, schema: str = None
) -> Dict[str, Any]:
  """Validate SQL query by executing it with LIMIT 0 to check syntax and table references.

  This function works with both single-line and multi-line SQL queries. It normalizes
  the query format and validates against the database to ensure proper syntax and
  table/column existence before dashboard creation.

  Args:
      query: SQL query to validate (single-line or multi-line string format)
      warehouse_id: SQL warehouse ID for execution
      catalog: Optional catalog to use for three-part table names
      schema: Optional schema to use for three-part table names

  Returns:
      {
          "valid": bool,              # True if query is valid
          "error": str,               # Error message if invalid, None if valid
          "columns": list,            # List of column names returned by query
          "message": str              # Success message with column info
      }
  """
  try:
    # Import here to avoid circular dependencies
    from databricks.sdk import WorkspaceClient

    # Initialize Databricks SDK
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # Clean query for validation (remove trailing semicolons and whitespace)
    clean_query = str(query).strip().rstrip(';').strip()

    # Create validation query - use LIMIT 0 to check syntax without returning data
    # Also get column information for widget field validation
    validation_query = f'SELECT * FROM ({clean_query}) AS validation_subquery LIMIT 0'

    # Build the full query with catalog/schema if provided
    full_query = validation_query
    if catalog and schema:
      full_query = f'USE CATALOG {catalog}; USE SCHEMA {schema}; {validation_query}'

    print(f'🔍 Validating SQL query: {clean_query[:100]}...')

    # Execute the validation query
    result = w.statement_execution.execute_statement(
      warehouse_id=warehouse_id,
      statement=full_query,
      wait_timeout='10s',  # Shorter timeout for validation
    )

    # Extract column information for widget field validation
    columns = []
    if result.manifest and result.manifest.schema and result.manifest.schema.columns:
      columns = [col.name for col in result.manifest.schema.columns]

    return {
      'valid': True,
      'error': None,
      'columns': columns,
      'message': f'Query validated successfully. Found {len(columns)} columns: {", ".join(columns[:5])}{"..." if len(columns) > 5 else ""}',
    }

  except Exception as e:
    error_msg = str(e)
    print(f'❌ SQL validation failed: {error_msg}')

    # Parse common SQL errors to provide helpful feedback
    if 'TABLE_OR_VIEW_NOT_FOUND' in error_msg:
      return {
        'valid': False,
        'error': f'Table or view not found. Please check table names and ensure they exist in the specified catalog/schema. Error: {error_msg}',
        'columns': [],
      }
    elif 'PARSE_SYNTAX_ERROR' in error_msg:
      return {
        'valid': False,
        'error': f'SQL syntax error. Please check your query syntax. Error: {error_msg}',
        'columns': [],
      }
    elif 'PERMISSION_DENIED' in error_msg:
      return {
        'valid': False,
        'error': f'Permission denied. Please ensure you have access to the tables and warehouse. Error: {error_msg}',
        'columns': [],
      }
    else:
      return {'valid': False, 'error': f'Query validation failed: {error_msg}', 'columns': []}


def validate_widget_fields(
  widget_config: Dict[str, Any], available_columns: List[str]
) -> Dict[str, Any]:
  """Validate that widget field references exist in the dataset columns.

  Args:
      widget_config: Widget configuration with field references
      available_columns: List of available column names from the dataset

  Returns:
      {"valid": bool, "error": str, "warnings": list} - validation result
  """
  config = widget_config.get('config', {})
  widget_type = widget_config.get('type', '')

  warnings = []
  missing_fields = []

  # Check fields based on widget type
  if widget_type in ['bar', 'line', 'area', 'scatter']:
    # Chart widgets with x/y axes
    if 'x_field' in config and config['x_field'] not in available_columns:
      missing_fields.append(f"x_field: '{config['x_field']}'")
    if 'y_field' in config and config['y_field'] not in available_columns:
      missing_fields.append(f"y_field: '{config['y_field']}'")
    if 'color_field' in config and config['color_field'] not in available_columns:
      missing_fields.append(f"color_field: '{config['color_field']}'")

  elif widget_type == 'pie':
    # Pie chart with category/value
    if 'category_field' in config and config['category_field'] not in available_columns:
      missing_fields.append(f"category_field: '{config['category_field']}'")
    if 'value_field' in config and config['value_field'] not in available_columns:
      missing_fields.append(f"value_field: '{config['value_field']}'")

  elif widget_type == 'counter':
    # Counter with value field
    if 'value_field' in config and config['value_field'] not in available_columns:
      missing_fields.append(f"value_field: '{config['value_field']}'")

  elif widget_type == 'funnel':
    # Funnel with stage and value fields
    if 'stage_field' in config and config['stage_field'] not in available_columns:
      missing_fields.append(f"stage_field: '{config['stage_field']}'")
    if 'value_field' in config and config['value_field'] not in available_columns:
      missing_fields.append(f"value_field: '{config['value_field']}'")

    # Check for fallback categorical fields if stage_field is missing
    if 'stage_field' not in config:
      fallback_found = False
      for field_key in ['category_field', 'x_field', 'color_field']:
        if field_key in config and config[field_key] in available_columns:
          fallback_found = True
          break
        elif field_key in config and config[field_key] not in available_columns:
          missing_fields.append(f"{field_key} (used as stage_field): '{config[field_key]}'")

      if not fallback_found and any(
        key in config for key in ['category_field', 'x_field', 'color_field']
      ):
        warnings.append('Funnel widget: no valid categorical field found for stage dimension')

  elif widget_type == 'histogram':
    # Histogram with x field
    if 'x_field' in config and config['x_field'] not in available_columns:
      missing_fields.append(f"x_field: '{config['x_field']}'")

  elif widget_type == 'table':
    # Table with specific columns
    if 'columns' in config:
      for col in config['columns']:
        if col not in available_columns:
          missing_fields.append(f"table column: '{col}'")

  elif widget_type == 'choropleth-map':
    # Choropleth map with location and color fields
    if 'location_field' in config and config['location_field'] not in available_columns:
      missing_fields.append(f"location_field: '{config['location_field']}'")
    if 'color_field' in config and config['color_field'] not in available_columns:
      missing_fields.append(f"color_field: '{config['color_field']}'")

  elif widget_type == 'symbol-map':
    # Symbol map with lat/lng and optional color/size fields
    if 'latitude_field' in config and config['latitude_field'] not in available_columns:
      missing_fields.append(f"latitude_field: '{config['latitude_field']}'")
    if 'longitude_field' in config and config['longitude_field'] not in available_columns:
      missing_fields.append(f"longitude_field: '{config['longitude_field']}'")
    if 'color_field' in config and config['color_field'] not in available_columns:
      missing_fields.append(f"color_field: '{config['color_field']}'")
    if 'size_field' in config and config['size_field'] not in available_columns:
      missing_fields.append(f"size_field: '{config['size_field']}'")

  # Generate result
  if missing_fields:
    return {
      'valid': False,
      'error': f"Widget '{widget_type}' references fields that don't exist in the dataset: {', '.join(missing_fields)}. Available columns: {', '.join(available_columns)}",
      'warnings': warnings,
    }

  return {'valid': True, 'error': None, 'warnings': warnings}


def load_dashboard_tools(mcp_server):
  """Register simplified dashboard tools with MCP server."""

  @mcp_server.tool()
  def create_dashboard_file(
    name: str,
    warehouse_id: str,
    datasets: List[Dict[str, str]],
    file_path: str,
    widgets: List[Dict[str, Any]] = None,
    validate_sql: bool = True,
    catalog: str = None,
    schema: str = None,
  ) -> Dict[str, Any]:
    """Creates a complete .lvdash.json file compatible with Databricks Lakeview dashboards.

    IMPORTANT: This tool creates the dashboard file directly on the filesystem at the specified path.
    The file will be saved automatically and you'll receive confirmation of successful creation.

    COMPREHENSIVE WIDGET SUPPORT:
    This tool supports all Lakeview widget types with full schema compliance and advanced configuration options.
    All widgets support positioning, styling, and interactive features according to Lakeview specifications.

    DATASET OPTIMIZATION GUIDANCE:
    Prefer fewer raw datasets with widget-level transformations over multiple pre-aggregated datasets.
    This approach:
    - Supports more widgets with fewer datasets
    - Improves performance through Lakeview's native aggregation
    - Simplifies maintenance and modifications
    - Provides single source of truth per data source

    Example optimization:
    Instead of:  Multiple datasets (raw_sales, monthly_sales, product_sales)
    Use:         Single raw dataset + widget expressions for aggregations

    Widget Expression Support:
    All widgets support field transformations using {field_key}_expression pattern:
    - Direct SQL: "y_expression": "SUM(`revenue`)"
    - Date functions: "x_expression": "DATE_TRUNC('MONTH', `date`)"
    - Binning: "x_expression": "BIN_FLOOR(`score`, 10)"
    - Helper functions available: get_aggregation_expression(), get_date_trunc_expression(), etc.

    Args:
        name: Dashboard display name (appears at the top of the dashboard)
        warehouse_id: SQL warehouse ID for running queries
        datasets: List of data sources, each with structure:
            {
                "name": "Human readable name",           # Display name for the dataset
                "query": "SELECT col1, col2 FROM table"  # SQL query (single or multi-line)
                       OR                                 # Examples:
                       '''                                # Simple single-line query
                       SELECT
                           product_name,
                           SUM(revenue) as total_revenue
                       FROM sales_data
                       WHERE date >= '2024-01-01'
                       GROUP BY product_name
                       ORDER BY total_revenue DESC
                       ''',                               # Complex multi-line query
                "parameters": [                          # Optional: Query parameters
                    {
                        "displayName": "param_name",     # Parameter display name
                        "keyword": "param_name",         # Parameter keyword in query
                        "dataType": "STRING|DATE|NUMBER", # Parameter data type
                        "defaultSelection": {            # Default parameter value
                            "values": {"dataType": "STRING", "values": [{"value": "default"}]}
                        }
                    }
                ]
            }
        widgets: List of widgets, each with structure:
            {
                "type": "bar|line|counter|table|pie|...",  # Widget type (16 types supported)
                "dataset": "Dataset Name",                 # Must match dataset name
                "config": {                                # Widget-specific configuration
                    "x_field": "column_name",              # X-axis field (charts)
                    "y_field": "column_name",              # Y-axis field (charts)
                    "color_field": "column_name",          # Color grouping (optional)
                    "value_field": "column_name",          # Value field (counters)
                    "category_field": "column_name",       # Category field (pie charts)
                    "columns": ["col1", "col2"],           # Table columns (tables)
                    "title": "Widget Title",               # Custom widget title
                    "show_title": true                     # Show/hide title
                },
                "position": {                              # Optional: Custom positioning
                    "x": 0, "y": 0,                       # Grid coordinates
                    "width": 6, "height": 4               # Size in grid units (12-column grid)
                }
            }
        file_path: Path to save the dashboard JSON file
        validate_sql: Whether to validate SQL queries before creating dashboard (default: True)
            - Checks SQL syntax using LIMIT 0 queries
            - Validates table/view existence and permissions
            - Verifies widget field references against actual columns
            - Provides detailed error messages for debugging
        catalog: Optional catalog name for SQL execution context
            Used for validation and three-part table names
        schema: Optional schema name for SQL execution context
            Used for validation and three-part table names

    Widget Types Supported:
        Charts: bar, line, area, scatter, pie, histogram, heatmap, box
        Display: counter, table, pivot, text
        Maps: choropleth-map
        Advanced: sankey (flow diagrams)
        Filters: filter-single-select, filter-multi-select, filter-date-range

    Returns:
        {
            "success": true,
            "file_path": "path/to/dashboard.lvdash.json",
            "content": "...complete JSON content as string...",
            "file_size": 1234,
            "message": "Dashboard file successfully created at path/to/dashboard.lvdash.json (1234 bytes)",
            "validation_results": {                    # If validate_sql=True
                "queries_validated": [                 # SQL validation results
                    {
                        "dataset": "Dataset Name",
                        "valid": true,
                        "error": null,
                        "columns": ["col1", "col2", "col3"],
                        "message": "Query validated successfully. Found 3 columns: col1, col2, col3"
                    }
                ],
                "widget_validations": [                # Widget field validation results
                    {
                        "widget_type": "bar",
                        "dataset": "Dataset Name",
                        "valid": true,
                        "error": null,
                        "warnings": []
                    }
                ],
                "warnings": []                         # Any warnings encountered
            }
        }

    Examples:
        # Single-line query dashboard (generates queryLines: ["SELECT..."])
        result = create_dashboard_file(
            name="Simple Sales Dashboard",
            warehouse_id="abc123",
            datasets=[{
                "name": "Sales Data",
                "query": "SELECT product, revenue FROM sales_transactions WHERE revenue > 100"
            }],
            widgets=[{
                "type": "bar",
                "dataset": "Sales Data",
                "config": {"x_field": "product", "y_field": "revenue"}
            }],
            file_path="path/simple_sales_dashboard.lvdash.json"
        )
        # File is automatically saved! Check result["success"] for confirmation

        # Multi-line query dashboard (generates queryLines: ["SELECT \\n", "            product, \\n", ...])
        result = create_dashboard_file(
            name="Advanced Sales Dashboard",
            warehouse_id="abc123",
            datasets=[{
                "name": "Sales Analysis",
                "query": \"\"\"
                    SELECT
                        product,
                        SUM(revenue) as total_revenue,
                        COUNT(*) as sales_count
                    FROM sales_transactions
                    WHERE sales_date >= '2024-01-01'
                    GROUP BY product
                    ORDER BY total_revenue DESC
                \"\"\"
            }],
            widgets=[{
                "type": "bar",
                "dataset": "Sales Analysis",
                "config": {"x_field": "product", "y_field": "total_revenue"}
            }],
            file_path="path/advanced_sales_dashboard.lvdash.json"
        )
        # File is automatically saved! Check result["success"] for confirmation

        # Mixed format dashboard with parameters
        result = create_dashboard_file(
            name="Executive Dashboard",
            warehouse_id="analytics_warehouse",
            datasets=[
                {
                    "name": "Revenue Metrics",
                    # Multi-line query generates proper queryLines array
                    "query": \"\"\"
                        SELECT
                            region,
                            SUM(revenue) as total_revenue,
                            COUNT(DISTINCT customer_id) as unique_customers
                        FROM sales
                        WHERE date >= :start_date
                        GROUP BY region
                        ORDER BY total_revenue DESC
                    \"\"\",
                    "parameters": [{
                        "displayName": "Start Date",
                        "keyword": "start_date",
                        "dataType": "DATE",
                        "defaultSelection": {"values": {"dataType": "DATE", "values": [{"value": "2024-01-01"}]}}
                    }]
                },
                {
                    "name": "Customer Count",
                    # Single-line query generates queryLines: ["SELECT COUNT(*)..."]
                    "query": "SELECT COUNT(*) as total_customers FROM customers WHERE active = true"
                }
            ],
            widgets=[
                {"type": "counter", "dataset": "Revenue Metrics", "config": {"value_field": "total_revenue", "title": "Total Revenue"}},
                {"type": "bar", "dataset": "Revenue Metrics", "config": {"x_field": "region", "y_field": "total_revenue"}},
                {"type": "counter", "dataset": "Customer Count", "config": {"value_field": "total_customers", "title": "Total Customers"}}
            ],
            file_path="path/executive_dashboard.lvdash.json",
            catalog="production",
            schema="analytics"
        )
        # File is automatically saved! Check result["success"] for confirmation

        # DATASET OPTIMIZATION EXAMPLE - Single raw dataset with widget-level transformations
        result = create_dashboard_file(
            name="Optimized Sales Dashboard",
            warehouse_id="analytics_warehouse",
            datasets=[
                {
                    "name": "Raw Sales Data",
                    "query": \"\"\"
                        SELECT
                            product,
                            region,
                            revenue,
                            order_date,
                            customer_id
                        FROM sales_transactions
                        WHERE order_date >= '2024-01-01'
                    \"\"\"
                }
            ],
            widgets=[
                # Monthly revenue trend using date truncation
                {
                    "type": "line",
                    "dataset": "Raw Sales Data",
                    "config": {
                        "x_field": "month",
                        "x_expression": "DATE_TRUNC('MONTH', `order_date`)",
                        "y_field": "monthly_revenue",
                        "y_expression": "SUM(`revenue`)",
                        "title": "Monthly Revenue Trend"
                    }
                },
                # Product performance using aggregation
                {
                    "type": "bar",
                    "dataset": "Raw Sales Data",
                    "config": {
                        "x_field": "product",
                        "y_field": "total_sales",
                        "y_expression": "SUM(`revenue`)",
                        "title": "Product Sales Performance"
                    }
                },
                # Customer count by region using count distinct
                {
                    "type": "bar",
                    "dataset": "Raw Sales Data",
                    "config": {
                        "x_field": "region",
                        "y_field": "unique_customers",
                        "y_expression": "COUNT(DISTINCT `customer_id`)",
                        "title": "Unique Customers by Region"
                    }
                }
            ],
            file_path="path/optimized_sales_dashboard.lvdash.json"
        )
        # This approach uses 1 dataset to support 3 different aggregated visualizations!
    """
    try:
      if widgets is None:
        widgets = []

      # Validate basic requirements
      if not name or not warehouse_id or not file_path:
        return {
          'success': False,
          'error': 'Missing required parameters: name, warehouse_id, file_path',
        }

      if not datasets:
        return {'success': False, 'error': 'At least one dataset is required'}

      # Ensure file path ends with .lvdash.json
      if not file_path.endswith('.lvdash.json'):
        file_path += '.lvdash.json'

      # SQL Validation Phase
      validation_results = {'queries_validated': [], 'widget_validations': [], 'warnings': []}

      if validate_sql:
        print('🔍 Starting SQL validation for dashboard datasets...')

        # Validate each dataset query
        for i, dataset in enumerate(datasets):
          query = dataset['query']
          dataset_name = dataset['name']

          print(f"🔍 Validating dataset '{dataset_name}' query...")
          validation_result = validate_sql_query(query, warehouse_id, catalog, schema)

          validation_results['queries_validated'].append(
            {
              'dataset': dataset_name,
              'valid': validation_result['valid'],
              'error': validation_result['error'],
              'columns': validation_result['columns'],
              'message': validation_result.get('message', ''),
            }
          )

          # If query is invalid, return error immediately
          if not validation_result['valid']:
            return {
              'success': False,
              'error': f"Dataset '{dataset_name}' has invalid SQL query: {validation_result['error']}",
              'validation_results': validation_results,
            }

          # Validate widgets that reference this dataset
          dataset_columns = validation_result['columns']
          for widget in widgets:
            if widget.get('dataset') == dataset_name:
              print(
                f"🔍 Validating widget '{widget.get('type', 'unknown')}' fields against dataset '{dataset_name}'..."
              )
              widget_validation = validate_widget_fields(widget, dataset_columns)

              validation_results['widget_validations'].append(
                {
                  'widget_type': widget.get('type', 'unknown'),
                  'dataset': dataset_name,
                  'valid': widget_validation['valid'],
                  'error': widget_validation['error'],
                  'warnings': widget_validation['warnings'],
                }
              )

              # If widget field validation fails, return error
              if not widget_validation['valid']:
                return {
                  'success': False,
                  'error': f'Widget validation failed: {widget_validation["error"]}',
                  'validation_results': validation_results,
                }

              # Collect warnings
              validation_results['warnings'].extend(widget_validation['warnings'])

        print('✅ All SQL queries and widget fields validated successfully!')
      else:
        validation_results['warnings'].append('SQL validation was skipped (validate_sql=False)')

      # Create dashboard JSON with automatic layout optimization
      dashboard_json = create_optimized_dashboard_json(
        name, warehouse_id, datasets, widgets, enable_optimization=True
      )

      # Prepare dashboard content for client
      result = prepare_dashboard_for_client(dashboard_json, file_path)
      result['validation_results'] = validation_results

      return result

    except Exception as e:
      return {'success': False, 'error': f'Failed to create dashboard: {str(e)}'}

  @mcp_server.tool()
  def validate_dashboard_sql(
    datasets: List[Dict[str, str]],
    warehouse_id: str,
    widgets: List[Dict[str, Any]] = None,
    catalog: str = None,
    schema: str = None,
  ) -> Dict[str, Any]:
    """Validate SQL queries and widget field references for dashboard datasets.

    Comprehensive validation tool that checks SQL syntax, table existence, permissions,
    and widget field references before dashboard creation. Automatically handles proper
    queryLines format conversion during validation process.

    Args:
        datasets: List of data sources with structure matching create_dashboard_file:
            [
                {
                    "name": "Human readable name",
                    "query": "SQL query (single-line or multi-line format supported)",
                    "parameters": [                           # Optional query parameters
                        {
                            "displayName": "param_name",
                            "keyword": "param_name",
                            "dataType": "STRING|DATE|NUMBER",
                            "defaultSelection": {"values": {"dataType": "STRING", "values": [{"value": "default"}]}}
                        }
                    ]
                }
            ]
        warehouse_id: SQL warehouse ID for validation execution
        widgets: List of widgets with structure matching create_dashboard_file:
            [
                {
                    "type": "bar|line|counter|table|pie|...",
                    "dataset": "Dataset Name",                 # Must match dataset name
                    "config": {
                        "x_field": "column_name",              # Will be validated against actual columns
                        "y_field": "column_name",
                        "color_field": "column_name",
                        "value_field": "column_name",
                        "category_field": "column_name",
                        "columns": ["col1", "col2"]
                    }
                }
            ]
        catalog: Optional catalog name for SQL execution context
            Used for three-part table names (catalog.schema.table)
        schema: Optional schema name for SQL execution context
            Used for three-part table names (catalog.schema.table)

    Validation Checks Performed:
        SQL Validation:
        - Syntax validation using LIMIT 0 queries
        - Table/view existence verification
        - Permission checks (SELECT access)
        - Column discovery for widget field validation
        - Parameter validation (if parameters provided)

        Widget Validation:
        - Field existence in dataset columns
        - Widget-type specific field requirements
        - Field name case sensitivity checks
        - Missing field detection with suggestions

    Returns:
        {
            "success": true|false,
            "message": "Validation summary message",
            "error": "Error description (if success=false)",
            "validation_results": {
                "queries_validated": [
                    {
                        "dataset": "Dataset Name",
                        "valid": true|false,
                        "error": "Error message or null",
                        "columns": ["col1", "col2", "col3"],      # Available columns
                        "message": "Validation success message"
                    }
                ],
                "widget_validations": [
                    {
                        "widget_type": "bar",
                        "dataset": "Dataset Name",
                        "valid": true|false,
                        "error": "Missing field details or null",
                        "warnings": ["Warning messages"]
                    }
                ],
                "warnings": ["General warnings"]
            }
        }

    Common Error Types:
        SQL Errors:
        - "TABLE_OR_VIEW_NOT_FOUND": Table doesn't exist or wrong name
        - "PARSE_SYNTAX_ERROR": SQL syntax issues
        - "PERMISSION_DENIED": No SELECT access to table/warehouse

        Widget Errors:
        - Field reference errors: "Widget 'bar' references fields that don't exist"
        - Available columns listed in error message for easy fixing
        - Type-specific requirements (e.g., pie charts need category_field + value_field)

    Examples:
        # Validate single-line query (would generate queryLines: ["SELECT..."])
        validate_dashboard_sql(
            datasets=[{
                "name": "Simple Sales",
                "query": "SELECT product, revenue FROM sales_transactions WHERE revenue > 100"
            }],
            warehouse_id="abc123",
            widgets=[{
                "type": "bar",
                "dataset": "Simple Sales",
                "config": {"x_field": "product", "y_field": "revenue"}
            }]
        )

        # Validate multi-line query (would generate queryLines array with line breaks preserved)
        validate_dashboard_sql(
            datasets=[{
                "name": "Complex Sales",
                "query": \"\"\"
                    SELECT
                        product,
                        SUM(revenue) as total_revenue,
                        COUNT(*) as sales_count
                    FROM sales_transactions
                    WHERE revenue > 0
                    GROUP BY product
                    ORDER BY total_revenue DESC
                \"\"\"
            }],
            warehouse_id="abc123",
            widgets=[{
                "type": "bar",
                "dataset": "Complex Sales",
                "config": {"x_field": "product", "y_field": "total_revenue"}
            }]
        )

        # Validate complex CTE query with parameters
        validate_dashboard_sql(
            datasets=[{
                "name": "Regional Analysis",
                "query": \"\"\"
                    WITH regional_sales AS (
                        SELECT
                            region,
                            revenue,
                            customer_id,
                            date
                        FROM sales
                        WHERE date >= :start_date
                    )
                    SELECT
                        region,
                        SUM(revenue) as total,
                        COUNT(DISTINCT customer_id) as unique_customers
                    FROM regional_sales
                    GROUP BY region
                    ORDER BY total DESC
                \"\"\",
                "parameters": [{
                    "displayName": "Start Date",
                    "keyword": "start_date",
                    "dataType": "DATE",
                    "defaultSelection": {"values": {"dataType": "DATE", "values": [{"value": "2024-01-01"}]}}
                }]
            }],
            warehouse_id="analytics_warehouse",
            widgets=[{
                "type": "bar",
                "dataset": "Regional Analysis",
                "config": {"x_field": "region", "y_field": "total"}
            }],
            catalog="production",
            schema="analytics"
        )
    """
    try:
      if widgets is None:
        widgets = []

      validation_results = {'queries_validated': [], 'widget_validations': [], 'warnings': []}

      print('🔍 Starting SQL validation for dashboard datasets...')

      # Validate each dataset query
      for dataset in datasets:
        query = dataset['query']
        dataset_name = dataset['name']

        print(f"🔍 Validating dataset '{dataset_name}' query...")
        validation_result = validate_sql_query(query, warehouse_id, catalog, schema)

        validation_results['queries_validated'].append(
          {
            'dataset': dataset_name,
            'valid': validation_result['valid'],
            'error': validation_result['error'],
            'columns': validation_result['columns'],
            'message': validation_result.get('message', ''),
          }
        )

        # Continue validation even if one query fails (collect all errors)
        if validation_result['valid']:
          # Validate widgets that reference this dataset
          dataset_columns = validation_result['columns']
          for widget in widgets:
            if widget.get('dataset') == dataset_name:
              print(
                f"🔍 Validating widget '{widget.get('type', 'unknown')}' fields against dataset '{dataset_name}'..."
              )
              widget_validation = validate_widget_fields(widget, dataset_columns)

              validation_results['widget_validations'].append(
                {
                  'widget_type': widget.get('type', 'unknown'),
                  'dataset': dataset_name,
                  'valid': widget_validation['valid'],
                  'error': widget_validation['error'],
                  'warnings': widget_validation['warnings'],
                }
              )

              # Collect warnings
              validation_results['warnings'].extend(widget_validation['warnings'])

      # Check if any validation failed
      query_failures = [q for q in validation_results['queries_validated'] if not q['valid']]
      widget_failures = [w for w in validation_results['widget_validations'] if not w['valid']]

      if query_failures or widget_failures:
        error_messages = []
        if query_failures:
          error_messages.extend([f"Dataset '{q['dataset']}': {q['error']}" for q in query_failures])
        if widget_failures:
          error_messages.extend(
            [f"Widget '{w['widget_type']}': {w['error']}" for w in widget_failures]
          )

        return {
          'success': False,
          'error': 'Validation failed. Issues found: ' + '; '.join(error_messages),
          'validation_results': validation_results,
        }

      print('✅ All SQL queries and widget fields validated successfully!')
      return {
        'success': True,
        'message': 'All SQL queries and widget field references are valid',
        'validation_results': validation_results,
      }

    except Exception as e:
      return {'success': False, 'error': f'Validation failed with error: {str(e)}'}

  @mcp_server.tool()
  def get_widget_configuration_guide(widget_type: str = None) -> Dict[str, Any]:
    """Get comprehensive configuration guide for Lakeview dashboard widgets.

    Provides detailed configuration options, required fields, examples, and best practices
    for creating dashboard widgets. Use this to understand available options before
    creating dashboards with create_dashboard_file.

    Args:
        widget_type: Optional specific widget type to get detailed info for.
                    If not provided, returns overview of all widget types.
                    Supported values:
                    - Chart widgets: "bar", "line", "area", "scatter", "pie", "histogram", "heatmap", "box", "funnel", "combo"
                    - Map widgets: "choropleth-map", "symbol-map"
                    - Display widgets: "counter", "table", "pivot", "text"
                    - Advanced widgets: "sankey"
                    - Filter widgets: "filter-single-select", "filter-multi-select", "filter-date-range-picker", "range-slider"

    Returns:
        Comprehensive widget configuration guide with examples and best practices.
    """
    # Widget categories for overview
    widget_categories = {
      'chart': [
        'bar',
        'line',
        'area',
        'scatter',
        'pie',
        'histogram',
        'heatmap',
        'box',
        'funnel',
        'combo',
      ],
      'map': ['choropleth-map', 'symbol-map'],
      'display': ['counter', 'table', 'pivot', 'text'],
      'advanced': ['sankey'],
      'filter': [
        'filter-single-select',
        'filter-multi-select',
        'filter-date-range-picker',
        'range-slider',
      ],
    }

    if widget_type is None:
      return {
        'widget_categories': widget_categories,
        'quick_reference': {
          'common_fields': [
            'x_field',
            'y_field',
            'color_field',
            'size_field',
            'value_field',
            'category_field',
          ],
          'scale_types': ['categorical', 'quantitative', 'temporal'],
          'color_schemes': ['redblue', 'viridis', 'plasma', 'inferno', 'magma'],
          'positioning': {'grid_columns': 12, 'auto_layout': '2-column'},
          'table_column_types': ['string', 'integer', 'float', 'date', 'boolean'],
          'table_display_types': ['string', 'number', 'datetime', 'link', 'image'],
        },
        'transformation_examples': {
          'description': 'Use {field_key}_expression for custom SQL transformations',
          'examples': [
            {
              'config': {
                'x_field': 'revenue',
                'x_expression': 'SUM(`revenue`)',
                'y_field': 'date',
                'y_expression': "DATE_TRUNC('MONTH', `date`)",
              },
              'description': 'Monthly revenue aggregation',
            },
            {
              'config': {
                'x_field': 'score',
                'x_expression': 'BIN_FLOOR(`score`, 10)',
                'y_field': 'count',
                'y_expression': 'COUNT(`*`)',
              },
              'description': 'Score distribution histogram',
            },
          ],
        },
        'common_patterns': {
          'aggregations': [
            'SUM(`field`)',
            'AVG(`field`)',
            'COUNT(`field`)',
            'COUNT(DISTINCT `field`)',
          ],
          'date_functions': [
            "DATE_TRUNC('MONTH', `date`)",
            "DATE_TRUNC('DAY', `timestamp`)",
            "DATE_TRUNC('YEAR', `created_at`)",
          ],
          'binning': [
            'BIN_FLOOR(`value`, 10)',
            'BIN_FLOOR(`score`, 5)',
            'BIN_FLOOR(`amount`, 100)',
          ],
          'helper_functions': {
            "get_aggregation_expression('revenue', 'sum')": 'SUM(`revenue`)',
            "get_date_trunc_expression('date', 'month')": "DATE_TRUNC('MONTH', `date`)",
            "get_bin_expression('score', 10)": 'BIN_FLOOR(`score`, 10)',
            'get_count_star_expression()': 'COUNT(`*`)',
          },
        },
        'dataset_optimization': {
          'description': 'Prefer widget-level transformations over multiple datasets',
          'best_practices': [
            'Use one raw dataset per data source',
            'Apply aggregations at widget level with expressions',
            'Avoid creating pre-aggregated datasets for each visualization',
            'Let Lakeview handle widget-level aggregations efficiently',
          ],
          'example': {
            'recommended': 'Single dataset + widget expressions',
            'avoid': 'Multiple pre-aggregated datasets',
          },
          'benefits': [
            'Fewer datasets to manage',
            "Better performance through Lakeview's native aggregation",
            'More flexible - easy to change aggregations',
            'Single source of truth per data source',
          ],
        },
        'usage': 'Call this function with a specific widget_type parameter to get detailed configuration options for that widget type.',
      }

    # Detailed configurations for specific widget types
    widget_configs = {
      'bar': {
        'description': 'Bar charts for categorical data visualization',
        'version': 3,
        'required_fields': ['x_field', 'y_field'],
        'optional_fields': {
          'color_field': 'Field for color grouping/series',
          'x_scale_type': 'Scale type for x-axis (categorical, quantitative, temporal)',
          'y_scale_type': 'Scale type for y-axis',
          'show_labels': 'Show data labels on bars',
          'colors': 'Custom color palette array',
          'title': 'Widget title',
          'x_axis_title': 'Custom x-axis title',
          'y_axis_title': 'Custom y-axis title',
          'x_expression': 'Custom SQL expression for x-axis (e.g., \'DATE_TRUNC("MONTH", `date`)\')',
          'y_expression': "Custom SQL expression for y-axis (e.g., 'SUM(`revenue`)')",
        },
        'examples': [
          {
            'name': 'Simple bar chart',
            'config': {'x_field': 'region', 'y_field': 'sales', 'title': 'Sales by Region'},
          },
          {
            'name': 'Grouped bar chart',
            'config': {
              'x_field': 'region',
              'y_field': 'sales',
              'color_field': 'product_category',
              'colors': ['#1f77b4', '#ff7f0e', '#2ca02c'],
              'show_labels': True,
            },
          },
          {
            'name': 'Monthly revenue aggregation (with expressions)',
            'config': {
              'x_field': 'month',
              'x_expression': "DATE_TRUNC('MONTH', `order_date`)",
              'y_field': 'total_revenue',
              'y_expression': 'SUM(`revenue`)',
              'title': 'Monthly Revenue Totals',
            },
          },
          {
            'name': 'Product sales with count aggregation',
            'config': {
              'x_field': 'product',
              'y_field': 'order_count',
              'y_expression': 'COUNT(`order_id`)',
              'title': 'Orders by Product',
            },
          },
        ],
      },
      'funnel': {
        'description': 'Funnel charts for conversion and step-wise data analysis',
        'version': 3,
        'required_fields': ['value_field'],
        'preferred_fields': ['stage_field', 'value_field'],
        'fallback_fields': ['category_field', 'x_field', 'color_field'],
        'field_notes': 'If stage_field is not provided, the system will attempt to use category_field, x_field, or color_field as the categorical dimension',
        'optional_fields': {
          'stage_display_name': 'Display name for stage field',
          'value_display_name': 'Display name for value field',
          'title': 'Widget title',
        },
        'examples': [
          {
            'name': 'Customer conversion funnel',
            'config': {
              'stage_field': 'tier',
              'value_field': 'customers',
              'title': 'Customer Loyalty Funnel',
            },
          },
          {
            'name': 'Sales pipeline funnel',
            'config': {
              'stage_field': 'stage',
              'value_field': 'deals',
              'stage_display_name': 'Sales Stage',
              'value_display_name': 'Deal Count',
            },
          },
          {
            'name': 'Flight volume funnel (using fallback)',
            'config': {
              'value_field': 'total_flights',
              'category_field': 'UniqueCarrier',
              'title': 'Flight Volume Funnel by Carrier',
            },
          },
        ],
      },
      'symbol-map': {
        'description': 'Point-based geographic visualizations with latitude/longitude coordinates',
        'version': 3,
        'required_fields': ['latitude_field', 'longitude_field'],
        'optional_fields': {
          'size_field': 'Field for point size encoding',
          'color_field': 'Field for color encoding',
          'color_scale_type': 'Scale type for color (categorical or quantitative)',
          'title': 'Widget title',
        },
        'examples': [
          {
            'name': 'Store locations with revenue',
            'config': {
              'latitude_field': 'lat',
              'longitude_field': 'lng',
              'size_field': 'store_size',
              'color_field': 'revenue',
              'title': 'Store Performance Map',
            },
          }
        ],
      },
      'table': {
        'description': 'Data tables with advanced formatting and interactive features',
        'version': 1,
        'required_fields': ['columns'],
        'optional_fields': {
          'items_per_page': 'Number of items per page',
          'condensed': 'Use condensed table layout',
          'with_row_number': 'Show row numbers',
          'title': 'Widget title',
        },
        'examples': [
          {'name': 'Simple table', 'config': {'columns': ['name', 'revenue', 'date']}},
          {
            'name': 'Advanced formatted table',
            'config': {
              'columns': [
                {'field': 'name', 'title': 'Customer', 'type': 'string'},
                {
                  'field': 'revenue',
                  'title': 'Revenue',
                  'type': 'float',
                  'display_as': 'number',
                  'number_format': '$,.0f',
                },
                {
                  'field': 'date',
                  'title': 'Date',
                  'type': 'date',
                  'display_as': 'datetime',
                  'date_format': 'MMM DD, YYYY',
                },
              ],
              'items_per_page': 25,
              'title': 'Customer Revenue Table',
            },
          },
        ],
      },
      'filter-single-select': {
        'description': 'Single-select dropdown filter for dashboard interactivity',
        'version': 2,
        'required_fields': ['field'],
        'optional_fields': {
          'display_name': 'Display name for the filter field',
          'title': 'Widget title',
          'default_field': 'Default field if none specified',
        },
        'examples': [
          {
            'name': 'State filter',
            'config': {'field': 'state', 'display_name': 'State', 'title': 'Filter by State'},
          },
          {
            'name': 'Category filter',
            'config': {
              'field': 'category',
              'display_name': 'Product Category',
              'title': 'Filter by Category',
            },
          },
        ],
      },
      'filter-multi-select': {
        'description': 'Multi-select dropdown filter for dashboard interactivity',
        'version': 2,
        'required_fields': ['field'],
        'optional_fields': {
          'display_name': 'Display name for the filter field',
          'title': 'Widget title',
        },
        'examples': [
          {
            'name': 'Regions filter',
            'config': {'field': 'region', 'display_name': 'Region', 'title': 'Select Regions'},
          }
        ],
      },
      'filter-date-range-picker': {
        'description': 'Date range picker filter for temporal data filtering',
        'version': 2,
        'required_fields': ['field'],
        'optional_fields': {
          'display_name': 'Display name for the date field',
          'title': 'Widget title',
        },
        'examples': [
          {
            'name': 'Date range filter',
            'config': {'field': 'date', 'display_name': 'Date Range', 'title': 'Select Date Range'},
          }
        ],
      },
    }

    if widget_type in widget_configs:
      return {
        'widget_type': widget_type,
        **widget_configs[widget_type],
        'transformation_support': {
          'description': 'All widgets support field expressions for custom SQL transformations',
          'pattern': "Use {field_key}_expression for custom SQL (e.g., 'y_expression': 'SUM(`revenue`)')",
          'helper_functions': [
            'get_aggregation_expression(field, func) - Generate aggregation expressions',
            'get_date_trunc_expression(field, interval) - Generate date truncation expressions',
            'get_bin_expression(field, width) - Generate binning expressions',
            'get_count_star_expression() - Generate count(*) expression',
          ],
        },
        'best_practices': [
          'Ensure field names match exactly with dataset columns',
          'Use appropriate scale types for data types',
          'Consider widget positioning in 12-column grid',
          'Add meaningful titles for better dashboard readability',
          'Prefer widget-level transformations over multiple datasets',
          'Use helper functions for common SQL patterns',
          'Always wrap field names in backticks in expressions',
        ],
      }
    else:
      return {
        'error': f"Widget type '{widget_type}' not recognized",
        'supported_types': [item for sublist in widget_categories.values() for item in sublist],
      }
