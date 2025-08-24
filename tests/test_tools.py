"""Test all MCP tool modules with mocked responses."""

import json
import os
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# Import tool loading functions
from server.tools import load_tools
from server.tools.core import load_core_tools
from server.tools.unity_catalog import load_uc_tools
from server.tools.sql_operations import load_sql_tools
from server.tools.jobs_pipelines import load_job_tools
from server.tools.dashboards import load_dashboard_tools
from server.tools.data_management import load_data_tools
from server.tools.governance import load_governance_tools



@pytest.fixture
def mock_responses():
    """Load mock responses from fixtures file."""
    fixtures_path = Path(__file__).parent / "fixtures" / "mock_responses.json"
    with open(fixtures_path, 'r') as f:
        return json.load(f)


class TestCoreTools:
    """Test core MCP tools."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, mcp_server, mock_env_vars):
        """Test health check tool."""
        # Load tools and test
        load_core_tools(mcp_server)
        
        # Test that the tool was registered
        tools = await mcp_server.get_tools()
        assert 'health' in tools
        
        # Test the health function logic directly
        # We need to get the actual function from the tool registration
        health_tool = mcp_server._tool_manager._tools['health']
        result = health_tool.fn()
        expected_result = {
            'status': 'healthy',
            'service': 'databricks-mcp',
            'databricks_configured': True,  # Set by mock_env_vars
        }
        
        assert result == expected_result


class TestUnityCatalogTools:
    """Test Unity Catalog MCP tools."""
    
    @pytest.mark.asyncio
    async def test_list_uc_catalogs(self, mcp_server, mock_workspace_client, mock_responses):
        """Test listing Unity Catalog catalogs."""
        # Setup mock using Phase 2 utilities
        from tests.utils import create_mock_catalog
        
        mock_catalogs = [
            create_mock_catalog("main"),
            create_mock_catalog("dev")
        ]
        
        # Setup mock before loading tools
        mock_workspace_client.catalogs.list.return_value = mock_catalogs
        
        # Load tools and test
        load_uc_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_uc_catalogs']
        result = tool.fn()
        
        # Assert
        assert result['success'] is True
        assert result['count'] == 2
        assert len(result['catalogs']) == 2
        assert result['catalogs'][0]['name'] == 'main'
        assert result['catalogs'][1]['name'] == 'dev'
    
    @pytest.mark.asyncio
    async def test_describe_uc_catalog(self, mcp_server, mock_workspace_client, mock_responses):
        """Test describing a Unity Catalog catalog."""
        # Setup mock catalog
        mock_catalog = Mock()
        mock_catalog.name = 'main'
        mock_catalog.owner = 'test@example.com'
        mock_catalog.created_at = 1234567890
        
        # Setup mock schemas using Phase 2 utilities
        from tests.utils import create_mock_schema
        
        mock_schemas = [
            create_mock_schema("main", "default"),
            create_mock_schema("main", "bronze")
        ]
        
        mock_workspace_client.catalogs.get.return_value = mock_catalog
        mock_workspace_client.schemas.list.return_value = mock_schemas
        
        # Load tools and test
        load_uc_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['describe_uc_catalog']
        result = tool.fn('main')
        
        # Assert
        assert result['success'] is True
        assert result['catalog']['name'] == 'main'
        assert len(result['schemas']) == 2
        assert result['schemas'][0]['name'] == 'default'
        assert result['schemas'][1]['name'] == 'bronze'
    
    @pytest.mark.asyncio
    async def test_describe_uc_schema(self, mcp_server, mock_workspace_client, mock_responses):
        """Test describing Unity Catalog schema."""
        # Setup mock schema
        mock_schema = Mock()
        mock_schema.name = 'default'
        mock_schema.catalog_name = 'main'
        mock_schema.owner = 'test@example.com'
        
        # Setup mock tables using Phase 2 utilities
        from tests.utils import create_mock_table
        
        mock_tables = [
            create_mock_table("main", "default", "users")
        ]
        
        mock_workspace_client.schemas.get.return_value = mock_schema
        mock_workspace_client.tables.list.return_value = mock_tables
        
        # Load tools and test
        load_uc_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['describe_uc_schema']
        result = tool.fn('catalog1', 'schema1')
        
        # Assert
        assert result['success'] is True
        assert result['schema']['name'] == 'default'
        assert len(result['tables']) == 1
        assert result['tables'][0]['name'] == 'users'
    
    @pytest.mark.asyncio
    async def test_describe_uc_table(self, mcp_server, mock_workspace_client, mock_responses):
        """Test describing Unity Catalog table."""
        # Setup mock table using Phase 2 utilities
        from tests.utils import create_mock_table
        
        mock_table = create_mock_table("main", "default", "users")
        
        # Mock columns attribute
        mock_columns = []
        mock_table.columns = mock_columns
        
        # Mock partitioning attribute
        mock_partitioning = []
        mock_table.partitioning = mock_partitioning
        
        # Mock the table.get method
        mock_workspace_client.tables.get.return_value = mock_table
        
        # Load tools and test
        load_uc_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['describe_uc_table']
        result = tool.fn('main.default.users')
        
        # Assert
        assert result['success'] is True
        assert result['table']['name'] == 'users'


class TestSQLOperationsTools:
    """Test SQL Operations MCP tools."""
    
    @pytest.mark.asyncio
    async def test_list_warehouses(self, mcp_server, mock_workspace_client, mock_responses):
        """Test listing SQL warehouses."""
        # Setup mock warehouses using Phase 2 utilities
        mock_warehouses = []
        warehouse_data = mock_responses['warehouses'][0]  # Use flat structure
        
        mock_warehouse = Mock()
        mock_warehouse.id = warehouse_data['id']
        mock_warehouse.name = warehouse_data['name']
        mock_warehouse.state = warehouse_data['state']
        mock_warehouse.size = warehouse_data['size']
        mock_warehouse.auto_stop_mins = warehouse_data['auto_stop_mins']
        mock_warehouses.append(mock_warehouse)
        
        mock_workspace_client.sql_warehouses.list.return_value = mock_warehouses
        
        # Load tools and test
        load_sql_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_warehouses']
        result = tool.fn()
        
        # Assert
        assert result['success'] is True
        assert result['count'] == 1
        assert result['warehouses'][0]['name'] == 'Test Warehouse'
    
    @pytest.mark.asyncio
    async def test_execute_dbsql(self, mcp_server, mock_workspace_client, mock_responses):
        """Test executing SQL query."""
        # Setup mock query execution
        mock_execution = Mock()
        mock_execution.id = 'execution1'
        mock_execution.status = 'FINISHED'
        
        # Mock result with data_array
        mock_result = Mock()
        mock_result.data_array = [['col1', 'col2'], ['val1', 'val2']]
        mock_execution.result = mock_result
        
        # Mock manifest with schema columns
        mock_manifest = Mock()
        mock_columns = [Mock(name='col1'), Mock(name='col2')]
        mock_manifest.schema.columns = mock_columns
        mock_execution.manifest = mock_manifest
        
        mock_workspace_client.statement_execution.execute_statement.return_value = mock_execution
        
        # Load tools and test
        load_sql_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['execute_dbsql']
        result = tool.fn('SELECT * FROM test_table', 'warehouse1')
        
        # Assert
        assert result['success'] is True
        assert result['row_count'] == 2
        assert 'data' in result
        assert 'columns' in result['data']
        assert 'rows' in result['data']


class TestJobsPipelinesTools:
    """Test Jobs and Pipelines MCP tools."""
    
    @pytest.mark.asyncio
    async def test_list_jobs(self, mcp_server, mock_workspace_client, mock_responses):
        """Test listing Databricks jobs."""
        # Setup mock jobs using flat structure
        mock_jobs = []
        job_data = mock_responses['jobs'][0]  # Use flat structure
        
        mock_job = Mock()
        mock_job.job_id = job_data['job_id']
        mock_job.creator_user_name = job_data['creator_user_name']
        mock_job.created_time = job_data['created_time']
        
        # Mock settings with name
        mock_settings = Mock()
        mock_settings.name = job_data['job_name']
        mock_job.settings = mock_settings
        
        mock_jobs.append(mock_job)
        
        mock_workspace_client.jobs.list.return_value = mock_jobs
        
        # Load tools and test
        load_job_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_jobs']
        result = tool.fn()
        
        # Assert
        assert result['success'] is True
        assert result['count'] == 1
        assert result['jobs'][0]['name'] == 'Test Job 1'
    
    @pytest.mark.asyncio
    async def test_list_pipelines(self, mcp_server, mock_workspace_client, mock_responses):
        """Test listing Databricks pipelines."""
        # Setup mock pipelines using flat structure
        mock_pipelines = []
        pipeline_data = mock_responses['pipelines'][0]  # Use flat structure
        
        mock_pipeline = Mock()
        mock_pipeline.pipeline_id = pipeline_data['pipeline_id']
        mock_pipeline.name = pipeline_data['name']
        mock_pipeline.state = pipeline_data['state']
        mock_pipeline.creator_user_name = pipeline_data['creator_user_name']
        mock_pipeline.created_time = pipeline_data['created_time']
        mock_pipelines.append(mock_pipeline)
        
        mock_workspace_client.pipelines.list_pipelines.return_value = mock_pipelines
        
        # Load tools and test
        load_job_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_pipelines']
        result = tool.fn()
        
        # Assert
        assert result['success'] is True
        assert result['count'] == 1
        assert result['pipelines'][0]['name'] == 'Test Pipeline 1'


class TestDashboardTools:
    """Test Dashboard MCP tools."""
    
    @pytest.mark.asyncio
    async def test_list_dashboards(self, mcp_server, mock_workspace_client, mock_responses):
        """Test listing Databricks dashboards."""
        # Load tools and test
        load_dashboard_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_dashboards']
        result = tool.fn()
        
        # Assert
        assert result['success'] is True
        assert result['count'] == 0  # This is a placeholder function that always returns 0
        assert 'dashboards' in result
        assert result['message'] == 'Legacy dashboard listing initiated'


class TestDataManagementTools:
    """Test Data Management MCP tools."""
    
    @pytest.mark.asyncio
    async def test_list_dbfs_files(self, mcp_server, mock_workspace_client, mock_responses):
        """Test listing DBFS files."""
        # Setup mock files using flat structure
        mock_files = []
        file_data = mock_responses['volumes'][0]  # Use flat structure
        
        mock_file = Mock()
        mock_file.path = file_data['name']
        mock_file.is_dir = False
        mock_file.file_size = 1024
        mock_files.append(mock_file)
        
        mock_workspace_client.dbfs.list.return_value = mock_files
        
        # Load tools and test
        load_data_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_dbfs_files']
        result = tool.fn('/test')
        
        # Assert
        assert result['success'] is True
        assert result['count'] == 1
        assert result['files'][0]['path'] == 'volume1'


class TestGovernanceTools:
    """Test Governance MCP tools."""
    
    @pytest.mark.asyncio
    async def test_list_governance_rules(self, mcp_server, mock_workspace_client, mock_responses):
        """Test listing governance rules."""
        # Load tools and test
        load_governance_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_governance_rules']
        result = tool.fn()
        
        # Assert
        assert result['success'] is True
        assert result['count'] == 0  # This is a placeholder function that always returns 0
        assert 'rules' in result
        assert result['message'] == 'Governance rule listing initiated'








class TestToolIntegration:
    """Test tool integration and loading."""
    
    @pytest.mark.asyncio
    async def test_all_tools_load_successfully(self, mcp_server, mock_env_vars):
        """Test that all tools load without errors."""
        # This should not raise any exceptions
        load_tools(mcp_server)
        
        # Verify tools were loaded
        tools = await mcp_server.get_tools()
        assert len(tools) > 0
        
        # Check that key tool categories are present
        tool_names = list(tools.keys())
        assert 'health' in tool_names  # Core tools
        assert 'list_uc_catalogs' in tool_names  # Unity Catalog tools
        assert 'list_warehouses' in tool_names  # SQL tools
        assert 'list_jobs' in tool_names  # Jobs tools
        assert 'list_dashboards' in tool_names  # Dashboard tools
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, mcp_server, mock_workspace_client):
        """Test that tools handle errors gracefully."""
        # Setup mock to raise exception
        mock_workspace_client.catalogs.list.side_effect = Exception("Test error")
        
        # Load tools and test
        load_uc_tools(mcp_server)
        tool = mcp_server._tool_manager._tools['list_uc_catalogs']
        result = tool.fn()
        
        # Assert error handling
        assert result['success'] is False
        assert 'error' in result
        assert result['catalogs'] == []
        assert result['count'] == 0
