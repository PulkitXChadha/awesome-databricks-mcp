"""Simple layout optimization for Databricks dashboards.

This module provides intelligent dashboard layout optimization while following
the project's SIMPLE philosophy. No enterprise patterns, no abstractions,
just direct implementation of automatic layout intelligence.
"""

import hashlib
import os
import re
import time
from typing import Optional

# Simple cache using dictionary (no classes, no threading)
ANALYSIS_CACHE = {}
CACHE_TIMESTAMPS = {}
CACHE_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 100


def get_cached_result(query_hash: str) -> Optional[dict]:
  """Simple cache lookup with TTL check."""
  if query_hash in ANALYSIS_CACHE:
    timestamp = CACHE_TIMESTAMPS.get(query_hash, 0)
    if time.time() - timestamp < CACHE_TTL:
      return ANALYSIS_CACHE[query_hash]
    else:
      # Expired - remove it
      del ANALYSIS_CACHE[query_hash]
      del CACHE_TIMESTAMPS[query_hash]
  return None


def store_cached_result(query_hash: str, result: dict):
  """Simple cache storage with size limit."""
  # Basic size management
  if len(ANALYSIS_CACHE) >= MAX_CACHE_SIZE:
    # Remove oldest entry
    if CACHE_TIMESTAMPS:
      oldest = min(CACHE_TIMESTAMPS, key=CACHE_TIMESTAMPS.get)
      del ANALYSIS_CACHE[oldest]
      del CACHE_TIMESTAMPS[oldest]

  ANALYSIS_CACHE[query_hash] = result
  CACHE_TIMESTAMPS[query_hash] = time.time()


def analyze_widget_data(query: str, warehouse_id: str) -> dict:
  """Analyze query to get data characteristics for layout optimization.

  Returns row count, column count, data patterns, and complexity score.
  """
  try:
    # Simple cache check
    cache_key = f'{warehouse_id}:{hashlib.md5(query.encode()).hexdigest()}'
    cached = get_cached_result(cache_key)
    if cached:
      return cached

    # Get client directly
    from databricks.sdk import WorkspaceClient

    client = WorkspaceClient(host=os.getenv('DATABRICKS_HOST'), token=os.getenv('DATABRICKS_TOKEN'))

    # Analyze query structure first
    query_lower = query.lower()

    # Detect data patterns from query
    data_patterns = {
      'is_time_series': bool(re.search(r'date|time|timestamp|month|year|week|day', query_lower)),
      'is_aggregate': bool(re.search(r'sum\(|count\(|avg\(|max\(|min\(|group by', query_lower)),
      'is_single_value': bool(
        re.search(r'count\(\*\)|sum\(.*\)|avg\(.*\)|max\(.*\)|min\(.*\)', query_lower)
        and 'group by' not in query_lower
      ),
      'is_categorical': bool(re.search(r'group by|distinct', query_lower)),
      'has_multiple_metrics': len(re.findall(r'(sum|count|avg|max|min)\([^)]+\)', query_lower)) > 1,
      'is_hierarchical': bool(re.search(r'parent|child|tree|hierarchy|level', query_lower)),
      'has_currency': bool(re.search(r'price|cost|revenue|amount|salary|budget|\$', query_lower)),
      'has_percentage': bool(re.search(r'percent|rate|ratio|proportion', query_lower)),
      'has_geography': bool(
        re.search(r'country|state|city|region|location|latitude|longitude', query_lower)
      ),
    }

    # Sample the query to get actual data characteristics
    sampled_query = f'SELECT * FROM ({query}) base_query LIMIT 100'

    result = client.sql.statement_execution.execute_statement(
      warehouse_id=warehouse_id, statement=sampled_query, wait_timeout='30s'
    )

    # Basic counting and analysis
    row_count = 0
    column_count = 0
    column_types = []
    numeric_columns = 0
    date_columns = 0
    text_columns = 0

    if result.result and result.result.data_array:
      row_count = len(result.result.data_array)

      if result.manifest and result.manifest.schema and result.manifest.schema.columns:
        columns = result.manifest.schema.columns
        column_count = len(columns)

        for col in columns:
          col_type = col.type_name.lower() if col.type_name else 'string'
          column_types.append(col_type)

          if (
            'int' in col_type
            or 'float' in col_type
            or 'double' in col_type
            or 'decimal' in col_type
          ):
            numeric_columns += 1
          elif 'date' in col_type or 'time' in col_type:
            date_columns += 1
          else:
            text_columns += 1

    # Calculate complexity score (0-10)
    complexity_score = min(
      10,
      (
        min(5, row_count // 20)  # More rows = higher complexity
        + min(3, column_count // 3)  # More columns = higher complexity
        + (2 if data_patterns['has_multiple_metrics'] else 0)
      ),
    )

    # Determine recommended widget type based on patterns
    recommended_widget = determine_recommended_widget(
      data_patterns, row_count, column_count, numeric_columns, date_columns
    )

    analysis_result = {
      'row_count': row_count,
      'column_count': column_count,
      'column_types': column_types,
      'numeric_columns': numeric_columns,
      'date_columns': date_columns,
      'text_columns': text_columns,
      'data_patterns': data_patterns,
      'complexity_score': complexity_score,
      'recommended_widget': recommended_widget,
    }

    store_cached_result(cache_key, analysis_result)
    return analysis_result

  except Exception as e:
    # Return sensible defaults on error
    return {
      'row_count': 10,
      'column_count': 3,
      'column_types': [],
      'numeric_columns': 1,
      'date_columns': 0,
      'text_columns': 2,
      'data_patterns': {},
      'complexity_score': 3,
      'recommended_widget': None,
      'error': str(e),
    }


def determine_recommended_widget(
  data_patterns: dict, row_count: int, column_count: int, numeric_columns: int, date_columns: int
) -> Optional[str]:
  """Determine the best widget type based on data characteristics."""
  # Single value patterns - use counter or gauge
  if data_patterns.get('is_single_value'):
    if data_patterns.get('has_percentage'):
      return 'gauge'
    return 'counter'

  # Time series data - use line or area chart
  if data_patterns.get('is_time_series') and date_columns > 0:
    if row_count > 100:
      return 'area'
    return 'line'

  # Categorical comparisons
  if data_patterns.get('is_categorical'):
    if row_count <= 5:
      return 'pie'
    elif row_count <= 10:
      return 'bar'
    else:
      return 'table'

  # Geographic data - use map
  if data_patterns.get('has_geography'):
    return 'map'

  # Multiple metrics - use table or pivot
  if data_patterns.get('has_multiple_metrics'):
    if column_count > 5:
      return 'pivot'
    return 'table'

  # Default based on data volume
  if row_count == 1 and column_count == 1:
    return 'counter'
  elif row_count <= 10 and numeric_columns > 0:
    return 'bar'
  elif row_count > 50 or column_count > 5:
    return 'table'
  else:
    return 'bar'


def calculate_widget_dimensions(widget_type: str, data_analysis: dict) -> dict:
  """Calculate optimal widget dimensions based on type and data characteristics.

  Uses the 12-column grid system. Optimized for better visual layout.
  """
  row_count = data_analysis.get('row_count', 10)
  column_count = data_analysis.get('column_count', 3)
  complexity_score = data_analysis.get('complexity_score', 3)
  data_patterns = data_analysis.get('data_patterns', {})

  # Counter widgets - compact KPI display
  if widget_type == 'counter':
    return {'width': 3, 'height': 2}

  # Gauge widgets - slightly larger than counters
  if widget_type == 'gauge':
    return {'width': 3, 'height': 2}

  # Markdown/text widgets - based on content
  if widget_type == 'markdown':
    return {'width': 6, 'height': 2}

  # Table widgets - need more space for columns
  if widget_type == 'table':
    if column_count > 8:
      return {'width': 12, 'height': 6}
    elif column_count > 5:
      return {'width': 9, 'height': 5}
    elif column_count > 3:
      return {'width': 6, 'height': 5}
    else:
      return {'width': 6, 'height': 4}

  # Pivot tables - always large
  if widget_type == 'pivot':
    return {'width': 9, 'height': 6}

  # Pie charts - square-ish aspect ratio
  if widget_type == 'pie':
    if row_count > 8:
      return {'width': 4, 'height': 4}
    return {'width': 4, 'height': 4}

  # Line and area charts - wider for time series
  if widget_type in ['line', 'area']:
    if data_patterns.get('is_time_series'):
      if row_count > 100:
        return {'width': 12, 'height': 4}
      elif row_count > 50:
        return {'width': 6, 'height': 4}
      else:
        return {'width': 6, 'height': 4}
    return {'width': 6, 'height': 4}

  # Bar charts - width based on number of categories
  if widget_type == 'bar':
    if row_count > 20:
      return {'width': 12, 'height': 5}
    elif row_count > 10:
      return {'width': 6, 'height': 4}
    else:
      return {'width': 6, 'height': 4}

  # Scatter plots - need space for point distribution
  if widget_type == 'scatter':
    if row_count > 100:
      return {'width': 6, 'height': 5}
    return {'width': 6, 'height': 4}

  # Heatmaps - wide format for better visibility
  if widget_type == 'heatmap':
    return {'width': 12, 'height': 5}

  # Funnel charts
  if widget_type == 'funnel':
    return {'width': 4, 'height': 4}

  # Box plots
  if widget_type == 'box':
    return {'width': 6, 'height': 4}

  # Map widgets - need space for geographic display
  if widget_type == 'map':
    return {'width': 6, 'height': 5}

  # Default sizing based on complexity
  if complexity_score >= 7:
    return {'width': 6, 'height': 5}
  elif complexity_score >= 4:
    return {'width': 6, 'height': 4}
  else:
    return {'width': 6, 'height': 4}


def group_related_widgets(widgets: list) -> list:
  """Group related widgets together based on their data patterns and names.

  Returns widgets in optimized order.
  """
  # Simple grouping by widget type priority
  priority_order = {
    'counter': 1,  # KPIs first
    'gauge': 1,
    'line': 2,  # Trends second
    'area': 2,
    'bar': 3,  # Comparisons third
    'pie': 3,
    'table': 4,  # Details last
    'pivot': 4,
    'scatter': 5,
    'heatmap': 5,
    'funnel': 5,
    'box': 5,
    'map': 6,
    'markdown': 7,  # Text at the end
  }

  # Sort widgets by priority
  sorted_widgets = sorted(widgets, key=lambda w: priority_order.get(w.get('type', 'bar'), 10))

  # Group similar widgets together
  grouped = []
  current_group = []
  current_type = None

  for widget in sorted_widgets:
    widget_type = widget.get('type', 'bar')

    # Check if widget name suggests it's a KPI
    name_lower = widget.get('name', '').lower()
    is_kpi = any(kpi in name_lower for kpi in ['total', 'sum', 'count', 'average', 'kpi', 'metric'])

    if is_kpi and widget_type in ['counter', 'gauge']:
      # KPIs always go in the first group
      if not grouped and current_group:
        grouped.append(current_group)
        current_group = []
      current_group.append(widget)
    elif widget_type == current_type or priority_order.get(widget_type, 10) == priority_order.get(
      current_type, 10
    ):
      current_group.append(widget)
    else:
      if current_group:
        grouped.append(current_group)
      current_group = [widget]
      current_type = widget_type

  if current_group:
    grouped.append(current_group)

  # Flatten groups back to list
  result = []
  for group in grouped:
    result.extend(group)

  return result


def position_widgets(widgets: list) -> list:
  """Intelligent widget positioning using a 12-column grid system.

  Places widgets optimally based on their dimensions and relationships.
  """
  # Group related widgets first
  widgets = group_related_widgets(widgets)

  # Track occupied cells in the grid
  occupied = {}  # Key: (x, y), Value: True if occupied

  def is_space_available(x: int, y: int, width: int, height: int) -> bool:
    """Check if a space is available in the grid."""
    for row in range(y, y + height):
      for col in range(x, x + width):
        if (col, row) in occupied:
          return False
    return True

  def mark_space_occupied(x: int, y: int, width: int, height: int):
    """Mark a space as occupied in the grid."""
    for row in range(y, y + height):
      for col in range(x, x + width):
        occupied[(col, row)] = True

  def find_next_available_position(width: int, height: int, start_y: int = 0) -> tuple:
    """Find the next available position for a widget of given dimensions."""
    y = start_y
    while y < 100:  # Reasonable limit to prevent infinite loop
      for x in range(13 - width):  # 12 columns, ensure widget fits
        if is_space_available(x, y, width, height):
          return x, y
      y += 1
    return 0, y  # Fallback to leftmost position

  current_y = 0
  kpi_widgets = []

  # First pass: collect all KPI widgets
  for i, widget in enumerate(widgets):
    if 'dimensions' not in widget:
      data = widget.get('data_analysis', {})
      widget['dimensions'] = calculate_widget_dimensions(widget.get('type', 'bar'), data)

    widget_type = widget.get('type', 'bar')
    if widget_type in ['counter', 'gauge']:
      kpi_widgets.append((i, widget))

  # Position KPI widgets first (they should be at the top)
  if kpi_widgets:
    kpi_row_x = 0
    kpi_row_y = 0
    kpi_row_height = 0

    for idx, widget in kpi_widgets:
      dims = widget['dimensions']

      # Check if we need to move to next row
      if kpi_row_x + dims['width'] > 12:
        kpi_row_y += kpi_row_height
        kpi_row_x = 0
        kpi_row_height = 0

      # Set position
      widget['position'] = {
        'x': kpi_row_x,
        'y': kpi_row_y,
        'width': dims['width'],
        'height': dims['height'],
      }

      # Mark space as occupied
      mark_space_occupied(kpi_row_x, kpi_row_y, dims['width'], dims['height'])

      # Update for next KPI widget
      kpi_row_x += dims['width']
      kpi_row_height = max(kpi_row_height, dims['height'])

    # Update starting Y for non-KPI widgets
    current_y = kpi_row_y + kpi_row_height

  # Position non-KPI widgets
  for i, widget in enumerate(widgets):
    widget_type = widget.get('type', 'bar')

    # Skip if already positioned (KPI widgets)
    if 'position' in widget:
      continue

    dims = widget['dimensions']

    # Find best position for this widget
    x, y = find_next_available_position(dims['width'], dims['height'], current_y)

    # Set position
    widget['position'] = {'x': x, 'y': y, 'width': dims['width'], 'height': dims['height']}

    # Mark space as occupied
    mark_space_occupied(x, y, dims['width'], dims['height'])

    # Update current_y to encourage row-based layout
    if x == 0:  # Started a new row
      current_y = y

  return widgets


def detect_and_fix_overlaps(widgets: list) -> list:
  """Detect and fix any overlapping widgets in the layout.

  More robust implementation that handles all edge cases.
  """
  if not widgets:
    return widgets

  # Sort widgets by position for consistent processing
  widgets = sorted(
    widgets, key=lambda w: (w.get('position', {}).get('y', 0), w.get('position', {}).get('x', 0))
  )

  # Track occupied spaces
  occupied = {}  # Key: (x, y), Value: widget index

  def is_overlapping(x: int, y: int, width: int, height: int, widget_idx: int) -> bool:
    """Check if a widget position overlaps with already placed widgets."""
    for row in range(y, y + height):
      for col in range(x, min(x + width, 12)):  # Ensure we don't go beyond grid
        if (col, row) in occupied and occupied[(col, row)] != widget_idx:
          return True
    return False

  def mark_occupied(x: int, y: int, width: int, height: int, widget_idx: int):
    """Mark cells as occupied by a widget."""
    for row in range(y, y + height):
      for col in range(x, min(x + width, 12)):
        occupied[(col, row)] = widget_idx

  def find_free_position(width: int, height: int, start_y: int = 0) -> tuple:
    """Find next available position for a widget."""
    for y in range(start_y, start_y + 50):  # Reasonable search limit
      for x in range(13 - width):  # Ensure widget fits horizontally
        if not is_overlapping(x, y, width, height, -1):
          return x, y
    # Fallback: place at the bottom
    return 0, start_y + 50

  # Process each widget
  for i, widget in enumerate(widgets):
    if 'position' not in widget:
      continue

    pos = widget['position']

    # Validate position boundaries
    if pos['x'] < 0:
      pos['x'] = 0
    if pos['y'] < 0:
      pos['y'] = 0
    if pos['x'] + pos['width'] > 12:
      # Adjust width if it extends beyond grid
      if pos['width'] <= 12:
        pos['x'] = 12 - pos['width']
      else:
        pos['width'] = 12
        pos['x'] = 0

    # Check for overlap
    if is_overlapping(pos['x'], pos['y'], pos['width'], pos['height'], i):
      # Find new position
      new_x, new_y = find_free_position(pos['width'], pos['height'], pos['y'])
      widget['position']['x'] = new_x
      widget['position']['y'] = new_y

    # Mark as occupied
    mark_occupied(
      widget['position']['x'],
      widget['position']['y'],
      widget['position']['width'],
      widget['position']['height'],
      i,
    )

  return widgets


def optimize_dashboard_layout(widgets: list, warehouse_id: str, datasets: list = None) -> list:
  """Main function to optimize dashboard layout.

  Analyzes data, calculates dimensions, and positions widgets intelligently.
  """
  optimized_widgets = []

  for widget in widgets:
    widget_copy = widget.copy()

    # Skip if position is already manually specified
    if 'position' in widget_copy:
      optimized_widgets.append(widget_copy)
      continue

    # Get query from widget or dataset
    query = None
    if 'query' in widget_copy:
      query = widget_copy['query']
    elif 'dataset' in widget_copy and datasets:
      # Find matching dataset
      for ds in datasets:
        if ds.get('name') == widget_copy['dataset']:
          query = ds.get('query')
          break

    # Analyze data if we have a query
    if query and warehouse_id:
      analysis = analyze_widget_data(query, warehouse_id)
      widget_copy['data_analysis'] = analysis

      # Use recommended widget type if not specified
      if not widget_copy.get('type') and analysis.get('recommended_widget'):
        widget_copy['type'] = analysis['recommended_widget']
    else:
      # Use default analysis
      widget_copy['data_analysis'] = {'row_count': 10, 'column_count': 3, 'complexity_score': 3}

    # Calculate dimensions
    widget_copy['dimensions'] = calculate_widget_dimensions(
      widget_copy.get('type', 'bar'), widget_copy.get('data_analysis', {})
    )

    optimized_widgets.append(widget_copy)

  # Position all widgets
  optimized_widgets = position_widgets(optimized_widgets)

  # Fix any overlaps
  optimized_widgets = detect_and_fix_overlaps(optimized_widgets)

  return optimized_widgets


def validate_layout(widgets: list) -> dict:
  """Validate the layout for common issues.

  Returns validation results with any warnings or errors.
  """
  issues = []
  warnings = []

  # Check for widgets outside grid bounds
  for widget in widgets:
    if 'position' not in widget:
      issues.append(f"Widget '{widget.get('name', 'unnamed')}' missing position")
      continue

    pos = widget['position']
    if pos['x'] < 0 or pos['x'] >= 12:
      issues.append(f"Widget '{widget.get('name', 'unnamed')}' x position {pos['x']} out of bounds")
    if pos['y'] < 0:
      issues.append(f"Widget '{widget.get('name', 'unnamed')}' y position {pos['y']} is negative")
    if pos['width'] <= 0 or pos['width'] > 12:
      issues.append(f"Widget '{widget.get('name', 'unnamed')}' width {pos['width']} invalid")
    if pos['height'] <= 0:
      issues.append(f"Widget '{widget.get('name', 'unnamed')}' height {pos['height']} invalid")
    if pos['x'] + pos['width'] > 12:
      warnings.append(f"Widget '{widget.get('name', 'unnamed')}' extends beyond grid boundary")

  # Check for excessive vertical spacing
  if widgets:
    max_y = max(w['position']['y'] + w['position']['height'] for w in widgets if 'position' in w)
    if max_y > 50:
      warnings.append(f'Dashboard is very tall (height: {max_y}), consider reorganizing')

  return {'valid': len(issues) == 0, 'issues': issues, 'warnings': warnings}
