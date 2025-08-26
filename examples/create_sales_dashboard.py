#!/usr/bin/env python3
"""
End-to-end example: Create a comprehensive sales analytics dashboard.

This script demonstrates the complete workflow for building a sales dashboard
with multiple widget types, filters, and automatic layout.

Requirements:
- Databricks workspace with sample sales data
- SQL warehouse configured
- Appropriate permissions for dashboard creation
"""

import os
import sys
from typing import List, Dict, Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from server.tools.dashboards import (
    create_lakeview_dashboard,
    create_dashboard_dataset,
    test_dataset_query,
    add_widget_to_dashboard,
    auto_layout_dashboard
)


class SalesDashboardBuilder:
    """Builder class for creating a comprehensive sales analytics dashboard."""

    def __init__(self, warehouse_id: str):
        """Initialize the dashboard builder.
        
        Args:
            warehouse_id: Databricks SQL warehouse ID for query execution
        """
        self.warehouse_id = warehouse_id
        self.dashboard_id = None
        self.datasets = {}
        self.widgets = []
        
    def create_dashboard(self) -> Dict[str, Any]:
        """Create the main dashboard container.
        
        Returns:
            Dashboard creation result
        """
        print("🏗️  Creating Sales Analytics Dashboard...")
        
        dashboard_config = {
            'name': 'Sales Analytics Dashboard',
            'description': 'Comprehensive sales performance analysis with KPIs, trends, and breakdowns',
            'tags': ['sales', 'analytics', 'performance', 'kpi']
        }
        
        result = create_lakeview_dashboard(dashboard_config)
        
        if result['success']:
            self.dashboard_id = result['dashboard_id']
            print(f"✅ Dashboard created successfully: {self.dashboard_id}")
            print(f"   Name: {result['name']}")
            print(f"   Type: {result['type']}")
        else:
            print(f"❌ Dashboard creation failed: {result['error']}")
            raise Exception("Dashboard creation failed")
            
        return result
    
    def create_datasets(self) -> Dict[str, Any]:
        """Create all necessary datasets for the dashboard.
        
        Returns:
            Results of dataset creation operations
        """
        print("\n📊 Creating datasets...")
        
        # Dataset definitions
        datasets_config = [
            {
                'name': 'Daily Sales Summary',
                'query': '''
                    SELECT 
                        DATE(order_date) as date,
                        region,
                        product_category,
                        SUM(revenue) as total_revenue,
                        SUM(quantity) as total_quantity,
                        COUNT(DISTINCT customer_id) as unique_customers,
                        AVG(revenue) as avg_order_value
                    FROM sales_transactions 
                    WHERE order_date >= CURRENT_DATE - INTERVAL 90 DAYS
                    GROUP BY DATE(order_date), region, product_category
                    ORDER BY date DESC
                ''',
                'description': 'Daily aggregated sales data with regional and product breakdowns'
            },
            {
                'name': 'Regional Performance',
                'query': '''
                    SELECT 
                        region,
                        SUM(revenue) as total_revenue,
                        COUNT(*) as total_orders,
                        AVG(revenue) as avg_order_value,
                        COUNT(DISTINCT customer_id) as unique_customers,
                        MAX(order_date) as last_order_date
                    FROM sales_transactions
                    WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAYS
                    GROUP BY region
                    ORDER BY total_revenue DESC
                ''',
                'description': 'Regional sales performance summary'
            },
            {
                'name': 'Product Performance',
                'query': '''
                    SELECT 
                        product_category,
                        product_name,
                        SUM(revenue) as total_revenue,
                        SUM(quantity) as total_quantity,
                        AVG(revenue/quantity) as avg_unit_price,
                        COUNT(DISTINCT customer_id) as unique_customers
                    FROM sales_transactions
                    WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAYS
                    GROUP BY product_category, product_name
                    ORDER BY total_revenue DESC
                    LIMIT 50
                ''',
                'description': 'Top performing products and categories'
            },
            {
                'name': 'Customer Segments',
                'query': '''
                    WITH customer_metrics AS (
                        SELECT 
                            customer_id,
                            COUNT(*) as order_count,
                            SUM(revenue) as total_spent,
                            AVG(revenue) as avg_order_value,
                            MAX(order_date) as last_order_date,
                            MIN(order_date) as first_order_date
                        FROM sales_transactions
                        GROUP BY customer_id
                    )
                    SELECT 
                        CASE 
                            WHEN total_spent >= 1000 AND order_count >= 10 THEN 'VIP'
                            WHEN total_spent >= 500 AND order_count >= 5 THEN 'Premium'
                            WHEN total_spent >= 100 AND order_count >= 2 THEN 'Regular'
                            ELSE 'New'
                        END as customer_segment,
                        COUNT(*) as customer_count,
                        AVG(total_spent) as avg_total_spent,
                        AVG(order_count) as avg_order_count,
                        AVG(avg_order_value) as avg_order_value
                    FROM customer_metrics
                    GROUP BY 1
                    ORDER BY customer_count DESC
                ''',
                'description': 'Customer segmentation analysis'
            }
        ]
        
        results = {}
        
        for dataset_config in datasets_config:
            print(f"   Creating dataset: {dataset_config['name']}")
            
            # Test the query first
            test_result = test_dataset_query(
                query=dataset_config['query'],
                warehouse_id=self.warehouse_id,
                limit=10
            )
            
            if not test_result['success']:
                print(f"   ⚠️  Query test failed: {test_result['error']}")
                continue
                
            print(f"   ✓ Query validated ({test_result['row_count']} rows)")
            
            # Create the dataset
            dataset_result = create_dashboard_dataset(
                dashboard_id=self.dashboard_id,
                name=dataset_config['name'],
                query=dataset_config['query'],
                warehouse_id=self.warehouse_id
            )
            
            if dataset_result['success']:
                self.datasets[dataset_config['name']] = dataset_result
                print(f"   ✅ Dataset created: {dataset_result['dataset_id']}")
            else:
                print(f"   ❌ Dataset creation failed: {dataset_result['error']}")
            
            results[dataset_config['name']] = dataset_result
        
        return results
    
    def create_kpi_widgets(self) -> List[Dict[str, Any]]:
        """Create KPI counter widgets for key metrics.
        
        Returns:
            List of widget creation results
        """
        print("\n📈 Creating KPI widgets...")
        
        kpi_widgets = [
            {
                'type': 'counter_widget',
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'value_field': 'total_revenue',
                    'aggregation': 'sum',
                    'title': 'Total Revenue (90 days)',
                    'format_type': 'currency',
                    'color': 'green'
                }
            },
            {
                'type': 'counter_widget', 
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'value_field': 'total_quantity',
                    'aggregation': 'sum',
                    'title': 'Units Sold (90 days)',
                    'format_type': 'number',
                    'color': 'blue'
                }
            },
            {
                'type': 'counter_widget',
                'params': {
                    'dataset_name': 'Daily Sales Summary', 
                    'value_field': 'unique_customers',
                    'aggregation': 'sum',
                    'title': 'Active Customers (90 days)',
                    'format_type': 'number',
                    'color': 'purple'
                }
            },
            {
                'type': 'counter_widget',
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'value_field': 'avg_order_value',
                    'aggregation': 'avg',
                    'title': 'Avg Order Value',
                    'format_type': 'currency',
                    'color': 'orange'
                }
            }
        ]
        
        results = []
        for widget_config in kpi_widgets:
            print(f"   Creating: {widget_config['params']['title']}")
            
            # Import and call the appropriate tool
            if widget_config['type'] == 'counter_widget':
                from server.tools.dashboards import create_counter_widget
                widget_result = create_counter_widget(**widget_config['params'])
            
            # Add to dashboard
            if widget_result['success']:
                add_result = add_widget_to_dashboard(
                    dashboard_id=self.dashboard_id,
                    widget_spec=widget_result['widget_spec']
                )
                
                if add_result['success']:
                    self.widgets.append(add_result)
                    print(f"   ✅ KPI widget added: {widget_config['params']['title']}")
                    results.append(add_result)
                else:
                    print(f"   ❌ Failed to add widget: {add_result['error']}")
            else:
                print(f"   ❌ Widget creation failed: {widget_result['error']}")
        
        return results
    
    def create_chart_widgets(self) -> List[Dict[str, Any]]:
        """Create chart widgets for trend analysis.
        
        Returns:
            List of widget creation results
        """
        print("\n📊 Creating chart widgets...")
        
        chart_widgets = [
            {
                'type': 'line_chart',
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'x_field': 'date',
                    'y_field': 'total_revenue',
                    'color_field': 'region',
                    'title': 'Revenue Trend by Region',
                    'description': '90-day revenue trend broken down by region'
                }
            },
            {
                'type': 'bar_chart',
                'params': {
                    'dataset_name': 'Regional Performance',
                    'x_field': 'region',
                    'y_field': 'total_revenue',
                    'title': 'Revenue by Region (30 days)',
                    'color_field': 'region'
                }
            },
            {
                'type': 'pie_chart',
                'params': {
                    'dataset_name': 'Product Performance',
                    'category_field': 'product_category',
                    'value_field': 'total_revenue',
                    'title': 'Revenue by Product Category',
                    'show_percentages': True
                }
            },
            {
                'type': 'scatter_plot',
                'params': {
                    'dataset_name': 'Regional Performance',
                    'x_field': 'total_orders',
                    'y_field': 'total_revenue',
                    'size_field': 'unique_customers',
                    'color_field': 'region',
                    'title': 'Orders vs Revenue by Region'
                }
            }
        ]
        
        results = []
        for widget_config in chart_widgets:
            print(f"   Creating: {widget_config['params']['title']}")
            
            # Import and call the appropriate tool
            if widget_config['type'] == 'line_chart':
                from server.tools.dashboards import create_line_chart
                widget_result = create_line_chart(**widget_config['params'])
            elif widget_config['type'] == 'bar_chart':
                from server.tools.dashboards import create_bar_chart
                widget_result = create_bar_chart(**widget_config['params'])
            elif widget_config['type'] == 'pie_chart':
                from server.tools.dashboards import create_pie_chart
                widget_result = create_pie_chart(**widget_config['params'])
            elif widget_config['type'] == 'scatter_plot':
                from server.tools.dashboards import create_scatter_plot
                widget_result = create_scatter_plot(**widget_config['params'])
            
            # Add to dashboard
            if widget_result['success']:
                add_result = add_widget_to_dashboard(
                    dashboard_id=self.dashboard_id,
                    widget_spec=widget_result['widget_spec']
                )
                
                if add_result['success']:
                    self.widgets.append(add_result)
                    print(f"   ✅ Chart widget added: {widget_config['params']['title']}")
                    results.append(add_result)
                else:
                    print(f"   ❌ Failed to add widget: {add_result['error']}")
            else:
                print(f"   ❌ Widget creation failed: {widget_result['error']}")
        
        return results
    
    def create_table_widgets(self) -> List[Dict[str, Any]]:
        """Create data table widgets for detailed views.
        
        Returns:
            List of widget creation results
        """
        print("\n📋 Creating table widgets...")
        
        table_widgets = [
            {
                'type': 'data_table',
                'params': {
                    'dataset_name': 'Product Performance',
                    'columns': ['product_category', 'product_name', 'total_revenue', 'total_quantity', 'unique_customers'],
                    'title': 'Top Products Performance',
                    'page_size': 20,
                    'sortable': True,
                    'searchable': True
                }
            },
            {
                'type': 'pivot_table',
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'row_fields': ['region'],
                    'column_fields': ['product_category'],
                    'value_fields': ['total_revenue'],
                    'aggregations': {'total_revenue': 'sum'},
                    'title': 'Revenue Pivot: Region vs Product Category'
                }
            }
        ]
        
        results = []
        for widget_config in table_widgets:
            print(f"   Creating: {widget_config['params']['title']}")
            
            # Import and call the appropriate tool
            if widget_config['type'] == 'data_table':
                from server.tools.dashboards import create_data_table
                widget_result = create_data_table(**widget_config['params'])
            elif widget_config['type'] == 'pivot_table':
                from server.tools.dashboards import create_pivot_table
                widget_result = create_pivot_table(**widget_config['params'])
            
            # Add to dashboard
            if widget_result['success']:
                add_result = add_widget_to_dashboard(
                    dashboard_id=self.dashboard_id,
                    widget_spec=widget_result['widget_spec']
                )
                
                if add_result['success']:
                    self.widgets.append(add_result)
                    print(f"   ✅ Table widget added: {widget_config['params']['title']}")
                    results.append(add_result)
                else:
                    print(f"   ❌ Failed to add widget: {add_result['error']}")
            else:
                print(f"   ❌ Widget creation failed: {widget_result['error']}")
        
        return results
    
    def create_filter_widgets(self) -> List[Dict[str, Any]]:
        """Create filter widgets for interactive analysis.
        
        Returns:
            List of widget creation results
        """
        print("\n🔍 Creating filter widgets...")
        
        filter_widgets = [
            {
                'type': 'dropdown_filter',
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'filter_field': 'region',
                    'title': 'Select Region',
                    'multi_select': True,
                    'default_values': ['North', 'South', 'East', 'West']
                }
            },
            {
                'type': 'date_range_filter',
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'date_field': 'date',
                    'title': 'Date Range',
                    'default_range': {
                        'start': '2024-01-01',
                        'end': '2024-12-31'
                    }
                }
            },
            {
                'type': 'dropdown_filter',
                'params': {
                    'dataset_name': 'Daily Sales Summary',
                    'filter_field': 'product_category',
                    'title': 'Product Category',
                    'multi_select': True
                }
            }
        ]
        
        results = []
        for widget_config in filter_widgets:
            print(f"   Creating: {widget_config['params']['title']}")
            
            # Import and call the appropriate tool
            if widget_config['type'] == 'dropdown_filter':
                from server.tools.dashboards import create_dropdown_filter
                widget_result = create_dropdown_filter(**widget_config['params'])
            elif widget_config['type'] == 'date_range_filter':
                from server.tools.dashboards import create_date_range_filter
                widget_result = create_date_range_filter(**widget_config['params'])
            
            # Add to dashboard
            if widget_result['success']:
                add_result = add_widget_to_dashboard(
                    dashboard_id=self.dashboard_id,
                    widget_spec=widget_result['widget_spec']
                )
                
                if add_result['success']:
                    self.widgets.append(add_result)
                    print(f"   ✅ Filter widget added: {widget_config['params']['title']}")
                    results.append(add_result)
                else:
                    print(f"   ❌ Failed to add widget: {add_result['error']}")
            else:
                print(f"   ❌ Widget creation failed: {widget_result['error']}")
        
        return results
    
    def apply_layout(self) -> Dict[str, Any]:
        """Apply automatic layout to organize all widgets.
        
        Returns:
            Layout application result
        """
        print("\n🎨 Applying automatic layout...")
        
        layout_result = auto_layout_dashboard(
            dashboard_id=self.dashboard_id,
            layout_type='grid'
        )
        
        if layout_result['success']:
            print(f"✅ Grid layout applied to {layout_result['widgets_arranged']} widgets")
        else:
            print(f"❌ Layout application failed: {layout_result['error']}")
        
        return layout_result
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the created dashboard.
        
        Returns:
            Dashboard summary information
        """
        summary = {
            'dashboard_id': self.dashboard_id,
            'total_widgets': len(self.widgets),
            'datasets_created': len(self.datasets),
            'widget_types': {},
            'success': True
        }
        
        # Count widget types
        for widget in self.widgets:
            widget_type = widget.get('widget_type', 'unknown')
            summary['widget_types'][widget_type] = summary['widget_types'].get(widget_type, 0) + 1
        
        print("\n📋 Dashboard Creation Summary:")
        print(f"   Dashboard ID: {summary['dashboard_id']}")
        print(f"   Total Widgets: {summary['total_widgets']}")
        print(f"   Datasets Created: {summary['datasets_created']}")
        print("   Widget Types:")
        for widget_type, count in summary['widget_types'].items():
            print(f"     - {widget_type}: {count}")
        
        return summary


def main():
    """Main execution function."""
    # Get warehouse ID from environment or command line
    warehouse_id = os.getenv('DATABRICKS_SQL_WAREHOUSE_ID')
    
    if not warehouse_id:
        if len(sys.argv) > 1:
            warehouse_id = sys.argv[1]
        else:
            print("❌ Error: SQL Warehouse ID required")
            print("   Set DATABRICKS_SQL_WAREHOUSE_ID environment variable")
            print("   Or provide as command line argument:")
            print("   python create_sales_dashboard.py <warehouse-id>")
            sys.exit(1)
    
    print("🚀 Starting Sales Dashboard Creation")
    print(f"   Using SQL Warehouse: {warehouse_id}")
    print("=" * 60)
    
    try:
        # Create dashboard builder
        builder = SalesDashboardBuilder(warehouse_id)
        
        # Execute build steps
        dashboard_result = builder.create_dashboard()
        datasets_result = builder.create_datasets()
        
        # Create widgets in logical order
        kpi_results = builder.create_kpi_widgets()
        chart_results = builder.create_chart_widgets()
        table_results = builder.create_table_widgets()
        filter_results = builder.create_filter_widgets()
        
        # Apply layout
        layout_result = builder.apply_layout()
        
        # Generate summary
        summary = builder.generate_summary()
        
        print("\n🎉 Sales Dashboard created successfully!")
        print(f"   Dashboard URL: [Your Databricks workspace]/dashboards/{summary['dashboard_id']}")
        print(f"   Total widgets: {summary['total_widgets']}")
        print(f"   Datasets: {summary['datasets_created']}")
        
        return summary
        
    except Exception as e:
        print(f"\n❌ Dashboard creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()