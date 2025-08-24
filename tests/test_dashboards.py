"""Test dashboard tools."""
import pytest
from unittest.mock import patch, Mock
from tests.utils import assert_success_response
from server.tools.dashboards import load_dashboard_tools

class TestDashboardTools:
    """Test dashboard operations."""
    
    @pytest.mark.unit
    def test_list_lakeview_dashboards(self, mcp_server, mock_env_vars):
        """Test listing Lakeview dashboards."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            # Mock dashboard listing (placeholder implementation)
            mock_client.return_value = Mock()
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_lakeview_dashboards']
            result = tool.fn()
            
            assert_success_response(result)
            assert result['message'] == 'Lakeview dashboard listing initiated'
            assert result['count'] == 0
            assert 'note' in result
    
    @pytest.mark.unit
    def test_get_lakeview_dashboard(self, mcp_server, mock_env_vars):
        """Test getting specific Lakeview dashboard."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            mock_client.return_value = Mock()
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['get_lakeview_dashboard']
            result = tool.fn(dashboard_id="dashboard-123")
            
            assert_success_response(result)
            assert result['dashboard_id'] == "dashboard-123"
            assert result['message'] == 'Lakeview dashboard dashboard-123 details retrieval initiated'
    
    @pytest.mark.unit
    def test_create_lakeview_dashboard(self, mcp_server, mock_env_vars):
        """Test creating Lakeview dashboard."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            mock_client.return_value = Mock()
            
            dashboard_config = {"name": "Test Dashboard", "description": "Test"}
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
            result = tool.fn(dashboard_config=dashboard_config)
            
            assert_success_response(result)
            assert result['dashboard_config'] == dashboard_config
            assert result['message'] == 'Lakeview dashboard creation initiated'
    
    @pytest.mark.unit
    def test_list_legacy_dashboards(self, mcp_server, mock_env_vars):
        """Test listing legacy dashboards."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            mock_client.return_value = Mock()
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_dashboards']
            result = tool.fn()
            
            assert_success_response(result)
            assert result['message'] == 'Legacy dashboard listing initiated'
            assert result['count'] == 0
    
    @pytest.mark.unit
    def test_update_lakeview_dashboard(self, mcp_server, mock_env_vars):
        """Test updating Lakeview dashboard."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            mock_client.return_value = Mock()
            
            updates = {"name": "Updated Dashboard", "description": "Updated"}
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['update_lakeview_dashboard']
            result = tool.fn(dashboard_id="dashboard-123", updates=updates)
            
            assert_success_response(result)
            assert result['dashboard_id'] == "dashboard-123"
            assert result['updates'] == updates
            assert result['message'] == 'Lakeview dashboard dashboard-123 update initiated'
    
    @pytest.mark.unit
    def test_delete_lakeview_dashboard(self, mcp_server, mock_env_vars):
        """Test deleting Lakeview dashboard."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            mock_client.return_value = Mock()
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['delete_lakeview_dashboard']
            result = tool.fn(dashboard_id="dashboard-123")
            
            assert_success_response(result)
            assert result['dashboard_id'] == "dashboard-123"
            assert result['message'] == 'Lakeview dashboard dashboard-123 deletion initiated'
    
    @pytest.mark.unit
    def test_share_lakeview_dashboard(self, mcp_server, mock_env_vars):
        """Test sharing Lakeview dashboard."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            mock_client.return_value = Mock()
            
            share_config = {"users": ["user1@example.com"], "permission": "READ"}
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['share_lakeview_dashboard']
            result = tool.fn(dashboard_id="dashboard-123", share_config=share_config)
            
            assert_success_response(result)
            assert result['dashboard_id'] == "dashboard-123"
            assert result['share_config'] == share_config
            assert result['message'] == 'Lakeview dashboard dashboard-123 sharing initiated'
    
    @pytest.mark.unit
    def test_get_dashboard_permissions(self, mcp_server, mock_env_vars):
        """Test getting dashboard permissions."""
        with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
            mock_client.return_value = Mock()
            
            load_dashboard_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['get_dashboard_permissions']
            result = tool.fn(dashboard_id="dashboard-123")
            
            assert_success_response(result)
            assert result['dashboard_id'] == "dashboard-123"
            assert result['message'] == 'Dashboard permissions retrieved for dashboard-123'
