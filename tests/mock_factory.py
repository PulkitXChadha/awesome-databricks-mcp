"""Factory for creating mock Databricks objects."""
from unittest.mock import Mock, MagicMock
from tests.utils import load_mock_response

class MockWorkspaceClientFactory:
    """Factory for creating configured mock WorkspaceClient."""
    
    @staticmethod
    def create_with_catalogs():
        """Create mock client with catalog data."""
        client = Mock()
        
        # Setup catalogs using flat structure
        catalog_data = load_mock_response("catalogs")
        catalogs = []
        for cat in catalog_data:
            mock_cat = Mock()
            for key, value in cat.items():
                setattr(mock_cat, key, value)
            catalogs.append(mock_cat)
        
        client.catalogs.list.return_value = catalogs
        client.catalogs.get.side_effect = lambda name: next(
            (c for c in catalogs if c.name == name), None
        )
        
        return client
    
    @staticmethod
    def create_with_error():
        """Create mock client that raises errors."""
        client = Mock()
        client.catalogs.list.side_effect = Exception("Connection failed")
        client.schemas.list.side_effect = Exception("Connection failed")
        client.tables.list.side_effect = Exception("Connection failed")
        return client
    
    @staticmethod
    def create_empty():
        """Create mock client with no data."""
        client = Mock()
        client.catalogs.list.return_value = []
        client.schemas.list.return_value = []
        client.tables.list.return_value = []
        client.warehouses.list.return_value = []
        return client
    
    @staticmethod
    def create_with_warehouses():
        """Create mock client with warehouse data."""
        client = Mock()
        
        # Setup warehouses using flat structure
        warehouse_data = load_mock_response("warehouses")
        warehouses = []
        for wh in warehouse_data:
            mock_wh = Mock()
            for key, value in wh.items():
                setattr(mock_wh, key, value)
            warehouses.append(mock_wh)
        
        client.warehouses.list.return_value = warehouses
        return client
