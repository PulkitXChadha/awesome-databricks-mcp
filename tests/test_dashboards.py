"""Consolidated dashboard tests following CLAUDE.md simplicity guidelines."""

import tempfile
from unittest.mock import Mock, patch

import pytest

from server.tools.lakeview_dashboard import load_dashboard_tools


class TestDashboardCreation:
    """Test dashboard creation functionality."""

    @pytest.mark.unit
    def test_simple_dashboard_creation(self, mcp_server, mock_env_vars):
        """Test creating a simple dashboard with basic widgets."""
        load_dashboard_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['create_dashboard_file']

        with tempfile.NamedTemporaryFile(suffix='.lvdash.json', delete=False) as temp_file:
            result = tool.fn(
                name='Sales Dashboard',
                warehouse_id='test-warehouse',
                datasets=[{
                    'name': 'Sales Data',
                    'query': 'SELECT month, revenue FROM sales'
                }],
                widgets=[
                    {
                        'type': 'counter',
                        'dataset': 'Sales Data',
                        'config': {
                            'value_field': 'revenue',
                            'title': 'Total Revenue'
                        },
                        'position': {'x': 0, 'y': 0, 'width': 3, 'height': 2}
                    },
                    {
                        'type': 'bar',
                        'dataset': 'Sales Data',
                        'config': {
                            'x_field': 'month',
                            'y_field': 'revenue',
                            'title': 'Monthly Sales'
                        },
                        'position': {'x': 3, 'y': 0, 'width': 9, 'height': 4}
                    }
                ],
                file_path=temp_file.name,
                validate_sql=False
            )

            assert result['success'] is True
            assert 'file_path' in result

    @pytest.mark.unit
    def test_dashboard_with_all_widget_types(self, mcp_server, mock_env_vars):
        """Test creating dashboard with various widget types."""
        load_dashboard_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['create_dashboard_file']

        with tempfile.NamedTemporaryFile(suffix='.lvdash.json', delete=False) as temp_file:
            result = tool.fn(
                name='Analytics Dashboard',
                warehouse_id='test-warehouse',
                datasets=[{
                    'name': 'Analytics Data',
                    'query': 'SELECT product, category, sales, date FROM products'
                }],
                widgets=[
                    {
                        'type': 'counter',
                        'dataset': 'Analytics Data',
                        'config': {'value_field': 'sales', 'title': 'Total Sales'}
                    },
                    {
                        'type': 'table',
                        'dataset': 'Analytics Data',
                        'config': {'columns': ['product', 'sales'], 'title': 'Top Products'}
                    },
                    {
                        'type': 'line',
                        'dataset': 'Analytics Data',
                        'config': {'x_field': 'date', 'y_field': 'sales', 'title': 'Growth Trend'}
                    },
                    {
                        'type': 'pie',
                        'dataset': 'Analytics Data',
                        'config': {'category_field': 'category', 'value_field': 'sales', 'title': 'Category Distribution'}
                    }
                ],
                file_path=temp_file.name,
                validate_sql=False
            )

            assert result['success'] is True
            assert 'file_path' in result

    @pytest.mark.unit
    def test_dashboard_creation_with_validation_disabled(self, mcp_server, mock_env_vars):
        """Test dashboard creation with SQL validation disabled."""
        load_dashboard_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['create_dashboard_file']

        with tempfile.NamedTemporaryFile(suffix='.lvdash.json', delete=False) as temp_file:
            result = tool.fn(
                name='Test Dashboard',
                warehouse_id='test-warehouse',
                datasets=[{
                    'name': 'Test Data',
                    'query': 'SELECT * FROM nonexistent_table'  # This would fail validation
                }],
                widgets=[{
                    'type': 'counter',
                    'dataset': 'Test Data',
                    'config': {'value_field': 'count'}
                }],
                file_path=temp_file.name,
                validate_sql=False  # Disable validation
            )

            assert result['success'] is True
            assert 'file_path' in result


class TestDashboardValidation:
    """Test dashboard validation functionality."""

    @pytest.mark.unit
    def test_validation_disabled_works(self, mcp_server, mock_env_vars):
        """Test that validation can be disabled."""
        load_dashboard_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['create_dashboard_file']

        with tempfile.NamedTemporaryFile(suffix='.lvdash.json', delete=False) as temp_file:
            result = tool.fn(
                name='Test Dashboard',
                warehouse_id='test-warehouse',
                datasets=[{
                    'name': 'Test Data',
                    'query': 'SELECT * FROM any_table'  # This would fail validation if enabled
                }],
                widgets=[{
                    'type': 'counter',
                    'dataset': 'Test Data',
                    'config': {'value_field': 'count'}
                }],
                file_path=temp_file.name,
                validate_sql=False  # Validation disabled
            )

            assert result['success'] is True
            assert 'file_path' in result


class TestWidgetConfiguration:
    """Test widget configuration guide."""

    @pytest.mark.unit
    def test_widget_configuration_guide(self, mcp_server, mock_env_vars):
        """Test getting widget configuration guide."""
        load_dashboard_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['get_widget_configuration_guide']

        result = tool.fn()

        assert 'widget_categories' in result
        assert 'quick_reference' in result
        assert len(result['widget_categories']) > 0

    @pytest.mark.unit
    def test_specific_widget_guide(self, mcp_server, mock_env_vars):
        """Test getting guide for specific widget type."""
        load_dashboard_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['get_widget_configuration_guide']

        result = tool.fn(widget_type='bar')

        assert 'widget_type' in result
        assert result['widget_type'] == 'bar'
        assert 'required_fields' in result
        assert 'optional_fields' in result
        assert 'examples' in result