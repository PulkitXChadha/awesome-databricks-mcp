#!/usr/bin/env python3
"""End-to-end example: Update an existing dashboard with new widgets and modifications.

This script demonstrates how to:
1. Retrieve an existing dashboard
2. Add new widgets with different configurations
3. Update existing widgets
4. Remove obsolete widgets
5. Reorganize layout
6. Update dashboard metadata

Requirements:
- Existing Databricks dashboard
- SQL warehouse configured
- Permissions to modify the dashboard
"""

import os
import sys
from typing import Any, Dict, List

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from server.tools.dashboards import (  # noqa: E402
  add_widget_to_dashboard,
  auto_layout_dashboard,
  get_lakeview_dashboard,
  remove_dashboard_widget,
  reposition_widget,
  update_dashboard_widget,
  update_lakeview_dashboard,
)


class DashboardUpdater:
  """Class for updating existing dashboards with new widgets and modifications."""

  def __init__(self, dashboard_id: str, warehouse_id: str):
    """Initialize the dashboard updater.

    Args:
        dashboard_id: ID of the existing dashboard to update
        warehouse_id: Databricks SQL warehouse ID for query execution
    """
    self.dashboard_id = dashboard_id
    self.warehouse_id = warehouse_id
    self.dashboard_info = None
    self.existing_widgets = []
    self.added_widgets = []
    self.updated_widgets = []
    self.removed_widgets = []

  def analyze_existing_dashboard(self) -> Dict[str, Any]:
    """Analyze the existing dashboard structure and content.

    Returns:
        Analysis results including widget inventory
    """
    print(f'🔍 Analyzing existing dashboard: {self.dashboard_id}')

    result = get_lakeview_dashboard(dashboard_id=self.dashboard_id)

    if not result['success']:
      raise Exception(f'Failed to retrieve dashboard: {result["error"]}')

    self.dashboard_info = result['dashboard']
    self.existing_widgets = self.dashboard_info.get('widgets', [])

    analysis = {
      'dashboard_id': self.dashboard_id,
      'name': self.dashboard_info.get('name', 'Unnamed Dashboard'),
      'description': self.dashboard_info.get('description', ''),
      'widget_count': len(self.existing_widgets),
      'widget_types': {},
      'layout_bounds': {'max_x': 0, 'max_y': 0},
      'recommendations': [],
    }

    # Analyze existing widgets
    for widget in self.existing_widgets:
      widget_type = widget.get('type', 'unknown')
      analysis['widget_types'][widget_type] = analysis['widget_types'].get(widget_type, 0) + 1

      # Track layout bounds
      position = widget.get('position', {})
      if position:
        x = position.get('x', 0)
        y = position.get('y', 0)
        width = position.get('width', 0)
        height = position.get('height', 0)

        analysis['layout_bounds']['max_x'] = max(analysis['layout_bounds']['max_x'], x + width)
        analysis['layout_bounds']['max_y'] = max(analysis['layout_bounds']['max_y'], y + height)

    # Generate recommendations
    if analysis['widget_count'] > 20:
      analysis['recommendations'].append('Consider splitting into multiple dashboards')

    if 'filter' not in str(analysis['widget_types']).lower():
      analysis['recommendations'].append('Add filter widgets for better interactivity')

    if analysis['layout_bounds']['max_y'] > 50:
      analysis['recommendations'].append('Dashboard is very tall, consider reorganizing layout')

    print('✅ Dashboard analysis complete:')
    print(f'   Name: {analysis["name"]}')
    print(f'   Widgets: {analysis["widget_count"]}')
    print(f'   Widget Types: {analysis["widget_types"]}')
    print(
      f'   Layout Size: {analysis["layout_bounds"]["max_x"]}x{analysis["layout_bounds"]["max_y"]}'
    )

    if analysis['recommendations']:
      print('💡 Recommendations:')
      for rec in analysis['recommendations']:
        print(f'   - {rec}')

    return analysis

  def update_dashboard_metadata(self, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update dashboard metadata like name, description, tags.

    Args:
        updates: Dictionary of updates to apply

    Returns:
        Update operation result
    """
    print('📝 Updating dashboard metadata...')

    result = update_lakeview_dashboard(dashboard_id=self.dashboard_id, updates=updates)

    if result['success']:
      print('✅ Dashboard metadata updated')
      for key, value in updates.items():
        print(f'   {key}: {value}')
    else:
      print(f'❌ Failed to update metadata: {result["error"]}')

    return result

  def add_new_widgets(self, widget_specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add new widgets to the dashboard.

    Args:
        widget_specs: List of widget specifications to add

    Returns:
        List of addition results
    """
    print(f'➕ Adding {len(widget_specs)} new widgets...')

    results = []

    for i, widget_spec in enumerate(widget_specs):
      widget_title = widget_spec.get('title', f'Widget {i + 1}')
      print(f'   Adding: {widget_title}')

      result = add_widget_to_dashboard(dashboard_id=self.dashboard_id, widget_spec=widget_spec)

      if result['success']:
        self.added_widgets.append(result)
        print(f'   ✅ Added: {widget_title}')
      else:
        print(f'   ❌ Failed to add {widget_title}: {result["error"]}')

      results.append(result)

    return results

  def update_existing_widgets(self, widget_updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Update existing widgets with new configurations.

    Args:
        widget_updates: List of widget update specifications

    Returns:
        List of update results
    """
    print(f'🔄 Updating {len(widget_updates)} existing widgets...')

    results = []

    for update_spec in widget_updates:
      widget_id = update_spec['widget_id']
      updates = update_spec['updates']
      widget_name = updates.get('title', f'Widget {widget_id}')

      print(f'   Updating: {widget_name}')

      result = update_dashboard_widget(
        dashboard_id=self.dashboard_id, widget_id=widget_id, updates=updates
      )

      if result['success']:
        self.updated_widgets.append(result)
        print(f'   ✅ Updated: {widget_name}')

        # Log what was updated
        for key, value in updates.items():
          print(f'     - {key}: {value}')
      else:
        print(f'   ❌ Failed to update {widget_name}: {result["error"]}')

      results.append(result)

    return results

  def remove_obsolete_widgets(self, widget_ids_to_remove: List[str]) -> List[Dict[str, Any]]:
    """Remove obsolete widgets from the dashboard.

    Args:
        widget_ids_to_remove: List of widget IDs to remove

    Returns:
        List of removal results
    """
    print(f'🗑️  Removing {len(widget_ids_to_remove)} obsolete widgets...')

    results = []

    for widget_id in widget_ids_to_remove:
      # Find widget info for logging
      widget_info = next(
        (w for w in self.existing_widgets if w.get('widget_id') == widget_id), None
      )
      widget_name = widget_info.get('title', widget_id) if widget_info else widget_id

      print(f'   Removing: {widget_name}')

      result = remove_dashboard_widget(dashboard_id=self.dashboard_id, widget_id=widget_id)

      if result['success']:
        self.removed_widgets.append(result)
        print(f'   ✅ Removed: {widget_name}')
      else:
        print(f'   ❌ Failed to remove {widget_name}: {result["error"]}')

      results.append(result)

    return results

  def reorganize_layout(self, layout_type: str = 'grid') -> Dict[str, Any]:
    """Reorganize the dashboard layout after modifications.

    Args:
        layout_type: Type of layout to apply ('grid', 'vertical', 'horizontal', 'masonry')

    Returns:
        Layout reorganization result
    """
    print(f'🎨 Reorganizing dashboard with {layout_type} layout...')

    result = auto_layout_dashboard(dashboard_id=self.dashboard_id, layout_type=layout_type)

    if result['success']:
      print(f'✅ Layout reorganized: {result["widgets_arranged"]} widgets arranged')
    else:
      print(f'❌ Layout reorganization failed: {result["error"]}')

    return result

  def reposition_specific_widgets(
    self, repositioning_specs: List[Dict[str, Any]]
  ) -> List[Dict[str, Any]]:
    """Reposition specific widgets to custom positions.

    Args:
        repositioning_specs: List of repositioning specifications

    Returns:
        List of repositioning results
    """
    print(f'📐 Repositioning {len(repositioning_specs)} widgets...')

    results = []

    for spec in repositioning_specs:
      widget_id = spec['widget_id']
      new_position = spec['position']

      # Find widget info for logging
      widget_info = next(
        (w for w in self.existing_widgets if w.get('widget_id') == widget_id), None
      )
      widget_name = widget_info.get('title', widget_id) if widget_info else widget_id

      print(f'   Repositioning: {widget_name}')
      print(
        f'     New position: x={new_position["x"]}, y={new_position["y"]}, '
        f'w={new_position["width"]}, h={new_position["height"]}'
      )

      result = reposition_widget(
        dashboard_id=self.dashboard_id, widget_id=widget_id, position=new_position
      )

      if result['success']:
        print(f'   ✅ Repositioned: {widget_name}')
      else:
        print(f'   ❌ Failed to reposition {widget_name}: {result["error"]}')

      results.append(result)

    return results

  def create_enhancement_widgets(self) -> List[Dict[str, Any]]:
    """Create enhancement widgets based on dashboard analysis.

    Returns:
        List of enhancement widget specifications
    """
    enhancements = []

    # Add summary text widget
    enhancements.append(
      {
        'type': 'text_widget',
        'title': 'Dashboard Updates',
        'content': f"""
# Dashboard Enhancement Summary

**Last Updated:** {self._get_current_timestamp()}

## Recent Improvements
- ✅ Added interactive filters
- ✅ Enhanced visualizations
- ✅ Improved layout organization
- ✅ Updated data sources

## Key Features
- **Real-time Data**: Automatic refresh every 15 minutes
- **Interactive Filtering**: Multi-level drill-down capability
- **Mobile Responsive**: Optimized for all screen sizes
- **Export Ready**: PDF and image export available

*Dashboard ID: {self.dashboard_id}*
            """,
        'content_type': 'markdown',
      }
    )

    # Add performance monitoring if not present
    performance_widgets = [
      w for w in self.existing_widgets if 'performance' in w.get('title', '').lower()
    ]
    if not performance_widgets:
      enhancements.append(
        {
          'type': 'counter_widget',
          'title': 'Dashboard Load Time',
          'dataset_name': 'system_metrics',
          'value_field': 'load_time_ms',
          'aggregation': 'avg',
          'format_type': 'number',
          'color': 'blue',
        }
      )

    # Add filter widgets if missing
    filter_widgets = [w for w in self.existing_widgets if 'filter' in w.get('type', '').lower()]
    if len(filter_widgets) < 2:
      enhancements.extend(
        [
          {
            'type': 'dropdown_filter',
            'title': 'Category Filter',
            'dataset_name': 'main_data',
            'filter_field': 'category',
            'multi_select': True,
          },
          {
            'type': 'date_range_filter',
            'title': 'Date Range',
            'dataset_name': 'main_data',
            'date_field': 'created_date',
          },
        ]
      )

    return enhancements

  def _get_current_timestamp(self) -> str:
    """Get current timestamp formatted for display."""
    from datetime import datetime

    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  def generate_update_summary(self) -> Dict[str, Any]:
    """Generate a comprehensive summary of all updates made.

    Returns:
        Update summary report
    """
    summary = {
      'dashboard_id': self.dashboard_id,
      'dashboard_name': self.dashboard_info.get('name', 'Unknown')
      if self.dashboard_info
      else 'Unknown',
      'original_widget_count': len(self.existing_widgets),
      'widgets_added': len(self.added_widgets),
      'widgets_updated': len(self.updated_widgets),
      'widgets_removed': len(self.removed_widgets),
      'final_widget_count': len(self.existing_widgets)
      + len(self.added_widgets)
      - len(self.removed_widgets),
      'update_timestamp': self._get_current_timestamp(),
      'success': True,
    }

    print('\n📊 Dashboard Update Summary:')
    print(f'   Dashboard: {summary["dashboard_name"]} ({summary["dashboard_id"]})')
    print(f'   Original Widgets: {summary["original_widget_count"]}')
    print(f'   Added: {summary["widgets_added"]}')
    print(f'   Updated: {summary["widgets_updated"]}')
    print(f'   Removed: {summary["widgets_removed"]}')
    print(f'   Final Count: {summary["final_widget_count"]}')
    print(f'   Updated At: {summary["update_timestamp"]}')

    return summary


def create_example_update_plan() -> Dict[str, Any]:
  """Create an example update plan for demonstration.

  Returns:
      Example update plan with various modifications
  """
  return {
    'metadata_updates': {
      'description': 'Enhanced dashboard with improved visualizations and interactive filters',
      'tags': ['analytics', 'enhanced', 'interactive', 'updated'],
    },
    'new_widgets': [
      {
        'type': 'text_widget',
        'title': 'Dashboard Overview',
        'content': """
# Welcome to the Enhanced Dashboard

This dashboard has been updated with:
- 📊 New interactive visualizations
- 🔍 Advanced filtering capabilities
- 📱 Mobile-responsive design
- ⚡ Improved performance

Use the filters on the right to customize your view.
                """,
        'content_type': 'markdown',
      },
      {
        'type': 'counter_widget',
        'title': 'Total Records',
        'dataset_name': 'main_dataset',
        'value_field': 'record_count',
        'aggregation': 'sum',
        'format_type': 'number',
        'color': 'green',
      },
    ],
    'widget_updates': [
      # Example: Update an existing widget (you'd need to know the actual widget_id)
      {
        'widget_id': 'existing_widget_1',
        'updates': {
          'title': 'Updated Sales Chart',
          'color_scheme': 'viridis',
          'description': 'Enhanced sales visualization with trend analysis',
        },
      }
    ],
    'widgets_to_remove': [
      # Example: Remove obsolete widgets (you'd need actual widget_ids)
      # 'obsolete_widget_1',
      # 'old_counter_widget'
    ],
    'repositioning': [
      {'widget_id': 'header_widget', 'position': {'x': 0, 'y': 0, 'width': 12, 'height': 2}}
    ],
    'layout_type': 'grid',
  }


def main():
  """Main execution function for dashboard updating."""
  # Get parameters from command line or environment
  if len(sys.argv) < 2:
    print('❌ Error: Dashboard ID required')
    print('Usage: python update_existing_dashboard.py <dashboard-id> [warehouse-id]')
    print('   dashboard-id: ID of the dashboard to update')
    print('   warehouse-id: SQL warehouse ID (or set DATABRICKS_SQL_WAREHOUSE_ID)')
    sys.exit(1)

  dashboard_id = sys.argv[1]

  warehouse_id = os.getenv('DATABRICKS_SQL_WAREHOUSE_ID')
  if len(sys.argv) > 2:
    warehouse_id = sys.argv[2]

  if not warehouse_id:
    print('❌ Error: SQL Warehouse ID required')
    print('   Set DATABRICKS_SQL_WAREHOUSE_ID environment variable')
    print('   Or provide as second command line argument')
    sys.exit(1)

  print('🚀 Starting Dashboard Update Process')
  print(f'   Dashboard ID: {dashboard_id}')
  print(f'   SQL Warehouse: {warehouse_id}')
  print('=' * 60)

  try:
    # Create dashboard updater
    updater = DashboardUpdater(dashboard_id, warehouse_id)

    # Analyze existing dashboard
    updater.analyze_existing_dashboard()

    # Get update plan (in real usage, this would be customized)
    update_plan = create_example_update_plan()

    print('\n📋 Update Plan:')
    print(f'   Metadata updates: {len(update_plan["metadata_updates"])}')
    print(f'   New widgets: {len(update_plan["new_widgets"])}')
    print(f'   Widget updates: {len(update_plan["widget_updates"])}')
    print(f'   Widgets to remove: {len(update_plan["widgets_to_remove"])}')
    print(f'   Layout type: {update_plan["layout_type"]}')

    # Execute updates
    print('\n🔧 Executing Updates...')

    # Update metadata
    if update_plan['metadata_updates']:
      updater.update_dashboard_metadata(update_plan['metadata_updates'])

    # Add new widgets (including enhancements)
    all_new_widgets = update_plan['new_widgets'] + updater.create_enhancement_widgets()
    if all_new_widgets:
      updater.add_new_widgets(all_new_widgets)

    # Update existing widgets
    if update_plan['widget_updates']:
      updater.update_existing_widgets(update_plan['widget_updates'])

    # Remove obsolete widgets
    if update_plan['widgets_to_remove']:
      updater.remove_obsolete_widgets(update_plan['widgets_to_remove'])

    # Reposition specific widgets
    if update_plan['repositioning']:
      updater.reposition_specific_widgets(update_plan['repositioning'])

    # Reorganize layout
    updater.reorganize_layout(update_plan['layout_type'])

    # Generate final summary
    summary = updater.generate_update_summary()

    print('\n🎉 Dashboard update completed successfully!')
    print(f'   Updated Dashboard: {summary["dashboard_name"]}')
    print(f'   Final widget count: {summary["final_widget_count"]}')
    print(
      f'   Net change: {summary["final_widget_count"] - summary["original_widget_count"]} widgets'
    )
    print(f'   Dashboard URL: [Your Databricks workspace]/dashboards/{dashboard_id}')

    print('\n💡 Next Steps:')
    print('   1. Review the updated dashboard layout')
    print('   2. Test all interactive filters and widgets')
    print('   3. Update dashboard sharing permissions if needed')
    print('   4. Schedule regular refresh intervals for data')
    print('   5. Gather feedback from dashboard users')

    return summary

  except Exception as e:
    print(f'\n❌ Dashboard update failed: {str(e)}')
    import traceback

    traceback.print_exc()
    sys.exit(1)


if __name__ == '__main__':
  main()
