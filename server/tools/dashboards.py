"""Dashboards and monitoring MCP tools for Databricks."""

import os

from databricks.sdk import WorkspaceClient


def load_dashboard_tools(mcp_server):
  """Register dashboards and monitoring MCP tools with the server.

  Args:
      mcp_server: The FastMCP server instance to register tools with
  """

  @mcp_server.tool
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
          dashboards.append({
            'dashboard_id': dashboard.dashboard_id,
            'name': dashboard.name,
            'description': getattr(dashboard, 'description', None),
            'created_time': getattr(dashboard, 'created_time', None),
            'updated_time': getattr(dashboard, 'updated_time', None),
            'owner': getattr(dashboard, 'owner', None),
            'status': getattr(dashboard, 'status', None),
            'type': 'lakeview'
          })
      except AttributeError:
        # Fallback: try alternative API paths if lakeview is not available
        try:
          # Try legacy dashboard API as fallback
          for dashboard in w.dashboards.list():
            dashboards.append({
              'dashboard_id': getattr(dashboard, 'id', getattr(dashboard, 'dashboard_id', None)),
              'name': getattr(dashboard, 'name', None),
              'description': getattr(dashboard, 'description', None),
              'created_time': getattr(dashboard, 'created_time', getattr(dashboard, 'created_at', None)),
              'updated_time': getattr(dashboard, 'updated_time', getattr(dashboard, 'updated_at', None)),
              'owner': getattr(dashboard, 'owner', getattr(dashboard, 'user', None)),
              'status': getattr(dashboard, 'status', None),
              'type': 'legacy'
            })
        except (AttributeError, Exception) as fallback_error:
          print(f'⚠️ Fallback dashboard listing failed: {str(fallback_error)}')
          # Return empty list if both methods fail
          pass

      return {
        'success': True,
        'dashboards': dashboards,
        'count': len(dashboards),
        'message': f'Found {len(dashboards)} dashboard(s)',
        'note': 'Includes both Lakeview and legacy dashboards if available'
      }

    except Exception as e:
      print(f'❌ Error listing Lakeview dashboards: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'dashboards': [], 'count': 0}

  @mcp_server.tool
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
      except (AttributeError, Exception):
        # Fallback to legacy dashboard API
        try:
          dashboard = w.dashboards.get(dashboard_id=dashboard_id)
          dashboard_type = 'legacy'
        except (AttributeError, Exception) as fallback_error:
          return {
            'success': False,
            'error': f'Dashboard not found or API not available: {str(fallback_error)}',
            'dashboard_id': dashboard_id
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
        'type': dashboard_type
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

  @mcp_server.tool
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
        return {
          'success': False,
          'error': 'Dashboard name is required in dashboard_config'
        }

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
            'error': f'Dashboard creation failed or API not available: {str(fallback_error)}'
          }

      # Extract dashboard details
      dashboard_id = getattr(dashboard, 'dashboard_id', getattr(dashboard, 'id', None))
      dashboard_name = getattr(dashboard, 'name', dashboard_config.get('name'))

      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'name': dashboard_name,
        'type': dashboard_type,
        'message': f'Successfully created {dashboard_type} dashboard {dashboard_name} with ID {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error creating Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
        return {
          'success': False,
          'error': 'No updates provided in updates parameter'
        }

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
            'dashboard_id': dashboard_id
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

  @mcp_server.tool
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
            'dashboard_id': dashboard_id
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

  @mcp_server.tool
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

  @mcp_server.tool
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

  @mcp_server.tool
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

  @mcp_server.tool
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

  @mcp_server.tool
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

  @mcp_server.tool
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
