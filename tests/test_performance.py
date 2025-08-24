"""Performance baseline tests for critical MCP tools.

Tests measure execution time of mocked tool operations to establish
performance baselines and detect regressions.
"""

import time
from unittest.mock import Mock, patch

import pytest
from fastmcp import FastMCP

from server.tools.core import load_core_tools
from server.tools.sql_operations import load_sql_tools
from server.tools.unity_catalog import load_uc_tools as load_catalog_tools


# Performance thresholds in seconds (for mocked operations)
THRESHOLDS = {
    'health': 0.1,              # Health check should be instant
    'list_warehouses': 0.5,      # List operations should be fast
    'execute_dbsql': 2.0,        # Query execution can take longer
    'list_uc_catalogs': 1.0,     # Catalog listing moderate time
    'describe_uc_catalog': 1.0,  # Catalog description moderate time
    'describe_uc_table': 1.5,    # Table description with metadata
}


@pytest.fixture
def mcp_server():
    """Create MCP server instance for testing."""
    return FastMCP("test-server")


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv('DATABRICKS_HOST', 'https://test.databricks.com')
    monkeypatch.setenv('DATABRICKS_TOKEN', 'test-token-123')
    monkeypatch.setenv('DATABRICKS_SQL_WAREHOUSE_ID', 'test-warehouse-id')


def measure_execution_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return end_time - start_time, result


@pytest.mark.performance
class TestPerformanceBaselines:
    """Test suite for performance baseline measurements."""
    
    def test_health_check_performance(self, mcp_server, mock_env_vars):
        """Test health check performance."""
        # Load core tools
        load_core_tools(mcp_server)
        
        # Get health tool
        health_tool = mcp_server._tool_manager._tools['health']
        
        # Measure execution time
        execution_time, result = measure_execution_time(health_tool.fn)
        
        # Validate result
        assert result['status'] == 'healthy'  # Health tool returns 'status', not 'success'
        
        # Check performance threshold
        assert execution_time < THRESHOLDS['health'], (
            f"Health check took {execution_time:.3f}s, "
            f"exceeds threshold of {THRESHOLDS['health']}s"
        )
    
    @patch('server.tools.sql_operations.WorkspaceClient')
    def test_list_warehouses_performance(self, mock_client, mcp_server, mock_env_vars):
        """Test list warehouses performance."""
        # Setup mock warehouses
        mock_client.return_value.sql_warehouses.list.return_value = [
            Mock(id="warehouse1", name="Test Warehouse 1", state="RUNNING"),
            Mock(id="warehouse2", name="Test Warehouse 2", state="STOPPED"),
        ]
        
        # Load SQL tools
        load_sql_tools(mcp_server)
        
        # Get list warehouses tool
        list_warehouses_tool = mcp_server._tool_manager._tools['list_warehouses']
        
        # Measure execution time
        execution_time, result = measure_execution_time(list_warehouses_tool.fn)
        
        # Validate result
        assert result['success'] is True
        assert len(result['warehouses']) == 2
        
        # Check performance threshold
        assert execution_time < THRESHOLDS['list_warehouses'], (
            f"List warehouses took {execution_time:.3f}s, "
            f"exceeds threshold of {THRESHOLDS['list_warehouses']}s"
        )
    
    @patch('server.tools.sql_operations.WorkspaceClient')
    def test_execute_dbsql_performance(self, mock_client, mcp_server, mock_env_vars):
        """Test SQL query execution performance."""
        # Mock statement execution
        mock_response = Mock()
        mock_response.statement_id = "stmt123"
        mock_response.status.state = "SUCCEEDED"
        mock_response.result = Mock(
            data_array=[["value1", "value2"]],
        )
        mock_response.manifest.schema.columns = [
            Mock(name="col1", type_text="STRING"),
            Mock(name="col2", type_text="INT"),
        ]
        mock_client.return_value.statement_execution.execute_statement.return_value = mock_response
        
        # Load SQL tools
        load_sql_tools(mcp_server)
        
        # Get execute_dbsql tool
        execute_tool = mcp_server._tool_manager._tools['execute_dbsql']
        
        # Measure execution time with sample query
        execution_time, result = measure_execution_time(
            execute_tool.fn,
            query="SELECT * FROM test_table LIMIT 10",
            warehouse_id="warehouse1"
        )
        
        # Validate result
        assert result['success'] is True
        assert 'data' in result
        
        # Check performance threshold
        assert execution_time < THRESHOLDS['execute_dbsql'], (
            f"Execute SQL took {execution_time:.3f}s, "
            f"exceeds threshold of {THRESHOLDS['execute_dbsql']}s"
        )
    
    @patch('server.tools.unity_catalog.WorkspaceClient')
    def test_list_catalogs_performance(self, mock_client, mcp_server, mock_env_vars):
        """Test list Unity Catalog catalogs performance."""
        # Setup mock catalogs
        mock_client.return_value.catalogs.list.return_value = [
            Mock(name="catalog1", comment="Test Catalog 1"),
            Mock(name="catalog2", comment="Test Catalog 2"),
        ]
        
        # Load catalog tools
        load_catalog_tools(mcp_server)
        
        # Get list catalogs tool
        list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
        
        # Measure execution time
        execution_time, result = measure_execution_time(list_catalogs_tool.fn)
        
        # Validate result
        assert result['success'] is True
        assert len(result['catalogs']) == 2
        
        # Check performance threshold
        assert execution_time < THRESHOLDS['list_uc_catalogs'], (
            f"List catalogs took {execution_time:.3f}s, "
            f"exceeds threshold of {THRESHOLDS['list_uc_catalogs']}s"
        )
    
    @patch('server.tools.unity_catalog.WorkspaceClient')
    def test_describe_catalog_performance(self, mock_client, mcp_server, mock_env_vars):
        """Test describe Unity Catalog catalog performance."""
        # Mock catalog details
        mock_catalog = Mock()
        mock_catalog.name = "catalog1"
        mock_catalog.catalog_type = "MANAGED"
        mock_catalog.comment = "Test Catalog 1"
        mock_catalog.owner = "test_user"
        mock_catalog.created_at = 1234567890
        mock_catalog.updated_at = 1234567890
        mock_catalog.properties = {}
        mock_client.return_value.catalogs.get.return_value = mock_catalog
        
        # Setup mock schemas
        mock_client.return_value.schemas.list.return_value = [
            Mock(name="schema1", full_name="catalog1.schema1", comment=None, owner="test_user", 
                 created_at=1234567890, updated_at=1234567890, properties={}),
            Mock(name="schema2", full_name="catalog1.schema2", comment=None, owner="test_user",
                 created_at=1234567890, updated_at=1234567890, properties={}),
        ]
        
        # Load catalog tools
        load_catalog_tools(mcp_server)
        
        # Get describe catalog tool
        describe_catalog_tool = mcp_server._tool_manager._tools['describe_uc_catalog']
        
        # Measure execution time
        execution_time, result = measure_execution_time(
            describe_catalog_tool.fn,
            catalog_name="catalog1"
        )
        
        # Validate result
        assert result['success'] is True
        assert result['catalog']['name'] == 'catalog1'
        
        # Check performance threshold
        assert execution_time < THRESHOLDS['describe_uc_catalog'], (
            f"Describe catalog took {execution_time:.3f}s, "
            f"exceeds threshold of {THRESHOLDS['describe_uc_catalog']}s"
        )
    
    @patch('server.tools.unity_catalog.WorkspaceClient')
    def test_describe_table_performance(self, mock_client, mcp_server, mock_env_vars):
        """Test describe Unity Catalog table performance."""
        # Mock table info
        mock_table = Mock()
        mock_table.name = "test_table"
        mock_table.catalog_name = "catalog1"
        mock_table.schema_name = "schema1"
        mock_table.table_type = "MANAGED"
        # Create proper column mocks with all required attributes
        col1 = Mock()
        col1.name = "id"
        col1.type_text = "BIGINT"
        col1.comment = "Primary key"
        col1.nullable = False
        col1.partition_index = None
        
        col2 = Mock()
        col2.name = "name"
        col2.type_text = "STRING"
        col2.comment = "Name field"
        col2.nullable = True
        col2.partition_index = None
        
        mock_table.columns = [col1, col2]
        mock_table.properties = {"delta.enableChangeDataFeed": "true"}
        mock_table.comment = "Test table"
        mock_table.owner = "test_user"
        mock_table.created_at = 1234567890
        mock_table.updated_at = 1234567890
        mock_table.storage_location = None
        mock_table.partitioning = []
        mock_table.data_source_format = "DELTA"
        mock_client.return_value.tables.get.return_value = mock_table
        
        # Load catalog tools
        load_catalog_tools(mcp_server)
        
        # Get describe table tool
        describe_table_tool = mcp_server._tool_manager._tools['describe_uc_table']
        
        # Measure execution time
        execution_time, result = measure_execution_time(
            describe_table_tool.fn,
            table_name="catalog1.schema1.test_table"
        )
        
        # Validate result
        assert result['success'] is True
        assert result['table']['name'] == 'test_table'
        
        # Check performance threshold
        assert execution_time < THRESHOLDS['describe_uc_table'], (
            f"Describe table took {execution_time:.3f}s, "
            f"exceeds threshold of {THRESHOLDS['describe_uc_table']}s"
        )


@pytest.mark.performance
class TestPerformanceRegression:
    """Test suite for detecting performance regressions."""
    
    @patch('server.tools.sql_operations.WorkspaceClient')
    def test_batch_operations_performance(self, mock_client, mcp_server, mock_env_vars):
        """Test performance of batch operations."""
        # Setup mock warehouses
        mock_client.return_value.sql_warehouses.list.return_value = [
            Mock(id="warehouse1", name="Test Warehouse 1", state="RUNNING"),
            Mock(id="warehouse2", name="Test Warehouse 2", state="STOPPED"),
        ]
        
        # Load SQL tools
        load_sql_tools(mcp_server)
        
        # Get list warehouses tool
        list_warehouses_tool = mcp_server._tool_manager._tools['list_warehouses']
        
        # Run operation multiple times to detect variance
        execution_times = []
        for _ in range(5):
            execution_time, _ = measure_execution_time(list_warehouses_tool.fn)
            execution_times.append(execution_time)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        # Check consistency (max should not be more than 10x min for mocked operations)
        # Mocked operations can have high variance due to Python overhead
        if min_time > 0:  # Avoid division by zero
            assert max_time < min_time * 10, (
                f"Performance variance too high: min={min_time:.3f}s, max={max_time:.3f}s"
            )
        
        # Check average is within threshold
        assert avg_time < THRESHOLDS['list_warehouses'], (
            f"Average execution time {avg_time:.3f}s exceeds threshold"
        )
    
    @patch('server.tools.unity_catalog.WorkspaceClient')
    def test_complex_query_performance(self, mock_client, mcp_server, mock_env_vars):
        """Test performance with complex operations."""
        # Mock a more complex catalog structure
        mock_client.return_value.tables.list.return_value = [
            Mock(name=f"table_{i}", table_type="MANAGED")
            for i in range(100)  # Simulate 100 tables
        ]
        
        # Load catalog tools
        load_catalog_tools(mcp_server)
        
        # Get describe schema tool (which lists tables)
        describe_schema_tool = mcp_server._tool_manager._tools['describe_uc_schema']
        
        # Measure execution time with large dataset
        execution_time, result = measure_execution_time(
            describe_schema_tool.fn,
            catalog_name="catalog1",
            schema_name="schema1"
        )
        
        # Even with 100 tables, should complete quickly (mocked)
        assert execution_time < 2.0, (
            f"Complex operation took {execution_time:.3f}s, "
            "performance degrades with larger datasets"
        )


@pytest.mark.performance
def test_tool_loading_performance(mcp_server, mock_env_vars):
    """Test that tool loading itself is performant."""
    start_time = time.perf_counter()
    
    # Load all tool modules
    load_core_tools(mcp_server)
    load_sql_tools(mcp_server)
    load_catalog_tools(mcp_server)
    
    end_time = time.perf_counter()
    loading_time = end_time - start_time
    
    # Tool loading should be fast (under 1 second)
    assert loading_time < 1.0, (
        f"Tool loading took {loading_time:.3f}s, "
        "initialization performance needs optimization"
    )
    
    # Verify tools were loaded
    assert 'health' in mcp_server._tool_manager._tools
    assert 'list_warehouses' in mcp_server._tool_manager._tools
    assert 'list_uc_catalogs' in mcp_server._tool_manager._tools


@pytest.mark.performance
def test_concurrent_tool_execution(mcp_server, mock_env_vars):
    """Test performance under concurrent execution scenarios."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
        # Setup mock warehouses
        mock_client.return_value.sql_warehouses.list.return_value = [
            Mock(id="warehouse1", name="Test Warehouse 1", state="RUNNING"),
            Mock(id="warehouse2", name="Test Warehouse 2", state="STOPPED"),
        ]
        # Load SQL tools
        load_sql_tools(mcp_server)
        
        # Get tool
        list_warehouses_tool = mcp_server._tool_manager._tools['list_warehouses']
        
        # Simulate rapid consecutive calls
        start_time = time.perf_counter()
        for _ in range(10):
            result = list_warehouses_tool.fn()
            assert result['success'] is True
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        avg_time = total_time / 10
        
        # Average time per call should still meet threshold
        assert avg_time < THRESHOLDS['list_warehouses'], (
            f"Average execution time {avg_time:.3f}s under load "
            f"exceeds threshold of {THRESHOLDS['list_warehouses']}s"
        )