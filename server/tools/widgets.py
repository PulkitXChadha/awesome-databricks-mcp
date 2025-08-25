"""Widget creation and management tools for Databricks Lakeview dashboards.

This module provides direct widget creation functions following SIMPLE patterns.
No abstract classes, no factories, just direct function calls.
"""

import os
import uuid
from typing import Any, List, Optional

from databricks.sdk import WorkspaceClient

# ============================================================================
# Chart Widget Functions (7 types)
# ============================================================================


def create_bar_chart_widget(
  title: str, x_field: str, y_field: str, dataset_query: str, position: dict = None
) -> dict:
  """Create a bar chart widget specification.

  Args:
      title: Widget title
      x_field: Field for x-axis (categories)
      y_field: Field for y-axis (values)
      dataset_query: SQL query for the dataset
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'bar_chart_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'bar_chart',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'bar',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': {
        'x': {'fieldName': x_field, 'displayName': x_field, 'type': 'categorical'},
        'y': {'fieldName': y_field, 'displayName': y_field, 'type': 'quantitative'},
      },
    },
    'position': position or {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  }


def create_line_chart_widget(
  title: str, x_field: str, y_field: str, dataset_query: str, position: dict = None
) -> dict:
  """Create a line chart widget specification.

  Args:
      title: Widget title
      x_field: Field for x-axis (typically time)
      y_field: Field for y-axis (values)
      dataset_query: SQL query for the dataset
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'line_chart_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'line_chart',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'line',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': {
        'x': {'fieldName': x_field, 'displayName': x_field, 'type': 'temporal'},
        'y': {'fieldName': y_field, 'displayName': y_field, 'type': 'quantitative'},
      },
    },
    'position': position or {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  }


def create_area_chart_widget(
  title: str, x_field: str, y_field: str, dataset_query: str, position: dict = None
) -> dict:
  """Create an area chart widget specification.

  Args:
      title: Widget title
      x_field: Field for x-axis (typically time)
      y_field: Field for y-axis (values)
      dataset_query: SQL query for the dataset
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'area_chart_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'area_chart',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'area',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': {
        'x': {'fieldName': x_field, 'displayName': x_field, 'type': 'temporal'},
        'y': {'fieldName': y_field, 'displayName': y_field, 'type': 'quantitative'},
      },
    },
    'position': position or {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  }


def create_pie_chart_widget(
  title: str, category_field: str, value_field: str, dataset_query: str, position: dict = None
) -> dict:
  """Create a pie chart widget specification.

  Args:
      title: Widget title
      category_field: Field for categories (slices)
      value_field: Field for values (slice sizes)
      dataset_query: SQL query for the dataset
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'pie_chart_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'pie_chart',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'pie',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': {
        'category': {
          'fieldName': category_field,
          'displayName': category_field,
          'type': 'categorical',
        },
        'value': {'fieldName': value_field, 'displayName': value_field, 'type': 'quantitative'},
      },
    },
    'position': position or {'x': 0, 'y': 0, 'width': 3, 'height': 3},
  }


def create_scatter_plot_widget(
  title: str,
  x_field: str,
  y_field: str,
  dataset_query: str,
  size_field: str = None,
  color_field: str = None,
  position: dict = None,
) -> dict:
  """Create a scatter plot widget specification.

  Args:
      title: Widget title
      x_field: Field for x-axis
      y_field: Field for y-axis
      dataset_query: SQL query for the dataset
      size_field: Optional field for point sizes
      color_field: Optional field for point colors
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'scatter_plot_{uuid.uuid4().hex[:8]}'

  encodings = {
    'x': {'fieldName': x_field, 'displayName': x_field, 'type': 'quantitative'},
    'y': {'fieldName': y_field, 'displayName': y_field, 'type': 'quantitative'},
  }

  if size_field:
    encodings['size'] = {'fieldName': size_field, 'displayName': size_field, 'type': 'quantitative'}

  if color_field:
    encodings['color'] = {
      'fieldName': color_field,
      'displayName': color_field,
      'type': 'categorical',
    }

  return {
    'id': widget_id,
    'type': 'scatter_plot',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'scatter',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': encodings,
    },
    'position': position or {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  }


def create_histogram_widget(
  title: str, value_field: str, dataset_query: str, bins: int = 20, position: dict = None
) -> dict:
  """Create a histogram widget specification.

  Args:
      title: Widget title
      value_field: Field for distribution analysis
      dataset_query: SQL query for the dataset
      bins: Number of bins for the histogram
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'histogram_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'histogram',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'histogram',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': {
        'value': {
          'fieldName': value_field,
          'displayName': value_field,
          'type': 'quantitative',
          'binCount': bins,
        }
      },
    },
    'position': position or {'x': 0, 'y': 0, 'width': 4, 'height': 3},
  }


def create_combo_chart_widget(
  title: str,
  x_field: str,
  bar_fields: List[str],
  line_fields: List[str],
  dataset_query: str,
  position: dict = None,
) -> dict:
  """Create a combo chart widget specification.

  Args:
      title: Widget title
      x_field: Field for x-axis
      bar_fields: List of fields to display as bars
      line_fields: List of fields to display as lines
      dataset_query: SQL query for the dataset
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'combo_chart_{uuid.uuid4().hex[:8]}'

  encodings = {'x': {'fieldName': x_field, 'displayName': x_field, 'type': 'categorical'}}

  # Add bar field encodings
  for i, field in enumerate(bar_fields):
    encodings[f'bar_y_{i}'] = {
      'fieldName': field,
      'displayName': field,
      'type': 'quantitative',
      'chartType': 'bar',
    }

  # Add line field encodings
  for i, field in enumerate(line_fields):
    encodings[f'line_y_{i}'] = {
      'fieldName': field,
      'displayName': field,
      'type': 'quantitative',
      'chartType': 'line',
    }

  return {
    'id': widget_id,
    'type': 'combo_chart',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'combo',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': encodings,
    },
    'position': position or {'x': 0, 'y': 0, 'width': 5, 'height': 3},
  }


# ============================================================================
# Data Widget Functions (4 types)
# ============================================================================


def create_counter_widget(
  title: str,
  value_field: str,
  dataset_query: str,
  aggregation: str = 'sum',
  format_string: str = None,
  position: dict = None,
) -> dict:
  """Create a counter widget specification.

  Args:
      title: Widget title
      value_field: Field to display
      dataset_query: SQL query for the dataset
      aggregation: Aggregation type (sum, avg, min, max, count)
      format_string: Optional format string for the value
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'counter_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'counter',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'counter',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': {
        'value': {
          'fieldName': value_field,
          'displayName': value_field,
          'aggregation': aggregation,
          'format': format_string or '{value}',
        }
      },
    },
    'position': position or {'x': 0, 'y': 0, 'width': 2, 'height': 2},
  }


def create_delta_counter_widget(
  title: str,
  value_field: str,
  comparison_field: str,
  dataset_query: str,
  aggregation: str = 'sum',
  format_string: str = None,
  position: dict = None,
) -> dict:
  """Create a delta counter widget specification.

  Args:
      title: Widget title
      value_field: Field for current value
      comparison_field: Field for comparison value
      dataset_query: SQL query for the dataset
      aggregation: Aggregation type (sum, avg, min, max, count)
      format_string: Optional format string for the value
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'delta_counter_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'delta_counter',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'delta_counter',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': {
        'value': {
          'fieldName': value_field,
          'displayName': value_field,
          'aggregation': aggregation,
          'format': format_string or '{value}',
        },
        'comparison': {
          'fieldName': comparison_field,
          'displayName': comparison_field,
          'aggregation': aggregation,
        },
      },
    },
    'position': position or {'x': 0, 'y': 0, 'width': 2, 'height': 2},
  }


def create_data_table_widget(
  title: str, columns: List[str], dataset_query: str, row_limit: int = 100, position: dict = None
) -> dict:
  """Create a data table widget specification.

  Args:
      title: Widget title
      columns: List of column names to display
      dataset_query: SQL query for the dataset
      row_limit: Maximum number of rows to display
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'data_table_{uuid.uuid4().hex[:8]}'

  column_specs = [{'fieldName': col, 'displayName': col, 'type': 'auto'} for col in columns]

  return {
    'id': widget_id,
    'type': 'data_table',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'table',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'columns': column_specs,
      'rowLimit': row_limit,
    },
    'position': position or {'x': 0, 'y': 0, 'width': 6, 'height': 4},
  }


def create_pivot_table_widget(
  title: str,
  row_fields: List[str],
  column_fields: List[str],
  value_field: str,
  dataset_query: str,
  aggregation: str = 'sum',
  position: dict = None,
) -> dict:
  """Create a pivot table widget specification.

  Args:
      title: Widget title
      row_fields: Fields for row grouping
      column_fields: Fields for column grouping
      value_field: Field for cell values
      dataset_query: SQL query for the dataset
      aggregation: Aggregation type (sum, avg, min, max, count)
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'pivot_table_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'pivot_table',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'pivot',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'rows': [{'fieldName': field, 'displayName': field} for field in row_fields],
      'columns': [{'fieldName': field, 'displayName': field} for field in column_fields],
      'values': {'fieldName': value_field, 'displayName': value_field, 'aggregation': aggregation},
    },
    'position': position or {'x': 0, 'y': 0, 'width': 6, 'height': 4},
  }


# ============================================================================
# Filter Widget Functions (4 types)
# ============================================================================


def create_dropdown_filter_widget(
  title: str,
  field_name: str,
  dataset_query: str,
  multi_select: bool = False,
  default_value: Any = None,
  position: dict = None,
) -> dict:
  """Create a dropdown filter widget specification.

  Args:
      title: Widget title
      field_name: Field to filter on
      dataset_query: SQL query for the dataset
      multi_select: Whether to allow multiple selections
      default_value: Default selected value(s)
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'dropdown_filter_{uuid.uuid4().hex[:8]}'

  spec = {
    'version': 3,
    'widgetType': 'filter_dropdown',
    'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
    'field': {'fieldName': field_name, 'displayName': field_name, 'multiSelect': multi_select},
  }

  if default_value is not None:
    spec['field']['defaultValue'] = default_value

  return {
    'id': widget_id,
    'type': 'dropdown_filter',
    'title': title,
    'spec': spec,
    'position': position or {'x': 0, 'y': 0, 'width': 2, 'height': 1},
  }


def create_date_range_filter_widget(
  title: str,
  field_name: str,
  dataset_query: str,
  default_start: str = None,
  default_end: str = None,
  position: dict = None,
) -> dict:
  """Create a date range filter widget specification.

  Args:
      title: Widget title
      field_name: Date field to filter on
      dataset_query: SQL query for the dataset
      default_start: Default start date (YYYY-MM-DD)
      default_end: Default end date (YYYY-MM-DD)
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'date_range_filter_{uuid.uuid4().hex[:8]}'

  spec = {
    'version': 3,
    'widgetType': 'filter_date_range',
    'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
    'field': {'fieldName': field_name, 'displayName': field_name, 'type': 'date'},
  }

  if default_start and default_end:
    spec['field']['defaultRange'] = {'start': default_start, 'end': default_end}

  return {
    'id': widget_id,
    'type': 'date_range_filter',
    'title': title,
    'spec': spec,
    'position': position or {'x': 0, 'y': 0, 'width': 3, 'height': 1},
  }


def create_slider_filter_widget(
  title: str,
  field_name: str,
  dataset_query: str,
  min_value: float = None,
  max_value: float = None,
  default_value: float = None,
  step: float = None,
  position: dict = None,
) -> dict:
  """Create a slider filter widget specification.

  Args:
      title: Widget title
      field_name: Numeric field to filter on
      dataset_query: SQL query for the dataset
      min_value: Minimum slider value
      max_value: Maximum slider value
      default_value: Default slider value
      step: Slider step increment
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'slider_filter_{uuid.uuid4().hex[:8]}'

  spec = {
    'version': 3,
    'widgetType': 'filter_slider',
    'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
    'field': {'fieldName': field_name, 'displayName': field_name, 'type': 'numeric'},
  }

  if min_value is not None:
    spec['field']['min'] = min_value
  if max_value is not None:
    spec['field']['max'] = max_value
  if default_value is not None:
    spec['field']['defaultValue'] = default_value
  if step is not None:
    spec['field']['step'] = step

  return {
    'id': widget_id,
    'type': 'slider_filter',
    'title': title,
    'spec': spec,
    'position': position or {'x': 0, 'y': 0, 'width': 3, 'height': 1},
  }


def create_text_input_filter_widget(
  title: str,
  field_name: str,
  dataset_query: str,
  placeholder: str = None,
  default_value: str = None,
  position: dict = None,
) -> dict:
  """Create a text input filter widget specification.

  Args:
      title: Widget title
      field_name: Field to filter on
      dataset_query: SQL query for the dataset
      placeholder: Placeholder text
      default_value: Default input value
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'text_filter_{uuid.uuid4().hex[:8]}'

  spec = {
    'version': 3,
    'widgetType': 'filter_text',
    'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
    'field': {'fieldName': field_name, 'displayName': field_name, 'type': 'text'},
  }

  if placeholder:
    spec['field']['placeholder'] = placeholder
  if default_value:
    spec['field']['defaultValue'] = default_value

  return {
    'id': widget_id,
    'type': 'text_filter',
    'title': title,
    'spec': spec,
    'position': position or {'x': 0, 'y': 0, 'width': 2, 'height': 1},
  }


# ============================================================================
# Specialty Widget Functions (4 types)
# ============================================================================


def create_map_widget(
  title: str,
  latitude_field: str,
  longitude_field: str,
  dataset_query: str,
  value_field: str = None,
  label_field: str = None,
  position: dict = None,
) -> dict:
  """Create a map widget specification.

  Args:
      title: Widget title
      latitude_field: Field containing latitude values
      longitude_field: Field containing longitude values
      dataset_query: SQL query for the dataset
      value_field: Optional field for marker sizes/colors
      label_field: Optional field for marker labels
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'map_widget_{uuid.uuid4().hex[:8]}'

  encodings = {
    'latitude': {'fieldName': latitude_field, 'displayName': latitude_field, 'type': 'latitude'},
    'longitude': {
      'fieldName': longitude_field,
      'displayName': longitude_field,
      'type': 'longitude',
    },
  }

  if value_field:
    encodings['value'] = {
      'fieldName': value_field,
      'displayName': value_field,
      'type': 'quantitative',
    }

  if label_field:
    encodings['label'] = {'fieldName': label_field, 'displayName': label_field, 'type': 'text'}

  return {
    'id': widget_id,
    'type': 'map',
    'title': title,
    'spec': {
      'version': 3,
      'widgetType': 'map',
      'dataset': {'name': f'dataset_{widget_id}', 'query': dataset_query},
      'encodings': encodings,
    },
    'position': position or {'x': 0, 'y': 0, 'width': 5, 'height': 4},
  }


def create_text_widget(
  title: str, content: str, markdown: bool = True, position: dict = None
) -> dict:
  """Create a text widget specification.

  Args:
      title: Widget title
      content: Text content (supports markdown)
      markdown: Whether to render as markdown
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'text_widget_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'text',
    'title': title,
    'spec': {'version': 3, 'widgetType': 'text', 'content': content, 'markdown': markdown},
    'position': position or {'x': 0, 'y': 0, 'width': 3, 'height': 2},
  }


def create_image_widget(
  title: str, image_url: str, alt_text: str = None, position: dict = None
) -> dict:
  """Create an image widget specification.

  Args:
      title: Widget title
      image_url: URL of the image to display
      alt_text: Alternative text for the image
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'image_widget_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'image',
    'title': title,
    'spec': {'version': 3, 'widgetType': 'image', 'url': image_url, 'altText': alt_text or title},
    'position': position or {'x': 0, 'y': 0, 'width': 3, 'height': 3},
  }


def create_iframe_widget(title: str, embed_url: str, position: dict = None) -> dict:
  """Create an iframe widget specification.

  Args:
      title: Widget title
      embed_url: URL to embed in the iframe
      position: Optional position dict with x, y, width, height

  Returns:
      Widget specification dictionary
  """
  widget_id = f'iframe_widget_{uuid.uuid4().hex[:8]}'

  return {
    'id': widget_id,
    'type': 'iframe',
    'title': title,
    'spec': {'version': 3, 'widgetType': 'iframe', 'url': embed_url},
    'position': position or {'x': 0, 'y': 0, 'width': 4, 'height': 4},
  }


# ============================================================================
# Widget Management Functions
# ============================================================================


def add_widget_to_dashboard(dashboard_id: str, widget_spec: dict) -> dict:
  """Add a widget to an existing Lakeview dashboard.

  Args:
      dashboard_id: ID of the dashboard to add widget to
      widget_spec: Widget specification from create_*_widget functions

  Returns:
      Result dictionary with success status
  """
  try:
    # Initialize Databricks SDK
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # Get current dashboard
    dashboard = w.lakeview.get(dashboard_id=dashboard_id)

    # Add widget to dashboard
    widgets = getattr(dashboard, 'widgets', []) or []
    widgets.append(widget_spec)

    # Update dashboard with new widget
    w.lakeview.update(dashboard_id=dashboard_id, widgets=widgets)

    return {
      'success': True,
      'message': f'Widget {widget_spec["id"]} added to dashboard {dashboard_id}',
      'widget_id': widget_spec['id'],
    }

  except Exception as e:
    return {'success': False, 'error': f'Failed to add widget: {str(e)}'}


def remove_widget_from_dashboard(dashboard_id: str, widget_id: str) -> dict:
  """Remove a widget from a Lakeview dashboard.

  Args:
      dashboard_id: ID of the dashboard
      widget_id: ID of the widget to remove

  Returns:
      Result dictionary with success status
  """
  try:
    # Initialize Databricks SDK
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # Get current dashboard
    dashboard = w.lakeview.get(dashboard_id=dashboard_id)

    # Remove widget from dashboard
    widgets = getattr(dashboard, 'widgets', []) or []
    widgets = [w for w in widgets if w.get('id') != widget_id]

    # Update dashboard without the widget
    w.lakeview.update(dashboard_id=dashboard_id, widgets=widgets)

    return {'success': True, 'message': f'Widget {widget_id} removed from dashboard {dashboard_id}'}

  except Exception as e:
    return {'success': False, 'error': f'Failed to remove widget: {str(e)}'}


def update_widget_position(dashboard_id: str, widget_id: str, position: dict) -> dict:
  """Update the position of a widget in a dashboard.

  Args:
      dashboard_id: ID of the dashboard
      widget_id: ID of the widget to update
      position: New position dict with x, y, width, height

  Returns:
      Result dictionary with success status
  """
  try:
    # Initialize Databricks SDK
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # Get current dashboard
    dashboard = w.lakeview.get(dashboard_id=dashboard_id)

    # Update widget position
    widgets = getattr(dashboard, 'widgets', []) or []
    for widget in widgets:
      if widget.get('id') == widget_id:
        widget['position'] = position
        break

    # Update dashboard with new widget positions
    w.lakeview.update(dashboard_id=dashboard_id, widgets=widgets)

    return {
      'success': True,
      'message': f'Widget {widget_id} position updated',
      'new_position': position,
    }

  except Exception as e:
    return {'success': False, 'error': f'Failed to update widget position: {str(e)}'}


def create_dashboard_with_widgets(name: str, description: str, widgets: List[dict]) -> dict:
  """Create a new Lakeview dashboard with multiple widgets.

  Args:
      name: Dashboard name
      description: Dashboard description
      widgets: List of widget specifications

  Returns:
      Result dictionary with dashboard ID and success status
  """
  try:
    # Initialize Databricks SDK
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # Create dashboard with widgets
    dashboard = w.lakeview.create(name=name, description=description, widgets=widgets)

    dashboard_id = getattr(dashboard, 'dashboard_id', None)

    return {
      'success': True,
      'message': f'Dashboard {name} created with {len(widgets)} widgets',
      'dashboard_id': dashboard_id,
      'widget_count': len(widgets),
    }

  except Exception as e:
    return {'success': False, 'error': f'Failed to create dashboard: {str(e)}'}


# ============================================================================
# MCP Tool Registration
# ============================================================================


def load_widget_tools(mcp_server):
  """Register widget MCP tools with the server.

  Args:
      mcp_server: The FastMCP server instance to register tools with
  """

  # Data widgets (unique to widgets module)
  @mcp_server.tool
  def create_counter(
    title: str,
    value_field: str,
    dataset_query: str,
    aggregation: str = 'sum',
    position: Optional[dict] = None,
  ) -> dict:
    """Create a counter widget for displaying a single KPI."""
    return create_counter_widget(title, value_field, dataset_query, aggregation, None, position)

  # Filter widgets (unique to widgets module)  
  @mcp_server.tool
  def create_date_filter(
    title: str, field_name: str, dataset_query: str, position: Optional[dict] = None
  ) -> dict:
    """Create a date range filter widget for temporal filtering."""
    return create_date_range_filter_widget(title, field_name, dataset_query, None, None, position)

  # Widget management tools (unique to widgets module)
  @mcp_server.tool
  def add_widget_to_lakeview_dashboard(dashboard_id: str, widget_spec: dict) -> dict:
    """Add a widget to an existing Lakeview dashboard."""
    return add_widget_to_dashboard(dashboard_id, widget_spec)

  @mcp_server.tool
  def create_lakeview_dashboard_with_widgets(
    name: str, description: str, widgets: List[dict]
  ) -> dict:
    """Create a new Lakeview dashboard with multiple widgets."""
    return create_dashboard_with_widgets(name, description, widgets)
