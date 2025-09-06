"""Widget specification functions for all Lakeview widget types.

Simple, direct widget creation with proper Lakeview JSON structure.
Supports all 16 widget types with correct encodings and specifications.
"""

import uuid
from typing import Any, Dict, List

# Widget version mapping according to schema requirements
WIDGET_VERSIONS = {
  'bar': 3,
  'line': 3,
  'area': 3,
  'scatter': 3,
  'heatmap': 3,
  'histogram': 3,
  'pie': 3,
  'box': 3,
  'funnel': 3,
  'combo': 3,
  'sankey': 1,
  'pivot': 1,
  'counter': 2,
  'table': 1,
  'filter-single-select': 2,
  'filter-multi-select': 2,
  'filter-date-range-picker': 2,
  'range-slider': 3,
  'choropleth-map': 3,
  'symbol-map': 3,
}


def generate_id() -> str:
  """Generate 8-character hex ID for Lakeview objects."""
  return str(uuid.uuid4())[:8]


# Simple SQL Expression Helper Functions (Phase 1 Enhancement)


def get_aggregation_expression(field: str, func: str) -> str:
  """Return aggregation SQL expression - direct and simple.

  Args:
      field: Column name to aggregate
      func: Aggregation function (SUM, AVG, COUNT, etc.)

  Returns:
      SQL expression string like 'SUM(`field_name`)'

  Examples:
      get_aggregation_expression("revenue", "sum") -> "SUM(`revenue`)"
      get_aggregation_expression("customer_id", "count") -> "COUNT(`customer_id`)"
      get_aggregation_expression("score", "avg") -> "AVG(`score`)"
  """
  return f'{func.upper()}(`{field}`)'


def get_date_trunc_expression(field: str, interval: str) -> str:
  """Return date truncation SQL expression - direct and simple.

  Args:
      field: Date/timestamp column name
      interval: Date interval (DAY, MONTH, YEAR, HOUR, etc.)

  Returns:
      SQL expression string like 'DATE_TRUNC("MONTH", `field_name`)'

  Examples:
      get_date_trunc_expression("date", "month") -> 'DATE_TRUNC("MONTH", `date`)'
      get_date_trunc_expression("timestamp", "day") -> 'DATE_TRUNC("DAY", `timestamp`)'
      get_date_trunc_expression("created_at", "year") -> 'DATE_TRUNC("YEAR", `created_at`)'
  """
  return f'DATE_TRUNC("{interval.upper()}", `{field}`)'


def get_bin_expression(field: str, width: int) -> str:
  """Return binning SQL expression - direct and simple.

  Args:
      field: Numeric column name to bin
      width: Bin width for grouping values

  Returns:
      SQL expression string like 'BIN_FLOOR(`field_name`, 10)'

  Examples:
      get_bin_expression("score", 10) -> "BIN_FLOOR(`score`, 10)"
      get_bin_expression("age", 5) -> "BIN_FLOOR(`age`, 5)"
      get_bin_expression("value", 100) -> "BIN_FLOOR(`value`, 100)"
  """
  return f'BIN_FLOOR(`{field}`, {width})'


def get_count_star_expression() -> str:
  """Return count(*) expression - direct and simple.

  Returns:
      SQL expression string 'COUNT(`*`)'

  Example:
      get_count_star_expression() -> "COUNT(`*`)"
  """
  return 'COUNT(`*`)'


def validate_expression_basic(expression: str) -> Dict[str, Any]:
  """Simple validation for common SQL patterns - no complex schemas.

  Args:
      expression: SQL expression string to validate

  Returns:
      Dict with validation result: {"valid": bool, "error": str|None}

  Examples:
      validate_expression_basic("SUM(`revenue`)") -> {"valid": True, "error": None}
      validate_expression_basic("DROP TABLE users") -> {"valid": False, "error": "Potentially dangerous pattern: DROP"}
      validate_expression_basic("revenue") -> {"valid": False, "error": "Expression should reference fields with backticks"}
  """
  try:
    # Basic checks for SQL injection patterns
    dangerous_patterns = ['DROP', 'DELETE', 'UPDATE', 'INSERT', '--', ';']
    expression_upper = expression.upper()

    for pattern in dangerous_patterns:
      if pattern in expression_upper:
        return {'valid': False, 'error': f'Potentially dangerous pattern: {pattern}'}

    # Check for basic SQL structure
    if '`' not in expression and expression != 'COUNT(`*)':
      return {'valid': False, 'error': 'Expression should reference fields with backticks'}

    return {'valid': True, 'error': None}
  except Exception as e:
    return {'valid': False, 'error': str(e)}


def find_dataset_id(dataset_name: str, datasets: List[Dict[str, Any]]) -> str:
  """Find dataset ID by display name."""
  for ds in datasets:
    if ds['displayName'] == dataset_name:
      return ds['name']

  # If not found, return the first dataset or generate new ID
  return datasets[0]['name'] if datasets else generate_id()


def create_standard_axis_encoding(
  field_name: str, scale_type: str, config: Dict, encoding_type: str = None
) -> Dict:
  """Create standardized axis encoding with required scale structure.

  Args:
      field_name: The field name for the encoding
      scale_type: Scale type (categorical, quantitative, temporal)
      config: Widget configuration containing additional settings
      encoding_type: Optional encoding type for config key lookups

  Returns:
      Standardized encoding structure with scale, axis, and display settings
  """
  encoding = {'fieldName': field_name, 'scale': {'type': scale_type}}

  # Add display name
  if encoding_type:
    display_name_key = f'{encoding_type}_display_name'
    if display_name_key in config:
      encoding['displayName'] = config[display_name_key]
    else:
      encoding['displayName'] = field_name
  else:
    encoding['displayName'] = config.get(f'{field_name}_display_name', field_name)

  # Add axis configuration if present
  if encoding_type:
    axis_title_key = f'{encoding_type}_axis_title'
    if axis_title_key in config:
      encoding['axis'] = {'title': config[axis_title_key]}

  # Add sort configuration for categorical scales
  if scale_type == 'categorical' and encoding_type:
    sort_key = f'{encoding_type}_sort'
    if sort_key in config:
      encoding['scale']['sort'] = {'by': config[sort_key]}

  return encoding


def create_color_scale(scale_type: str, config: Dict) -> Dict[str, Any]:
  """Create color scale with ramp and mapping support.

  Args:
      scale_type: Scale type (categorical, quantitative)
      config: Widget configuration with color settings

  Returns:
      Color scale configuration with ramps or mappings
  """
  scale = {'type': scale_type}

  # Add color ramp for quantitative scales
  if scale_type == 'quantitative' and 'color_scheme' in config:
    scale['colorRamp'] = {
      'mode': 'scheme',
      'scheme': config['color_scheme'],  # redblue, viridis, plasma, etc.
    }

  # Add custom mappings for categorical scales
  if scale_type == 'categorical' and 'color_mappings' in config:
    scale['mappings'] = config['color_mappings']

  return scale


def create_advanced_encoding(
  field_name: str, config: Dict[str, Any], encoding_type: str
) -> Dict[str, Any]:
  """Create advanced encoding with scale, axis, and display configuration.

  Args:
      field_name: The field name for the encoding
      config: Widget configuration containing scale/axis settings
      encoding_type: Type of encoding (x, y, color, size, etc.)

  Returns:
      Advanced encoding structure with scale, axis, and display settings
  """
  encoding = {'fieldName': field_name}

  # Add scale configuration with defaults if not specified
  scale_key = f'{encoding_type}_scale_type'
  scale_type = config.get(scale_key)

  # Set default scale types if not provided
  if scale_type is None:
    if encoding_type == 'x':
      scale_type = 'categorical'  # Default for x-axis in bar charts
    elif encoding_type == 'y':
      scale_type = 'quantitative'  # Default for y-axis in bar charts
    elif encoding_type == 'color':
      scale_type = 'categorical'  # Default for color grouping
    else:
      scale_type = 'quantitative'  # Default for other encodings like size

  # Create scale configuration
  if encoding_type == 'color':
    encoding['scale'] = create_color_scale(scale_type, config)
  else:
    scale = {'type': scale_type}

    # Add sort configuration for categorical scales
    if scale_type == 'categorical':
      sort_key = f'{encoding_type}_sort'
      if sort_key in config:
        scale['sort'] = {'by': config[sort_key]}

    encoding['scale'] = scale

  # Add axis configuration
  axis_title_key = f'{encoding_type}_axis_title'
  if axis_title_key in config:
    encoding['axis'] = {'title': config[axis_title_key]}

  # Add display name
  display_name_key = f'{encoding_type}_display_name'
  if display_name_key in config:
    encoding['displayName'] = config[display_name_key]
  else:
    encoding['displayName'] = field_name

  # Add legend configuration for color encoding
  if encoding_type == 'color' and 'legend_title' in config:
    encoding['legend'] = {'title': config['legend_title']}

  return encoding


def create_frame_config(config: Dict[str, Any]) -> Dict[str, Any]:
  """Create frame configuration for widget title and display."""
  frame = {}

  if 'title' in config:
    frame['title'] = config['title']
    frame['showTitle'] = config.get('show_title', True)

  return frame


def create_widget_queries(
  widget_config: Dict[str, Any], datasets: List[Dict]
) -> List[Dict[str, Any]]:
  """Create widget queries with field expressions and aggregations.

  Based on analysis of actual Lakeview dashboard examples, widgets typically need
  a 'fields' array in the query to specify which fields to use and how to aggregate them.
  This function now generates fields arrays by default for all widgets with field references.
  """
  config = widget_config.get('config', {})
  dataset_id = find_dataset_id(widget_config['dataset'], datasets)

  query = {'datasetName': dataset_id, 'disaggregated': config.get('disaggregated', False)}

  # Always generate fields array for widgets with field references
  # This matches the structure seen in real Lakeview dashboard examples
  fields = []

  # Add field expressions for each encoding
  for field_key in [
    'x_field',
    'y_field',
    'color_field',
    'size_field',
    'value_field',
    'category_field',
    'source_field',
    'target_field',
    'stage_field',
    'location_field',
    'latitude_field',
    'longitude_field',
  ]:
    if field_key in config:
      field_name = config[field_key]

      # Check if there's a custom expression
      expression_key = field_key.replace('_field', '_expression')
      if expression_key in config:
        fields.append({'name': field_name, 'expression': config[expression_key]})
      else:
        # Default expression (direct field reference)
        # This matches the format seen in example dashboards: "`field_name`"
        fields.append({'name': field_name, 'expression': f'`{field_name}`'})

  # Special handling for table widgets with column arrays
  if 'columns' in config and isinstance(config['columns'], list):
    for col in config['columns']:
      # Avoid duplicates if column is already added via other field keys
      if not any(f['name'] == col for f in fields):
        fields.append({'name': col, 'expression': f'`{col}`'})

  # Add fields array if we have any fields
  # This ensures the query format matches actual Lakeview dashboard examples
  if fields:
    query['fields'] = fields

  return [{'name': 'main_query', 'query': query}]


def create_widget_spec(
  widget_config: Dict[str, Any], datasets: List[Dict], dashboard_id: str = None
) -> Dict[str, Any]:
  """Create widget spec for any widget type with advanced Lakeview features.

  Args:
      widget_config: Widget configuration with structure:
          {
              "type": str,
              "dataset": str,
              "config": {
                  "x_field": str,
                  "y_field": str,
                  "x_scale_type": "categorical|quantitative|temporal",
                  "y_scale_type": "categorical|quantitative|temporal",
                  "color_mappings": [{"value": str, "color": str}],
                  "title": str,
                  "show_title": bool,
                  "version": int,
                  "custom_expressions": bool
              }
          }
      datasets: List of available datasets

  Returns:
      Complete widget specification for Lakeview dashboard with advanced features
  """
  widget_type = widget_config.get('type', 'table')

  # Chart widgets
  if widget_type == 'bar':
    return create_advanced_bar_widget(widget_config, datasets)
  elif widget_type == 'line':
    return create_advanced_line_widget(widget_config, datasets)
  elif widget_type == 'area':
    return create_advanced_area_widget(widget_config, datasets)
  elif widget_type == 'scatter':
    return create_advanced_scatter_widget(widget_config, datasets)
  elif widget_type == 'pie':
    return create_advanced_pie_widget(widget_config, datasets)
  elif widget_type == 'histogram':
    return create_advanced_histogram_widget(widget_config, datasets)
  elif widget_type == 'heatmap':
    return create_advanced_heatmap_widget(widget_config, datasets)
  elif widget_type == 'box':
    return create_box_widget(widget_config, datasets)
  elif widget_type == 'sankey':
    return create_sankey_widget(widget_config, datasets)
  elif widget_type == 'choropleth-map':
    return create_choropleth_widget(widget_config, datasets)
  elif widget_type == 'symbol-map':
    return create_symbol_map_widget(widget_config, datasets)
  elif widget_type == 'funnel':
    return create_funnel_widget(widget_config, datasets)
  elif widget_type == 'combo':
    return create_combo_widget(widget_config, datasets)
  elif widget_type == 'range-slider':
    return create_range_slider_widget(widget_config, datasets)

  # Display widgets
  elif widget_type == 'counter':
    return create_advanced_counter_widget(widget_config, datasets)
  elif widget_type == 'table':
    return create_advanced_table_widget(widget_config, datasets)
  elif widget_type == 'pivot':
    return create_advanced_pivot_widget(widget_config, datasets)
  elif widget_type == 'text':
    return create_advanced_text_widget(widget_config, datasets)

  # Filter widgets - Standardized versions with parameter support
  elif widget_type == 'filter-single-select':
    return create_filter_single_select_widget(widget_config, datasets, dashboard_id)
  elif widget_type == 'filter-multi-select':
    return create_filter_multi_select_widget(widget_config, datasets, dashboard_id)
  elif widget_type == 'filter-date-range-picker':
    return create_filter_date_range_widget(widget_config, datasets, dashboard_id)
  elif widget_type == 'filter-date-range':  # Legacy compatibility
    return create_filter_date_range_widget(widget_config, datasets, dashboard_id)

  # Legacy filter widget names (for compatibility)
  elif widget_type == 'dropdown':
    return create_filter_single_select_widget(widget_config, datasets, dashboard_id)
  elif widget_type == 'multi_select':
    return create_filter_multi_select_widget(widget_config, datasets, dashboard_id)
  elif widget_type == 'date_range':
    return create_filter_date_range_widget(widget_config, datasets, dashboard_id)
  elif widget_type == 'slider':
    return create_slider_widget(widget_config, datasets)
  elif widget_type == 'text_search':
    return create_text_search_widget(widget_config, datasets)

  else:
    # Default to table widget for unknown types
    return create_advanced_table_widget(widget_config, datasets)


# Advanced Chart Widgets


def create_advanced_bar_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced bar chart widget spec with scales, axes, and legends."""
  widget_config = config.get('config', {})

  encodings = {}

  # X-axis encoding with advanced features
  if 'x_field' in widget_config:
    encodings['x'] = create_advanced_encoding(widget_config['x_field'], widget_config, 'x')

  # Y-axis encoding with advanced features
  if 'y_field' in widget_config:
    encodings['y'] = create_advanced_encoding(widget_config['y_field'], widget_config, 'y')

  # Color encoding with custom mappings
  if 'color_field' in widget_config:
    encodings['color'] = create_advanced_encoding(
      widget_config['color_field'], widget_config, 'color'
    )

  # Build widget spec
  spec = {'version': WIDGET_VERSIONS['bar'], 'widgetType': 'bar', 'encodings': encodings}

  # Add frame configuration
  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


# Legacy function for backward compatibility
def create_bar_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy bar widget creation - redirects to advanced version."""
  return create_advanced_bar_widget(config, datasets)


def create_advanced_line_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced line chart widget spec with scales, axes, and legends."""
  widget_config = config.get('config', {})

  encodings = {}

  # X-axis encoding (typically temporal for line charts)
  if 'x_field' in widget_config:
    encodings['x'] = create_advanced_encoding(widget_config['x_field'], widget_config, 'x')

  # Y-axis encoding
  if 'y_field' in widget_config:
    encodings['y'] = create_advanced_encoding(widget_config['y_field'], widget_config, 'y')

  # Color encoding for multiple series
  if 'color_field' in widget_config:
    encodings['color'] = create_advanced_encoding(
      widget_config['color_field'], widget_config, 'color'
    )

  spec = {'version': WIDGET_VERSIONS['line'], 'widgetType': 'line', 'encodings': encodings}

  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


def create_line_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy line widget creation - redirects to advanced version."""
  return create_advanced_line_widget(config, datasets)


def create_advanced_area_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced area chart widget spec."""
  widget_config = config.get('config', {})

  encodings = {}

  # X-axis encoding
  if 'x_field' in widget_config:
    encodings['x'] = create_advanced_encoding(widget_config['x_field'], widget_config, 'x')

  # Y-axis encoding
  if 'y_field' in widget_config:
    encodings['y'] = create_advanced_encoding(widget_config['y_field'], widget_config, 'y')

  # Color encoding for stacking
  if 'color_field' in widget_config:
    encodings['color'] = create_advanced_encoding(
      widget_config['color_field'], widget_config, 'color'
    )

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['area'],
      'widgetType': 'area',
      'encodings': encodings,
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(config, datasets),
  }


def create_area_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy area widget creation - redirects to advanced version."""
  return create_advanced_area_widget(config, datasets)


def create_advanced_scatter_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced scatter plot widget spec with full encoding support."""
  widget_config = config.get('config', {})

  encodings = {}

  # X-axis encoding
  if 'x_field' in widget_config:
    encodings['x'] = create_advanced_encoding(widget_config['x_field'], widget_config, 'x')

  # Y-axis encoding
  if 'y_field' in widget_config:
    encodings['y'] = create_advanced_encoding(widget_config['y_field'], widget_config, 'y')

  # Color encoding with custom mappings (important for scatter plots)
  if 'color_field' in widget_config:
    encodings['color'] = create_advanced_encoding(
      widget_config['color_field'], widget_config, 'color'
    )

  # Size encoding for bubble charts
  if 'size_field' in widget_config:
    encodings['size'] = create_advanced_encoding(widget_config['size_field'], widget_config, 'size')

  spec = {'version': WIDGET_VERSIONS['scatter'], 'widgetType': 'scatter', 'encodings': encodings}

  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


def create_scatter_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy scatter widget creation - redirects to advanced version."""
  return create_advanced_scatter_widget(config, datasets)


def create_advanced_pie_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create pie chart with correct angle/color encodings."""
  widget_config = config.get('config', {})

  encodings = {}

  # Angle encoding (value field)
  if 'value_field' in widget_config:
    encodings['angle'] = {
      'fieldName': widget_config['value_field'],
      'scale': {'type': 'quantitative'},
      'displayName': widget_config.get('value_display_name', widget_config['value_field']),
    }

  # Color encoding (category field)
  if 'category_field' in widget_config:
    encodings['color'] = {
      'fieldName': widget_config['category_field'],
      'scale': {'type': 'categorical'},
      'displayName': widget_config.get('category_display_name', widget_config['category_field']),
    }

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['pie'],
      'widgetType': 'pie',
      'encodings': encodings,
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(config, datasets),
  }


def create_pie_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy pie chart widget creation - redirects to advanced version."""
  return create_advanced_pie_widget(config, datasets)


def create_advanced_histogram_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced histogram widget spec.

  Histograms require both X and Y encodings according to the Lakeview schema:
  - X: quantitative or temporal scale with binning for numeric distribution
  - Y: quantitative scale with count aggregation (count(*) by default)

  Critical: The query fields must match the encoding fieldNames exactly.
  For histograms, this means the query must provide binned fields with proper SQL expressions.
  """
  widget_config = config.get('config', {})

  encodings = {}

  # X-field encoding with binning (required)
  if 'x_field' in widget_config:
    x_field = widget_config['x_field']
    bin_width = widget_config.get('bin_width', 10)  # Default bin width

    # Create binned field expression for histograms
    binned_field = f'bin({x_field}, binWidth={bin_width})'

    encodings['x'] = {
      'fieldName': binned_field,
      'scale': {'type': 'quantitative'},
      'displayName': widget_config.get('x_display_name', x_field),
    }

  # Y-field encoding with count aggregation (required for histograms)
  y_field = widget_config.get('y_field', 'count(*)')

  encodings['y'] = {
    'fieldName': y_field,
    'scale': {'type': 'quantitative'},
    'displayName': widget_config.get('y_display_name', 'Count of Records'),
  }

  # Prepare config for query generation with proper binned fields
  updated_config = config.copy()
  histogram_config = widget_config.copy()

  # Critical fix: Ensure the query fields match the encoding fieldNames exactly
  if 'x_field' in widget_config:
    x_field = widget_config['x_field']
    bin_width = widget_config.get('bin_width', 10)

    # The binned field name must match what's in encodings
    binned_field = f'bin({x_field}, binWidth={bin_width})'

    # Set up both the field name and expression for the binned field
    histogram_config['x_field'] = binned_field  # This matches the encoding fieldName
    histogram_config['x_expression'] = get_bin_expression(
      x_field, bin_width
    )  # This is the SQL expression

  # Set up count field with proper expression
  histogram_config['y_field'] = y_field
  histogram_config['y_expression'] = (
    get_count_star_expression() if y_field == 'count(*)' else y_field
  )

  updated_config['config'] = histogram_config

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['histogram'],
      'widgetType': 'histogram',
      'encodings': encodings,
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(updated_config, datasets),
  }


def create_histogram_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy histogram widget creation - redirects to advanced version."""
  return create_advanced_histogram_widget(config, datasets)


def create_advanced_heatmap_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create heatmap widget with color ramp support."""
  widget_config = config.get('config', {})

  encodings = {}

  # X and Y axis encodings
  if 'x_field' in widget_config:
    encodings['x'] = {
      'fieldName': widget_config['x_field'],
      'scale': {'type': 'categorical'},
      'displayName': widget_config.get('x_display_name', widget_config['x_field']),
    }

    # Add axis title hiding option
    if widget_config.get('hide_x_title'):
      encodings['x']['axis'] = {'hideTitle': True}

  if 'y_field' in widget_config:
    encodings['y'] = {
      'fieldName': widget_config['y_field'],
      'scale': {'type': 'categorical'},
      'displayName': widget_config.get('y_display_name', widget_config['y_field']),
    }

    if widget_config.get('hide_y_title'):
      encodings['y']['axis'] = {'hideTitle': True}

  # Color encoding with color ramp - support both color_field and value_field
  color_field = widget_config.get('color_field') or widget_config.get('value_field')
  if color_field:
    color_scale = create_color_scale('quantitative', widget_config)
    encodings['color'] = {
      'fieldName': color_field,
      'scale': color_scale,
      'displayName': widget_config.get('color_display_name')
      or widget_config.get('value_display_name', color_field),
    }

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['heatmap'],
      'widgetType': 'heatmap',
      'encodings': encodings,
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(config, datasets),
  }


def create_heatmap_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy heatmap widget creation - redirects to advanced version."""
  return create_advanced_heatmap_widget(config, datasets)


# Display Widgets


def create_advanced_counter_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced counter widget spec with proper encoding structure.

  Counter widgets have a simple value encoding without scale properties,
  according to the Lakeview schema and dashboard examples.
  """
  widget_config = config.get('config', {})

  encodings = {}

  # Value encoding with display name - NO scale property for counter widgets
  if 'value_field' in widget_config:
    encodings['value'] = {
      'fieldName': widget_config['value_field'],
      'displayName': widget_config.get('value_display_name', widget_config['value_field']),
    }

  spec = {'version': WIDGET_VERSIONS['counter'], 'widgetType': 'counter', 'encodings': encodings}

  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


def create_counter_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Legacy counter widget creation - redirects to advanced version."""
  return create_advanced_counter_widget(config, datasets)


def create_table_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create table widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'columns' in widget_config:
    encodings['columns'] = [{'fieldName': col} for col in widget_config['columns']]

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'table', 'encodings': encodings},
    'queries': create_widget_queries(config, datasets),
  }


def create_pivot_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create pivot table widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'rows' in widget_config:
    encodings['rows'] = [{'fieldName': row} for row in widget_config['rows']]
  if 'columns' in widget_config:
    encodings['columns'] = [{'fieldName': col} for col in widget_config['columns']]
  if 'values' in widget_config:
    encodings['values'] = [{'fieldName': val} for val in widget_config['values']]

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'pivot', 'encodings': encodings},
    'queries': create_widget_queries(config, datasets),
  }


def create_text_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create text widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'text' in widget_config:
    encodings['text'] = widget_config['text']
  if 'markdown' in widget_config:
    encodings['markdown'] = widget_config['markdown']

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'text', 'encodings': encodings},
    'queries': []
    if not config.get('dataset')
    else [
      {
        'name': generate_id(),
        'query': {'datasetName': find_dataset_id(config['dataset'], datasets)},
      }
    ],
  }


# Filter Widgets


def create_dropdown_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create dropdown filter widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'field' in widget_config:
    encodings['field'] = {'fieldName': widget_config['field']}
  if 'label' in widget_config:
    encodings['label'] = widget_config['label']

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'dropdown', 'encodings': encodings},
    'queries': create_widget_queries(config, datasets),
  }


def create_multi_select_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create multi-select filter widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'field' in widget_config:
    encodings['field'] = {'fieldName': widget_config['field']}
  if 'label' in widget_config:
    encodings['label'] = widget_config['label']

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'multiSelect', 'encodings': encodings},
    'queries': create_widget_queries(config, datasets),
  }


def create_date_range_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create date range filter widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'field' in widget_config:
    encodings['field'] = {'fieldName': widget_config['field']}
  if 'label' in widget_config:
    encodings['label'] = widget_config['label']
  if 'start_date' in widget_config:
    encodings['startDate'] = widget_config['start_date']
  if 'end_date' in widget_config:
    encodings['endDate'] = widget_config['end_date']

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'dateRange', 'encodings': encodings},
    'queries': create_widget_queries(config, datasets),
  }


def create_slider_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create slider filter widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'field' in widget_config:
    encodings['field'] = {'fieldName': widget_config['field']}
  if 'label' in widget_config:
    encodings['label'] = widget_config['label']
  if 'min_value' in widget_config:
    encodings['minValue'] = widget_config['min_value']
  if 'max_value' in widget_config:
    encodings['maxValue'] = widget_config['max_value']

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'slider', 'encodings': encodings},
    'queries': create_widget_queries(config, datasets),
  }


def create_text_search_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create text search filter widget spec."""
  widget_config = config.get('config', {})

  encodings = {}
  if 'field' in widget_config:
    encodings['field'] = {'fieldName': widget_config['field']}
  if 'label' in widget_config:
    encodings['label'] = widget_config['label']
  if 'placeholder' in widget_config:
    encodings['placeholder'] = widget_config['placeholder']

  return {
    'name': generate_id(),
    'spec': {'widgetType': 'textSearch', 'encodings': encodings},
    'queries': create_widget_queries(config, datasets),
  }


# Advanced Widget Types


def create_filter_single_select_widget(
  config: Dict, datasets: List[Dict], dashboard_id: str = None
) -> Dict[str, Any]:
  """Create standardized single-select filter widget."""
  widget_config = config.get('config', {})

  fields = []

  # Support both new and legacy field configurations
  if 'fields' in widget_config:
    # New array-based field configuration
    for field_config in widget_config['fields']:
      if isinstance(field_config, dict) and 'fieldName' in field_config:
        field = {
          'fieldName': field_config['fieldName'],
          'displayName': field_config.get('displayName', field_config['fieldName']),
        }
        if 'queryName' in field_config:
          field['queryName'] = field_config['queryName']
        fields.append(field)
  elif 'field' in widget_config:
    # Legacy single field configuration
    field = {
      'fieldName': widget_config['field'],
      'displayName': widget_config.get('display_name', widget_config['field']),
    }

    # Generate queryName from dataset if available
    if 'query_name' in widget_config:
      field['queryName'] = widget_config['query_name']
    elif datasets and dashboard_id:
      # Auto-generate queryName from first dataset
      dataset_id = find_dataset_id(widget_config.get('dataset', ''), datasets)
      if dataset_id:
        field['queryName'] = (
          f'dashboards/{dashboard_id}/datasets/{dataset_id}_{widget_config["field"]}'
        )

    fields.append(field)

  # If no fields configured, try to infer from query data
  if not fields and datasets and dashboard_id:
    # Get first available string/categorical field from dataset
    dataset_id = find_dataset_id(widget_config.get('dataset', ''), datasets)
    if dataset_id:
      # Create a default field - this should be configured properly by caller
      default_field = widget_config.get('default_field', 'category')
      field = {
        'fieldName': default_field,
        'displayName': default_field.replace('_', ' ').title(),
        'queryName': f'dashboards/{dashboard_id}/datasets/{dataset_id}_{default_field}',
      }
      fields.append(field)

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['filter-single-select'],
      'widgetType': 'filter-single-select',
      'encodings': {'fields': fields},
      'frame': create_frame_config(widget_config),
    },
  }


def create_filter_multi_select_widget(
  config: Dict, datasets: List[Dict], dashboard_id: str = None
) -> Dict[str, Any]:
  """Create standardized multi-select filter widget."""
  widget_config = config.get('config', {})

  fields = []

  # Support both new and legacy field configurations
  if 'fields' in widget_config:
    # New array-based field configuration
    for field_config in widget_config['fields']:
      if isinstance(field_config, dict) and 'fieldName' in field_config:
        field = {
          'fieldName': field_config['fieldName'],
          'displayName': field_config.get('displayName', field_config['fieldName']),
        }
        if 'queryName' in field_config:
          field['queryName'] = field_config['queryName']
        fields.append(field)
  elif 'field' in widget_config:
    # Legacy single field configuration
    field = {
      'fieldName': widget_config['field'],
      'displayName': widget_config.get('display_name', widget_config['field']),
    }

    # Generate queryName from dataset if available
    if 'query_name' in widget_config:
      field['queryName'] = widget_config['query_name']
    elif datasets and dashboard_id:
      # Auto-generate queryName from first dataset
      dataset_id = find_dataset_id(widget_config.get('dataset', ''), datasets)
      if dataset_id:
        field['queryName'] = (
          f'dashboards/{dashboard_id}/datasets/{dataset_id}_{widget_config["field"]}'
        )

    fields.append(field)

  # If no fields configured, try to infer from query data
  if not fields and datasets and dashboard_id:
    # Get first available string/categorical field from dataset
    dataset_id = find_dataset_id(widget_config.get('dataset', ''), datasets)
    if dataset_id:
      # Create a default field - this should be configured properly by caller
      default_field = widget_config.get('default_field', 'category')
      field = {
        'fieldName': default_field,
        'displayName': default_field.replace('_', ' ').title(),
        'queryName': f'dashboards/{dashboard_id}/datasets/{dataset_id}_{default_field}',
      }
      fields.append(field)

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['filter-multi-select'],
      'widgetType': 'filter-multi-select',
      'encodings': {'fields': fields},
      'frame': create_frame_config(widget_config),
    },
  }


def create_filter_date_range_widget(
  config: Dict, datasets: List[Dict], dashboard_id: str = None
) -> Dict[str, Any]:
  """Create standardized date range filter widget."""
  widget_config = config.get('config', {})

  fields = []

  # Support both new and legacy field configurations
  if 'fields' in widget_config:
    # New array-based field configuration
    for field_config in widget_config['fields']:
      if isinstance(field_config, dict) and 'fieldName' in field_config:
        field = {
          'fieldName': field_config['fieldName'],
          'displayName': field_config.get('displayName', field_config['fieldName']),
        }
        if 'queryName' in field_config:
          field['queryName'] = field_config['queryName']
        fields.append(field)
  elif 'field' in widget_config:
    # Legacy single field configuration
    field = {
      'fieldName': widget_config['field'],
      'displayName': widget_config.get('display_name', widget_config['field']),
    }

    # Generate queryName from dataset if available
    if 'query_name' in widget_config:
      field['queryName'] = widget_config['query_name']
    elif datasets and dashboard_id:
      # Auto-generate queryName from first dataset
      dataset_id = find_dataset_id(widget_config.get('dataset', ''), datasets)
      if dataset_id:
        field['queryName'] = (
          f'dashboards/{dashboard_id}/datasets/{dataset_id}_{widget_config["field"]}'
        )

    fields.append(field)

  # If no fields configured, try to infer from query data
  if not fields and datasets and dashboard_id:
    # Get first available date/temporal field from dataset
    dataset_id = find_dataset_id(widget_config.get('dataset', ''), datasets)
    if dataset_id:
      # Create a default field - this should be configured properly by caller
      default_field = widget_config.get('default_field', 'date')
      field = {
        'fieldName': default_field,
        'displayName': default_field.replace('_', ' ').title(),
        'queryName': f'dashboards/{dashboard_id}/datasets/{dataset_id}_{default_field}',
      }
      fields.append(field)

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['filter-date-range-picker'],
      'widgetType': 'filter-date-range-picker',
      'encodings': {'fields': fields},
      'frame': create_frame_config(widget_config),
    },
  }


def create_sankey_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create Sankey diagram widget."""
  widget_config = config.get('config', {})

  encodings = {}

  # Value field (required)
  if 'value_field' in widget_config:
    encodings['value'] = {
      'fieldName': widget_config['value_field'],
      'displayName': widget_config.get('value_display_name', 'Value'),
    }

  # Stages array (source and target fields)
  stages = []
  if 'source_field' in widget_config:
    stages.append(
      {
        'fieldName': widget_config['source_field'],
        'displayName': widget_config.get('source_display_name', 'Source'),
      }
    )
  if 'target_field' in widget_config:
    stages.append(
      {
        'fieldName': widget_config['target_field'],
        'displayName': widget_config.get('target_display_name', 'Target'),
      }
    )

  if stages:
    encodings['stages'] = stages

  spec = {'version': 1, 'widgetType': 'sankey', 'encodings': encodings}

  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


def create_box_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create box plot widget with correct Lakeview structure."""
  widget_config = config.get('config', {})

  encodings = {}

  # X-axis (categorical field) - REQUIRED for box plots
  x_field = widget_config.get('x_field') or widget_config.get('category_field')
  if x_field:
    encodings['x'] = {'fieldName': x_field, 'scale': {'type': 'categorical'}}
  else:
    # Box plots require an x-axis field
    return {
      'name': generate_id(),
      'spec': {'error': 'Box plots require an x_field or category_field'},
      'queries': [],
    }

  # Y-axis structure for box plots (requires statistical fields)
  y_encoding = {'scale': {'type': 'quantitative'}}

  # Box plot requires specific statistical fields
  if 'min_field' in widget_config:
    y_encoding['whiskerStart'] = {'fieldName': widget_config['min_field']}
  if 'q1_field' in widget_config:
    y_encoding['boxStart'] = {'fieldName': widget_config['q1_field']}
  if 'median_field' in widget_config:
    y_encoding['boxMid'] = {'fieldName': widget_config['median_field']}
  if 'q3_field' in widget_config:
    y_encoding['boxEnd'] = {'fieldName': widget_config['q3_field']}
  if 'max_field' in widget_config:
    y_encoding['whiskerEnd'] = {'fieldName': widget_config['max_field']}

  # If no statistical fields are provided, fall back to a simple value field
  if not any(
    key in y_encoding for key in ['whiskerStart', 'boxStart', 'boxMid', 'boxEnd', 'whiskerEnd']
  ):
    if 'value_field' in widget_config:
      y_encoding['fieldName'] = widget_config['value_field']
    else:
      # Y-axis requires at least one field
      return {
        'name': generate_id(),
        'spec': {
          'error': 'Box plots require statistical fields (min_field, q1_field, etc.) or value_field'
        },
        'queries': [],
      }

  encodings['y'] = y_encoding

  spec = {'version': 3, 'widgetType': 'box', 'encodings': encodings}

  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


def create_choropleth_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create choropleth map widget with proper region encoding structure."""
  widget_config = config.get('config', {})

  encodings = {}

  # Color encoding for the quantitative value
  if 'color_field' in widget_config:
    encodings['color'] = create_advanced_encoding(
      widget_config['color_field'], widget_config, 'color'
    )

  # Region encoding for geographical data
  if 'location_field' in widget_config:
    location_field = widget_config['location_field']
    geo_type = widget_config.get('geo_type', 'state')  # Default to state

    # Map geo_type to geographic role
    geo_role_mapping = {
      'country': 'admin0-unit-code',
      'state': 'admin1-unit-code',
      'county': 'admin2-unit-code',
      'zipcode': 'zipcode',
    }

    # Map geo_type to admin level
    admin_level_mapping = {
      'country': 'admin0',
      'state': 'admin1',
      'county': 'admin2',
      'zipcode': 'zipcode',
    }

    geo_role = geo_role_mapping.get(geo_type, 'admin1-unit-code')
    admin_level = admin_level_mapping.get(geo_type, 'admin1')

    encodings['region'] = {
      'regionType': 'mapbox-v4-admin',
      admin_level: {
        'fieldName': location_field,
        'type': 'field',
        'geographicRole': geo_role,
        'displayName': widget_config.get('location_display_name', location_field.title()),
      },
    }

  spec = {
    'version': 1,  # Using version 1 as per real examples, not schema version 3
    'widgetType': 'choropleth-map',
    'encodings': encodings,
  }

  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


# Advanced implementations are now defined inline above


def create_advanced_table_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create table widget with full column specifications."""
  widget_config = config.get('config', {})

  columns = []
  if 'columns' in widget_config:
    for i, col_config in enumerate(widget_config['columns']):
      if isinstance(col_config, str):
        # Simple column name - create basic column
        column = {
          'fieldName': col_config,
          'type': 'string',  # Default type
          'displayAs': 'string',  # Default display
          'visible': True,
          'order': i,
          'title': col_config,
        }
      else:
        # Full column configuration
        column = {
          'fieldName': col_config['field'],
          'type': col_config.get('type', 'string'),
          'displayAs': col_config.get('display_as', 'string'),
          'visible': col_config.get('visible', True),
          'order': col_config.get('order', i),
          'title': col_config.get('title', col_config['field']),
        }

        # Add optional formatting
        if 'number_format' in col_config:
          column['numberFormat'] = col_config['number_format']
        if 'date_format' in col_config:
          column['dateTimeFormat'] = col_config['date_format']

        # Add link configuration
        if col_config.get('display_as') == 'link':
          column['linkUrlTemplate'] = col_config.get('link_url', '')
          column['linkTextTemplate'] = col_config.get('link_text', '')
          column['linkOpenInNewTab'] = col_config.get('link_new_tab', True)

        # Add image configuration
        if col_config.get('display_as') == 'image':
          column['imageUrlTemplate'] = col_config.get('image_url', '')
          column['imageWidth'] = col_config.get('image_width', '100px')
          column['imageHeight'] = col_config.get('image_height', '100px')

        # Add boolean values
        if col_config.get('type') == 'boolean':
          column['booleanValues'] = col_config.get('boolean_values', ['false', 'true'])

        # Add content alignment
        if 'align' in col_config:
          column['alignContent'] = col_config['align']

        # Add search capability
        column['allowSearch'] = col_config.get('allow_search', True)

        # Add HTML support
        column['allowHTML'] = col_config.get('allow_html', False)

      columns.append(column)

  # Build table spec
  spec = {
    'version': WIDGET_VERSIONS['table'],
    'widgetType': 'table',
    'encodings': {'columns': columns},
  }

  # Add table-specific options
  if 'items_per_page' in widget_config:
    spec['itemsPerPage'] = widget_config['items_per_page']
  if 'pagination_size' in widget_config:
    spec['paginationSize'] = widget_config['pagination_size']
  if 'condensed' in widget_config:
    spec['condensed'] = widget_config['condensed']
  if 'with_row_number' in widget_config:
    spec['withRowNumber'] = widget_config['with_row_number']
  if 'allow_html_default' in widget_config:
    spec['allowHTMLByDefault'] = widget_config['allow_html_default']

  # Add frame
  frame = create_frame_config(widget_config)
  if frame:
    spec['frame'] = frame

  return {'name': generate_id(), 'spec': spec, 'queries': create_widget_queries(config, datasets)}


def create_advanced_pivot_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced pivot widget - currently redirects to simple version."""
  return create_pivot_widget(config, datasets)


def create_advanced_text_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create advanced text widget - currently redirects to simple version."""
  return create_text_widget(config, datasets)


# New Missing Widget Types Implementation


def create_symbol_map_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create symbol map widget with latitude/longitude encoding."""
  widget_config = config.get('config', {})

  encodings = {}

  # Required latitude/longitude encodings
  if 'latitude_field' in widget_config:
    encodings['latitude'] = {
      'fieldName': widget_config['latitude_field'],
      'displayName': widget_config.get('latitude_display_name', 'Latitude'),
    }

  if 'longitude_field' in widget_config:
    encodings['longitude'] = {
      'fieldName': widget_config['longitude_field'],
      'displayName': widget_config.get('longitude_display_name', 'Longitude'),
    }

  # Optional size encoding
  if 'size_field' in widget_config:
    encodings['size'] = {
      'fieldName': widget_config['size_field'],
      'scale': {'type': 'quantitative'},
      'displayName': widget_config.get('size_display_name', widget_config['size_field']),
    }

  # Optional color encoding
  if 'color_field' in widget_config:
    color_scale_type = widget_config.get('color_scale_type', 'categorical')
    encodings['color'] = {
      'fieldName': widget_config['color_field'],
      'scale': create_color_scale(color_scale_type, widget_config),
      'displayName': widget_config.get('color_display_name', widget_config['color_field']),
    }

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['symbol-map'],
      'widgetType': 'symbol-map',
      'encodings': encodings,
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(config, datasets),
  }


def create_funnel_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create funnel widget with x/y encodings matching working examples.

  Funnel charts require both value_field (quantitative) and stage_field (categorical).
  If stage_field is missing, we'll attempt to infer it from available fields.
  """
  widget_config = config.get('config', {})

  encodings = {}

  # X encoding (quantitative value) - required
  if 'value_field' in widget_config:
    encodings['x'] = {
      'fieldName': widget_config['value_field'],
      'scale': {'type': 'quantitative'},
      'displayName': widget_config.get('value_display_name', widget_config['value_field']),
    }

  # Y encoding (categorical stage) - required
  if 'stage_field' in widget_config:
    encodings['y'] = {
      'fieldName': widget_config['stage_field'],
      'scale': {'type': 'categorical'},
      'displayName': widget_config.get('stage_display_name', widget_config['stage_field']),
    }
  else:
    # If stage_field is missing, try to infer from other common field names
    # This handles cases where only value_field is provided
    potential_stage_fields = []

    # Check for common categorical field names in the config
    for field_key in ['category_field', 'x_field', 'color_field']:
      if field_key in widget_config and field_key != 'value_field':
        potential_stage_fields.append(widget_config[field_key])

    # Use the first available categorical field as stage_field
    if potential_stage_fields:
      stage_field = potential_stage_fields[0]
      encodings['y'] = {
        'fieldName': stage_field,
        'scale': {'type': 'categorical'},
        'displayName': widget_config.get('stage_display_name', stage_field),
      }

  # Add label configuration as shown in working examples
  encodings['label'] = {'show': True}

  # Validation: Ensure both x and y encodings are present for funnel charts
  if 'x' not in encodings:
    raise ValueError('Funnel chart requires a value_field for the x (quantitative) encoding')
  if 'y' not in encodings:
    raise ValueError(
      'Funnel chart requires a stage_field for the y (categorical) encoding. '
      "Please provide either 'stage_field', 'category_field', 'x_field', or 'color_field' "
      'in the widget configuration for the categorical dimension.'
    )

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['funnel'],
      'widgetType': 'funnel',
      'encodings': encodings,
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(config, datasets),
  }


def create_combo_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create combo chart with multiple y-axis fields and chart types."""
  widget_config = config.get('config', {})

  encodings = {}

  # X-axis encoding
  if 'x_field' in widget_config:
    x_scale_type = widget_config.get('x_scale_type', 'categorical')
    encodings['x'] = {
      'fieldName': widget_config['x_field'],
      'scale': {'type': x_scale_type},
      'displayName': widget_config.get('x_display_name', widget_config['x_field']),
    }

  # Y-axis with multiple fields and chart types
  if 'y_fields' in widget_config:
    y_fields = []
    for field_config in widget_config['y_fields']:
      y_fields.append(
        {
          'fieldName': field_config['field'],
          'displayName': field_config.get('displayName', field_config['field']),
          'chartType': field_config.get('chartType', 'bar'),
        }
      )

    encodings['y'] = {'fields': y_fields, 'scale': {'type': 'quantitative'}}

  # Optional secondary y-axis
  if 'y2_fields' in widget_config:
    y2_fields = []
    for field_config in widget_config['y2_fields']:
      y2_fields.append(
        {
          'fieldName': field_config['field'],
          'displayName': field_config.get('displayName', field_config['field']),
          'chartType': field_config.get('chartType', 'line'),
        }
      )

    encodings['y2'] = {'fields': y2_fields, 'scale': {'type': 'quantitative'}}

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['combo'],
      'widgetType': 'combo',
      'encodings': encodings,
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(config, datasets),
  }


def create_range_slider_widget(config: Dict, datasets: List[Dict]) -> Dict[str, Any]:
  """Create range slider filter widget."""
  widget_config = config.get('config', {})

  fields = []
  if 'field' in widget_config:
    field_config = {
      'fieldName': widget_config['field'],
      'displayName': widget_config.get('display_name', widget_config['field']),
      'dataType': widget_config.get('data_type', 'integer'),
    }

    # Add min/max/step if provided
    if 'min_value' in widget_config:
      field_config['min'] = widget_config['min_value']
    if 'max_value' in widget_config:
      field_config['max'] = widget_config['max_value']
    if 'step' in widget_config:
      field_config['step'] = widget_config['step']

    fields.append(field_config)

  return {
    'name': generate_id(),
    'spec': {
      'version': WIDGET_VERSIONS['range-slider'],
      'widgetType': 'range-slider',
      'encodings': {'fields': fields},
      'frame': create_frame_config(widget_config),
    },
    'queries': create_widget_queries(config, datasets),
  }
