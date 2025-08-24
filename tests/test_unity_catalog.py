"""Test Unity Catalog tools."""
import pytest
from unittest.mock import patch, Mock
from tests.utils import assert_success_response, assert_error_response
from tests.mock_factory import MockWorkspaceClientFactory
from server.tools.unity_catalog import load_uc_tools

class TestUnityCatalogTools:
    """Test Unity Catalog operations."""
    
    @pytest.mark.unit
    def test_list_uc_catalogs_success(self, mcp_server, mock_env_vars):
        """Test successful catalog listing."""
        with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
            mock_client.return_value = MockWorkspaceClientFactory.create_with_catalogs()
            
            load_uc_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_uc_catalogs']
            result = tool.fn()
            
            assert_success_response(result)
            assert result['count'] == 2
            assert len(result['catalogs']) == 2
            assert result['catalogs'][0]['name'] == 'main'
    
    @pytest.mark.unit
    def test_list_uc_catalogs_empty(self, mcp_server, mock_env_vars):
        """Test catalog listing with no catalogs."""
        with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
            mock_client.return_value = MockWorkspaceClientFactory.create_empty()
            
            load_uc_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_uc_catalogs']
            result = tool.fn()
            
            assert_success_response(result)
            assert result['count'] == 0
            assert result['catalogs'] == []
    
    @pytest.mark.unit
    def test_list_uc_catalogs_error(self, mcp_server, mock_env_vars):
        """Test catalog listing with connection error."""
        with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
            mock_client.return_value = MockWorkspaceClientFactory.create_with_error()
            
            load_uc_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_uc_catalogs']
            result = tool.fn()
            
            assert_error_response(result)
            assert 'Connection failed' in result['error']
    
    @pytest.mark.unit
    def test_describe_uc_catalog(self, mcp_server, mock_env_vars):
        """Test describing a specific catalog."""
        with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
            client = MockWorkspaceClientFactory.create_with_catalogs()
            
            # Add schemas to the catalog
            from tests.utils import create_mock_schema
            schemas = [
                create_mock_schema("main", "default"),
                create_mock_schema("main", "bronze")
            ]
            client.schemas.list.return_value = schemas
            mock_client.return_value = client
            
            load_uc_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['describe_uc_catalog']
            result = tool.fn("main")
            
            assert_success_response(result)
            assert result['catalog']['name'] == 'main'
            assert len(result['schemas']) == 2
    
    @pytest.mark.unit
    def test_describe_uc_schema(self, mcp_server, mock_env_vars):
        """Test describing a specific schema."""
        with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
            client = Mock()
            
            # Mock schema
            mock_schema = Mock()
            mock_schema.name = 'default'
            mock_schema.catalog_name = 'main'
            mock_schema.owner = 'test@example.com'
            client.schemas.get.return_value = mock_schema
            
            # Mock tables
            from tests.utils import create_mock_table
            tables = [create_mock_table("main", "default", "users")]
            client.tables.list.return_value = tables
            mock_client.return_value = client
            
            load_uc_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['describe_uc_schema']
            result = tool.fn('main', 'default')
            
            assert_success_response(result)
            assert result['schema']['name'] == 'default'
            assert len(result['tables']) == 1
            assert result['tables'][0]['name'] == 'users'
    
    @pytest.mark.unit
    def test_describe_uc_table(self, mcp_server, mock_env_vars):
        """Test describing a specific table."""
        with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
            client = Mock()
            
            # Mock table
            from tests.utils import create_mock_table
            mock_table = create_mock_table("main", "default", "users")
            mock_table.columns = []
            mock_table.partitioning = []
            client.tables.get.return_value = mock_table
            mock_client.return_value = client
            
            load_uc_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['describe_uc_table']
            result = tool.fn('main.default.users')
            
            assert_success_response(result)
            assert result['table']['name'] == 'users'
    
    # Note: list_uc_schemas and list_uc_tables tools are not implemented yet
    # These tests will be added when those tools are implemented
