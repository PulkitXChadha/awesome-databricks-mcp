"""Widget type definitions and constants for Lakeview dashboard widgets.

This module provides type definitions and constants following SIMPLE patterns.
Direct dictionary structures, no complex classes or inheritance.
"""

import uuid
from typing import Any, Dict, List, Optional, TypedDict

# ============================================================================
# Type Definitions
# ============================================================================


class PositionDict(TypedDict):
  """Position and size specification for widgets."""

  x: int
  y: int
  width: int
  height: int


class EncodingDict(TypedDict):
  """Field encoding specification for widgets."""

  fieldName: str
  displayName: str
  type: Optional[str]


class DatasetDict(TypedDict):
  """Dataset specification for widgets."""

  name: str
  query: str


class WidgetSpecDict(TypedDict):
  """Widget specification structure."""

  version: int
  widgetType: str
  dataset: Optional[DatasetDict]
  encodings: Optional[Dict[str, Any]]


class WidgetDict(TypedDict):
  """Complete widget structure."""

  id: str
  type: str
  title: str
  spec: WidgetSpecDict
  position: PositionDict


# ============================================================================
# Widget Type Constants
# ============================================================================

# Chart Widget Types
CHART_WIDGET_TYPES = {
  'bar_chart': {
    'name': 'Bar Chart',
    'description': 'Create bar charts for comparing categorical data',
    'required_fields': ['x_field', 'y_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  },
  'line_chart': {
    'name': 'Line Chart',
    'description': 'Create line charts for showing trends over time',
    'required_fields': ['x_field', 'y_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  },
  'area_chart': {
    'name': 'Area Chart',
    'description': 'Create area charts for cumulative data over time',
    'required_fields': ['x_field', 'y_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  },
  'pie_chart': {
    'name': 'Pie Chart',
    'description': 'Create pie charts for proportional data',
    'required_fields': ['category_field', 'value_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 3, 'height': 3},
  },
  'scatter_plot': {
    'name': 'Scatter Plot',
    'description': 'Create scatter plots for correlation analysis',
    'required_fields': ['x_field', 'y_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  },
  'histogram': {
    'name': 'Histogram',
    'description': 'Create histograms for distribution analysis',
    'required_fields': ['value_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  },
  'combo_chart': {
    'name': 'Combo Chart',
    'description': 'Create combination charts mixing bar and line types',
    'required_fields': ['x_field', 'bar_fields', 'line_fields'],
    'default_position': {'x': 0, 'y': 0, 'width': 5, 'height': 3},
  },
}

# Data Widget Types
DATA_WIDGET_TYPES = {
  'counter': {
    'name': 'Counter',
    'description': 'Display single KPI values',
    'required_fields': ['value_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 2, 'height': 2},
  },
  'delta_counter': {
    'name': 'Delta Counter',
    'description': 'Display KPI with change indicator',
    'required_fields': ['value_field', 'comparison_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 2, 'height': 2},
  },
  'data_table': {
    'name': 'Data Table',
    'description': 'Display detailed tabular data',
    'required_fields': ['columns'],
    'default_position': {'x': 0, 'y': 0, 'width': 6, 'height': 4},
  },
  'pivot_table': {
    'name': 'Pivot Table',
    'description': 'Display cross-tabulation analysis',
    'required_fields': ['row_fields', 'column_fields', 'value_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 6, 'height': 4},
  },
}

# Filter Widget Types
FILTER_WIDGET_TYPES = {
  'dropdown_filter': {
    'name': 'Dropdown Filter',
    'description': 'Single or multi-select dropdown filtering',
    'required_fields': ['field_name'],
    'default_position': {'x': 0, 'y': 0, 'width': 2, 'height': 1},
  },
  'date_range_filter': {
    'name': 'Date Range Filter',
    'description': 'Temporal filtering with date range picker',
    'required_fields': ['field_name'],
    'default_position': {'x': 0, 'y': 0, 'width': 3, 'height': 1},
  },
  'slider_filter': {
    'name': 'Slider Filter',
    'description': 'Numeric range selection with slider',
    'required_fields': ['field_name'],
    'default_position': {'x': 0, 'y': 0, 'width': 3, 'height': 1},
  },
  'text_input_filter': {
    'name': 'Text Input Filter',
    'description': 'Search functionality with text input',
    'required_fields': ['field_name'],
    'default_position': {'x': 0, 'y': 0, 'width': 2, 'height': 1},
  },
}

# Specialty Widget Types
SPECIALTY_WIDGET_TYPES = {
  'map': {
    'name': 'Map Widget',
    'description': 'Geographic visualization with markers',
    'required_fields': ['latitude_field', 'longitude_field'],
    'default_position': {'x': 0, 'y': 0, 'width': 5, 'height': 4},
  },
  'text': {
    'name': 'Text Widget',
    'description': 'Display titles, markdown, and dividers',
    'required_fields': ['content'],
    'default_position': {'x': 0, 'y': 0, 'width': 3, 'height': 2},
  },
  'image': {
    'name': 'Image Widget',
    'description': 'Display logos, diagrams, and images',
    'required_fields': ['image_url'],
    'default_position': {'x': 0, 'y': 0, 'width': 3, 'height': 3},
  },
  'iframe': {
    'name': 'Iframe Widget',
    'description': 'Embed external content via iframe',
    'required_fields': ['embed_url'],
    'default_position': {'x': 0, 'y': 0, 'width': 4, 'height': 4},
  },
}

# All widget types combined
ALL_WIDGET_TYPES = {
  **CHART_WIDGET_TYPES,
  **DATA_WIDGET_TYPES,
  **FILTER_WIDGET_TYPES,
  **SPECIALTY_WIDGET_TYPES,
}


# ============================================================================
# Widget Categories
# ============================================================================

WIDGET_CATEGORIES = {
  'chart': {
    'name': 'Chart Widgets',
    'description': 'Visualization widgets for displaying data trends and comparisons',
    'types': list(CHART_WIDGET_TYPES.keys()),
  },
  'data': {
    'name': 'Data Widgets',
    'description': 'Widgets for displaying raw data and key metrics',
    'types': list(DATA_WIDGET_TYPES.keys()),
  },
  'filter': {
    'name': 'Filter Widgets',
    'description': 'Interactive widgets for filtering dashboard data',
    'types': list(FILTER_WIDGET_TYPES.keys()),
  },
  'specialty': {
    'name': 'Specialty Widgets',
    'description': 'Special-purpose widgets for maps, text, images, and embedded content',
    'types': list(SPECIALTY_WIDGET_TYPES.keys()),
  },
}


# ============================================================================
# Field Type Constants
# ============================================================================

FIELD_TYPES = {
  'categorical': 'Categorical data (strings, discrete values)',
  'quantitative': 'Numeric data (integers, floats)',
  'temporal': 'Date/time data',
  'latitude': 'Geographic latitude coordinates',
  'longitude': 'Geographic longitude coordinates',
  'text': 'Text/string data for labels',
  'auto': 'Automatic type detection',
}

AGGREGATION_TYPES = {
  'sum': 'Sum of values',
  'avg': 'Average of values',
  'min': 'Minimum value',
  'max': 'Maximum value',
  'count': 'Count of records',
  'count_distinct': 'Count of unique values',
}

SCALE_TYPES = {
  'linear': 'Linear scale',
  'log': 'Logarithmic scale',
  'sqrt': 'Square root scale',
  'symlog': 'Symmetric logarithmic scale',
  'time': 'Time scale',
  'utc': 'UTC time scale',
}


# ============================================================================
# Validation Functions
# ============================================================================


def validate_widget_type(widget_type: str) -> bool:
  """Check if widget type is valid.

  Args:
      widget_type: Widget type to validate

  Returns:
      True if valid, False otherwise
  """
  return widget_type in ALL_WIDGET_TYPES


def validate_position(position: dict) -> bool:
  """Check if position dictionary is valid.

  Args:
      position: Position dictionary to validate

  Returns:
      True if valid, False otherwise
  """
  required_keys = ['x', 'y', 'width', 'height']
  return all(key in position for key in required_keys) and all(
    isinstance(position[key], int) for key in required_keys
  )


def get_widget_info(widget_type: str) -> Optional[Dict[str, Any]]:
  """Get information about a widget type.

  Args:
      widget_type: Widget type to get info for

  Returns:
      Widget info dictionary or None if not found
  """
  return ALL_WIDGET_TYPES.get(widget_type)


def get_default_position(widget_type: str) -> Dict[str, int]:
  """Get default position for a widget type.

  Args:
      widget_type: Widget type to get default position for

  Returns:
      Default position dictionary
  """
  widget_info = get_widget_info(widget_type)
  if widget_info:
    return widget_info['default_position']
  return {'x': 0, 'y': 0, 'width': 3, 'height': 3}


def get_required_fields(widget_type: str) -> List[str]:
  """Get required fields for a widget type.

  Args:
      widget_type: Widget type to get required fields for

  Returns:
      List of required field names
  """
  widget_info = get_widget_info(widget_type)
  if widget_info:
    return widget_info['required_fields']
  return []


def list_widget_types_by_category() -> Dict[str, List[str]]:
  """Get all widget types organized by category.

  Returns:
      Dictionary mapping category names to lists of widget types
  """
  return {category: info['types'] for category, info in WIDGET_CATEGORIES.items()}


def get_widget_category(widget_type: str) -> Optional[str]:
  """Get the category for a specific widget type.

  Args:
      widget_type: Widget type to find category for

  Returns:
      Category name or None if not found
  """
  for category, info in WIDGET_CATEGORIES.items():
    if widget_type in info['types']:
      return category
  return None


# ============================================================================
# Widget Specification Helpers
# ============================================================================


def create_basic_encoding(field_name: str, field_type: str = 'auto') -> EncodingDict:
  """Create a basic field encoding.

  Args:
      field_name: Name of the field
      field_type: Type of the field

  Returns:
      Encoding dictionary
  """
  return {'fieldName': field_name, 'displayName': field_name, 'type': field_type}


def create_dataset_spec(query: str, widget_id: str) -> DatasetDict:
  """Create a dataset specification.

  Args:
      query: SQL query for the dataset
      widget_id: Unique widget identifier

  Returns:
      Dataset dictionary
  """
  return {'name': f'dataset_{widget_id}', 'query': query}


def create_widget_frame(title: str, show_title: bool = True) -> Dict[str, Any]:
  """Create a widget frame specification.

  Args:
      title: Widget title
      show_title: Whether to show the title

  Returns:
      Frame dictionary
  """
  return {'showTitle': show_title, 'title': title}


def generate_widget_id(widget_type: str) -> str:
  """Generate a unique widget ID.

  Args:
      widget_type: Type of widget

  Returns:
      Unique widget identifier
  """
  return f'{widget_type}_{uuid.uuid4().hex[:8]}'
