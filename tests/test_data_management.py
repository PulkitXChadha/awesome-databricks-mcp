"""Test data management tools."""
import pytest
from unittest.mock import patch, Mock
from tests.utils import assert_success_response, assert_error_response
from server.tools.data_management import load_data_tools

class TestDataManagementTools:
    """Test data management operations."""
    
    @pytest.mark.unit
    def test_list_dbfs_files(self, mcp_server, mock_env_vars):
        """Test listing DBFS files."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            # Mock DBFS file listing
            mock_file = Mock()
            mock_file.path = "/test/file.txt"
            mock_file.is_dir = False
            mock_file.file_size = 1024
            mock_file.modification_time = 1234567890
            
            mock_client.return_value.dbfs.list.return_value = [mock_file]
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_dbfs_files']
            result = tool.fn(path="/test")
            
            assert_success_response(result)
            assert result['path'] == "/test"
            assert result['count'] == 1
            assert result['files'][0]['path'] == "/test/file.txt"
            assert result['files'][0]['is_dir'] is False
    
    @pytest.mark.unit
    def test_get_dbfs_file_info(self, mcp_server, mock_env_vars):
        """Test getting DBFS file information."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            # Mock file status
            mock_status = Mock()
            mock_status.path = "/test/file.txt"
            mock_status.is_dir = False
            mock_status.file_size = 1024
            mock_status.modification_time = 1234567890
            
            mock_client.return_value.dbfs.get_status.return_value = mock_status
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['get_dbfs_file_info']
            result = tool.fn(path="/test/file.txt")
            
            assert_success_response(result)
            assert result['path'] == "/test/file.txt"
            assert result['file_info']['file_size'] == 1024
    
    @pytest.mark.unit
    def test_read_dbfs_file(self, mcp_server, mock_env_vars):
        """Test reading DBFS file content."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            # Mock file content
            mock_content = b"Hello, World!"
            mock_client.return_value.dbfs.read.return_value = mock_content
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['read_dbfs_file']
            result = tool.fn(path="/test/file.txt")
            
            assert_success_response(result)
            assert result['path'] == "/test/file.txt"
            assert result['content'] == "Hello, World!"
            assert result['content_type'] == 'text'
    
    @pytest.mark.unit
    def test_write_dbfs_file(self, mcp_server, mock_env_vars):
        """Test writing to DBFS file."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            mock_client.return_value.dbfs.put.return_value = None
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['write_dbfs_file']
            result = tool.fn(path="/test/file.txt", content="Test content")
            
            assert_success_response(result)
            assert result['path'] == "/test/file.txt"
            assert result['content_length'] == 12
            assert result['overwrite'] is False
    
    @pytest.mark.unit
    def test_list_external_locations(self, mcp_server, mock_env_vars):
        """Test listing external locations."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            # Mock external locations
            mock_location = Mock()
            mock_location.name = "test-location"
            mock_location.url = "s3://bucket/path"
            mock_location.credential_name = "test-cred"
            mock_location.read_only = False
            mock_location.owner = "test@example.com"
            mock_location.created_time = 1234567890
            mock_location.updated_time = 1234567890
            
            mock_client.return_value.external_locations.list.return_value = [mock_location]
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_external_locations']
            result = tool.fn()
            
            assert_success_response(result)
            assert result['count'] == 1
            assert result['locations'][0]['name'] == "test-location"
            assert result['locations'][0]['url'] == "s3://bucket/path"
    
    @pytest.mark.unit
    def test_list_volumes(self, mcp_server, mock_env_vars):
        """Test listing Unity Catalog volumes."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            # Mock volumes
            mock_volume = Mock()
            mock_volume.name = "test-volume"
            mock_volume.catalog_name = "main"
            mock_volume.schema_name = "default"
            mock_volume.volume_type = "EXTERNAL"
            mock_volume.storage_location = "s3://bucket/volume"
            mock_volume.owner = "test@example.com"
            mock_volume.created_time = 1234567890
            mock_volume.updated_time = 1234567890
            mock_volume.comment = "Test volume"
            mock_volume.properties = {}
            
            mock_client.return_value.volumes.list.return_value = [mock_volume]
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_volumes']
            result = tool.fn(catalog_name="main", schema_name="default")
            
            assert_success_response(result)
            assert result['count'] == 1
            assert result['volumes'][0]['name'] == "test-volume"
            assert result['volumes'][0]['volume_type'] == "EXTERNAL"
    
    @pytest.mark.unit
    def test_create_volume(self, mcp_server, mock_env_vars):
        """Test creating a Unity Catalog volume."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            mock_client.return_value.volumes.create.return_value = None
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['create_volume']
            result = tool.fn(
                catalog_name="main",
                schema_name="default",
                volume_name="new-volume",
                volume_type="EXTERNAL",
                storage_location="s3://bucket/new-volume"
            )
            
            assert_success_response(result)
            assert result['volume_name'] == "new-volume"
            assert result['volume_type'] == "EXTERNAL"
            assert result['message'] == 'Volume new-volume created successfully in main.default'
    
    @pytest.mark.unit
    def test_delete_dbfs_path(self, mcp_server, mock_env_vars):
        """Test deleting a DBFS path."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            mock_client.return_value.dbfs.delete.return_value = None
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['delete_dbfs_path']
            result = tool.fn(path="/test/file.txt")
            
            assert_success_response(result)
            assert result['path'] == "/test/file.txt"
            assert result['message'] == 'Path /test/file.txt deleted successfully'
    
    @pytest.mark.unit
    def test_copy_dbfs_file(self, mcp_server, mock_env_vars):
        """Test copying a DBFS file."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            # Mock file operations
            mock_reader = Mock()
            mock_reader.read.return_value = b"test content"
            mock_writer = Mock()
            
            mock_client.return_value.dbfs.read.return_value.__enter__.return_value = mock_reader
            mock_client.return_value.dbfs.write.return_value.__enter__.return_value = mock_writer
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['copy_dbfs_file']
            result = tool.fn(source_path="/test/file.txt", destination_path="/test/copy.txt")
            
            assert_success_response(result)
            assert result['source_path'] == "/test/file.txt"
            assert result['destination_path'] == "/test/copy.txt"
            assert result['message'] == 'File copied successfully from /test/file.txt to /test/copy.txt'
    
    @pytest.mark.unit
    def test_move_dbfs_path(self, mcp_server, mock_env_vars):
        """Test moving a DBFS path."""
        with patch('server.tools.data_management.WorkspaceClient') as mock_client:
            mock_client.return_value.dbfs.move.return_value = None
            
            load_data_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['move_dbfs_path']
            result = tool.fn(source="/test/file.txt", destination="/test/moved.txt")
            
            assert_success_response(result)
            assert result['source'] == "/test/file.txt"
            assert result['destination'] == "/test/moved.txt"
            assert result['message'] == 'Path moved successfully from /test/file.txt to /test/moved.txt'
