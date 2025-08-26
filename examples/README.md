# Dashboard Examples

This directory contains comprehensive end-to-end examples demonstrating how to use the Databricks MCP server to create and manage Lakeview dashboards.

## Overview

These examples showcase real-world dashboard creation workflows, from simple analytics dashboards to complex monitoring systems. Each script is fully documented and demonstrates best practices for dashboard development.

## Examples

### 1. Sales Analytics Dashboard (`create_sales_dashboard.py`)

**Purpose**: Create a comprehensive sales analytics dashboard with KPIs, trends, and breakdowns.

**Features**:
- 📊 Multiple chart types (line, bar, pie, scatter)
- 📈 KPI counters for key metrics
- 📋 Data tables and pivot tables
- 🔍 Interactive filters
- 🎨 Automatic grid layout

**Usage**:
```bash
# Using environment variable
export DATABRICKS_SQL_WAREHOUSE_ID="your-warehouse-id"
python create_sales_dashboard.py

# Or with command line argument
python create_sales_dashboard.py your-warehouse-id
```

**Datasets Created**:
- Daily Sales Summary (90-day rolling)
- Regional Performance Analysis
- Product Performance Metrics
- Customer Segmentation Analysis

**Widgets Created**:
- 4 KPI counters (Revenue, Units, Customers, AOV)
- 4 chart visualizations (trend, regional, category, correlation)
- 2 data tables (products, pivot)
- 3 filter widgets (region, date, category)

### 2. System Monitoring Dashboard (`create_monitoring_dashboard.py`)

**Purpose**: Build an operational monitoring dashboard for system health and performance.

**Features**:
- 🚨 Real-time alert monitoring
- ⚡ Performance metrics and trends
- ❌ Error rate tracking
- 💾 Resource utilization monitoring
- 📊 SLA compliance tracking
- 🔍 Advanced filtering capabilities

**Usage**:
```bash
export DATABRICKS_SQL_WAREHOUSE_ID="your-warehouse-id"
python create_monitoring_dashboard.py
```

**Monitoring Areas**:
- System health metrics (CPU, memory, disk)
- Error rate analysis and trends
- Performance trends and percentiles
- Alert status and resolution times
- Resource utilization across nodes
- SLA compliance tracking

**Advanced Features**:
- Masonry layout for mixed widget sizes
- Fallback queries for demo purposes
- Real-time timestamp integration
- Alert threshold documentation

### 3. Dashboard Update Workflow (`update_existing_dashboard.py`)

**Purpose**: Demonstrate how to update and enhance existing dashboards.

**Features**:
- 🔍 Dashboard analysis and recommendations
- 📝 Metadata updates (name, description, tags)
- ➕ Adding new widgets
- 🔄 Updating existing widgets
- 🗑️ Removing obsolete widgets
- 📐 Custom widget positioning
- 🎨 Layout reorganization

**Usage**:
```bash
python update_existing_dashboard.py dashboard-id [warehouse-id]
```

**Update Operations**:
- Analyze existing dashboard structure
- Update dashboard metadata
- Add enhancement widgets
- Modify existing widget properties
- Remove outdated components
- Reorganize layout for better UX
- Generate comprehensive update summary

## Common Prerequisites

### 1. Environment Setup

```bash
# Required environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-access-token"
export DATABRICKS_SQL_WAREHOUSE_ID="your-warehouse-id"
```

### 2. Data Requirements

Each example expects certain data structures. You can:

1. **Use your own data**: Modify the SQL queries to match your schema
2. **Create sample data**: Use the provided sample data generation scripts
3. **Use fallback queries**: Some examples include fallback queries for demo purposes

### 3. Permissions

Ensure your user/token has:
- Dashboard creation and modification permissions
- SQL warehouse access
- Data access for the queries used

## Running the Examples

### Basic Usage

1. **Set up environment**:
   ```bash
   cd /path/to/awesome-databricks-mcp
   export DATABRICKS_SQL_WAREHOUSE_ID="your-warehouse-id"
   ```

2. **Run an example**:
   ```bash
   python examples/create_sales_dashboard.py
   ```

3. **View results**:
   - Check console output for dashboard URL
   - Navigate to your Databricks workspace
   - Find the dashboard in the Dashboards section

### Advanced Usage

For production use, consider:

1. **Customizing queries**: Adapt SQL queries to your data schema
2. **Modifying layouts**: Adjust widget sizes and positions
3. **Adding authentication**: Implement proper authentication flows
4. **Error handling**: Add robust error handling and retries
5. **Logging**: Implement comprehensive logging for debugging

## Example Data Structures

### Sales Data Schema
```sql
CREATE TABLE sales_transactions (
  order_date DATE,
  customer_id STRING,
  region STRING,
  product_category STRING,
  product_name STRING,
  quantity INT,
  revenue DECIMAL(10,2)
);
```

### System Metrics Schema
```sql
CREATE TABLE system_metrics (
  timestamp TIMESTAMP,
  service_name STRING,
  environment STRING,
  cpu_usage_percent DOUBLE,
  memory_usage_percent DOUBLE,
  disk_usage_percent DOUBLE,
  response_time_ms DOUBLE
);
```

## Customization Guide

### 1. Modifying Widget Types

```python
# Instead of bar chart, create line chart
widget_result = create_line_chart(
    dataset_name='your_data',
    x_field='date',
    y_field='value',
    color_field='category'
)
```

### 2. Custom Positioning

```python
# Specify exact widget position
custom_position = {
    'x': 0,      # Grid column (0-11)
    'y': 0,      # Grid row
    'width': 6,  # Width in grid units
    'height': 4  # Height in grid units
}
```

### 3. Adding Filters

```python
# Add interactive dropdown filter
filter_result = create_dropdown_filter(
    dataset_name='your_data',
    filter_field='category',
    title='Category Filter',
    multi_select=True,
    default_values=['Category1', 'Category2']
)
```

## Troubleshooting

### Common Issues

1. **Query Failures**:
   - Verify table names and column names exist
   - Check data access permissions
   - Use the fallback query patterns for testing

2. **Widget Creation Errors**:
   - Ensure field names match your data schema
   - Verify data types are compatible with widget types
   - Check for null values that might cause issues

3. **Layout Problems**:
   - Widgets may overlap if positioned manually
   - Use auto-layout for automatic positioning
   - Check grid boundaries (12 columns max)

### Debug Mode

Add debug logging to any example:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug output
print(f"Debug: Creating widget with params: {widget_params}")
```

### Performance Tips

1. **Limit query results**: Use LIMIT clauses for large datasets
2. **Optimize joins**: Avoid complex joins in widget queries  
3. **Cache datasets**: Reuse datasets across multiple widgets
4. **Batch operations**: Group widget additions for efficiency

## Contributing

When adding new examples:

1. **Follow the pattern**: Use the same structure as existing examples
2. **Document thoroughly**: Include comprehensive docstrings and comments
3. **Handle errors**: Implement proper error handling and user feedback
4. **Test thoroughly**: Verify examples work with different data scenarios
5. **Update README**: Add documentation for new examples

## Support

For questions about these examples:

1. Check the main project README for setup instructions
2. Review the API documentation in `docs/`
3. Look at the test files in `tests/` for additional patterns
4. Open an issue in the GitHub repository

## License

These examples are provided under the same license as the main project. See the LICENSE file for details.