"""Simplified integration tests following CLAUDE.md guidelines."""

import pytest

from server.tools import load_tools


class TestToolIntegration:
    """Test tool loading and integration."""

    @pytest.mark.integration
    def test_all_tools_load_without_errors(self, mcp_server, mock_env_vars):
        """Test that all tools load without errors."""
        # This should not raise any exceptions
        load_tools(mcp_server)

        # Verify tools were loaded
        tools = mcp_server._tool_manager._tools
        assert len(tools) > 0

        # Check that key tool categories are present
        tool_names = list(tools.keys())
        assert 'health' in tool_names  # Core tools
        assert 'describe_uc_catalog' in tool_names  # Unity Catalog tools
        assert 'list_warehouses' in tool_names  # SQL tools
        assert 'list_jobs' in tool_names  # Jobs tools
        assert 'create_dashboard_file' in tool_names  # Dashboard tools

    @pytest.mark.integration
    def test_health_tool_works(self, mcp_server, mock_env_vars):
        """Test that health tool works without external dependencies."""
        load_tools(mcp_server)
        
        health_tool = mcp_server._tool_manager._tools['health']
        result = health_tool.fn()

        assert result['status'] == 'healthy'
        assert result['service'] == 'databricks-mcp'
        assert 'databricks_configured' in result

    @pytest.mark.integration
    def test_tool_registration_consistency(self, mcp_server, mock_env_vars):
        """Test that tool registration is consistent across loads."""
        # Load tools twice
        load_tools(mcp_server)
        first_tools = mcp_server._tool_manager._tools
        first_count = len(first_tools)

        # Clear and reload
        mcp_server._tool_manager._tools.clear()
        load_tools(mcp_server)
        second_tools = mcp_server._tool_manager._tools
        second_count = len(second_tools)

        # Should have same number of tools
        assert first_count == second_count, 'Tool count should be consistent'

        # Should have same tool names
        first_names = set(first_tools.keys())
        second_names = set(second_tools.keys())
        assert first_names == second_names, 'Tool names should be consistent'

    @pytest.mark.integration
    def test_tools_have_proper_structure(self, mcp_server, mock_env_vars):
        """Test that all tools have proper structure."""
        load_tools(mcp_server)
        
        tools = mcp_server._tool_manager._tools
        
        for tool_name, tool in tools.items():
            # Each tool should have a name
            assert tool.name == tool_name
            
            # Each tool should have a description
            assert tool.description is not None
            assert len(tool.description) > 0
            
            # Each tool should be callable
            assert callable(tool.fn)

    @pytest.mark.integration
    def test_dashboard_tools_integration(self, mcp_server, mock_env_vars):
        """Test dashboard tools integration."""
        load_tools(mcp_server)
        
        # Check dashboard tools are loaded
        tools = mcp_server._tool_manager._tools
        dashboard_tools = [
            'create_dashboard_file',
            'validate_dashboard_sql',
            'get_widget_configuration_guide'
        ]
        
        for tool_name in dashboard_tools:
            assert tool_name in tools, f'Dashboard tool {tool_name} not loaded'
            
            # Test that tool has proper structure
            tool = tools[tool_name]
            assert tool.description is not None
            assert len(tool.description) > 0