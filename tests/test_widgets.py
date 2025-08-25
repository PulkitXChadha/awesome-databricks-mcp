"""Tests for widget creation and management functionality."""

from unittest.mock import Mock, patch

import pytest

from server.models.widget_types import (
  ALL_WIDGET_TYPES,
  WIDGET_CATEGORIES,
  get_default_position,
  get_widget_info,
  validate_position,
  validate_widget_type,
)
from server.tools.widgets import (
  # Management functions
  add_widget_to_dashboard,
  create_bar_chart_widget,
  create_combo_chart_widget,
  # Data widgets
  create_counter_widget,
  create_dashboard_with_widgets,
  create_data_table_widget,
  create_date_range_filter_widget,
  create_delta_counter_widget,
  # Filter widgets
  create_dropdown_filter_widget,
  create_histogram_widget,
  create_iframe_widget,
  create_image_widget,
  create_line_chart_widget,
  # Specialty widgets
  create_map_widget,
  create_pie_chart_widget,
  create_pivot_table_widget,
  create_scatter_plot_widget,
  create_slider_filter_widget,
  create_text_input_filter_widget,
  create_text_widget,
  load_widget_tools,
  remove_widget_from_dashboard,
)

# ============================================================================
# Chart Widget Tests
# ============================================================================


class TestChartWidgets:
  """Tests for chart widget creation functions."""

  def test_create_bar_chart_widget(self):
    """Test bar chart widget creation."""
    widget = create_bar_chart_widget(
      title='Sales by Region',
      x_field='region',
      y_field='sales',
      dataset_query='SELECT region, sales FROM sales_data',
    )

    assert widget['type'] == 'bar_chart'
    assert widget['title'] == 'Sales by Region'
    assert widget['spec']['widgetType'] == 'bar'
    assert 'region' in widget['spec']['encodings']['x']['fieldName']
    assert 'sales' in widget['spec']['encodings']['y']['fieldName']
    assert widget['position']['width'] == 4
    assert widget['position']['height'] == 3

  def test_create_line_chart_widget(self):
    """Test line chart widget creation."""
    widget = create_line_chart_widget(
      title='Revenue Over Time',
      x_field='date',
      y_field='revenue',
      dataset_query='SELECT date, revenue FROM revenue_data',
    )

    assert widget['type'] == 'line_chart'
    assert widget['spec']['widgetType'] == 'line'
    assert widget['spec']['encodings']['x']['type'] == 'temporal'
    assert widget['spec']['encodings']['y']['type'] == 'quantitative'

  def test_create_pie_chart_widget(self):
    """Test pie chart widget creation."""
    widget = create_pie_chart_widget(
      title='Market Share',
      category_field='company',
      value_field='market_share',
      dataset_query='SELECT company, market_share FROM market_data',
    )

    assert widget['type'] == 'pie_chart'
    assert widget['spec']['widgetType'] == 'pie'
    assert 'company' in widget['spec']['encodings']['category']['fieldName']
    assert 'market_share' in widget['spec']['encodings']['value']['fieldName']

  def test_create_scatter_plot_widget(self):
    """Test scatter plot widget creation."""
    widget = create_scatter_plot_widget(
      title='Price vs Quality',
      x_field='price',
      y_field='quality',
      dataset_query='SELECT price, quality FROM product_data',
      size_field='volume',
      color_field='category',
    )

    assert widget['type'] == 'scatter_plot'
    assert widget['spec']['widgetType'] == 'scatter'
    assert 'size' in widget['spec']['encodings']
    assert 'color' in widget['spec']['encodings']

  def test_create_histogram_widget(self):
    """Test histogram widget creation."""
    widget = create_histogram_widget(
      title='Age Distribution',
      value_field='age',
      dataset_query='SELECT age FROM customer_data',
      bins=25,
    )

    assert widget['type'] == 'histogram'
    assert widget['spec']['widgetType'] == 'histogram'
    assert widget['spec']['encodings']['value']['binCount'] == 25

  def test_create_combo_chart_widget(self):
    """Test combo chart widget creation."""
    widget = create_combo_chart_widget(
      title='Sales and Profit',
      x_field='month',
      bar_fields=['sales'],
      line_fields=['profit'],
      dataset_query='SELECT month, sales, profit FROM monthly_data',
    )

    assert widget['type'] == 'combo_chart'
    assert widget['spec']['widgetType'] == 'combo'
    assert 'bar_y_0' in widget['spec']['encodings']
    assert 'line_y_0' in widget['spec']['encodings']
    assert widget['spec']['encodings']['bar_y_0']['chartType'] == 'bar'
    assert widget['spec']['encodings']['line_y_0']['chartType'] == 'line'


# ============================================================================
# Data Widget Tests
# ============================================================================


class TestDataWidgets:
  """Tests for data widget creation functions."""

  def test_create_counter_widget(self):
    """Test counter widget creation."""
    widget = create_counter_widget(
      title='Total Sales',
      value_field='sales',
      dataset_query='SELECT SUM(sales) as sales FROM sales_data',
      aggregation='sum',
    )

    assert widget['type'] == 'counter'
    assert widget['spec']['widgetType'] == 'counter'
    assert widget['spec']['encodings']['value']['aggregation'] == 'sum'
    assert widget['position']['width'] == 2
    assert widget['position']['height'] == 2

  def test_create_delta_counter_widget(self):
    """Test delta counter widget creation."""
    widget = create_delta_counter_widget(
      title='Sales vs Last Month',
      value_field='current_sales',
      comparison_field='previous_sales',
      dataset_query='SELECT current_sales, previous_sales FROM sales_comparison',
    )

    assert widget['type'] == 'delta_counter'
    assert widget['spec']['widgetType'] == 'delta_counter'
    assert 'comparison' in widget['spec']['encodings']

  def test_create_data_table_widget(self):
    """Test data table widget creation."""
    widget = create_data_table_widget(
      title='Customer List',
      columns=['name', 'email', 'signup_date'],
      dataset_query='SELECT name, email, signup_date FROM customers',
      row_limit=50,
    )

    assert widget['type'] == 'data_table'
    assert widget['spec']['widgetType'] == 'table'
    assert len(widget['spec']['columns']) == 3
    assert widget['spec']['rowLimit'] == 50
    assert widget['position']['width'] == 6
    assert widget['position']['height'] == 4

  def test_create_pivot_table_widget(self):
    """Test pivot table widget creation."""
    widget = create_pivot_table_widget(
      title='Sales by Region and Product',
      row_fields=['region'],
      column_fields=['product'],
      value_field='sales',
      dataset_query='SELECT region, product, sales FROM sales_data',
    )

    assert widget['type'] == 'pivot_table'
    assert widget['spec']['widgetType'] == 'pivot'
    assert len(widget['spec']['rows']) == 1
    assert len(widget['spec']['columns']) == 1
    assert widget['spec']['values']['fieldName'] == 'sales'


# ============================================================================
# Filter Widget Tests
# ============================================================================


class TestFilterWidgets:
  """Tests for filter widget creation functions."""

  def test_create_dropdown_filter_widget(self):
    """Test dropdown filter widget creation."""
    widget = create_dropdown_filter_widget(
      title='Region Filter',
      field_name='region',
      dataset_query='SELECT DISTINCT region FROM sales_data',
      multi_select=True,
    )

    assert widget['type'] == 'dropdown_filter'
    assert widget['spec']['widgetType'] == 'filter_dropdown'
    assert widget['spec']['field']['multiSelect'] is True
    assert widget['position']['width'] == 2
    assert widget['position']['height'] == 1

  def test_create_date_range_filter_widget(self):
    """Test date range filter widget creation."""
    widget = create_date_range_filter_widget(
      title='Date Range',
      field_name='order_date',
      dataset_query='SELECT MIN(order_date), MAX(order_date) FROM orders',
      default_start='2024-01-01',
      default_end='2024-12-31',
    )

    assert widget['type'] == 'date_range_filter'
    assert widget['spec']['widgetType'] == 'filter_date_range'
    assert widget['spec']['field']['type'] == 'date'
    assert widget['spec']['field']['defaultRange']['start'] == '2024-01-01'

  def test_create_slider_filter_widget(self):
    """Test slider filter widget creation."""
    widget = create_slider_filter_widget(
      title='Price Range',
      field_name='price',
      dataset_query='SELECT MIN(price), MAX(price) FROM products',
      min_value=0,
      max_value=1000,
      step=10,
    )

    assert widget['type'] == 'slider_filter'
    assert widget['spec']['widgetType'] == 'filter_slider'
    assert widget['spec']['field']['min'] == 0
    assert widget['spec']['field']['max'] == 1000
    assert widget['spec']['field']['step'] == 10

  def test_create_text_input_filter_widget(self):
    """Test text input filter widget creation."""
    widget = create_text_input_filter_widget(
      title='Search Products',
      field_name='product_name',
      dataset_query='SELECT DISTINCT product_name FROM products',
      placeholder='Enter product name...',
    )

    assert widget['type'] == 'text_filter'
    assert widget['spec']['widgetType'] == 'filter_text'
    assert widget['spec']['field']['placeholder'] == 'Enter product name...'


# ============================================================================
# Specialty Widget Tests
# ============================================================================


class TestSpecialtyWidgets:
  """Tests for specialty widget creation functions."""

  def test_create_map_widget(self):
    """Test map widget creation."""
    widget = create_map_widget(
      title='Store Locations',
      latitude_field='lat',
      longitude_field='lon',
      dataset_query='SELECT lat, lon, store_name FROM stores',
      value_field='sales',
      label_field='store_name',
    )

    assert widget['type'] == 'map'
    assert widget['spec']['widgetType'] == 'map'
    assert widget['spec']['encodings']['latitude']['type'] == 'latitude'
    assert widget['spec']['encodings']['longitude']['type'] == 'longitude'
    assert 'value' in widget['spec']['encodings']
    assert 'label' in widget['spec']['encodings']

  def test_create_text_widget(self):
    """Test text widget creation."""
    widget = create_text_widget(
      title='Dashboard Title',
      content='# Sales Dashboard\n\nThis dashboard shows our Q4 sales performance.',
      markdown=True,
    )

    assert widget['type'] == 'text'
    assert widget['spec']['widgetType'] == 'text'
    assert widget['spec']['markdown'] is True
    assert 'Sales Dashboard' in widget['spec']['content']

  def test_create_image_widget(self):
    """Test image widget creation."""
    widget = create_image_widget(
      title='Company Logo', image_url='https://example.com/logo.png', alt_text='Company Logo'
    )

    assert widget['type'] == 'image'
    assert widget['spec']['widgetType'] == 'image'
    assert widget['spec']['url'] == 'https://example.com/logo.png'
    assert widget['spec']['altText'] == 'Company Logo'

  def test_create_iframe_widget(self):
    """Test iframe widget creation."""
    widget = create_iframe_widget(
      title='External Report', embed_url='https://example.com/embed/report'
    )

    assert widget['type'] == 'iframe'
    assert widget['spec']['widgetType'] == 'iframe'
    assert widget['spec']['url'] == 'https://example.com/embed/report'


# ============================================================================
# Widget Management Tests
# ============================================================================


class TestWidgetManagement:
  """Tests for widget management functions."""

  @patch('server.tools.widgets.WorkspaceClient')
  def test_add_widget_to_dashboard(self, mock_client):
    """Test adding widget to dashboard."""
    # Mock the workspace client
    mock_instance = Mock()
    mock_client.return_value = mock_instance

    # Mock dashboard with empty widgets
    mock_dashboard = Mock()
    mock_dashboard.widgets = []
    mock_instance.lakeview.get.return_value = mock_dashboard

    # Create a test widget
    widget = create_bar_chart_widget(
      title='Test Chart', x_field='x', y_field='y', dataset_query='SELECT x, y FROM test'
    )

    # Test adding widget
    result = add_widget_to_dashboard('dashboard_123', widget)

    assert result['success'] is True
    assert 'widget_id' in result
    mock_instance.lakeview.update.assert_called_once()

  @patch('server.tools.widgets.WorkspaceClient')
  def test_remove_widget_from_dashboard(self, mock_client):
    """Test removing widget from dashboard."""
    # Mock the workspace client
    mock_instance = Mock()
    mock_client.return_value = mock_instance

    # Mock dashboard with a widget
    mock_dashboard = Mock()
    mock_dashboard.widgets = [{'id': 'widget_123', 'type': 'bar_chart'}]
    mock_instance.lakeview.get.return_value = mock_dashboard

    # Test removing widget
    result = remove_widget_from_dashboard('dashboard_123', 'widget_123')

    assert result['success'] is True
    mock_instance.lakeview.update.assert_called_once()

  @patch('server.tools.widgets.WorkspaceClient')
  def test_create_dashboard_with_widgets(self, mock_client):
    """Test creating dashboard with multiple widgets."""
    # Mock the workspace client
    mock_instance = Mock()
    mock_client.return_value = mock_instance

    # Mock dashboard creation
    mock_dashboard = Mock()
    mock_dashboard.dashboard_id = 'new_dashboard_123'
    mock_instance.lakeview.create.return_value = mock_dashboard

    # Create test widgets
    widgets = [
      create_bar_chart_widget('Chart 1', 'x', 'y', 'SELECT x, y FROM test1'),
      create_counter_widget('Counter 1', 'count', 'SELECT COUNT(*) FROM test2'),
    ]

    # Test dashboard creation
    result = create_dashboard_with_widgets('Test Dashboard', 'A test dashboard', widgets)

    assert result['success'] is True
    assert result['dashboard_id'] == 'new_dashboard_123'
    assert result['widget_count'] == 2
    mock_instance.lakeview.create.assert_called_once()


# ============================================================================
# Widget Type Tests
# ============================================================================


class TestWidgetTypes:
  """Tests for widget type definitions and validation."""

  def test_validate_widget_type(self):
    """Test widget type validation."""
    assert validate_widget_type('bar_chart') is True
    assert validate_widget_type('counter') is True
    assert validate_widget_type('invalid_type') is False

  def test_validate_position(self):
    """Test position validation."""
    valid_position = {'x': 0, 'y': 0, 'width': 4, 'height': 3}
    invalid_position = {'x': 0, 'y': 0}

    assert validate_position(valid_position) is True
    assert validate_position(invalid_position) is False

  def test_get_widget_info(self):
    """Test getting widget information."""
    info = get_widget_info('bar_chart')
    assert info is not None
    assert info['name'] == 'Bar Chart'
    assert 'required_fields' in info

    assert get_widget_info('invalid_type') is None

  def test_get_default_position(self):
    """Test getting default position."""
    position = get_default_position('bar_chart')
    assert 'x' in position
    assert 'y' in position
    assert 'width' in position
    assert 'height' in position

  def test_all_widget_types_covered(self):
    """Test that all widget types are properly defined."""
    expected_types = [
      # Chart widgets
      'bar_chart',
      'line_chart',
      'area_chart',
      'pie_chart',
      'scatter_plot',
      'histogram',
      'combo_chart',
      # Data widgets
      'counter',
      'delta_counter',
      'data_table',
      'pivot_table',
      # Filter widgets
      'dropdown_filter',
      'date_range_filter',
      'slider_filter',
      'text_input_filter',
      # Specialty widgets
      'map',
      'text',
      'image',
      'iframe',
    ]

    for widget_type in expected_types:
      assert widget_type in ALL_WIDGET_TYPES

  def test_widget_categories(self):
    """Test widget categories are properly defined."""
    assert 'chart' in WIDGET_CATEGORIES
    assert 'data' in WIDGET_CATEGORIES
    assert 'filter' in WIDGET_CATEGORIES
    assert 'specialty' in WIDGET_CATEGORIES

    # Test that all widget types are in some category
    all_categorized = []
    for category in WIDGET_CATEGORIES.values():
      all_categorized.extend(category['types'])

    assert len(all_categorized) == len(ALL_WIDGET_TYPES)


# ============================================================================
# MCP Tool Registration Tests
# ============================================================================


class TestMCPToolRegistration:
  """Tests for MCP tool registration."""

  def test_load_widget_tools(self):
    """Test loading widget tools into MCP server."""
    mock_server = Mock()
    mock_server.tool = Mock(side_effect=lambda func: func)

    # Load widget tools
    load_widget_tools(mock_server)

    # Verify that tools were registered
    assert mock_server.tool.call_count > 0

  def test_mcp_tool_functions_exist(self):
    """Test that MCP tool wrapper functions are created."""
    mock_server = Mock()
    mock_server.tool = Mock(side_effect=lambda func: func)

    # This should not raise any errors
    load_widget_tools(mock_server)


# ============================================================================
# Integration Tests
# ============================================================================


class TestWidgetIntegration:
  """Integration tests for widget functionality."""

  def test_widget_creation_workflow(self):
    """Test complete widget creation workflow."""
    # Step 1: Create various widgets
    bar_chart = create_bar_chart_widget(
      'Sales by Region', 'region', 'sales', 'SELECT region, sales FROM sales_data'
    )

    counter = create_counter_widget(
      'Total Revenue', 'revenue', 'SELECT SUM(revenue) as revenue FROM sales_data'
    )

    filter_widget = create_dropdown_filter_widget(
      'Region Filter', 'region', 'SELECT DISTINCT region FROM sales_data'
    )

    # Step 2: Verify widget structures
    widgets = [bar_chart, counter, filter_widget]
    for widget in widgets:
      assert 'id' in widget
      assert 'type' in widget
      assert 'title' in widget
      assert 'spec' in widget
      assert 'position' in widget

    # Step 3: Verify different widget types
    assert bar_chart['type'] == 'bar_chart'
    assert counter['type'] == 'counter'
    assert filter_widget['type'] == 'dropdown_filter'

  def test_custom_positioning(self):
    """Test widgets with custom positioning."""
    custom_position = {'x': 2, 'y': 1, 'width': 6, 'height': 4}

    widget = create_data_table_widget(
      'Custom Table', ['col1', 'col2'], 'SELECT col1, col2 FROM table', position=custom_position
    )

    assert widget['position'] == custom_position

  def test_widget_field_validation(self):
    """Test that widgets handle field validation properly."""
    # This should work fine
    widget = create_pie_chart_widget(
      'Test Pie', 'category', 'value', 'SELECT category, value FROM data'
    )
    assert widget is not None

    # Test with empty fields (should still work but might have empty encodings)
    widget2 = create_scatter_plot_widget('Test Scatter', 'x', 'y', 'SELECT x, y FROM data')
    assert widget2 is not None
    assert len(widget2['spec']['encodings']) == 2  # x and y only


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestWidgetErrorHandling:
  """Tests for widget error handling."""

  @patch('server.tools.widgets.WorkspaceClient')
  def test_dashboard_api_error(self, mock_client):
    """Test handling of API errors."""
    # Mock client that raises an exception
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    mock_instance.lakeview.get.side_effect = Exception('API Error')

    widget = create_bar_chart_widget('Test', 'x', 'y', 'SELECT x, y FROM test')
    result = add_widget_to_dashboard('dashboard_123', widget)

    assert result['success'] is False
    assert 'error' in result

  def test_invalid_widget_positions(self):
    """Test handling of invalid positions."""
    # Positions should be created properly even if not explicitly validated
    widget = create_bar_chart_widget(
      'Test Chart',
      'x',
      'y',
      'SELECT x, y FROM test',
      position={'x': -1, 'y': -1, 'width': 0, 'height': 0},
    )

    # Widget should still be created with the invalid position
    assert widget['position']['x'] == -1
    assert widget['position']['width'] == 0



class TestAdvancedWidgetMCPTools:
  """Tests for advanced widget MCP tools in dashboard module."""

  @pytest.mark.unit
  def test_create_scatter_plot_mcp_tool(self, mcp_server, mock_env_vars):
    """Test scatter plot MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_scatter_plot']
      result = tool.fn(
        dataset_name='sales_data',
        x_field='price',
        y_field='quantity'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'scatter_plot'

  @pytest.mark.unit
  def test_create_histogram_mcp_tool(self, mcp_server, mock_env_vars):
    """Test histogram MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_histogram']
      result = tool.fn(
        dataset_name='user_data',
        value_field='age'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'histogram'

  @pytest.mark.unit
  def test_create_combo_chart_mcp_tool(self, mcp_server, mock_env_vars):
    """Test combo chart MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_combo_chart']
      result = tool.fn(
        dataset_name='revenue_data',
        x_field='month',
        bar_field='revenue',
        line_field='growth_rate'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'combo_chart'

  @pytest.mark.unit
  def test_create_pivot_table_mcp_tool(self, mcp_server, mock_env_vars):
    """Test pivot table MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_pivot_table']
      result = tool.fn(
        dataset_name='sales_data',
        row_fields=['region'],
        column_fields=['quarter'],
        value_fields=['revenue']
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'pivot_table'

  @pytest.mark.unit
  def test_create_delta_counter_mcp_tool(self, mcp_server, mock_env_vars):
    """Test delta counter MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_delta_counter']
      result = tool.fn(
        dataset_name='metrics',
        value_field='current_revenue',
        comparison_field='previous_revenue'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'delta_counter'

  @pytest.mark.unit
  def test_create_slider_filter_mcp_tool(self, mcp_server, mock_env_vars):
    """Test slider filter MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_slider_filter']
      result = tool.fn(
        dataset_name='product_data',
        numeric_field='price'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'slider_filter'

  @pytest.mark.unit
  def test_create_text_filter_mcp_tool(self, mcp_server, mock_env_vars):
    """Test text filter MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_text_filter']
      result = tool.fn(
        dataset_name='customer_data',
        text_field='customer_name'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'text_filter'

  @pytest.mark.unit
  def test_create_map_widget_mcp_tool(self, mcp_server, mock_env_vars):
    """Test map widget MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_map_widget']
      result = tool.fn(
        dataset_name='location_data',
        latitude_field='lat',
        longitude_field='lon'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'map_widget'

  @pytest.mark.unit
  def test_create_text_widget_mcp_tool(self, mcp_server, mock_env_vars):
    """Test text widget MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_text_widget']
      result = tool.fn(
        content='# Dashboard Title\nWelcome to our dashboard'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'text_widget'

  @pytest.mark.unit
  def test_create_image_widget_mcp_tool(self, mcp_server, mock_env_vars):
    """Test image widget MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_image_widget']
      result = tool.fn(
        image_url='https://company.com/logo.png'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'image_widget'

  @pytest.mark.unit
  def test_create_iframe_widget_mcp_tool(self, mcp_server, mock_env_vars):
    """Test iframe widget MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['create_iframe_widget']
      result = tool.fn(
        iframe_url='https://example.com/embedded-report'
      )
      
      assert_success_response(result)
      assert 'widget_spec' in result
      assert result['widget_spec']['type'] == 'iframe_widget'

  @pytest.mark.unit
  def test_auto_layout_dashboard_mcp_tool(self, mcp_server, mock_env_vars):
    """Test auto layout dashboard MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      
      # Mock dashboard with widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget1', 'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4}},
        {'widget_id': 'widget2', 'position': {'x': 0, 'y': 4, 'width': 6, 'height': 4}},
      ]
      
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = tool.fn(
        dashboard_id='dashboard-123',
        layout_type='grid'
      )
      
      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['layout_type'] == 'grid'

  @pytest.mark.unit
  def test_reposition_widget_mcp_tool(self, mcp_server, mock_env_vars):
    """Test reposition widget MCP tool."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      
      # Mock dashboard with existing widget
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget1', 'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4}},
      ]
      
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace
      
      tool = mcp_server._tool_manager._tools['reposition_widget']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_id='widget1',
        position={'x': 6, 'y': 0, 'width': 6, 'height': 4}
      )
      
      assert_success_response(result)
      assert result['widget_id'] == 'widget1'

  @pytest.mark.unit
  def test_widgets_module_counter_tool(self, mcp_server, mock_env_vars):
    """Test counter tool from widgets module."""
    load_widget_tools(mcp_server)
    
    tool = mcp_server._tool_manager._tools['create_counter']
    result = tool.fn(
      title='Total Sales',
      value_field='revenue',
      dataset_query='SELECT SUM(revenue) as revenue FROM sales'
    )
    
    # Widgets module tools return widget spec directly
    assert result['type'] == 'counter'
    assert result['title'] == 'Total Sales'
    assert 'id' in result

  @pytest.mark.unit
  def test_widgets_module_date_filter_tool(self, mcp_server, mock_env_vars):
    """Test date filter tool from widgets module."""
    load_widget_tools(mcp_server)
    
    tool = mcp_server._tool_manager._tools['create_date_filter']
    result = tool.fn(
      title='Date Range',
      field_name='order_date',
      dataset_query='SELECT order_date FROM orders'
    )
    
    # Widgets module tools return widget spec directly
    assert result['type'] == 'date_range_filter'
    assert result['title'] == 'Date Range'
    assert 'id' in result

  @pytest.mark.unit
  def test_add_widget_to_lakeview_dashboard_tool(self, mcp_server, mock_env_vars):
    """Test adding widget to Lakeview dashboard tool."""
    from tests.utils import assert_success_response
    
    load_widget_tools(mcp_server)
    
    with patch('server.tools.widgets.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      
      # Mock existing dashboard
      mock_dashboard = Mock()
      mock_dashboard.widgets = []
      
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace
      
      widget_spec = {
        'id': 'test_widget',
        'type': 'bar_chart',
        'title': 'Test Chart'
      }
      
      tool = mcp_server._tool_manager._tools['add_widget_to_lakeview_dashboard']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_spec=widget_spec
      )
      
      assert_success_response(result)
      assert result['widget_id'] == 'test_widget'

  @pytest.mark.unit
  def test_create_lakeview_dashboard_with_widgets_tool(self, mcp_server, mock_env_vars):
    """Test creating Lakeview dashboard with widgets tool."""
    from tests.utils import assert_success_response
    
    load_widget_tools(mcp_server)
    
    with patch('server.tools.widgets.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_workspace.lakeview.create.return_value = Mock(dashboard_id='new-dashboard-456')
      mock_client.return_value = mock_workspace
      
      widgets = [
        {'id': 'widget1', 'type': 'bar_chart', 'title': 'Chart 1'},
        {'id': 'widget2', 'type': 'counter', 'title': 'Counter 1'}
      ]
      
      tool = mcp_server._tool_manager._tools['create_lakeview_dashboard_with_widgets']
      result = tool.fn(
        name='Test Dashboard',
        description='A test dashboard with widgets',
        widgets=widgets
      )
      
      assert_success_response(result)
      assert result['dashboard_id'] == 'new-dashboard-456'


class TestAdvancedWidgetIntegration:
  """Test integration workflows for advanced widget tools."""

  @pytest.mark.unit
  def test_complete_dashboard_creation_workflow(self, mcp_server, mock_env_vars):
    """Test complete workflow with advanced widget tools."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_success_response
    
    load_dashboard_tools(mcp_server)
    load_widget_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_dashboard_client:
      with patch('server.tools.widgets.WorkspaceClient') as mock_widget_client:
        # Mock workspace clients
        mock_dashboard_workspace = Mock()
        mock_widget_workspace = Mock()
        
        mock_dashboard_client.return_value = mock_dashboard_workspace
        mock_widget_client.return_value = mock_widget_workspace
        
        # Mock dashboard creation
        mock_widget_workspace.lakeview.create.return_value = Mock(dashboard_id='new-dashboard-123')
        
        # Step 1: Create widgets using various advanced widget tools
        widgets = [
          {
            'id': 'scatter1',
            'type': 'scatter_plot',
            'title': 'Price vs Quantity Analysis'
          },
          {
            'id': 'map1',
            'type': 'map',
            'title': 'Geographic Distribution'
          }
        ]
        
        # Step 2: Create dashboard with widgets
        dashboard_tool = mcp_server._tool_manager._tools['create_lakeview_dashboard_with_widgets']
        dashboard_result = dashboard_tool.fn(
          name='Analytics Dashboard',
          description='Comprehensive analytics with advanced widgets',
          widgets=widgets
        )
        
        assert_success_response(dashboard_result)
        dashboard_id = dashboard_result['dashboard_id']
        
        # Step 3: Test auto-layout
        mock_dashboard = Mock()
        mock_dashboard.widgets = widgets
        mock_dashboard_workspace.lakeview.get.return_value = mock_dashboard
        
        layout_tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
        layout_result = layout_tool.fn(
          dashboard_id=dashboard_id,
          layout_type='grid'
        )
        
        assert_success_response(layout_result)

  @pytest.mark.unit
  def test_advanced_widget_error_scenarios(self, mcp_server, mock_env_vars):
    """Test error handling in advanced widget tools."""
    from server.tools.dashboards import load_dashboard_tools
    from tests.utils import assert_error_response
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_workspace.lakeview.get.side_effect = Exception('Dashboard not found')
      mock_client.return_value = mock_workspace
      
      # Test layout tool with non-existent dashboard
      layout_tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = layout_tool.fn(dashboard_id='non-existent-dashboard')
      
      assert_error_response(result)

  @pytest.mark.unit  
  def test_all_advanced_widget_tools_available(self, mcp_server, mock_env_vars):
    """Test that all advanced widget tools are properly registered."""
    from server.tools.dashboards import load_dashboard_tools
    
    load_dashboard_tools(mcp_server)
    load_widget_tools(mcp_server)
    
    expected_advanced_tools = [
      'create_scatter_plot', 'create_histogram', 'create_combo_chart',
      'create_pivot_table', 'create_delta_counter', 'create_slider_filter',
      'create_text_filter', 'create_map_widget', 'create_text_widget',
      'create_image_widget', 'create_iframe_widget', 'auto_layout_dashboard',
      'reposition_widget'
    ]
    
    tools = mcp_server._tool_manager._tools
    
    for tool_name in expected_advanced_tools:
      assert tool_name in tools, f"Advanced widget tool '{tool_name}' is not registered"
    
    # Also test widgets module specific tools
    widget_module_tools = [
      'create_counter', 'create_date_filter', 
      'add_widget_to_lakeview_dashboard', 'create_lakeview_dashboard_with_widgets'
    ]
    
    for tool_name in widget_module_tools:
      assert tool_name in tools, f"Widget module tool '{tool_name}' is not registered"


if __name__ == '__main__':
  # Run the tests
  pytest.main([__file__, '-v'])
