"""Data management MCP tools for Databricks."""

import os

from databricks.sdk import WorkspaceClient


def load_data_tools(mcp_server):
  """Register data management MCP tools with the server.

  Args:
      mcp_server: The FastMCP server instance to register tools with
  """

  @mcp_server.tool()
  def list_dbfs_files(path: str = '/') -> dict:
    """List files and directories in DBFS (Databricks File System).

    Args:
        path: DBFS path to list (default: '/')

    Returns:
        Dictionary with file listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List files in DBFS
      files = w.dbfs.list(path)

      file_list = []
      for file in files:
        file_list.append(
          {
            'path': file.path,
            'is_dir': file.is_dir,
            'file_size': file.file_size,
            'modification_time': file.modification_time,
          }
        )

      return {
        'success': True,
        'path': path,
        'files': file_list,
        'count': len(file_list),
        'message': f'Found {len(file_list)} file(s) in {path}',
      }

    except Exception as e:
      print(f'❌ Error listing DBFS files: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'files': [], 'count': 0}

  @mcp_server.tool()
  def get_dbfs_file_info(path: str) -> dict:
    """Get file/directory information from DBFS.

    Args:
        path: DBFS path to get information for

    Returns:
        Dictionary with file/directory information or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get file info
      file_info = w.dbfs.get_status(path)

      return {
        'success': True,
        'path': path,
        'file_info': {
          'path': file_info.path,
          'is_dir': file_info.is_dir,
          'file_size': file_info.file_size,
          'modification_time': file_info.modification_time,
        },
        'message': f'File information retrieved successfully for {path}',
      }

    except Exception as e:
      print(f'❌ Error getting DBFS file info: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def read_dbfs_file(path: str, offset: int = 0, length: int = None) -> dict:
    """Read file content from DBFS.

    Args:
        path: DBFS file path to read
        offset: Starting byte position (default: 0)
        length: Number of bytes to read (default: None for entire file)

    Returns:
        Dictionary with file content or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Read file content
      if length:
        content = w.dbfs.read(path, offset=offset, length=length)
      else:
        content = w.dbfs.read(path, offset=offset)

      # Convert bytes to string if possible
      try:
        content_str = content.decode('utf-8')
        content_type = 'text'
      except UnicodeDecodeError:
        content_str = str(content)
        content_type = 'binary'

      return {
        'success': True,
        'path': path,
        'offset': offset,
        'length': length,
        'content': content_str,
        'content_type': content_type,
        'actual_length': len(content),
        'message': f'File content read successfully from {path}',
      }

    except Exception as e:
      print(f'❌ Error reading DBFS file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def write_dbfs_file(path: str, content: str, overwrite: bool = False) -> dict:
    """Write content to a file in DBFS.

    Args:
        path: DBFS file path to write to
        content: Content to write to the file
        overwrite: Whether to overwrite existing file (default: False)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Convert string to bytes
      content_bytes = content.encode('utf-8')

      # Write file content
      w.dbfs.put(path, content_bytes, overwrite=overwrite)

      return {
        'success': True,
        'path': path,
        'content_length': len(content_bytes),
        'overwrite': overwrite,
        'message': f'File content written successfully to {path}',
      }

    except Exception as e:
      print(f'❌ Error writing DBFS file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def delete_dbfs_path(path: str, recursive: bool = False) -> dict:
    """Delete a file or directory from DBFS.

    Args:
        path: DBFS path to delete
        recursive: Whether to delete directory contents recursively (default: False)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete path
      w.dbfs.delete(path, recursive=recursive)

      return {
        'success': True,
        'path': path,
        'recursive': recursive,
        'message': f'Path {path} deleted successfully',
      }

    except Exception as e:
      print(f'❌ Error deleting DBFS path: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def create_dbfs_directory(path: str) -> dict:
    """Create a directory in DBFS.

    Args:
        path: DBFS directory path to create

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create directory
      w.dbfs.mkdirs(path)

      return {
        'success': True,
        'path': path,
        'message': f'Directory {path} created successfully',
      }

    except Exception as e:
      print(f'❌ Error creating DBFS directory: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def move_dbfs_path(source: str, destination: str) -> dict:
    """Move/rename a file or directory in DBFS.

    Args:
        source: Source DBFS path
        destination: Destination DBFS path

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Move path
      w.dbfs.move(source, destination)

      return {
        'success': True,
        'source': source,
        'destination': destination,
        'message': f'Path moved successfully from {source} to {destination}',
      }

    except Exception as e:
      print(f'❌ Error moving DBFS path: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def copy_dbfs_file(source_path: str, destination_path: str) -> dict:
    """Copy a file in DBFS from source to destination.

    Args:
        source_path: Source DBFS file path
        destination_path: Destination DBFS file path

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Read source file
      with w.dbfs.read(source_path) as reader:
        content = reader.read()

      # Write to destination
      with w.dbfs.write(destination_path, overwrite=True) as writer:
        writer.write(content)

      return {
        'success': True,
        'source_path': source_path,
        'destination_path': destination_path,
        'message': f'File copied successfully from {source_path} to {destination_path}',
      }

    except Exception as e:
      print(f'❌ Error copying DBFS file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def list_external_locations() -> dict:
    """List all external locations configured in the workspace.

    Returns:
        Dictionary with external location listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List external locations
      locations = w.external_locations.list()

      location_list = []
      for location in locations:
        location_list.append(
          {
            'name': location.name,
            'url': location.url,
            'credential_name': location.credential_name,
            'read_only': location.read_only,
            'owner': location.owner,
            'created_time': location.created_time,
            'updated_time': location.updated_time,
          }
        )

      return {
        'success': True,
        'locations': location_list,
        'count': len(location_list),
        'message': f'Found {len(location_list)} external location(s)',
      }

    except Exception as e:
      print(f'❌ Error listing external locations: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'locations': [], 'count': 0}

  @mcp_server.tool()
  def list_volumes(catalog_name: str, schema_name: str) -> dict:
    """List all volumes within a specific schema.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema to list volumes from

    Returns:
        Dictionary containing list of volumes with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List volumes in the schema
      volumes = w.volumes.list(catalog_name=catalog_name, schema_name=schema_name)

      volume_list = []
      for volume in volumes:
        volume_list.append(
          {
            'name': volume.name,
            'volume_type': volume.volume_type,
            'storage_location': volume.storage_location,
            'owner': volume.owner,
            'created_time': volume.created_time,
            'updated_time': volume.updated_time,
            'comment': volume.comment,
            'properties': volume.properties,
          }
        )

      return {
        'success': True,
        'catalog_name': catalog_name,
        'schema_name': schema_name,
        'volumes': volume_list,
        'count': len(volume_list),
        'message': f'Found {len(volume_list)} volume(s) in schema {catalog_name}.{schema_name}',
      }

    except Exception as e:
      print(f'❌ Error listing volumes: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'volumes': [], 'count': 0}

  @mcp_server.tool()
  def create_volume(
    catalog_name: str,
    schema_name: str,
    volume_name: str,
    volume_type: str = 'EXTERNAL',
    storage_location: str = None,
    comment: str = None,
  ) -> dict:
    """Create a new Unity Catalog volume.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema
        volume_name: Name of the volume to create
        volume_type: Type of volume (EXTERNAL, MANAGED) - default: EXTERNAL
        storage_location: Storage location for external volumes
        comment: Optional comment for the volume

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Prepare volume configuration
      volume_config = {
        'name': volume_name,
        'volume_type': volume_type,
        'comment': comment,
      }

      if storage_location:
        volume_config['storage_location'] = storage_location

      # Create the volume
      w.volumes.create(catalog_name=catalog_name, schema_name=schema_name, **volume_config)

      return {
        'success': True,
        'volume_name': volume_name,
        'catalog_name': catalog_name,
        'schema_name': schema_name,
        'volume_type': volume_type,
        'storage_location': storage_location,
        'message': f'Volume {volume_name} created successfully in {catalog_name}.{schema_name}',
      }

    except Exception as e:
      print(f'❌ Error creating volume: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def describe_external_location(location_name: str) -> dict:
    """Get detailed external location information.

    Args:
        location_name: Name of the external location

    Returns:
        Dictionary with external location details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get external location details
      location = w.external_locations.get(location_name)

      return {
        'success': True,
        'location': {
          'name': location.name,
          'url': location.url,
          'credential_name': location.credential_name,
          'read_only': location.read_only,
          'owner': location.owner,
          'created_time': location.created_time,
          'updated_time': location.updated_time,
          'comment': location.comment,
          'metastore_id': location.metastore_id,
        },
        'message': f'External location {location_name} details retrieved successfully',
      }

    except Exception as e:
      print(f'❌ Error describing external location: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def list_storage_credentials() -> dict:
    """List all storage credentials configured in the workspace.

    Returns:
        Dictionary with storage credential listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List storage credentials
      credentials = w.storage_credentials.list()

      credential_list = []
      for cred in credentials:
        credential_list.append(
          {
            'name': cred.name,
            'owner': cred.owner,
            'created_time': cred.created_time,
            'updated_time': cred.updated_time,
            'comment': cred.comment,
          }
        )

      return {
        'success': True,
        'credentials': credential_list,
        'count': len(credential_list),
        'message': f'Found {len(credential_list)} storage credential(s)',
      }

    except Exception as e:
      print(f'❌ Error listing storage credentials: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'credentials': [], 'count': 0}

  @mcp_server.tool()
  def describe_storage_credential(credential_name: str) -> dict:
    """Get detailed storage credential information.

    Args:
        credential_name: Name of the storage credential

    Returns:
        Dictionary with storage credential details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get storage credential details
      credential = w.storage_credentials.get(credential_name)

      return {
        'success': True,
        'credential': {
          'name': credential.name,
          'owner': credential.owner,
          'created_time': credential.created_time,
          'updated_time': credential.updated_time,
          'comment': credential.comment,
          'metastore_id': credential.metastore_id,
        },
        'message': f'Storage credential {credential_name} details retrieved successfully',
      }

    except Exception as e:
      print(f'❌ Error describing storage credential: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def list_uc_permissions(
    catalog_name: str = None, schema_name: str = None, table_name: str = None
  ) -> dict:
    """List permissions for Unity Catalog objects.

    Args:
        catalog_name: Name of the catalog (optional)
        schema_name: Name of the schema (optional)
        table_name: Name of the table (optional)

    Returns:
        Dictionary with permission listings or error message
    """
    try:
      # Initialize Databricks SDK
      WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Permission listing requires specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'catalog': catalog_name,
        'schema': schema_name,
        'table': table_name,
        'message': 'Permission listing initiated',
        'note': (
          'Permission listing requires specific permissions and may not be '
          'directly accessible via SDK'
        ),
        'permissions': [],
        'count': 0,
      }

    except Exception as e:
      print(f'❌ Error listing permissions: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'permissions': [], 'count': 0}
