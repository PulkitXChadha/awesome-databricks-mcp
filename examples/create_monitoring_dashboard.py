#!/usr/bin/env python3
"""End-to-end example: Create a comprehensive system monitoring dashboard.

This script demonstrates building an operational monitoring dashboard
with real-time metrics, alerts, and performance indicators.

Requirements:
- Databricks workspace with system metrics data
- SQL warehouse configured
- Access to system/operational tables
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from server.tools.dashboards import (  # noqa: E402
  add_widget_to_dashboard,
  auto_layout_dashboard,
  create_dashboard_dataset,
  create_lakeview_dashboard,
  test_dataset_query,
)


class MonitoringDashboardBuilder:
  """Builder class for creating a system monitoring dashboard."""

  def __init__(self, warehouse_id: str):
    """Initialize the monitoring dashboard builder.

    Args:
        warehouse_id: Databricks SQL warehouse ID for query execution
    """
    self.warehouse_id = warehouse_id
    self.dashboard_id = None
    self.datasets = {}
    self.widgets = []
    self.current_time = datetime.now()

  def create_dashboard(self) -> Dict[str, Any]:
    """Create the main monitoring dashboard container.

    Returns:
        Dashboard creation result
    """
    print('🖥️  Creating System Monitoring Dashboard...')

    dashboard_config = {
      'name': 'System Monitoring Dashboard',
      'description': 'Real-time system performance monitoring with alerts and KPIs',
      'tags': ['monitoring', 'operations', 'performance', 'alerts', 'sla'],
    }

    result = create_lakeview_dashboard(dashboard_config)

    if result['success']:
      self.dashboard_id = result['dashboard_id']
      print(f'✅ Dashboard created successfully: {self.dashboard_id}')
      print(f'   Name: {result["name"]}')
      print(f'   Type: {result["type"]}')
    else:
      print(f'❌ Dashboard creation failed: {result["error"]}')
      raise Exception('Dashboard creation failed')

    return result

  def create_datasets(self) -> Dict[str, Any]:
    """Create monitoring datasets for various system metrics.

    Returns:
        Results of dataset creation operations
    """
    print('\n📊 Creating monitoring datasets...')

    # Define time windows for monitoring
    last_hour = (self.current_time - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    last_24h = (self.current_time - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    last_week = (self.current_time - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

    datasets_config = [
      {
        'name': 'System Health Metrics',
        'query': f"""
                    SELECT
                        DATE_FORMAT(timestamp, 'yyyy-MM-dd HH:mm') as time_bucket,
                        service_name,
                        environment,
                        AVG(cpu_usage_percent) as avg_cpu,
                        AVG(memory_usage_percent) as avg_memory,
                        AVG(disk_usage_percent) as avg_disk,
                        COUNT(*) as sample_count,
                        MAX(response_time_ms) as max_response_time,
                        AVG(response_time_ms) as avg_response_time
                    FROM system_metrics
                    WHERE timestamp >= '{last_24h}'
                    GROUP BY DATE_FORMAT(timestamp, 'yyyy-MM-dd HH:mm'), service_name, environment
                    ORDER BY time_bucket DESC
                """,
        'description': 'Real-time system health metrics aggregated by service and environment',
      },
      {
        'name': 'Error Rate Analysis',
        'query': f"""
                    SELECT
                        DATE_FORMAT(timestamp, 'yyyy-MM-dd HH') as hour,
                        service_name,
                        environment,
                        SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
                        COUNT(*) as total_requests,
                        ROUND(
                            SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                            2
                        ) as error_rate_percent,
                        SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) as server_error_count,
                        SUM(
                            CASE WHEN status_code BETWEEN 400 AND 499 THEN 1 ELSE 0 END
                        ) as client_error_count
                    FROM application_logs
                    WHERE timestamp >= '{last_24h}'
                    GROUP BY DATE_FORMAT(timestamp, 'yyyy-MM-dd HH'), service_name, environment
                    ORDER BY hour DESC
                """,
        'description': 'Error rate analysis with breakdown by error types',
      },
      {
        'name': 'Performance Trends',
        'query': f"""
                    SELECT
                        DATE(timestamp) as date,
                        service_name,
                        environment,
                        AVG(response_time_ms) as avg_response_time,
                        PERCENTILE_APPROX(response_time_ms, 0.95) as p95_response_time,
                        PERCENTILE_APPROX(response_time_ms, 0.99) as p99_response_time,
                        MAX(response_time_ms) as max_response_time,
                        COUNT(*) as request_count
                    FROM application_logs
                    WHERE timestamp >= '{last_week}'
                    AND response_time_ms IS NOT NULL
                    GROUP BY DATE(timestamp), service_name, environment
                    ORDER BY date DESC
                """,
        'description': 'Performance trends and response time percentiles',
      },
      {
        'name': 'Alert Status',
        'query': f"""
                    SELECT
                        alert_name,
                        service_name,
                        environment,
                        severity,
                        status,
                        COUNT(*) as alert_count,
                        MAX(timestamp) as last_triggered,
                        AVG(
                            UNIX_TIMESTAMP(resolved_at) - UNIX_TIMESTAMP(timestamp)
                        ) / 60 as avg_resolution_time_minutes
                    FROM system_alerts
                    WHERE timestamp >= '{last_24h}'
                    GROUP BY alert_name, service_name, environment, severity, status
                    ORDER BY last_triggered DESC
                """,
        'description': 'Current alert status and resolution metrics',
      },
      {
        'name': 'Resource Utilization',
        'query': f"""
                    SELECT
                        node_name,
                        environment,
                        timestamp,
                        cpu_cores_used,
                        cpu_cores_total,
                        ROUND(
                            cpu_cores_used * 100.0 / cpu_cores_total,
                            2
                        ) as cpu_utilization_percent,
                        memory_gb_used,
                        memory_gb_total,
                        ROUND(
                            memory_gb_used * 100.0 / memory_gb_total,
                            2
                        ) as memory_utilization_percent,
                        disk_gb_used,
                        disk_gb_total,
                        ROUND(disk_gb_used * 100.0 / disk_gb_total, 2) as disk_utilization_percent,
                        network_in_mbps,
                        network_out_mbps
                    FROM resource_metrics
                    WHERE timestamp >= '{last_hour}'
                    ORDER BY timestamp DESC
                """,
        'description': 'Detailed resource utilization across all nodes',
      },
      {
        'name': 'SLA Compliance',
        'query': f"""
                    WITH sla_metrics AS (
                        SELECT
                            service_name,
                            environment,
                            DATE(timestamp) as date,
                            COUNT(*) as total_requests,
                            SUM(
                                CASE WHEN response_time_ms <= 500 THEN 1 ELSE 0 END
                            ) as requests_under_500ms,
                            SUM(
                                CASE WHEN status_code < 400 THEN 1 ELSE 0 END
                            ) as successful_requests,
                            AVG(response_time_ms) as avg_response_time
                        FROM application_logs
                        WHERE timestamp >= '{last_week}'
                        GROUP BY service_name, environment, DATE(timestamp)
                    )
                    SELECT
                        service_name,
                        environment,
                        date,
                        total_requests,
                        ROUND(
                            requests_under_500ms * 100.0 / total_requests,
                            2
                        ) as performance_sla_percent,
                        ROUND(
                            successful_requests * 100.0 / total_requests,
                            2
                        ) as availability_sla_percent,
                        avg_response_time,
                        CASE
                            WHEN requests_under_500ms * 100.0 / total_requests >= 95
                            AND successful_requests * 100.0 / total_requests >= 99.9
                            THEN 'Met'
                            ELSE 'Missed'
                        END as sla_status
                    FROM sla_metrics
                    ORDER BY date DESC, service_name
                """,
        'description': 'SLA compliance tracking with performance and availability metrics',
      },
    ]

    results = {}

    for dataset_config in datasets_config:
      print(f'   Creating dataset: {dataset_config["name"]}')

      # Test the query first
      test_result = test_dataset_query(
        query=dataset_config['query'], warehouse_id=self.warehouse_id, limit=10
      )

      if not test_result['success']:
        print(f'   ⚠️  Query test failed: {test_result["error"]}')
        # Create fallback dataset for demo purposes
        fallback_query = self._create_fallback_query(dataset_config['name'])
        if fallback_query:
          test_result = test_dataset_query(
            query=fallback_query, warehouse_id=self.warehouse_id, limit=10
          )
          if test_result['success']:
            dataset_config['query'] = fallback_query
            print('   ✓ Using fallback query')
          else:
            continue
        else:
          continue

      print(f'   ✓ Query validated ({test_result["row_count"]} rows)')

      # Create the dataset
      dataset_result = create_dashboard_dataset(
        dashboard_id=self.dashboard_id,
        name=dataset_config['name'],
        query=dataset_config['query'],
        warehouse_id=self.warehouse_id,
      )

      if dataset_result['success']:
        self.datasets[dataset_config['name']] = dataset_result
        print(f'   ✅ Dataset created: {dataset_result["dataset_id"]}')
      else:
        print(f'   ❌ Dataset creation failed: {dataset_result["error"]}')

      results[dataset_config['name']] = dataset_result

    return results

  def _create_fallback_query(self, dataset_name: str) -> str:
    """Create fallback queries for demo when system tables don't exist.

    Args:
        dataset_name: Name of the dataset to create fallback for

    Returns:
        Fallback SQL query or None
    """
    fallback_queries = {
      'System Health Metrics': """
                SELECT
                    DATE_FORMAT(NOW(), 'yyyy-MM-dd HH:mm') as time_bucket,
                    'web-service' as service_name,
                    'production' as environment,
                    ROUND(RAND() * 100, 2) as avg_cpu,
                    ROUND(RAND() * 100, 2) as avg_memory,
                    ROUND(RAND() * 100, 2) as avg_disk,
                    100 as sample_count,
                    ROUND(RAND() * 1000, 2) as max_response_time,
                    ROUND(RAND() * 500, 2) as avg_response_time
                UNION ALL
                SELECT
                    DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 HOUR), 'yyyy-MM-dd HH:mm'),
                    'api-service',
                    'production',
                    ROUND(RAND() * 100, 2),
                    ROUND(RAND() * 100, 2),
                    ROUND(RAND() * 100, 2),
                    150,
                    ROUND(RAND() * 1000, 2),
                    ROUND(RAND() * 500, 2)
            """,
      'Error Rate Analysis': """
                SELECT
                    DATE_FORMAT(NOW(), 'yyyy-MM-dd HH') as hour,
                    'web-service' as service_name,
                    'production' as environment,
                    CAST(RAND() * 50 AS INT) as error_count,
                    1000 as total_requests,
                    ROUND(RAND() * 5, 2) as error_rate_percent,
                    CAST(RAND() * 10 AS INT) as server_error_count,
                    CAST(RAND() * 40 AS INT) as client_error_count
            """,
    }

    return fallback_queries.get(dataset_name)

  def create_alert_widgets(self) -> List[Dict[str, Any]]:
    """Create alert and status indicator widgets.

    Returns:
        List of widget creation results
    """
    print('\n🚨 Creating alert widgets...')

    alert_widgets = [
      {
        'type': 'counter_widget',
        'params': {
          'dataset_name': 'Alert Status',
          'value_field': 'alert_count',
          'aggregation': 'sum',
          'title': 'Active Alerts',
          'format_type': 'number',
          'color': 'red',
        },
      },
      {
        'type': 'counter_widget',
        'params': {
          'dataset_name': 'Alert Status',
          'value_field': 'avg_resolution_time_minutes',
          'aggregation': 'avg',
          'title': 'Avg Resolution Time (min)',
          'format_type': 'number',
          'color': 'yellow',
        },
      },
      {
        'type': 'text_widget',
        'params': {
          'content': f"""
# 🚨 System Status

**Last Updated:** {self.current_time.strftime('%Y-%m-%d %H:%M:%S')}

## Alert Thresholds
- 🔴 **Critical:** CPU > 90%, Memory > 95%, Error Rate > 5%
- 🟡 **Warning:** CPU > 80%, Memory > 85%, Error Rate > 2%
- 🟢 **Normal:** All metrics within acceptable ranges

## SLA Targets
- **Performance:** 95% of requests < 500ms
- **Availability:** 99.9% success rate
- **Resolution Time:** < 15 minutes
                    """,
          'content_type': 'markdown',
          'title': 'Alert Configuration',
        },
      },
    ]

    return self._create_widgets(alert_widgets, 'alert')

  def create_performance_widgets(self) -> List[Dict[str, Any]]:
    """Create performance monitoring widgets.

    Returns:
        List of widget creation results
    """
    print('\n⚡ Creating performance widgets...')

    performance_widgets = [
      {
        'type': 'line_chart',
        'params': {
          'dataset_name': 'System Health Metrics',
          'x_field': 'time_bucket',
          'y_field': 'avg_response_time',
          'color_field': 'service_name',
          'title': 'Response Time Trends',
          'description': 'Average response time by service over time',
        },
      },
      {
        'type': 'line_chart',
        'params': {
          'dataset_name': 'System Health Metrics',
          'x_field': 'time_bucket',
          'y_field': 'avg_cpu',
          'color_field': 'service_name',
          'title': 'CPU Usage Trends',
          'description': 'CPU utilization by service over time',
        },
      },
      {
        'type': 'line_chart',
        'params': {
          'dataset_name': 'System Health Metrics',
          'x_field': 'time_bucket',
          'y_field': 'avg_memory',
          'color_field': 'service_name',
          'title': 'Memory Usage Trends',
          'description': 'Memory utilization by service over time',
        },
      },
      {
        'type': 'histogram',
        'params': {
          'dataset_name': 'Performance Trends',
          'value_field': 'avg_response_time',
          'title': 'Response Time Distribution',
          'bins': 20,
          'color': 'blue',
        },
      },
    ]

    return self._create_widgets(performance_widgets, 'performance')

  def create_error_widgets(self) -> List[Dict[str, Any]]:
    """Create error monitoring widgets.

    Returns:
        List of widget creation results
    """
    print('\n❌ Creating error monitoring widgets...')

    error_widgets = [
      {
        'type': 'line_chart',
        'params': {
          'dataset_name': 'Error Rate Analysis',
          'x_field': 'hour',
          'y_field': 'error_rate_percent',
          'color_field': 'service_name',
          'title': 'Error Rate Trends',
          'description': 'Error rate percentage by service over time',
        },
      },
      {
        'type': 'bar_chart',
        'params': {
          'dataset_name': 'Error Rate Analysis',
          'x_field': 'service_name',
          'y_field': 'error_count',
          'color_field': 'environment',
          'title': 'Error Count by Service',
          'description': 'Total errors by service and environment',
        },
      },
      {
        'type': 'pie_chart',
        'params': {
          'dataset_name': 'Error Rate Analysis',
          'category_field': 'service_name',
          'value_field': 'error_count',
          'title': 'Error Distribution',
          'show_percentages': True,
        },
      },
    ]

    return self._create_widgets(error_widgets, 'error')

  def create_resource_widgets(self) -> List[Dict[str, Any]]:
    """Create resource utilization widgets.

    Returns:
        List of widget creation results
    """
    print('\n💾 Creating resource utilization widgets...')

    resource_widgets = [
      {
        'type': 'scatter_plot',
        'params': {
          'dataset_name': 'Resource Utilization',
          'x_field': 'cpu_utilization_percent',
          'y_field': 'memory_utilization_percent',
          'size_field': 'disk_utilization_percent',
          'color_field': 'environment',
          'title': 'Resource Utilization Matrix',
        },
      },
      {
        'type': 'bar_chart',
        'params': {
          'dataset_name': 'Resource Utilization',
          'x_field': 'node_name',
          'y_field': 'cpu_utilization_percent',
          'title': 'CPU Utilization by Node',
          'color_field': 'environment',
        },
      },
      {
        'type': 'bar_chart',
        'params': {
          'dataset_name': 'Resource Utilization',
          'x_field': 'node_name',
          'y_field': 'memory_utilization_percent',
          'title': 'Memory Utilization by Node',
          'color_field': 'environment',
        },
      },
    ]

    return self._create_widgets(resource_widgets, 'resource')

  def create_sla_widgets(self) -> List[Dict[str, Any]]:
    """Create SLA compliance widgets.

    Returns:
        List of widget creation results
    """
    print('\n📊 Creating SLA compliance widgets...')

    sla_widgets = [
      {
        'type': 'line_chart',
        'params': {
          'dataset_name': 'SLA Compliance',
          'x_field': 'date',
          'y_field': 'performance_sla_percent',
          'color_field': 'service_name',
          'title': 'Performance SLA Trends',
          'description': 'Percentage of requests meeting performance SLA',
        },
      },
      {
        'type': 'line_chart',
        'params': {
          'dataset_name': 'SLA Compliance',
          'x_field': 'date',
          'y_field': 'availability_sla_percent',
          'color_field': 'service_name',
          'title': 'Availability SLA Trends',
          'description': 'Percentage uptime by service',
        },
      },
      {
        'type': 'data_table',
        'params': {
          'dataset_name': 'SLA Compliance',
          'columns': [
            'service_name',
            'environment',
            'performance_sla_percent',
            'availability_sla_percent',
            'sla_status',
          ],
          'title': 'SLA Status Summary',
          'page_size': 15,
          'sortable': True,
        },
      },
    ]

    return self._create_widgets(sla_widgets, 'sla')

  def create_filter_widgets(self) -> List[Dict[str, Any]]:
    """Create filter widgets for interactive monitoring.

    Returns:
        List of widget creation results
    """
    print('\n🔍 Creating filter widgets...')

    filter_widgets = [
      {
        'type': 'dropdown_filter',
        'params': {
          'dataset_name': 'System Health Metrics',
          'filter_field': 'service_name',
          'title': 'Select Services',
          'multi_select': True,
        },
      },
      {
        'type': 'dropdown_filter',
        'params': {
          'dataset_name': 'System Health Metrics',
          'filter_field': 'environment',
          'title': 'Environment',
          'multi_select': True,
          'default_values': ['production'],
        },
      },
      {
        'type': 'date_range_filter',
        'params': {
          'dataset_name': 'System Health Metrics',
          'date_field': 'time_bucket',
          'title': 'Time Range',
        },
      },
      {
        'type': 'slider_filter',
        'params': {
          'dataset_name': 'Error Rate Analysis',
          'numeric_field': 'error_rate_percent',
          'title': 'Error Rate Threshold (%)',
          'min_value': 0,
          'max_value': 10,
          'step': 0.1,
          'default_value': 5.0,
        },
      },
    ]

    return self._create_widgets(filter_widgets, 'filter')

  def _create_widgets(
    self, widget_configs: List[Dict], widget_category: str
  ) -> List[Dict[str, Any]]:
    """Helper method to create widgets from configurations.

    Args:
        widget_configs: List of widget configurations
        widget_category: Category name for logging

    Returns:
        List of widget creation results
    """
    results = []

    for widget_config in widget_configs:
      widget_type = widget_config['type']
      params = widget_config['params']

      print(f'   Creating {widget_type}: {params.get("title", "Untitled")}')

      # Import and call the appropriate tool
      try:
        if widget_type == 'counter_widget':
          from server.tools.dashboards import create_counter_widget

          widget_result = create_counter_widget(**params)
        elif widget_type == 'line_chart':
          from server.tools.dashboards import create_line_chart

          widget_result = create_line_chart(**params)
        elif widget_type == 'bar_chart':
          from server.tools.dashboards import create_bar_chart

          widget_result = create_bar_chart(**params)
        elif widget_type == 'pie_chart':
          from server.tools.dashboards import create_pie_chart

          widget_result = create_pie_chart(**params)
        elif widget_type == 'scatter_plot':
          from server.tools.dashboards import create_scatter_plot

          widget_result = create_scatter_plot(**params)
        elif widget_type == 'histogram':
          from server.tools.dashboards import create_histogram

          widget_result = create_histogram(**params)
        elif widget_type == 'data_table':
          from server.tools.dashboards import create_data_table

          widget_result = create_data_table(**params)
        elif widget_type == 'text_widget':
          from server.tools.dashboards import create_text_widget

          widget_result = create_text_widget(**params)
        elif widget_type == 'dropdown_filter':
          from server.tools.dashboards import create_dropdown_filter

          widget_result = create_dropdown_filter(**params)
        elif widget_type == 'date_range_filter':
          from server.tools.dashboards import create_date_range_filter

          widget_result = create_date_range_filter(**params)
        elif widget_type == 'slider_filter':
          from server.tools.dashboards import create_slider_filter

          widget_result = create_slider_filter(**params)
        else:
          print(f'   ❌ Unknown widget type: {widget_type}')
          continue

        # Add to dashboard
        if widget_result['success']:
          add_result = add_widget_to_dashboard(
            dashboard_id=self.dashboard_id, widget_spec=widget_result['widget_spec']
          )

          if add_result['success']:
            self.widgets.append(add_result)
            print(
              f'   ✅ {widget_category.title()} widget added: {params.get("title", "Untitled")}'
            )
            results.append(add_result)
          else:
            print(f'   ❌ Failed to add widget: {add_result["error"]}')
        else:
          print(f'   ❌ Widget creation failed: {widget_result["error"]}')

      except Exception as e:
        print(f'   ❌ Error creating {widget_type}: {str(e)}')

    return results

  def apply_layout(self) -> Dict[str, Any]:
    """Apply automatic layout optimized for monitoring dashboards.

    Returns:
        Layout application result
    """
    print('\n🎨 Applying monitoring-optimized layout...')

    layout_result = auto_layout_dashboard(
      dashboard_id=self.dashboard_id,
      layout_type='masonry',  # Better for mixed widget sizes in monitoring
    )

    if layout_result['success']:
      print(f'✅ Masonry layout applied to {layout_result["widgets_arranged"]} widgets')
    else:
      print(f'❌ Layout application failed: {layout_result["error"]}')

    return layout_result

  def generate_summary(self) -> Dict[str, Any]:
    """Generate a summary of the monitoring dashboard.

    Returns:
        Dashboard summary information
    """
    summary = {
      'dashboard_id': self.dashboard_id,
      'total_widgets': len(self.widgets),
      'datasets_created': len(self.datasets),
      'widget_categories': {},
      'monitoring_features': {
        'real_time_metrics': True,
        'error_tracking': True,
        'resource_monitoring': True,
        'sla_compliance': True,
        'interactive_filters': True,
      },
      'success': True,
    }

    # Analyze widget types
    for widget in self.widgets:
      widget_type = widget.get('widget_type', 'unknown')
      if widget_type not in summary['widget_categories']:
        summary['widget_categories'][widget_type] = 0
      summary['widget_categories'][widget_type] += 1

    print('\n📋 Monitoring Dashboard Summary:')
    print(f'   Dashboard ID: {summary["dashboard_id"]}')
    print(f'   Total Widgets: {summary["total_widgets"]}')
    print(f'   Datasets Created: {summary["datasets_created"]}')
    print('   Monitoring Features:')
    for feature, enabled in summary['monitoring_features'].items():
      status = '✅' if enabled else '❌'
      print(f'     {status} {feature.replace("_", " ").title()}')
    print('   Widget Categories:')
    for category, count in summary['widget_categories'].items():
      print(f'     - {category}: {count}')

    return summary


def main():
  """Main execution function for monitoring dashboard creation."""
  # Get warehouse ID from environment or command line
  warehouse_id = os.getenv('DATABRICKS_SQL_WAREHOUSE_ID')

  if not warehouse_id:
    if len(sys.argv) > 1:
      warehouse_id = sys.argv[1]
    else:
      print('❌ Error: SQL Warehouse ID required')
      print('   Set DATABRICKS_SQL_WAREHOUSE_ID environment variable')
      print('   Or provide as command line argument:')
      print('   python create_monitoring_dashboard.py <warehouse-id>')
      sys.exit(1)

  print('🚀 Starting System Monitoring Dashboard Creation')
  print(f'   Using SQL Warehouse: {warehouse_id}')
  print(f'   Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
  print('=' * 60)

  try:
    # Create monitoring dashboard builder
    builder = MonitoringDashboardBuilder(warehouse_id)

    # Execute build steps
    builder.create_dashboard()
    builder.create_datasets()

    # Create widgets in logical groups
    builder.create_alert_widgets()
    builder.create_performance_widgets()
    builder.create_error_widgets()
    builder.create_resource_widgets()
    builder.create_sla_widgets()
    builder.create_filter_widgets()

    # Apply layout optimized for monitoring
    builder.apply_layout()

    # Generate summary
    summary = builder.generate_summary()

    print('\n🎉 Monitoring Dashboard created successfully!')
    print(f'   Dashboard URL: [Your Databricks workspace]/dashboards/{summary["dashboard_id"]}')
    print(f'   Total widgets: {summary["total_widgets"]}')
    print(f'   Monitoring datasets: {summary["datasets_created"]}')
    print('\n💡 Next Steps:')
    print('   1. Configure alert thresholds in your monitoring system')
    print('   2. Set up automated refresh intervals for real-time data')
    print('   3. Configure dashboard sharing for your ops team')
    print('   4. Set up alerting rules based on the metrics')

    return summary

  except Exception as e:
    print(f'\n❌ Monitoring dashboard creation failed: {str(e)}')
    import traceback

    traceback.print_exc()
    sys.exit(1)


if __name__ == '__main__':
  main()
