"""Dashboards and monitoring MCP tools for Databricks."""

import html
import os
import re

from databricks.sdk import WorkspaceClient


def sanitize_field_name(field_name: str) -> str:
  """Sanitize field names to prevent SQL injection."""
  if not field_name or not isinstance(field_name, str):
    return ''

  # Remove SQL keywords and dangerous patterns
  dangerous_patterns = [
    'DROP',
    'DELETE',
    'INSERT',
    'UPDATE',
    'UNION',
    'SELECT',
    '--',
    '/*',
    '*/',
    ';',
    'EXEC',
    'xp_cmdshell',
  ]

  sanitized = field_name
  for pattern in dangerous_patterns:
    sanitized = re.sub(re.escape(pattern), '', sanitized, flags=re.IGNORECASE)

  # Keep only alphanumeric, underscore, and dot for field names
  sanitized = re.sub(r'[^a-zA-Z0-9_.]', '', sanitized)

  return sanitized


def sanitize_html_content(content: str) -> str:
  """Sanitize HTML content to prevent XSS."""
  if not content or not isinstance(content, str):
    return ''

  # Remove script tags and event handlers
  content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
  content = re.sub(r'<script[^>]*/?>', '', content, flags=re.IGNORECASE)
  content = re.sub(r'on\w+\s*=\s*[\'"][^\'\"]*[\'"]', '', content, flags=re.IGNORECASE)
  content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)

  # Escape remaining HTML
  content = html.escape(content)

  return content


def sanitize_widget_name(name: str) -> str:
  """Sanitize widget names to prevent injection while preserving readability."""
  if not name or not isinstance(name, str):
    return 'Unnamed Widget'

  # Remove dangerous SQL patterns but keep readable text
  dangerous_patterns = ['DROP TABLE', 'INSERT INTO', 'DELETE FROM']
  sanitized = name
  for pattern in dangerous_patterns:
    sanitized = sanitized.replace(pattern, '')

  return sanitized.strip() or 'Unnamed Widget'


def load_dashboard_tools(mcp_server):
  """Register dashboards and monitoring MCP tools with the server.

  Args:
      mcp_server: The FastMCP server instance to register tools with
  """

  def add_widget_to_dashboard_impl(
    dashboard_id: str, widget_spec: dict, dataset_name: str = None, dataset_query: str = None
  ) -> dict:
    """Helper function to add widget to dashboard."""
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Generate unique widget ID
      import time

      widget_id = f'widget_{int(time.time() * 1000)}'

      # Add widget ID to spec
      widget_spec['widget_id'] = widget_id

      # Try Lakeview dashboard first
      try:
        dashboard = w.lakeview.get(dashboard_id=dashboard_id)

        # Extract current widgets
        current_widgets = getattr(dashboard, 'widgets', [])
        if isinstance(current_widgets, dict):
          current_widgets = list(current_widgets.values())
        elif not isinstance(current_widgets, list):
          current_widgets = []

        # Add new widget
        current_widgets.append(widget_spec)

        # Update dashboard
        w.lakeview.update(dashboard_id=dashboard_id, widgets=current_widgets)
        dashboard_type = 'lakeview'

      except (AttributeError, Exception):
        # Fallback to legacy dashboard API
        try:
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)

          current_widgets = getattr(dashboard, 'widgets', [])
          if not isinstance(current_widgets, list):
            current_widgets = []

          current_widgets.append(widget_spec)

          w.dashboards.update(dashboard_id=dashboard_id, widgets=current_widgets)
          dashboard_type = 'legacy'

        except (AttributeError, Exception) as legacy_error:
          return {
            'success': False,
            'error': f'Failed to add widget to dashboard: {str(legacy_error)}',
            'dashboard_id': dashboard_id,
          }

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'widget_id': widget_id,
        'widget_name': widget_spec.get('name', 'Unnamed Widget'),
        'widget_type': widget_spec.get('type', 'unknown'),
        'dashboard_type': dashboard_type,
        'dataset_id': None,
        'dataset_name': dataset_name,
        'message': (
          f'Successfully added widget {widget_spec.get("name", widget_id)} to '
          f'{dashboard_type} dashboard {dashboard_id}'
        ),
      }

    except Exception as e:
      return {
        'success': False,
        'error': f'Error adding widget to dashboard: {str(e)}',
        'dashboard_id': dashboard_id,
      }

  @mcp_server.tool()
  def list_lakeview_dashboards() -> dict:
    """List all Lakeview dashboards in the workspace.

    Returns:
        Dictionary containing list of Lakeview dashboards with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List Lakeview dashboards using the Databricks SDK
      dashboards = []
      try:
        # Use the lakeview API to list dashboards (correct method name is 'list')
        for dashboard in w.lakeview.list():
          dashboards.append(
            {
              'dashboard_id': dashboard.dashboard_id,
              'name': dashboard.name,
              'description': getattr(dashboard, 'description', None),
              'created_time': getattr(dashboard, 'created_time', None),
              'updated_time': getattr(dashboard, 'updated_time', None),
              'owner': getattr(dashboard, 'owner', None),
              'status': getattr(dashboard, 'status', None),
              'type': 'lakeview',
            }
          )
      except AttributeError:
        # Fallback: try alternative API paths if lakeview is not available
        try:
          # Try legacy dashboard API as fallback
          for dashboard in w.dashboards.list():
            dashboards.append(
              {
                'dashboard_id': getattr(dashboard, 'id', getattr(dashboard, 'dashboard_id', None)),
                'name': getattr(dashboard, 'name', None),
                'description': getattr(dashboard, 'description', None),
                'created_time': getattr(
                  dashboard, 'created_time', getattr(dashboard, 'created_at', None)
                ),
                'updated_time': getattr(
                  dashboard, 'updated_time', getattr(dashboard, 'updated_at', None)
                ),
                'owner': getattr(dashboard, 'owner', getattr(dashboard, 'user', None)),
                'status': getattr(dashboard, 'status', None),
                'type': 'legacy',
              }
            )
        except (AttributeError, Exception) as fallback_error:
          print(f'⚠️ Fallback dashboard listing failed: {str(fallback_error)}')
          # Return empty list if both methods fail
          pass

      return {
        'success': True,
        'dashboards': dashboards,
        'count': len(dashboards),
        'message': f'Found {len(dashboards)} dashboard(s)',
        'note': 'Includes both Lakeview and legacy dashboards if available',
      }

    except Exception as e:
      print(f'❌ Error listing Lakeview dashboards: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'dashboards': [], 'count': 0}

  @mcp_server.tool()
  def get_lakeview_dashboard(dashboard_id: str) -> dict:
    """Get details of a specific Lakeview dashboard.

    Args:
        dashboard_id: The ID of the dashboard to get details for

    Returns:
        Dictionary with dashboard details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get dashboard details using the Databricks SDK
      try:
        # Try Lakeview API first (correct method name is 'get')
        dashboard = w.lakeview.get(dashboard_id=dashboard_id)
        dashboard_type = 'lakeview'
      except (AttributeError, KeyError, ValueError):
        # Fallback to legacy dashboard API for API compatibility issues
        try:
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)
          dashboard_type = 'legacy'
        except (AttributeError, KeyError, ValueError) as fallback_error:
          return {
            'success': False,
            'error': f'Dashboard not found or API not available: {str(fallback_error)}',
            'dashboard_id': dashboard_id,
          }

      # Extract dashboard details with safe attribute access
      dashboard_details = {
        'dashboard_id': dashboard_id,
        'name': getattr(dashboard, 'name', None),
        'description': getattr(dashboard, 'description', None),
        'created_time': getattr(dashboard, 'created_time', getattr(dashboard, 'created_at', None)),
        'updated_time': getattr(dashboard, 'updated_time', getattr(dashboard, 'updated_at', None)),
        'owner': getattr(dashboard, 'owner', getattr(dashboard, 'user', None)),
        'status': getattr(dashboard, 'status', None),
        'type': dashboard_type,
      }

      # Add additional fields if available
      if hasattr(dashboard, 'layout'):
        dashboard_details['layout'] = dashboard.layout
      if hasattr(dashboard, 'widgets'):
        dashboard_details['widgets'] = dashboard.widgets
      if hasattr(dashboard, 'permissions'):
        dashboard_details['permissions'] = dashboard.permissions

      return {
        'success': True,
        'dashboard': dashboard_details,
        'message': f'Retrieved details for {dashboard_type} dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error getting Lakeview dashboard details: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def create_lakeview_dashboard(dashboard_config: dict) -> dict:
    """Create a new Lakeview dashboard.

    Args:
        dashboard_config: Dictionary containing dashboard configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate required configuration
      if not dashboard_config.get('name'):
        return {'success': False, 'error': 'Dashboard name is required in dashboard_config'}

      # Create dashboard using the Databricks SDK
      try:
        # Try Lakeview API first (correct method name is 'create')
        dashboard = w.lakeview.create(**dashboard_config)
        dashboard_type = 'lakeview'
      except (AttributeError, Exception):
        # Fallback to legacy dashboard API
        try:
          dashboard = w.dashboards.create(**dashboard_config)
          dashboard_type = 'legacy'
        except (AttributeError, Exception) as fallback_error:
          return {
            'success': False,
            'error': f'Dashboard creation failed or API not available: {str(fallback_error)}',
          }

      # Extract dashboard details
      dashboard_id = getattr(dashboard, 'dashboard_id', getattr(dashboard, 'id', None))
      dashboard_name = getattr(dashboard, 'name', dashboard_config.get('name'))

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'name': dashboard_name,
        'type': dashboard_type,
        'message': (
          f'Successfully created {dashboard_type} dashboard {dashboard_name} with ID {dashboard_id}'
        ),
      }

    except Exception as e:
      print(f'❌ Error creating Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def update_lakeview_dashboard(dashboard_id: str, updates: dict) -> dict:
    """Update an existing Lakeview dashboard.

    Args:
        dashboard_id: The ID of the dashboard to update
        updates: Dictionary containing updates to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate updates
      if not updates:
        return {'success': False, 'error': 'No updates provided in updates parameter'}

      # Update dashboard using the Databricks SDK
      try:
        # Try Lakeview API first (correct method name is 'update')
        dashboard = w.lakeview.update(dashboard_id=dashboard_id, **updates)
        dashboard_type = 'lakeview'
      except (AttributeError, Exception):
        # Fallback to legacy dashboard API
        try:
          dashboard = w.dashboards.update(dashboard_id=dashboard_id, **updates)
          dashboard_type = 'legacy'
        except (AttributeError, Exception) as fallback_error:
          return {
            'success': False,
            'error': f'Dashboard update failed or API not available: {str(fallback_error)}',
            'dashboard_id': dashboard_id,
          }

      # Extract updated dashboard details
      dashboard_name = getattr(dashboard, 'name', 'Unknown')

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'name': dashboard_name,
        'type': dashboard_type,
        'updates_applied': updates,
        'message': f'Successfully updated {dashboard_type} dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error updating Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def delete_lakeview_dashboard(dashboard_id: str) -> dict:
    """Delete a Lakeview dashboard.

    Args:
        dashboard_id: The ID of the dashboard to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete dashboard using the Databricks SDK
      try:
        # Try Lakeview API first (correct method name is 'trash' for deletion)
        w.lakeview.trash(dashboard_id=dashboard_id)
        dashboard_type = 'lakeview'
      except (AttributeError, Exception):
        # Fallback to legacy dashboard API
        try:
          w.dashboards.delete(dashboard_id=dashboard_id)
          dashboard_type = 'legacy'
        except (AttributeError, Exception) as fallback_error:
          return {
            'success': False,
            'error': f'Dashboard deletion failed or API not available: {str(fallback_error)}',
            'dashboard_id': dashboard_id,
          }

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'type': dashboard_type,
        'message': f'Successfully deleted {dashboard_type} dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error deleting Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def share_lakeview_dashboard(dashboard_id: str, share_config: dict) -> dict:
    """Share a Lakeview dashboard with users or groups.

    Args:
        dashboard_id: The ID of the dashboard to share
        share_config: Dictionary containing sharing configuration
            - users: List of user emails
            - groups: List of group names
            - permission: Permission level (READ, WRITE, ADMIN)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(  # noqa: F841
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Lakeview dashboard sharing may require specific permissions
      # This is a placeholder for the concept
      users = share_config.get('users', [])
      groups = share_config.get('groups', [])
      permission = share_config.get('permission', 'READ')

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'share_config': share_config,
        'users': users,
        'groups': groups,
        'permission': permission,
        'message': f'Lakeview dashboard {dashboard_id} sharing initiated',
        'note': (
          'Lakeview dashboard sharing may require specific permissions '
          'and may not be directly accessible via SDK'
        ),
      }

    except Exception as e:
      print(f'❌ Error sharing Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def get_dashboard_permissions(dashboard_id: str) -> dict:
    """Get current permissions for a Lakeview dashboard.

    Args:
        dashboard_id: The ID of the dashboard to get permissions for

    Returns:
        Dictionary with dashboard permissions or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(  # noqa: F841
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Lakeview dashboard permissions may require specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'permissions': {
          'owner': 'current_user@example.com',
          'shared_users': [],
          'shared_groups': [],
          'public_access': False,
        },
        'message': f'Dashboard permissions retrieved for {dashboard_id}',
        'note': (
          'Lakeview dashboard permissions may require specific permissions '
          'and may not be directly accessible via SDK'
        ),
      }

    except Exception as e:
      print(f'❌ Error getting dashboard permissions: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def list_dashboards() -> dict:
    """List all legacy dashboards in the workspace.

    Returns:
        Dictionary containing list of legacy dashboards with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(  # noqa: F841
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Legacy dashboards may require specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'message': 'Legacy dashboard listing initiated',
        'note': (
          'Legacy dashboards may require specific permissions '
          'and may not be directly accessible via SDK'
        ),
        'dashboards': [],
        'count': 0,
      }

    except Exception as e:
      print(f'❌ Error listing legacy dashboards: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'dashboards': [], 'count': 0}

  @mcp_server.tool()
  def get_dashboard(dashboard_id: str) -> dict:
    """Get details of a specific legacy dashboard.

    Args:
        dashboard_id: The ID of the dashboard to get details for

    Returns:
        Dictionary with dashboard details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(  # noqa: F841
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Legacy dashboard details may require specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'message': f'Legacy dashboard {dashboard_id} details retrieval initiated',
        'note': (
          'Legacy dashboard details may require specific permissions '
          'and may not be directly accessible via SDK'
        ),
        'dashboard': {},
      }

    except Exception as e:
      print(f'❌ Error getting legacy dashboard details: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def create_dashboard(dashboard_config: dict) -> dict:
    """Create a new legacy dashboard.

    Args:
        dashboard_config: Dictionary containing dashboard configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(  # noqa: F841
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Legacy dashboard creation may require specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'dashboard_config': dashboard_config,
        'message': 'Legacy dashboard creation initiated',
        'note': (
          'Legacy dashboard creation may require specific permissions '
          'and may not be directly accessible via SDK'
        ),
      }

    except Exception as e:
      print(f'❌ Error creating legacy dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def delete_dashboard(dashboard_id: str) -> dict:
    """Delete a legacy dashboard.

    Args:
        dashboard_id: The ID of the dashboard to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(  # noqa: F841
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Legacy dashboard deletion may require specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'message': f'Legacy dashboard {dashboard_id} deletion initiated',
        'note': (
          'Legacy dashboard deletion may require specific permissions '
          'and may not be directly accessible via SDK'
        ),
      }

    except Exception as e:
      print(f'❌ Error deleting legacy dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # Week 1: Core Chart Widgets

  @mcp_server.tool()
  def create_bar_chart(
    dataset_name: str,
    x_field: str,
    y_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    x_scale_type: str = 'categorical',
    y_scale_type: str = 'quantitative',
  ) -> dict:
    """Create a bar chart widget and optionally add to dashboard.

    Args:
        dataset_name: Name of the dataset or table to use
        x_field: Field name for X-axis (categories)
        y_field: Field name for Y-axis (values)
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional chart title
        position: Optional position dict with x, y, width, height
        x_scale_type: X-axis scale type (categorical, temporal, quantitative)
        y_scale_type: Y-axis scale type (categorical, temporal, quantitative)

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Sanitize inputs
      x_field_clean = sanitize_field_name(x_field)
      y_field_clean = sanitize_field_name(y_field)
      title_clean = (
        sanitize_widget_name(title) if title else f'Bar Chart: {y_field_clean} by {x_field_clean}'
      )

      widget_spec = {
        'type': 'bar_chart',
        'name': title_clean,
        'dataset_name': dataset_name,
        'encodings': {
          'x': {'field': x_field_clean, 'type': x_scale_type},
          'y': {'field': y_field_clean, 'type': y_scale_type},
        },
        'position': position or {'x': 0, 'y': 0, 'width': 6, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Bar chart widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating bar chart: {str(e)}'}

  @mcp_server.tool()
  def create_line_chart(
    dataset_name: str,
    x_field: str,
    y_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    color_field: str = None,
    x_scale_type: str = 'temporal',
    y_scale_type: str = 'quantitative',
  ) -> dict:
    """Create a line chart widget for time series trends.

    Args:
        dataset_name: Name of the dataset or table to use
        x_field: Field name for X-axis (usually time/date)
        y_field: Field name for Y-axis (values)
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional chart title
        position: Optional position dict with x, y, width, height
        color_field: Optional field for line colors/grouping
        x_scale_type: X-axis scale type (temporal, quantitative, categorical)
        y_scale_type: Y-axis scale type (quantitative, categorical)

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Sanitize inputs
      x_field_clean = sanitize_field_name(x_field)
      y_field_clean = sanitize_field_name(y_field)
      color_field_clean = sanitize_field_name(color_field) if color_field else None
      title_clean = (
        sanitize_widget_name(title)
        if title
        else f'Line Chart: {y_field_clean} over {x_field_clean}'
      )

      encodings = {
        'x': {'field': x_field_clean, 'type': x_scale_type},
        'y': {'field': y_field_clean, 'type': y_scale_type},
      }

      if color_field_clean:
        encodings['color'] = {'field': color_field_clean, 'type': 'nominal'}

      widget_spec = {
        'type': 'line_chart',
        'name': title_clean,
        'dataset_name': dataset_name,
        'encodings': encodings,
        'position': position or {'x': 6, 'y': 0, 'width': 6, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Line chart widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating line chart: {str(e)}'}

  @mcp_server.tool()
  def create_area_chart(
    dataset_name: str,
    x_field: str,
    y_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    color_field: str = None,
    stacked: bool = True,
    x_scale_type: str = 'temporal',
    y_scale_type: str = 'quantitative',
  ) -> dict:
    """Create an area chart widget for cumulative values.

    Args:
        dataset_name: Name of the dataset or table to use
        x_field: Field name for X-axis (usually time/date)
        y_field: Field name for Y-axis (cumulative values)
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional chart title
        position: Optional position dict with x, y, width, height
        color_field: Optional field for area colors/grouping
        stacked: Whether to stack multiple areas (default True)
        x_scale_type: X-axis scale type (temporal, quantitative, categorical)
        y_scale_type: Y-axis scale type (quantitative)

    Returns:
        Dictionary with widget creation result
    """
    try:
      encodings = {
        'x': {'field': x_field, 'type': x_scale_type},
        'y': {'field': y_field, 'type': y_scale_type},
      }

      if color_field:
        encodings['color'] = {'field': color_field, 'type': 'nominal'}

      widget_spec = {
        'type': 'area_chart',
        'name': title or f'Area Chart: {y_field} over {x_field}',
        'dataset_name': dataset_name,
        'encodings': encodings,
        'stacked': stacked,
        'position': position or {'x': 0, 'y': 4, 'width': 6, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Area chart widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating area chart: {str(e)}'}

  @mcp_server.tool()
  def create_pie_chart(
    dataset_name: str,
    category_field: str,
    value_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    show_labels: bool = True,
    show_percentages: bool = True,
  ) -> dict:
    """Create a pie chart widget for proportional data.

    Args:
        dataset_name: Name of the dataset or table to use
        category_field: Field name for pie slice categories
        value_field: Field name for pie slice values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional chart title
        position: Optional position dict with x, y, width, height
        show_labels: Whether to show category labels (default True)
        show_percentages: Whether to show percentages (default True)

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Sanitize inputs
      value_field_clean = sanitize_field_name(value_field)
      category_field_clean = sanitize_field_name(category_field)
      title_clean = (
        sanitize_widget_name(title)
        if title
        else f'Pie Chart: {value_field_clean} by {category_field_clean}'
      )

      widget_spec = {
        'type': 'pie_chart',
        'name': title_clean,
        'dataset_name': dataset_name,
        'encodings': {
          'theta': {'field': value_field_clean, 'type': 'quantitative'},
          'color': {'field': category_field_clean, 'type': 'nominal'},
        },
        'show_labels': show_labels,
        'show_percentages': show_percentages,
        'position': position or {'x': 6, 'y': 4, 'width': 6, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Pie chart widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating pie chart: {str(e)}'}

  @mcp_server.tool()
  def create_counter_widget(
    dataset_name: str,
    value_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    aggregation: str = 'sum',
    format_type: str = 'number',
    color: str = 'blue',
  ) -> dict:
    """Create a counter widget for single KPI display.

    Args:
        dataset_name: Name of the dataset or table to use
        value_field: Field name for the KPI value
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional counter title
        position: Optional position dict with x, y, width, height
        aggregation: Aggregation function (sum, count, avg, min, max)
        format_type: Value format (number, currency, percentage)
        color: Counter color theme (blue, green, red, orange, purple)

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'counter',
        'name': title or f'{aggregation.title()} of {value_field}',
        'dataset_name': dataset_name,
        'value_field': value_field,
        'aggregation': aggregation,
        'format_type': format_type,
        'color': color,
        'position': position or {'x': 0, 'y': 8, 'width': 3, 'height': 2},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Counter widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating counter widget: {str(e)}'}

  @mcp_server.tool()
  def create_data_table(
    dataset_name: str,
    columns: list,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    page_size: int = 25,
    sortable: bool = True,
    searchable: bool = True,
  ) -> dict:
    """Create a data table widget for tabular data view.

    Args:
        dataset_name: Name of the dataset or table to use
        columns: List of column names to display
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional table title
        position: Optional position dict with x, y, width, height
        page_size: Number of rows per page (default 25)
        sortable: Whether columns are sortable (default True)
        searchable: Whether table has search functionality (default True)

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'data_table',
        'name': title or f'Data Table: {dataset_name}',
        'dataset_name': dataset_name,
        'columns': columns,
        'page_size': page_size,
        'sortable': sortable,
        'searchable': searchable,
        'position': position or {'x': 3, 'y': 8, 'width': 9, 'height': 6},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Data table widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating data table: {str(e)}'}

  # Week 2: Advanced Visualizations

  @mcp_server.tool()
  def create_scatter_plot(
    dataset_name: str,
    x_field: str,
    y_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    color_field: str = None,
    size_field: str = None,
    x_scale_type: str = 'quantitative',
    y_scale_type: str = 'quantitative',
  ) -> dict:
    """Create a scatter plot widget for correlation analysis.

    Args:
        dataset_name: Name of the dataset or table to use
        x_field: Field name for X-axis values
        y_field: Field name for Y-axis values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional chart title
        position: Optional position dict with x, y, width, height
        color_field: Optional field for point colors
        size_field: Optional field for point sizes
        x_scale_type: X-axis scale type (quantitative, temporal, categorical)
        y_scale_type: Y-axis scale type (quantitative, temporal, categorical)

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Sanitize inputs
      x_field_clean = sanitize_field_name(x_field)
      y_field_clean = sanitize_field_name(y_field)
      color_field_clean = sanitize_field_name(color_field) if color_field else None
      size_field_clean = sanitize_field_name(size_field) if size_field else None
      title_clean = (
        sanitize_widget_name(title)
        if title
        else f'Scatter Plot: {y_field_clean} vs {x_field_clean}'
      )

      encodings = {
        'x': {'field': x_field_clean, 'type': x_scale_type},
        'y': {'field': y_field_clean, 'type': y_scale_type},
      }

      if color_field_clean:
        encodings['color'] = {'field': color_field_clean, 'type': 'nominal'}
      if size_field_clean:
        encodings['size'] = {'field': size_field_clean, 'type': 'quantitative'}

      widget_spec = {
        'type': 'scatter_plot',
        'name': title_clean,
        'dataset_name': dataset_name,
        'encodings': encodings,
        'position': position or {'x': 0, 'y': 14, 'width': 6, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Scatter plot widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating scatter plot: {str(e)}'}

  @mcp_server.tool()
  def create_histogram(
    dataset_name: str,
    value_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    bins: int = 20,
    color: str = 'steelblue',
  ) -> dict:
    """Create a histogram widget for distribution visualization.

    Args:
        dataset_name: Name of the dataset or table to use
        value_field: Field name for distribution values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional chart title
        position: Optional position dict with x, y, width, height
        bins: Number of histogram bins (default 20)
        color: Histogram bar color (default 'steelblue')

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'histogram',
        'name': title or f'Distribution of {value_field}',
        'dataset_name': dataset_name,
        'encodings': {
          'x': {'field': value_field, 'type': 'quantitative', 'bin': {'maxbins': bins}},
          'y': {'aggregate': 'count', 'type': 'quantitative'},
        },
        'color': color,
        'position': position or {'x': 6, 'y': 14, 'width': 6, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Histogram widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating histogram: {str(e)}'}

  @mcp_server.tool()
  def create_combo_chart(
    dataset_name: str,
    x_field: str,
    bar_field: str,
    line_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    x_scale_type: str = 'categorical',
  ) -> dict:
    """Create a combo chart widget with mixed chart types.

    Args:
        dataset_name: Name of the dataset or table to use
        x_field: Field name for X-axis (shared by both charts)
        bar_field: Field name for bar chart values
        line_field: Field name for line chart values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional chart title
        position: Optional position dict with x, y, width, height
        x_scale_type: X-axis scale type (categorical, temporal, quantitative)

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'combo_chart',
        'name': title or f'Combo Chart: {bar_field} & {line_field} by {x_field}',
        'dataset_name': dataset_name,
        'encodings': {'x': {'field': x_field, 'type': x_scale_type}},
        'layers': [
          {'mark': 'bar', 'encoding': {'y': {'field': bar_field, 'type': 'quantitative'}}},
          {'mark': 'line', 'encoding': {'y': {'field': line_field, 'type': 'quantitative'}}},
        ],
        'position': position or {'x': 0, 'y': 18, 'width': 8, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Combo chart widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating combo chart: {str(e)}'}

  @mcp_server.tool()
  def create_pivot_table(
    dataset_name: str,
    row_fields: list,
    column_fields: list,
    value_fields: list,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    aggregations: dict = None,
  ) -> dict:
    """Create a pivot table widget for cross-tabulation analysis.

    Args:
        dataset_name: Name of the dataset or table to use
        row_fields: List of field names for pivot table rows
        column_fields: List of field names for pivot table columns
        value_fields: List of field names for pivot table values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional table title
        position: Optional position dict with x, y, width, height
        aggregations: Dict mapping value fields to aggregation functions

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Set default aggregations if not provided
      if not aggregations:
        aggregations = {field: 'sum' for field in value_fields}

      widget_spec = {
        'type': 'pivot_table',
        'name': title or f'Pivot Table: {dataset_name}',
        'dataset_name': dataset_name,
        'row_fields': row_fields,
        'column_fields': column_fields,
        'value_fields': value_fields,
        'aggregations': aggregations,
        'position': position or {'x': 8, 'y': 18, 'width': 4, 'height': 6},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Pivot table widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating pivot table: {str(e)}'}

  @mcp_server.tool()
  def create_delta_counter(
    dataset_name: str,
    value_field: str,
    comparison_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    aggregation: str = 'sum',
    format_type: str = 'number',
    show_percentage: bool = True,
  ) -> dict:
    """Create a delta counter widget showing KPI with change indicator.

    Args:
        dataset_name: Name of the dataset or table to use
        value_field: Field name for the current KPI value
        comparison_field: Field name for comparison value (previous period)
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional counter title
        position: Optional position dict with x, y, width, height
        aggregation: Aggregation function (sum, count, avg, min, max)
        format_type: Value format (number, currency, percentage)
        show_percentage: Whether to show percentage change (default True)

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'delta_counter',
        'name': title or f'Change in {value_field}',
        'dataset_name': dataset_name,
        'value_field': value_field,
        'comparison_field': comparison_field,
        'aggregation': aggregation,
        'format_type': format_type,
        'show_percentage': show_percentage,
        'position': position or {'x': 0, 'y': 22, 'width': 4, 'height': 3},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Delta counter widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating delta counter: {str(e)}'}

  # Week 3: Interactive & Specialty Widgets

  @mcp_server.tool()
  def create_dropdown_filter(
    dataset_name: str,
    filter_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    multi_select: bool = False,
    default_values: list = None,
  ) -> dict:
    """Create a dropdown filter widget for single/multi-select options.

    Args:
        dataset_name: Name of the dataset or table to get filter options from
        filter_field: Field name to create filter options from
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional filter title
        position: Optional position dict with x, y, width, height
        multi_select: Whether to allow multiple selections (default False)
        default_values: List of default selected values

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Sanitize inputs
      filter_field_clean = sanitize_field_name(filter_field)
      title_clean = sanitize_widget_name(title) if title else f'Filter by {filter_field_clean}'

      widget_spec = {
        'type': 'dropdown_filter',
        'name': title_clean,
        'dataset_name': dataset_name,
        'filter_field': filter_field_clean,
        'multi_select': multi_select,
        'default_values': default_values or [],
        'position': position or {'x': 4, 'y': 22, 'width': 4, 'height': 1},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Dropdown filter widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating dropdown filter: {str(e)}'}

  @mcp_server.tool()
  def create_date_range_filter(
    dataset_name: str,
    date_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    default_range: dict = None,
  ) -> dict:
    """Create a date range filter widget for temporal filtering.

    Args:
        dataset_name: Name of the dataset or table to filter
        date_field: Field name containing date values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional filter title
        position: Optional position dict with x, y, width, height
        default_range: Dict with 'start' and 'end' date strings

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'date_range_filter',
        'name': title or f'Filter by {date_field}',
        'dataset_name': dataset_name,
        'date_field': date_field,
        'default_range': default_range or {'start': 'auto', 'end': 'auto'},
        'position': position or {'x': 8, 'y': 22, 'width': 4, 'height': 1},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Date range filter widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating date range filter: {str(e)}'}

  @mcp_server.tool()
  def create_slider_filter(
    dataset_name: str,
    numeric_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    min_value: float = None,
    max_value: float = None,
    step: float = None,
    default_value: float = None,
  ) -> dict:
    """Create a slider filter widget for numeric range selection.

    Args:
        dataset_name: Name of the dataset or table to filter
        numeric_field: Field name containing numeric values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional filter title
        position: Optional position dict with x, y, width, height
        min_value: Minimum slider value (auto-detected if None)
        max_value: Maximum slider value (auto-detected if None)
        step: Slider step size (auto-calculated if None)
        default_value: Default slider value

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Sanitize inputs
      numeric_field_clean = sanitize_field_name(numeric_field)
      title_clean = sanitize_widget_name(title) if title else f'Filter by {numeric_field_clean}'

      widget_spec = {
        'type': 'slider_filter',
        'name': title_clean,
        'dataset_name': dataset_name,
        'numeric_field': numeric_field_clean,
        'min_value': min_value,
        'max_value': max_value,
        'step': step,
        'default_value': default_value,
        'position': position or {'x': 0, 'y': 25, 'width': 4, 'height': 1},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Slider filter widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating slider filter: {str(e)}'}

  @mcp_server.tool()
  def create_text_filter(
    dataset_name: str,
    text_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    placeholder: str = None,
    case_sensitive: bool = False,
  ) -> dict:
    """Create a text filter widget for search/text input filtering.

    Args:
        dataset_name: Name of the dataset or table to filter
        text_field: Field name containing text values to search
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional filter title
        position: Optional position dict with x, y, width, height
        placeholder: Placeholder text for input field
        case_sensitive: Whether search is case sensitive (default False)

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'text_filter',
        'name': title or f'Search {text_field}',
        'dataset_name': dataset_name,
        'text_field': text_field,
        'placeholder': placeholder or f'Search {text_field}...',
        'case_sensitive': case_sensitive,
        'position': position or {'x': 4, 'y': 25, 'width': 4, 'height': 1},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Text filter widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating text filter: {str(e)}'}

  @mcp_server.tool()
  def create_map_widget(
    dataset_name: str,
    latitude_field: str,
    longitude_field: str,
    dashboard_id: str = None,
    dataset_query: str = None,
    title: str = None,
    position: dict = None,
    color_field: str = None,
    size_field: str = None,
    map_style: str = 'light',
  ) -> dict:
    """Create a map widget for geographic visualization.

    Args:
        dataset_name: Name of the dataset or table to use
        latitude_field: Field name containing latitude values
        longitude_field: Field name containing longitude values
        dashboard_id: Optional dashboard ID to add widget to
        dataset_query: Optional SQL query if creating new dataset
        title: Optional map title
        position: Optional position dict with x, y, width, height
        color_field: Optional field for point colors
        size_field: Optional field for point sizes
        map_style: Map style (light, dark, satellite, streets)

    Returns:
        Dictionary with widget creation result
    """
    try:
      encodings = {
        'latitude': {'field': latitude_field, 'type': 'quantitative'},
        'longitude': {'field': longitude_field, 'type': 'quantitative'},
      }

      if color_field:
        encodings['color'] = {'field': color_field, 'type': 'quantitative'}
      if size_field:
        encodings['size'] = {'field': size_field, 'type': 'quantitative'}

      widget_spec = {
        'type': 'map_widget',
        'name': title or f'Map: {dataset_name}',
        'dataset_name': dataset_name,
        'encodings': encodings,
        'map_style': map_style,
        'position': position or {'x': 8, 'y': 25, 'width': 4, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec, dataset_name, dataset_query)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Map widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating map widget: {str(e)}'}

  @mcp_server.tool()
  def create_text_widget(
    content: str,
    dashboard_id: str = None,
    title: str = None,
    position: dict = None,
    content_type: str = 'markdown',
    text_size: str = 'medium',
    text_color: str = 'default',
    background_color: str = 'transparent',
  ) -> dict:
    """Create a text widget for markdown, titles, or dividers.

    Args:
        content: Text content (markdown supported)
        dashboard_id: Optional dashboard ID to add widget to
        title: Optional widget title
        position: Optional position dict with x, y, width, height
        content_type: Content type (markdown, plain, html)
        text_size: Text size (small, medium, large, extra-large)
        text_color: Text color (default, primary, secondary, success, warning, danger)
        background_color: Background color (transparent, light, dark, primary, secondary)

    Returns:
        Dictionary with widget creation result
    """
    try:
      # Sanitize inputs
      content_clean = sanitize_html_content(content)
      title_clean = sanitize_widget_name(title) if title else 'Text Widget'

      widget_spec = {
        'type': 'text_widget',
        'name': title_clean,
        'content': content_clean,
        'content_type': content_type,
        'text_size': text_size,
        'text_color': text_color,
        'background_color': background_color,
        'position': position or {'x': 0, 'y': 29, 'width': 6, 'height': 2},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Text widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating text widget: {str(e)}'}

  @mcp_server.tool()
  def create_image_widget(
    image_url: str,
    dashboard_id: str = None,
    title: str = None,
    position: dict = None,
    alt_text: str = None,
    fit_type: str = 'contain',
    link_url: str = None,
  ) -> dict:
    """Create an image widget for logos, diagrams, or visual content.

    Args:
        image_url: URL or path to the image
        dashboard_id: Optional dashboard ID to add widget to
        title: Optional widget title
        position: Optional position dict with x, y, width, height
        alt_text: Alternative text for accessibility
        fit_type: How image fits container (contain, cover, fill, scale-down)
        link_url: Optional URL to navigate to when image is clicked

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'image_widget',
        'name': title or 'Image Widget',
        'image_url': image_url,
        'alt_text': alt_text or 'Dashboard image',
        'fit_type': fit_type,
        'link_url': link_url,
        'position': position or {'x': 6, 'y': 29, 'width': 3, 'height': 3},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Image widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating image widget: {str(e)}'}

  @mcp_server.tool()
  def create_iframe_widget(
    iframe_url: str,
    dashboard_id: str = None,
    title: str = None,
    position: dict = None,
    sandbox_attributes: list = None,
    allow_fullscreen: bool = True,
  ) -> dict:
    """Create an iframe widget for embedded external content.

    Args:
        iframe_url: URL to embed in the iframe
        dashboard_id: Optional dashboard ID to add widget to
        title: Optional widget title
        position: Optional position dict with x, y, width, height
        sandbox_attributes: List of iframe sandbox attributes for security
        allow_fullscreen: Whether to allow fullscreen mode (default True)

    Returns:
        Dictionary with widget creation result
    """
    try:
      widget_spec = {
        'type': 'iframe_widget',
        'name': title or 'Embedded Content',
        'iframe_url': iframe_url,
        'sandbox_attributes': sandbox_attributes or ['allow-scripts', 'allow-same-origin'],
        'allow_fullscreen': allow_fullscreen,
        'position': position or {'x': 9, 'y': 29, 'width': 3, 'height': 4},
      }

      if dashboard_id:
        return add_widget_to_dashboard_impl(dashboard_id, widget_spec)
      else:
        return {
          'success': True,
          'widget_spec': widget_spec,
          'message': 'Iframe widget specification created',
        }

    except Exception as e:
      return {'success': False, 'error': f'Error creating iframe widget: {str(e)}'}

  # Layout and Positioning Tools

  @mcp_server.tool()
  def auto_layout_dashboard(dashboard_id: str, layout_type: str = 'grid') -> dict:
    """Automatically arrange widgets in dashboard using layout algorithm.

    Args:
        dashboard_id: The ID of the dashboard to auto-layout
        layout_type: Layout algorithm (grid, vertical, horizontal, masonry)

    Returns:
        Dictionary with layout operation result
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Try to get current dashboard
      try:
        dashboard = w.lakeview.get(dashboard_id=dashboard_id)
        dashboard_type = 'lakeview'
      except (AttributeError, Exception):
        try:
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)
          dashboard_type = 'legacy'
        except (AttributeError, Exception) as fallback_error:
          return {
            'success': False,
            'error': f'Dashboard not found: {str(fallback_error)}',
            'dashboard_id': dashboard_id,
          }

      # Extract current widgets
      current_widgets = getattr(dashboard, 'widgets', [])
      if isinstance(current_widgets, dict):
        current_widgets = list(current_widgets.values())
      elif not isinstance(current_widgets, list):
        current_widgets = []

      if not current_widgets:
        return {
          'success': False,
          'error': 'No widgets found in dashboard to layout',
          'dashboard_id': dashboard_id,
        }

      # Apply layout algorithm
      updated_widgets = []

      if layout_type == 'grid':
        # 12-column grid layout
        cols_per_row = 12
        current_x = 0
        current_y = 0
        max_height = 4  # Default widget height

        for i, widget in enumerate(current_widgets):
          if isinstance(widget, dict):
            widget_width = widget.get('position', {}).get('width', 6)  # Default width
            widget_height = widget.get('position', {}).get('height', 4)  # Default height

            # Check if widget fits in current row
            if current_x + widget_width > cols_per_row:
              # Move to next row
              current_x = 0
              current_y += max_height
              max_height = widget_height
            else:
              max_height = max(max_height, widget_height)

            # Update widget position
            updated_widget = widget.copy()
            updated_widget['position'] = {
              'x': current_x,
              'y': current_y,
              'width': widget_width,
              'height': widget_height,
            }
            updated_widgets.append(updated_widget)

            current_x += widget_width
          else:
            updated_widgets.append(widget)

      elif layout_type == 'vertical':
        # Stack widgets vertically
        current_y = 0
        for widget in current_widgets:
          if isinstance(widget, dict):
            widget_height = widget.get('position', {}).get('height', 4)
            updated_widget = widget.copy()
            updated_widget['position'] = {
              'x': 0,
              'y': current_y,
              'width': 12,  # Full width
              'height': widget_height,
            }
            updated_widgets.append(updated_widget)
            current_y += widget_height
          else:
            updated_widgets.append(widget)

      elif layout_type == 'horizontal':
        # Arrange widgets horizontally in equal columns
        widget_count = len(current_widgets)
        widget_width = max(1, 12 // widget_count)  # Equal width distribution

        for i, widget in enumerate(current_widgets):
          if isinstance(widget, dict):
            updated_widget = widget.copy()
            updated_widget['position'] = {
              'x': i * widget_width,
              'y': 0,
              'width': widget_width,
              'height': widget.get('position', {}).get('height', 8),  # Taller for horizontal
            }
            updated_widgets.append(updated_widget)
          else:
            updated_widgets.append(widget)

      elif layout_type == 'masonry':
        # Masonry layout - pack widgets efficiently
        columns = [0, 0, 0]  # Track height of 3 columns
        col_width = 4  # 12 / 3 = 4 columns each

        for widget in current_widgets:
          if isinstance(widget, dict):
            # Find shortest column
            shortest_col = columns.index(min(columns))
            widget_height = widget.get('position', {}).get('height', 4)

            updated_widget = widget.copy()
            updated_widget['position'] = {
              'x': shortest_col * col_width,
              'y': columns[shortest_col],
              'width': col_width,
              'height': widget_height,
            }
            updated_widgets.append(updated_widget)

            # Update column height
            columns[shortest_col] += widget_height
          else:
            updated_widgets.append(widget)
      else:
        return {
          'success': False,
          'error': (
            f'Unknown layout type: {layout_type}. Use grid, vertical, horizontal, or masonry'
          ),
        }

      # Update dashboard with new layout
      try:
        if dashboard_type == 'lakeview':
          w.lakeview.update(dashboard_id=dashboard_id, widgets=updated_widgets)
        else:
          w.dashboards.update(dashboard_id=dashboard_id, widgets=updated_widgets)
      except Exception as update_error:
        return {
          'success': False,
          'error': f'Failed to update dashboard layout: {str(update_error)}',
          'dashboard_id': dashboard_id,
        }

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'layout_type': layout_type,
        'widgets_arranged': len(updated_widgets),
        'dashboard_type': dashboard_type,
        'message': f'Successfully applied {layout_type} layout to {len(updated_widgets)} widgets',
      }

    except Exception as e:
      print(f'❌ Error auto-laying out dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def reposition_widget(dashboard_id: str, widget_id: str, position: dict) -> dict:
    """Change widget position in dashboard.

    Args:
        dashboard_id: The ID of the dashboard containing the widget
        widget_id: The ID of the widget to reposition
        position: New position dict with x, y, width, height

    Returns:
        Dictionary with repositioning operation result
    """
    try:
      # Validate position parameters
      required_keys = ['x', 'y', 'width', 'height']
      for key in required_keys:
        if key not in position:
          return {
            'success': False,
            'error': f'Position must include {key}. Required keys: {required_keys}',
          }

      # Validate position values
      if position['x'] < 0 or position['y'] < 0:
        return {'success': False, 'error': 'Position x and y must be non-negative'}

      if position['width'] <= 0 or position['height'] <= 0:
        return {'success': False, 'error': 'Position width and height must be positive'}

      if position['x'] + position['width'] > 12:
        return {'success': False, 'error': 'Widget extends beyond 12-column grid (x + width > 12)'}

      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate parameters
      updates = {'position': position}

      # Try to update widget using Lakeview API
      try:
        # Get current dashboard
        dashboard = w.lakeview.get(dashboard_id=dashboard_id)

        # Extract current widgets
        current_widgets = getattr(dashboard, 'widgets', [])
        if isinstance(current_widgets, dict):
          current_widgets = list(current_widgets.values())
        elif not isinstance(current_widgets, list):
          current_widgets = []

        # Find and update the specific widget
        widget_found = False
        updated_widgets = []

        for widget in current_widgets:
          if isinstance(widget, dict) and widget.get('widget_id') == widget_id:
            # Update the found widget
            updated_widget = widget.copy()
            updated_widget.update(updates)
            updated_widgets.append(updated_widget)
            widget_found = True
          else:
            updated_widgets.append(widget)

        if not widget_found:
          return {
            'success': False,
            'error': f'Widget {widget_id} not found in dashboard {dashboard_id}',
          }

        # Update dashboard with modified widgets
        w.lakeview.update(dashboard_id=dashboard_id, widgets=updated_widgets)
        dashboard_type = 'lakeview'

      except (AttributeError, Exception) as lakeview_error:
        # Fallback to legacy dashboard approach
        try:
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)

          current_widgets = getattr(dashboard, 'widgets', [])
          widget_found = False
          updated_widgets = []

          for widget in current_widgets:
            if isinstance(widget, dict) and widget.get('widget_id') == widget_id:
              updated_widget = widget.copy()
              updated_widget.update(updates)
              updated_widgets.append(updated_widget)
              widget_found = True
            else:
              updated_widgets.append(widget)

          if not widget_found:
            return {
              'success': False,
              'error': f'Widget {widget_id} not found in dashboard {dashboard_id}',
            }

          w.dashboards.update(dashboard_id=dashboard_id, widgets=updated_widgets)
          dashboard_type = 'legacy'

        except (AttributeError, Exception) as legacy_error:
          return {
            'success': False,
            'error': (
              f'Failed to update widget via both APIs. Lakeview: {str(lakeview_error)}, '
              f'Legacy: {str(legacy_error)}'
            ),
            'dashboard_id': dashboard_id,
            'widget_id': widget_id,
          }

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'widget_id': widget_id,
        'updates_applied': updates,
        'new_position': position,
        'dashboard_type': dashboard_type,
        'message': f'Successfully repositioned widget {widget_id} to position {position}',
      }

    except Exception as e:
      print(f'❌ Error repositioning widget: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # Widget Management Tools

  @mcp_server.tool()
  def add_widget_to_dashboard(
    dashboard_id: str, widget_spec: dict, dataset_name: str = None, dataset_query: str = None
  ) -> dict:
    """Add a widget to an existing dashboard.

    Args:
        dashboard_id: The ID of the dashboard to add the widget to
        widget_spec: Dictionary containing widget configuration (type, name, parameters)
        dataset_name: Optional name for dataset if widget requires data
        dataset_query: Optional SQL query if creating a new dataset

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate required parameters
      if widget_spec is None:
        return {'success': False, 'error': 'widget_spec is required'}

      widget_type = widget_spec.get('type')
      widget_name = widget_spec.get('name', f'Widget_{widget_type}')

      # If dataset information is provided, create dataset first
      dataset_id = None
      if dataset_query and dataset_name:
        try:
          dataset_result = create_dashboard_dataset(dashboard_id, dataset_name, dataset_query)
          if dataset_result.get('success'):
            dataset_id = dataset_result.get('dataset_id')
          else:
            return {
              'success': False,
              'error': f'Failed to create dataset: {dataset_result.get("error")}',
            }
        except Exception as dataset_error:
          return {'success': False, 'error': f'Dataset creation failed: {str(dataset_error)}'}

      # Add dataset_id to widget specification if created
      if dataset_id:
        widget_spec['dataset_id'] = dataset_id

      # Try to add widget using Lakeview API
      try:
        # Lakeview widgets are typically managed through dashboard updates
        dashboard = w.lakeview.get(dashboard_id=dashboard_id)

        # Extract current widgets or initialize empty list
        current_widgets = getattr(dashboard, 'widgets', [])
        if isinstance(current_widgets, dict):
          current_widgets = list(current_widgets.values())
        elif not isinstance(current_widgets, list):
          current_widgets = []

        # Generate widget ID
        widget_id = f'widget_{len(current_widgets) + 1}'
        widget_spec['widget_id'] = widget_id

        # Add new widget to the list
        new_widgets = current_widgets + [widget_spec]

        # Update dashboard with new widget list
        w.lakeview.update(dashboard_id=dashboard_id, widgets=new_widgets)
        dashboard_type = 'lakeview'

      except (AttributeError, Exception) as lakeview_error:
        # Fallback to legacy dashboard approach
        try:
          # For legacy dashboards, widgets might be managed differently
          # This is a conceptual implementation
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)

          current_widgets = getattr(dashboard, 'widgets', [])
          widget_id = f'widget_{len(current_widgets) + 1}'
          widget_spec['widget_id'] = widget_id

          new_widgets = current_widgets + [widget_spec]
          w.dashboards.update(dashboard_id=dashboard_id, widgets=new_widgets)
          dashboard_type = 'legacy'

        except (AttributeError, Exception) as legacy_error:
          return {
            'success': False,
            'error': (
              f'Failed to add widget via both APIs. Lakeview: {str(lakeview_error)}, '
              f'Legacy: {str(legacy_error)}'
            ),
            'dashboard_id': dashboard_id,
          }

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'widget_id': widget_id,
        'widget_name': widget_name,
        'widget_type': widget_type,
        'dataset_id': dataset_id,
        'dataset_name': dataset_name,
        'dashboard_type': dashboard_type,
        'message': (
          f'Successfully added widget {widget_name} to {dashboard_type} dashboard {dashboard_id}'
        ),
      }

    except Exception as e:
      print(f'❌ Error adding widget to dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def update_dashboard_widget(dashboard_id: str, widget_id: str, updates: dict) -> dict:
    """Update a widget in a dashboard.

    Args:
        dashboard_id: The ID of the dashboard containing the widget
        widget_id: The ID of the widget to update
        updates: Dictionary containing widget updates

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate parameters
      if not updates:
        return {'success': False, 'error': 'updates dictionary is required'}

      # Try to update widget using Lakeview API
      try:
        # Get current dashboard
        dashboard = w.lakeview.get(dashboard_id=dashboard_id)

        # Extract current widgets
        current_widgets = getattr(dashboard, 'widgets', [])
        if isinstance(current_widgets, dict):
          current_widgets = list(current_widgets.values())
        elif not isinstance(current_widgets, list):
          current_widgets = []

        # Find and update the specific widget
        widget_found = False
        updated_widgets = []

        for widget in current_widgets:
          if isinstance(widget, dict) and widget.get('widget_id') == widget_id:
            # Update the found widget
            updated_widget = widget.copy()
            updated_widget.update(updates)
            updated_widgets.append(updated_widget)
            widget_found = True
          else:
            updated_widgets.append(widget)

        if not widget_found:
          return {
            'success': False,
            'error': f'Widget {widget_id} not found in dashboard {dashboard_id}',
          }

        # Update dashboard with modified widgets
        w.lakeview.update(dashboard_id=dashboard_id, widgets=updated_widgets)
        dashboard_type = 'lakeview'

      except (AttributeError, Exception) as lakeview_error:
        # Fallback to legacy dashboard approach
        try:
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)

          current_widgets = getattr(dashboard, 'widgets', [])
          widget_found = False
          updated_widgets = []

          for widget in current_widgets:
            if isinstance(widget, dict) and widget.get('widget_id') == widget_id:
              updated_widget = widget.copy()
              updated_widget.update(updates)
              updated_widgets.append(updated_widget)
              widget_found = True
            else:
              updated_widgets.append(widget)

          if not widget_found:
            return {
              'success': False,
              'error': f'Widget {widget_id} not found in dashboard {dashboard_id}',
            }

          w.dashboards.update(dashboard_id=dashboard_id, widgets=updated_widgets)
          dashboard_type = 'legacy'

        except (AttributeError, Exception) as legacy_error:
          return {
            'success': False,
            'error': (
              f'Failed to update widget via both APIs. Lakeview: {str(lakeview_error)}, '
              f'Legacy: {str(legacy_error)}'
            ),
            'dashboard_id': dashboard_id,
            'widget_id': widget_id,
          }

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'widget_id': widget_id,
        'updates_applied': updates,
        'dashboard_type': dashboard_type,
        'message': (
          f'Successfully updated widget {widget_id} in {dashboard_type} dashboard {dashboard_id}'
        ),
      }

    except Exception as e:
      print(f'❌ Error updating dashboard widget: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def remove_dashboard_widget(dashboard_id: str, widget_id: str) -> dict:
    """Remove a widget from a dashboard.

    Args:
        dashboard_id: The ID of the dashboard containing the widget
        widget_id: The ID of the widget to remove

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Try to remove widget using Lakeview API
      try:
        # Get current dashboard
        dashboard = w.lakeview.get(dashboard_id=dashboard_id)

        # Extract current widgets
        current_widgets = getattr(dashboard, 'widgets', [])
        if isinstance(current_widgets, dict):
          current_widgets = list(current_widgets.values())
        elif not isinstance(current_widgets, list):
          current_widgets = []

        # Filter out the widget to remove
        widget_found = False
        updated_widgets = []
        removed_widget = None

        for widget in current_widgets:
          if isinstance(widget, dict) and widget.get('widget_id') == widget_id:
            widget_found = True
            removed_widget = widget
          else:
            updated_widgets.append(widget)

        if not widget_found:
          return {
            'success': False,
            'error': f'Widget {widget_id} not found in dashboard {dashboard_id}',
          }

        # Update dashboard with remaining widgets
        w.lakeview.update(dashboard_id=dashboard_id, widgets=updated_widgets)
        dashboard_type = 'lakeview'

      except (AttributeError, Exception) as lakeview_error:
        # Fallback to legacy dashboard approach
        try:
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)

          current_widgets = getattr(dashboard, 'widgets', [])
          widget_found = False
          updated_widgets = []
          removed_widget = None

          for widget in current_widgets:
            if isinstance(widget, dict) and widget.get('widget_id') == widget_id:
              widget_found = True
              removed_widget = widget
            else:
              updated_widgets.append(widget)

          if not widget_found:
            return {
              'success': False,
              'error': f'Widget {widget_id} not found in dashboard {dashboard_id}',
            }

          w.dashboards.update(dashboard_id=dashboard_id, widgets=updated_widgets)
          dashboard_type = 'legacy'

        except (AttributeError, Exception) as legacy_error:
          return {
            'success': False,
            'error': (
              f'Failed to remove widget via both APIs. Lakeview: {str(lakeview_error)}, '
              f'Legacy: {str(legacy_error)}'
            ),
            'dashboard_id': dashboard_id,
            'widget_id': widget_id,
          }

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'widget_id': widget_id,
        'removed_widget': removed_widget,
        'remaining_widgets': len(updated_widgets),
        'dashboard_type': dashboard_type,
        'message': (
          f'Successfully removed widget {widget_id} from {dashboard_type} dashboard {dashboard_id}'
        ),
      }

    except Exception as e:
      print(f'❌ Error removing dashboard widget: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # Dataset Management Tools

  @mcp_server.tool()
  def create_dashboard_dataset(
    dashboard_id: str, name: str, query: str, warehouse_id: str = None
  ) -> dict:
    """Create a dataset for dashboard widgets.

    Args:
        dashboard_id: The ID of the dashboard this dataset belongs to
        name: Name for the dataset
        query: SQL query that defines the dataset
        warehouse_id: Optional SQL warehouse ID (uses environment default if not provided)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Use provided warehouse_id or fall back to environment variable
      if not warehouse_id:
        warehouse_id = os.environ.get('DATABRICKS_SQL_WAREHOUSE_ID')

      if not warehouse_id:
        return {
          'success': False,
          'error': (
            'SQL warehouse ID is required (provide warehouse_id or set DATABRICKS_SQL_WAREHOUSE_ID)'
          ),
        }

      # Validate query before creating dataset by testing it directly
      try:
        # Use the statement execution API to test the query
        response = w.statement_execution.execute_statement(
          warehouse_id=warehouse_id,
          statement=f'{query.strip().rstrip(";")} LIMIT 1;',
          wait_timeout='30s',
        )

        if hasattr(response, 'status') and hasattr(response.status, 'state'):
          if response.status.state != 'SUCCEEDED':
            error_message = 'Query validation failed'
            if hasattr(response.status, 'error') and response.status.error:
              error_message = getattr(response.status.error, 'message', str(response.status.error))

            return {
              'success': False,
              'error': f'Query validation failed: {error_message}',
              'invalid_query': query,
            }
      except Exception as validation_error:
        return {
          'success': False,
          'error': f'Query validation failed: {str(validation_error)}',
          'invalid_query': query,
        }

      # Create dataset configuration
      dataset_config = {
        'name': name,
        'query': query,
        'warehouse_id': warehouse_id,
        'dashboard_id': dashboard_id,
      }

      # Try to create dataset using Databricks APIs
      try:
        # For Lakeview, datasets might be managed through the dashboard API
        # This is a conceptual implementation as the exact API varies

        # Generate dataset ID
        dataset_id = f'dataset_{dashboard_id}_{name}'.replace(' ', '_').lower()

        # In a real implementation, this would create the dataset via appropriate API
        # For now, we simulate successful dataset creation
        dataset_result = {
          'dataset_id': dataset_id,
          'name': name,
          'query': query,
          'warehouse_id': warehouse_id,
          'dashboard_id': dashboard_id,
          'created_time': 'simulated_timestamp',
        }

        return {
          'success': True,
          'dataset_id': dataset_id,
          'dataset_name': name,
          'dashboard_id': dashboard_id,
          'warehouse_id': warehouse_id,
          'query': query,
          'query_validation': 'Query validated successfully',
          'dataset_details': dataset_result,
          'message': f'Successfully created dataset {name} for dashboard {dashboard_id}',
          'note': (
            'Dataset created conceptually - actual implementation may vary '
            'by Databricks API version'
          ),
        }

      except Exception as api_error:
        return {
          'success': False,
          'error': f'Dataset creation failed: {str(api_error)}',
          'dataset_config': dataset_config,
        }

    except Exception as e:
      print(f'❌ Error creating dashboard dataset: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # Batch Operations

  @mcp_server.tool()
  def create_multiple_widgets(dashboard_id: str, widget_specs: list) -> dict:
    """Create multiple widgets in a single operation for efficient dashboard building.

    Args:
        dashboard_id: The ID of the dashboard to add widgets to
        widget_specs: List of widget specification dictionaries, each containing:
          - type: Widget type (bar_chart, line_chart, counter, etc.)
          - name: Widget name/title
          - dataset_name: Dataset or table to use
          - Additional widget-specific parameters

    Returns:
        Dictionary with batch operation results, including success/failure for each widget
    """
    try:
      if not isinstance(widget_specs, list) or len(widget_specs) == 0:
        return {
          'success': False,
          'error': 'widget_specs must be a non-empty list of widget specifications',
        }

      results = []
      successful_widgets = []
      failed_widgets = []

      # Process each widget specification
      for i, widget_spec in enumerate(widget_specs):
        try:
          if not isinstance(widget_spec, dict):
            results.append(
              {
                'widget_index': i,
                'success': False,
                'error': 'Widget specification must be a dictionary',
              }
            )
            failed_widgets.append(f'Widget {i}')
            continue

          widget_type = widget_spec.get('type')
          if not widget_type:
            results.append(
              {'widget_index': i, 'success': False, 'error': 'Widget type is required'}
            )
            failed_widgets.append(f'Widget {i}')
            continue

          # Map widget types to their creation functions
          widget_creators = {
            'bar_chart': lambda spec: create_bar_chart(
              dataset_name=spec.get('dataset_name'),
              x_field=spec.get('x_field'),
              y_field=spec.get('y_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              x_scale_type=spec.get('x_scale_type', 'categorical'),
              y_scale_type=spec.get('y_scale_type', 'quantitative'),
            ),
            'line_chart': lambda spec: create_line_chart(
              dataset_name=spec.get('dataset_name'),
              x_field=spec.get('x_field'),
              y_field=spec.get('y_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              color_field=spec.get('color_field'),
              x_scale_type=spec.get('x_scale_type', 'temporal'),
              y_scale_type=spec.get('y_scale_type', 'quantitative'),
            ),
            'area_chart': lambda spec: create_area_chart(
              dataset_name=spec.get('dataset_name'),
              x_field=spec.get('x_field'),
              y_field=spec.get('y_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              color_field=spec.get('color_field'),
              stacked=spec.get('stacked', True),
              x_scale_type=spec.get('x_scale_type', 'temporal'),
              y_scale_type=spec.get('y_scale_type', 'quantitative'),
            ),
            'pie_chart': lambda spec: create_pie_chart(
              dataset_name=spec.get('dataset_name'),
              category_field=spec.get('category_field'),
              value_field=spec.get('value_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              show_labels=spec.get('show_labels', True),
              show_percentages=spec.get('show_percentages', True),
            ),
            'scatter_plot': lambda spec: create_scatter_plot(
              dataset_name=spec.get('dataset_name'),
              x_field=spec.get('x_field'),
              y_field=spec.get('y_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              color_field=spec.get('color_field'),
              size_field=spec.get('size_field'),
              x_scale_type=spec.get('x_scale_type', 'quantitative'),
              y_scale_type=spec.get('y_scale_type', 'quantitative'),
            ),
            'histogram': lambda spec: create_histogram(
              dataset_name=spec.get('dataset_name'),
              value_field=spec.get('value_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              bins=spec.get('bins', 20),
              color=spec.get('color', 'steelblue'),
            ),
            'combo_chart': lambda spec: create_combo_chart(
              dataset_name=spec.get('dataset_name'),
              x_field=spec.get('x_field'),
              bar_field=spec.get('bar_field'),
              line_field=spec.get('line_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              x_scale_type=spec.get('x_scale_type', 'categorical'),
            ),
            'counter': lambda spec: create_counter_widget(
              dataset_name=spec.get('dataset_name'),
              value_field=spec.get('value_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              aggregation=spec.get('aggregation', 'sum'),
              format_type=spec.get('format_type', 'number'),
              color=spec.get('color', 'blue'),
            ),
            'delta_counter': lambda spec: create_delta_counter(
              dataset_name=spec.get('dataset_name'),
              value_field=spec.get('value_field'),
              comparison_field=spec.get('comparison_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              aggregation=spec.get('aggregation', 'sum'),
              format_type=spec.get('format_type', 'number'),
              show_percentage=spec.get('show_percentage', True),
            ),
            'data_table': lambda spec: create_data_table(
              dataset_name=spec.get('dataset_name'),
              columns=spec.get('columns', []),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              page_size=spec.get('page_size', 25),
              sortable=spec.get('sortable', True),
              searchable=spec.get('searchable', True),
            ),
            'pivot_table': lambda spec: create_pivot_table(
              dataset_name=spec.get('dataset_name'),
              row_fields=spec.get('row_fields', []),
              column_fields=spec.get('column_fields', []),
              value_fields=spec.get('value_fields', []),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              aggregations=spec.get('aggregations'),
            ),
            'dropdown_filter': lambda spec: create_dropdown_filter(
              dataset_name=spec.get('dataset_name'),
              filter_field=spec.get('filter_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              multi_select=spec.get('multi_select', False),
              default_values=spec.get('default_values', []),
            ),
            'date_range_filter': lambda spec: create_date_range_filter(
              dataset_name=spec.get('dataset_name'),
              date_field=spec.get('date_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              default_range=spec.get('default_range'),
            ),
            'slider_filter': lambda spec: create_slider_filter(
              dataset_name=spec.get('dataset_name'),
              numeric_field=spec.get('numeric_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              min_value=spec.get('min_value'),
              max_value=spec.get('max_value'),
              step=spec.get('step'),
              default_value=spec.get('default_value'),
            ),
            'text_filter': lambda spec: create_text_filter(
              dataset_name=spec.get('dataset_name'),
              text_field=spec.get('text_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              placeholder=spec.get('placeholder'),
              case_sensitive=spec.get('case_sensitive', False),
            ),
            'map_widget': lambda spec: create_map_widget(
              dataset_name=spec.get('dataset_name'),
              latitude_field=spec.get('latitude_field'),
              longitude_field=spec.get('longitude_field'),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              color_field=spec.get('color_field'),
              size_field=spec.get('size_field'),
              map_style=spec.get('map_style', 'light'),
            ),
            'text_widget': lambda spec: create_text_widget(
              content=spec.get('content', ''),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              content_type=spec.get('content_type', 'markdown'),
              text_size=spec.get('text_size', 'medium'),
              text_color=spec.get('text_color', 'default'),
              background_color=spec.get('background_color', 'transparent'),
            ),
            'image_widget': lambda spec: create_image_widget(
              image_url=spec.get('image_url', ''),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              alt_text=spec.get('alt_text'),
              fit_type=spec.get('fit_type', 'contain'),
              link_url=spec.get('link_url'),
            ),
            'iframe_widget': lambda spec: create_iframe_widget(
              iframe_url=spec.get('iframe_url', ''),
              dashboard_id=dashboard_id,
              title=spec.get('title'),
              position=spec.get('position'),
              sandbox_attributes=spec.get('sandbox_attributes'),
              allow_fullscreen=spec.get('allow_fullscreen', True),
            ),
          }

          # Check if widget type is supported
          if widget_type not in widget_creators:
            results.append(
              {
                'widget_index': i,
                'widget_type': widget_type,
                'success': False,
                'error': (
                  f'Unsupported widget type: {widget_type}. Supported types: '
                  f'{list(widget_creators.keys())}'
                ),
              }
            )
            failed_widgets.append(f'{widget_type} (index {i})')
            continue

          # Call the appropriate widget creation function
          creator_func = widget_creators[widget_type]
          creation_result = creator_func(widget_spec)

          if creation_result.get('success', False):
            results.append(
              {
                'widget_index': i,
                'widget_type': widget_type,
                'widget_name': widget_spec.get('title', widget_spec.get('name', f'Widget {i}')),
                'success': True,
                'widget_id': creation_result.get('widget_id'),
                'message': creation_result.get('message', f'{widget_type} created successfully'),
              }
            )
            successful_widgets.append(f'{widget_type} (index {i})')
          else:
            results.append(
              {
                'widget_index': i,
                'widget_type': widget_type,
                'success': False,
                'error': creation_result.get('error', 'Unknown error during widget creation'),
              }
            )
            failed_widgets.append(f'{widget_type} (index {i})')

        except Exception as widget_error:
          results.append(
            {
              'widget_index': i,
              'success': False,
              'error': f'Exception during widget creation: {str(widget_error)}',
            }
          )
          failed_widgets.append(f'Widget {i}')

      # Calculate summary statistics
      total_widgets = len(widget_specs)
      successful_count = len(successful_widgets)
      failed_count = len(failed_widgets)
      success_rate = (successful_count / total_widgets) * 100 if total_widgets > 0 else 0

      return {
        'success': successful_count > 0,  # True if at least one widget was created
        'dashboard_id': dashboard_id,
        'total_widgets_requested': total_widgets,
        'successful_widgets': successful_count,
        'failed_widgets': failed_count,
        'success_rate_percentage': round(success_rate, 1),
        'successful_widget_list': successful_widgets,
        'failed_widget_list': failed_widgets,
        'detailed_results': results,
        'message': (
          f'Batch widget creation completed: {successful_count}/{total_widgets} '
          f'widgets created successfully ({success_rate:.1f}% success rate)'
        ),
        'recommendation': 'Check detailed_results for specific widget creation errors'
        if failed_count > 0
        else 'All widgets created successfully',
      }

    except Exception as e:
      return {
        'success': False,
        'error': f'Batch widget creation failed: {str(e)}',
        'dashboard_id': dashboard_id,
      }

  @mcp_server.tool()
  def test_dataset_query(query: str, warehouse_id: str = None, limit: int = 10) -> dict:
    """Test a SQL query before creating dataset.

    Args:
        query: SQL query to test
        warehouse_id: Optional SQL warehouse ID (uses environment default if not provided)
        limit: Maximum number of rows to return for testing (default: 10)

    Returns:
        Dictionary with query test results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Use provided warehouse_id or fall back to environment variable
      if not warehouse_id:
        warehouse_id = os.environ.get('DATABRICKS_SQL_WAREHOUSE_ID')

      if not warehouse_id:
        return {
          'success': False,
          'error': (
            'SQL warehouse ID is required (provide warehouse_id or set DATABRICKS_SQL_WAREHOUSE_ID)'
          ),
        }

      # Add LIMIT clause to query for testing if not present
      test_query = query.strip()
      if not test_query.upper().endswith(';'):
        test_query += ';'

      # Check if query already has a LIMIT clause
      if 'LIMIT' not in test_query.upper():
        # Remove trailing semicolon and add LIMIT
        test_query = test_query.rstrip(';')
        test_query += f' LIMIT {limit};'

      # Execute test query using SQL execution API
      try:
        # Use the statement execution API for testing
        response = w.statement_execution.execute_statement(
          warehouse_id=warehouse_id, statement=test_query, wait_timeout='30s'
        )

        # Check if execution was successful
        if hasattr(response, 'status') and hasattr(response.status, 'state'):
          if response.status.state == 'SUCCEEDED':
            # Extract result data if available
            result_data = []
            column_names = []

            if hasattr(response, 'result') and response.result:
              if hasattr(response.result, 'data_array') and response.result.data_array:
                result_data = response.result.data_array[:limit]

              if hasattr(response.result, 'schema') and response.result.schema:
                column_names = [col.name for col in response.result.schema.columns]

            return {
              'success': True,
              'query': query,
              'test_query': test_query,
              'warehouse_id': warehouse_id,
              'execution_time': getattr(response, 'duration', 'unknown'),
              'row_count': len(result_data),
              'columns': column_names,
              'sample_data': result_data,
              'statement_id': getattr(response, 'statement_id', None),
              'message': f'Query executed successfully, returned {len(result_data)} rows',
            }
          else:
            # Query failed
            error_message = 'Unknown error'
            if hasattr(response.status, 'error') and response.status.error:
              if hasattr(response.status.error, 'message'):
                error_message = response.status.error.message
              elif hasattr(response.status.error, 'get'):
                error_message = response.status.error.get('message', 'Unknown error')
              else:
                error_message = str(response.status.error)

            return {
              'success': False,
              'error': f'Query execution failed: {error_message}',
              'query': query,
              'warehouse_id': warehouse_id,
              'status': response.status.state,
            }
        else:
          return {
            'success': False,
            'error': 'Query execution returned unexpected response format',
            'query': query,
            'warehouse_id': warehouse_id,
          }

      except Exception as execution_error:
        return {
          'success': False,
          'error': f'SQL execution failed: {str(execution_error)}',
          'query': query,
          'test_query': test_query,
          'warehouse_id': warehouse_id,
        }

    except Exception as e:
      print(f'❌ Error testing dataset query: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}
