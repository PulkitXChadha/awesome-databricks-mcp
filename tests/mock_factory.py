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
    
    @staticmethod
    def create_with_jobs():
        """Create mock client with job data."""
        client = Mock()
        
        # Setup jobs
        mock_job = Mock()
        mock_job.job_id = 123
        mock_job.settings.name = "Test Job"
        mock_job.created_time = 1234567890
        mock_job.creator_user_name = "test@example.com"
        
        client.jobs.list.return_value = [mock_job]
        client.jobs.get.return_value = mock_job
        
        return client
    
    @staticmethod
    def create_with_pipelines():
        """Create mock client with pipeline data."""
        client = Mock()
        
        # Setup pipelines
        mock_pipeline = Mock()
        mock_pipeline.pipeline_id = "pipeline-123"
        mock_pipeline.name = "Test Pipeline"
        mock_pipeline.state = "IDLE"
        mock_pipeline.creator_user_name = "test@example.com"
        mock_pipeline.created_time = 1234567890
        
        client.pipelines.list_pipelines.return_value = [mock_pipeline]
        client.pipelines.get.return_value = mock_pipeline
        
        return client
    
    @staticmethod
    def create_with_clusters():
        """Create mock client with cluster data."""
        client = Mock()
        
        # Setup clusters
        mock_cluster = Mock()
        mock_cluster.cluster_id = "cluster-123"
        mock_cluster.cluster_name = "Test Cluster"
        mock_cluster.state = "RUNNING"
        mock_cluster.spark_version = "13.3.x-scala2.12"
        mock_cluster.node_type_id = "i3.xlarge"
        mock_cluster.num_workers = 2
        
        client.clusters.list.return_value = [mock_cluster]
        client.clusters.get.return_value = mock_cluster
        
        return client
    
    @staticmethod
    def create_with_dbfs():
        """Create mock client with DBFS data."""
        client = Mock()
        
        # Setup DBFS files
        mock_file = Mock()
        mock_file.path = "/test/file.txt"
        mock_file.is_dir = False
        mock_file.file_size = 1024
        mock_file.modification_time = 1234567890
        
        client.dbfs.list.return_value = [mock_file]
        client.dbfs.get_status.return_value = mock_file
        client.dbfs.read.return_value = b"Hello, World!"
        
        return client
    
    @staticmethod
    def create_with_volumes():
        """Create mock client with volume data."""
        client = Mock()
        
        # Setup volumes
        mock_volume = Mock()
        mock_volume.name = "test-volume"
        mock_volume.catalog_name = "main"
        mock_volume.schema_name = "default"
        mock_volume.volume_type = "EXTERNAL"
        mock_volume.storage_location = "s3://bucket/volume"
        mock_volume.owner = "test@example.com"
        mock_volume.created_time = 1234567890
        
        client.volumes.list.return_value = [mock_volume]
        
        return client
    
    @staticmethod
    def create_with_external_locations():
        """Create mock client with external location data."""
        client = Mock()
        
        # Setup external locations
        mock_location = Mock()
        mock_location.name = "test-location"
        mock_location.url = "s3://bucket/path"
        mock_location.credential_name = "test-cred"
        mock_location.read_only = False
        mock_location.owner = "test@example.com"
        mock_location.created_time = 1234567890
        mock_location.updated_time = 1234567890
        
        client.external_locations.list.return_value = [mock_location]
        
        return client
    
    @staticmethod
    def create_with_users():
        """Create mock client with user data."""
        client = Mock()
        
        # Setup user info
        mock_user = Mock()
        mock_user.user_name = "test@example.com"
        mock_user.display_name = "Test User"
        mock_user.active = True
        mock_user.groups = ["admins", "users"]
        
        client.users.get.return_value = mock_user
        
        return client
    
    @staticmethod
    def create_with_workspace():
        """Create mock client with workspace data."""
        client = Mock()
        
        # Setup workspace info
        mock_workspace = Mock()
        mock_workspace.workspace_id = 123456
        mock_workspace.workspace_name = "Test Workspace"
        mock_workspace.workspace_url = "https://test.cloud.databricks.com"
        mock_workspace.deployment_name = "test-deployment"
        
        client.workspace.get.return_value = mock_workspace
        
        return client
    
    @staticmethod
    def create_with_notebooks():
        """Create mock client with notebook data."""
        client = Mock()
        
        # Setup notebooks
        mock_notebook = Mock()
        mock_notebook.path = "/Users/test@example.com/Test Notebook"
        mock_notebook.language = "python"
        mock_notebook.created_time = 1234567890
        mock_notebook.modified_time = 1234567890
        
        client.workspace.list.return_value = [mock_notebook]
        
        # Setup notebook content
        mock_content = Mock()
        mock_content.content = "# Databricks notebook source\nprint('Hello, World!')"
        mock_content.language = "python"
        
        client.workspace.export.return_value = mock_content
        
        return client
    
    @staticmethod
    def create_with_libraries():
        """Create mock client with library data."""
        client = Mock()
        
        # Setup libraries
        mock_library = Mock()
        mock_library.library_id = "lib-123"
        mock_library.name = "pandas"
        mock_library.version = "2.0.0"
        mock_library.status = "INSTALLED"
        mock_library.install_time = 1234567890
        
        client.libraries.all_cluster_statuses.return_value = [mock_library]
        
        return client
    
    @staticmethod
    def create_comprehensive():
        """Create mock client with comprehensive data for all tool categories."""
        client = Mock()
        
        # Combine all mock data
        catalogs_client = MockWorkspaceClientFactory.create_with_catalogs()
        warehouses_client = MockWorkspaceClientFactory.create_with_warehouses()
        jobs_client = MockWorkspaceClientFactory.create_with_jobs()
        pipelines_client = MockWorkspaceClientFactory.create_with_pipelines()
        clusters_client = MockWorkspaceClientFactory.create_with_clusters()
        dbfs_client = MockWorkspaceClientFactory.create_with_dbfs()
        volumes_client = MockWorkspaceClientFactory.create_with_volumes()
        locations_client = MockWorkspaceClientFactory.create_with_external_locations()
        users_client = MockWorkspaceClientFactory.create_with_users()
        workspace_client = MockWorkspaceClientFactory.create_with_workspace()
        notebooks_client = MockWorkspaceClientFactory.create_with_notebooks()
        libraries_client = MockWorkspaceClientFactory.create_with_libraries()
        
        # Merge all attributes
        for attr_name in dir(catalogs_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(catalogs_client, attr_name))
        
        for attr_name in dir(warehouses_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(warehouses_client, attr_name))
        
        for attr_name in dir(jobs_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(jobs_client, attr_name))
        
        for attr_name in dir(pipelines_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(pipelines_client, attr_name))
        
        for attr_name in dir(clusters_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(clusters_client, attr_name))
        
        for attr_name in dir(dbfs_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(dbfs_client, attr_name))
        
        for attr_name in dir(volumes_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(volumes_client, attr_name))
        
        for attr_name in dir(locations_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(locations_client, attr_name))
        
        for attr_name in dir(users_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(users_client, attr_name))
        
        for attr_name in dir(workspace_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(workspace_client, attr_name))
        
        for attr_name in dir(notebooks_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(notebooks_client, attr_name))
        
        for attr_name in dir(libraries_client):
            if not attr_name.startswith('_'):
                setattr(client, attr_name, getattr(libraries_client, attr_name))
        
        return client
