"""Test SQL operations tools."""
import pytest
from unittest.mock import patch, Mock
from tests.utils import assert_success_response, load_mock_response
from server.tools.sql_operations import load_sql_tools

class TestSQLOperations:
    """Test SQL warehouse and query operations."""
    
    @pytest.mark.unit
    def test_list_warehouses(self, mcp_server, mock_env_vars):
        """Test listing SQL warehouses."""
        with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
            # Setup mock warehouses
            warehouse_data = load_mock_response("warehouses")
            warehouses = []
            for w in warehouse_data:
                mock_w = Mock()
                for key, value in w.items():
                    setattr(mock_w, key, value)
                warehouses.append(mock_w)
            
            mock_client.return_value.sql_warehouses.list.return_value = warehouses
            
            load_sql_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_warehouses']
            result = tool.fn()
            
            assert_success_response(result)
            assert len(result['warehouses']) == 1
            assert result['warehouses'][0]['name'] == 'Test Warehouse'
    
    @pytest.mark.unit
    def test_execute_dbsql(self, mcp_server, mock_env_vars):
        """Test executing SQL query."""
        with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
            # Mock statement execution
            mock_response = Mock()
            mock_response.statement_id = "stmt-123"
            mock_response.status.state = "SUCCEEDED"
            mock_response.result = Mock()
            mock_response.result.data_array = [["1", "Alice"], ["2", "Bob"]]
            mock_response.manifest.schema.columns = [
                Mock(name="id", type_text="LONG"),
                Mock(name="name", type_text="STRING")
            ]
            
            mock_client.return_value.statement_execution.execute_statement.return_value = mock_response
            
            load_sql_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['execute_dbsql']
            result = tool.fn(
                query="SELECT * FROM users",
                warehouse_id="test-warehouse"
            )
            
            assert_success_response(result)
            assert result['row_count'] == 2
            assert 'data' in result
            assert 'columns' in result['data']
            assert 'rows' in result['data']
    
    @pytest.mark.unit
    def test_list_warehouses_empty(self, mcp_server, mock_env_vars):
        """Test listing warehouses when none exist."""
        with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
            mock_client.return_value.sql_warehouses.list.return_value = []
            
            load_sql_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_warehouses']
            result = tool.fn()
            
            assert_success_response(result)
            assert result['count'] == 0
            assert result['warehouses'] == []
    
    @pytest.mark.unit
    def test_execute_dbsql_error(self, mcp_server, mock_env_vars):
        """Test SQL execution with error."""
        with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
            # Mock error response
            mock_response = Mock()
            mock_response.status.state = "FAILED"
            mock_response.status.error = Mock(message="SQL syntax error")
            
            mock_client.return_value.statement_execution.execute_statement.return_value = mock_response
            
            load_sql_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['execute_dbsql']
            result = tool.fn(
                query="INVALID SQL",
                warehouse_id="test-warehouse"
            )
            
            assert result['success'] is False
            assert 'error' in result
    
    @pytest.mark.unit
    def test_get_sql_warehouse(self, mcp_server, mock_env_vars):
        """Test getting warehouse status."""
        with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
            # Mock warehouse status
            mock_warehouse = Mock()
            mock_warehouse.id = "test-warehouse"
            mock_warehouse.state = "RUNNING"
            mock_warehouse.name = "Test Warehouse"
            mock_warehouse.size = "Small"
            mock_warehouse.auto_stop_mins = 60
            
            mock_client.return_value.sql_warehouses.get.return_value = mock_warehouse
            
            load_sql_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['get_sql_warehouse']
            result = tool.fn(warehouse_id="test-warehouse")
            
            assert_success_response(result)
            assert result['warehouse']['id'] == "test-warehouse"
            assert result['warehouse']['state'] == "RUNNING"
    
    @pytest.mark.unit
    def test_start_sql_warehouse(self, mcp_server, mock_env_vars):
        """Test starting a warehouse."""
        with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
            mock_client.return_value.sql_warehouses.start.return_value = None
            
            load_sql_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['start_sql_warehouse']
            result = tool.fn(warehouse_id="test-warehouse")
            
            assert_success_response(result)
            assert result['warehouse_id'] == "test-warehouse"
            assert result['message'] == "Warehouse test-warehouse started successfully"
    
    @pytest.mark.unit
    def test_stop_sql_warehouse(self, mcp_server, mock_env_vars):
        """Test stopping a warehouse."""
        with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
            mock_client.return_value.sql_warehouses.stop.return_value = None
            
            load_sql_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['stop_sql_warehouse']
            result = tool.fn(warehouse_id="test-warehouse")
            
            assert_success_response(result)
            assert result['warehouse_id'] == "test-warehouse"
            assert result['message'] == "Warehouse test-warehouse stopped successfully"
