#!/usr/bin/env python3
"""Inspect the available Lakeview API methods in the Databricks SDK."""

from databricks.sdk import WorkspaceClient


def inspect_lakeview_api():
  """Inspect the Lakeview API methods."""
  print('🔍 Inspecting Databricks SDK Lakeview API...')
  print('=' * 50)

  try:
    # Initialize client (this will fail without proper credentials, but we can inspect the structure)
    w = WorkspaceClient()

    print('✅ WorkspaceClient initialized successfully')

    # Check if lakeview attribute exists
    if hasattr(w, 'lakeview'):
      print('✅ lakeview attribute found')
      lakeview = w.lakeview

      # List all attributes and methods
      print('\n📋 Available lakeview attributes and methods:')
      for attr_name in dir(lakeview):
        if not attr_name.startswith('_'):
          attr = getattr(lakeview, attr_name)
          attr_type = type(attr).__name__
          print(f'  - {attr_name}: {attr_type}')

          # If it's a callable, try to get more info
          if callable(attr):
            try:
              # Get docstring if available
              doc = getattr(attr, '__doc__', 'No documentation')
              if doc:
                doc_lines = doc.strip().split('\n')
                first_line = doc_lines[0] if doc_lines else 'No description'
                print(f'    📝 {first_line}')
            except Exception as e:
              print(f'    ⚠️ Error getting doc: {e}')
    else:
      print('❌ lakeview attribute not found')

      # Check what attributes are available
      print('\n📋 Available WorkspaceClient attributes:')
      for attr_name in dir(w):
        if not attr_name.startswith('_') and not callable(getattr(w, attr_name)):
          print(f'  - {attr_name}')

    # Check for dashboard-related attributes
    print('\n🔍 Looking for dashboard-related attributes...')
    dashboard_attrs = [attr for attr in dir(w) if 'dashboard' in attr.lower()]
    if dashboard_attrs:
      print('✅ Found dashboard-related attributes:')
      for attr in dashboard_attrs:
        print(f'  - {attr}')
    else:
      print('❌ No dashboard-related attributes found')

    # Check for SQL-related attributes (legacy dashboards)
    print('\n🔍 Looking for SQL-related attributes...')
    sql_attrs = [attr for attr in dir(w) if 'sql' in attr.lower()]
    if sql_attrs:
      print('✅ Found SQL-related attributes:')
      for attr in sql_attrs:
        print(f'  - {attr}')

  except Exception as e:
    print(f'❌ Error initializing WorkspaceClient: {e}')
    print('\n💡 This is expected without proper Databricks credentials.')
    print('   The script is designed to inspect the API structure.')

    # Try to import and inspect the service modules directly
    print('\n🔍 Inspecting service modules directly...')
    try:
      from databricks.sdk.service import sql

      print('✅ sql service module found')

      # List available classes in sql module
      sql_classes = [cls for cls in dir(sql) if not cls.startswith('_') and cls.endswith('API')]
      print(f'📋 Available SQL API classes: {sql_classes}')

      # Check if there's a dashboards API
      if hasattr(sql, 'DashboardsAPI'):
        dashboards_api = sql.DashboardsAPI
        print('✅ DashboardsAPI found')

        # List methods
        methods = [
          method
          for method in dir(dashboards_api)
          if not method.startswith('_') and callable(getattr(dashboards_api, method))
        ]
        print(f'📋 Available methods: {methods}')

    except ImportError as import_error:
      print(f'❌ Could not import sql service module: {import_error}')
    except Exception as module_error:
      print(f'❌ Error inspecting sql module: {module_error}')


if __name__ == '__main__':
  inspect_lakeview_api()
