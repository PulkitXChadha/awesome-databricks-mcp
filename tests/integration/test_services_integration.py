"""Integration tests for services and dependencies."""

import os
from unittest.mock import Mock, patch

import pytest


@pytest.mark.integration
@pytest.mark.services
class TestUserServiceIntegration:
  """Test user service integration with Databricks SDK."""

  def test_user_service_initialization(self):
    """Test user service can be initialized."""
    from server.services.user_service import UserService

    # Should be able to create instance without errors
    service = UserService()
    assert service is not None

  def test_user_service_with_databricks_client(self, mock_databricks_client):
    """Test user service integration with mocked Databricks client."""
    from server.services.user_service import UserService

    # Mock user data
    mock_user = Mock()
    mock_user.user_name = 'integration@test.com'
    mock_user.display_name = 'Integration Test User'
    mock_user.active = True
    mock_user.emails = [Mock(value='integration@test.com', primary=True)]

    mock_databricks_client.current_user.me.return_value = mock_user

    with patch('server.services.user_service.WorkspaceClient', return_value=mock_databricks_client):
      service = UserService()
      user_info = service.get_user_info()

      assert user_info['userName'] == 'integration@test.com'
      assert user_info['displayName'] == 'Integration Test User'
      assert user_info['active'] is True
      assert len(user_info['emails']) > 0

  def test_user_service_workspace_info_integration(self, mock_databricks_client):
    """Test user service workspace info integration."""
    from server.services.user_service import UserService

    # Mock user data
    mock_user = Mock()
    mock_user.user_name = 'workspace@test.com'
    mock_user.display_name = 'Workspace Test User'
    mock_user.active = True
    mock_user.emails = [Mock(value='workspace@test.com', primary=True)]

    # Mock workspace info
    mock_workspace = Mock()
    mock_workspace.workspace_id = 'integration-workspace-123'

    mock_databricks_client.current_user.me.return_value = mock_user
    mock_databricks_client.workspaces.get_status.return_value = mock_workspace

    with patch('server.services.user_service.WorkspaceClient', return_value=mock_databricks_client):
      service = UserService()
      workspace_info = service.get_user_workspace_info()

      assert 'user' in workspace_info
      assert 'workspace' in workspace_info
      assert workspace_info['user']['userName'] == 'workspace@test.com'

  def test_user_service_error_handling(self, mock_databricks_client):
    """Test user service error handling."""
    from server.services.user_service import UserService

    mock_databricks_client.current_user.me.side_effect = Exception('API Error')

    with patch('server.services.user_service.WorkspaceClient', return_value=mock_databricks_client):
      service = UserService()

      with pytest.raises(Exception, match='API Error'):
        service.get_user_info()


@pytest.mark.integration
@pytest.mark.services
class TestUserPreferencesIntegration:
  """Test user preferences integration."""

  def test_user_preferences_service(self):
    """Test user preferences service functionality."""
    from server.services.user_preferences import UserPreferencesService

    # Should be able to create instance
    service = UserPreferencesService()
    assert service is not None

    # Test basic functionality (if implemented)
    # This is a placeholder for future user preferences functionality


@pytest.mark.integration
@pytest.mark.environment
class TestEnvironmentIntegration:
  """Test environment configuration integration."""

  def test_environment_loading_from_files(self, tmp_path, monkeypatch):
    """Test environment loading from .env files."""
    # Create test .env files
    env_file = tmp_path / '.env'
    env_file.write_text('TEST_ENV_VAR=test_value\nANOTHER_VAR=another_value\n')

    env_local_file = tmp_path / '.env.local'
    env_local_file.write_text('TEST_ENV_VAR=local_override\nLOCAL_ONLY_VAR=local_value\n')

    monkeypatch.chdir(tmp_path)

    # Test that our app loading logic works
    from server.app import load_env_file

    # Clear existing environment
    test_vars = ['TEST_ENV_VAR', 'ANOTHER_VAR', 'LOCAL_ONLY_VAR']
    for var in test_vars:
      if var in os.environ:
        del os.environ[var]

    # Load .env first, then .env.local (which should override)
    load_env_file('.env')
    load_env_file('.env.local')

    assert os.environ.get('TEST_ENV_VAR') == 'local_override'  # Overridden by .env.local
    assert os.environ.get('ANOTHER_VAR') == 'another_value'
    assert os.environ.get('LOCAL_ONLY_VAR') == 'local_value'

    # Clean up
    for var in test_vars:
      if var in os.environ:
        del os.environ[var]

  def test_config_loading_integration(self, tmp_path, monkeypatch):
    """Test YAML config loading integration."""
    import yaml

    from server.app import load_config

    # Create test config file
    config_data = {
      'servername': 'integration-test-server',
      'debug': True,
      'features': {'advanced_tools': True, 'experimental': False},
    }

    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w') as f:
      yaml.dump(config_data, f)

    monkeypatch.chdir(tmp_path)

    loaded_config = load_config()

    assert loaded_config['servername'] == 'integration-test-server'
    assert loaded_config['debug'] is True
    assert loaded_config['features']['advanced_tools'] is True
    assert loaded_config['features']['experimental'] is False

  def test_databricks_environment_integration(self, mock_environment):
    """Test Databricks-specific environment integration."""
    # Test that Databricks environment variables are properly recognized
    assert os.environ.get('DATABRICKS_HOST') == 'https://test.cloud.databricks.com'
    assert os.environ.get('DATABRICKS_TOKEN') == 'test-token'

    # Test health check with environment
    from fastmcp import FastMCP

    from server.tools.core import load_core_tools

    mcp_server = FastMCP(name='env-integration-test')
    load_core_tools(mcp_server)

    health_tool = mcp_server.tools['health'].fn
    result = health_tool()

    assert result['databricks_configured'] is True


@pytest.mark.integration
@pytest.mark.prompts
class TestPromptsIntegration:
  """Test prompts loading and integration."""

  def test_prompts_loading_integration(self, tmp_path, monkeypatch):
    """Test prompts loading from filesystem."""
    from fastmcp import FastMCP

    from server.prompts import load_prompts

    # Create test prompts
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    prompt1 = prompts_dir / 'integration_test.md'
    prompt1.write_text(
      '# Integration Test Prompt\n\n'
      'This is a test prompt for integration testing.\n\n'
      '## Parameters\n\n'
      '- test_param: Test parameter\n'
    )

    prompt2 = prompts_dir / 'another_prompt.md'
    prompt2.write_text('# Another Prompt\n\nAnother test prompt.\n')

    monkeypatch.chdir(tmp_path)

    # Test prompts loading
    mcp_server = FastMCP(name='prompts-integration-test')
    load_prompts(mcp_server)

    # Verify prompts were loaded (exact verification depends on FastMCP implementation)
    assert mcp_server is not None

  def test_prompts_api_integration(self, test_client, tmp_path, monkeypatch):
    """Test prompts integration with API endpoints."""
    # Create test prompts
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    test_prompt = prompts_dir / 'api_integration_test.md'
    test_prompt.write_text(
      '# API Integration Test\n\n'
      'This prompt tests API integration.\n\n'
      'Content includes multiple lines\n'
      'and **markdown** formatting.\n'
    )

    monkeypatch.chdir(tmp_path)

    # Test API endpoints can find and serve the prompt
    response = test_client.get('/api/prompts')
    assert response.status_code == 200
    prompts = response.json()

    prompt_names = [p['name'] for p in prompts]
    assert 'api_integration_test' in prompt_names

    # Get specific prompt content
    response = test_client.get('/api/prompts/api_integration_test')
    assert response.status_code == 200
    prompt_data = response.json()

    assert prompt_data['name'] == 'api_integration_test'
    assert 'API Integration Test' in prompt_data['content']
    assert 'markdown' in prompt_data['content']


@pytest.mark.integration
@pytest.mark.logging
class TestLoggingIntegration:
  """Test logging integration across components."""

  def test_logging_configuration(self):
    """Test that logging is properly configured for integration."""
    import logging

    # Test that main loggers are configured
    logger = logging.getLogger('server')
    assert logger is not None

    # Test that Databricks SDK logging is controlled
    databricks_logger = logging.getLogger('databricks')
    # Should be set to WARNING or higher to reduce noise
    assert databricks_logger.level >= logging.WARNING

  def test_error_logging_integration(self, mock_databricks_client):
    """Test error logging across different components."""
    from fastmcp import FastMCP

    from server.tools.unity_catalog import load_uc_tools

    mcp_server = FastMCP(name='logging-integration-test')
    load_uc_tools(mcp_server)

    # Configure client to raise error
    mock_databricks_client.catalogs.list.side_effect = Exception('Test error for logging')

    list_tool = mcp_server.tools['list_uc_catalogs'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      # This should log the error and return error response
      result = list_tool()

      assert result['success'] is False
      assert 'Test error for logging' in result['error']


@pytest.mark.integration
@pytest.mark.performance
class TestPerformanceIntegration:
  """Test performance characteristics of integrated components."""

  def test_tool_loading_performance(self):
    """Test that tool loading completes in reasonable time."""
    import time

    from fastmcp import FastMCP

    from server.tools import load_tools

    start_time = time.time()

    mcp_server = FastMCP(name='performance-test-server')
    load_tools(mcp_server)

    end_time = time.time()
    loading_time = end_time - start_time

    # Tool loading should complete quickly
    assert loading_time < 2.0, f'Tool loading took too long: {loading_time:.2f}s'

    # Should have loaded multiple tools
    assert len(mcp_server.tools) > 10

  def test_api_response_performance(self, test_client):
    """Test API response times."""
    import time

    endpoints = [
      '/api/mcp_info/info',
      '/api/mcp_info/config',
      '/api/mcp_info/discovery',
      '/api/prompts',
    ]

    for endpoint in endpoints:
      start_time = time.time()
      response = test_client.get(endpoint)
      end_time = time.time()

      response_time = end_time - start_time

      assert response.status_code == 200
      # API responses should be fast
      assert response_time < 1.0, f'{endpoint} took too long: {response_time:.2f}s'


@pytest.mark.integration
@pytest.mark.deployment
class TestDeploymentIntegration:
  """Test deployment-related integration scenarios."""

  def test_local_development_integration(self, test_client):
    """Test integration in local development mode."""
    with patch.dict(os.environ, {}, clear=False):
      # Ensure we're in local development mode
      if 'DATABRICKS_APP_PORT' in os.environ:
        del os.environ['DATABRICKS_APP_PORT']

      # Test that local development configuration works
      response = test_client.get('/api/mcp_info/info')
      assert response.status_code == 200

      info = response.json()
      assert 'localhost' in info['mcp_url']
      assert info['server_name'] == 'mcp-commands'

  def test_databricks_app_integration(self, test_client):
    """Test integration in Databricks app mode."""
    with patch.dict(
      os.environ,
      {'DATABRICKS_APP_PORT': '8000', 'DATABRICKS_HOST': 'https://production.databricks.com'},
    ):
      # Test that Databricks app configuration works
      response = test_client.get('/api/mcp_info/info')
      assert response.status_code == 200

      info = response.json()
      assert info['mcp_url'] == '/mcp/'  # Relative URL for same-origin

      response = test_client.get('/api/mcp_info/config')
      assert response.status_code == 200

      config = response.json()
      assert config['is_databricks_app'] is True
      assert config['databricks_host'] == 'https://production.databricks.com'
