"""Test utilities and mock factory."""
import pytest
from tests.utils import load_mock_response, create_mock_catalog, create_mock_schema, create_mock_table
from tests.mock_factory import MockWorkspaceClientFactory


class TestPhase2Utils:
    """Test Phase 2 utility functions."""
    
    def test_load_mock_response_flat(self):
        """Test loading flat mock responses."""
        catalogs = load_mock_response("catalogs")
        assert isinstance(catalogs, list)
        assert len(catalogs) == 2
        assert catalogs[0]["name"] == "main"
        assert catalogs[1]["name"] == "dev"
    
    def test_create_mock_catalog(self):
        """Test creating mock catalog objects."""
        catalog = create_mock_catalog("test_cat")
        assert catalog.name == "test_cat"
        assert catalog.owner == "test@example.com"
        assert catalog.created_at == 1234567890
    
    def test_create_mock_schema(self):
        """Test creating mock schema objects."""
        schema = create_mock_schema("main", "bronze")
        assert schema.catalog_name == "main"
        assert schema.name == "bronze"
        assert schema.full_name == "main.bronze"
    
    def test_create_mock_table(self):
        """Test creating mock table objects."""
        table = create_mock_table("main", "bronze", "users")
        assert table.catalog_name == "main"
        assert table.schema_name == "bronze"
        assert table.name == "users"
        assert table.full_name == "main.bronze.users"
        assert table.table_type == "MANAGED"
        assert table.data_source_format == "DELTA"


class TestMockWorkspaceClientFactory:
    """Test mock factory functionality."""
    
    def test_create_with_catalogs(self):
        """Test creating mock client with catalog data."""
        client = MockWorkspaceClientFactory.create_with_catalogs()
        assert client.catalogs.list.return_value is not None
        assert len(client.catalogs.list.return_value) == 2
        
        # Test get method
        catalog = client.catalogs.get("main")
        assert catalog.name == "main"
    
    def test_create_with_error(self):
        """Test creating mock client that raises errors."""
        client = MockWorkspaceClientFactory.create_with_error()
        
        with pytest.raises(Exception, match="Connection failed"):
            client.catalogs.list()
        
        with pytest.raises(Exception, match="Connection failed"):
            client.schemas.list()
    
    def test_create_empty(self):
        """Test creating mock client with no data."""
        client = MockWorkspaceClientFactory.create_empty()
        assert client.catalogs.list.return_value == []
        assert client.schemas.list.return_value == []
        assert client.tables.list.return_value == []
        assert client.warehouses.list.return_value == []
    
    def test_create_with_warehouses(self):
        """Test creating mock client with warehouse data."""
        client = MockWorkspaceClientFactory.create_with_warehouses()
        assert client.warehouses.list.return_value is not None
        assert len(client.warehouses.list.return_value) == 1
        assert client.warehouses.list.return_value[0].name == "Test Warehouse"
