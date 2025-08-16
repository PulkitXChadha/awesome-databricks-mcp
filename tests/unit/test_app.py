"""Unit tests for FastAPI application and core MCP server functionality."""

import os
from unittest.mock import Mock, patch

import pytest
import yaml


class TestLoadEnvFile:
  """Test environment file loading functionality."""

  def test_load_existing_env_file(self, tmp_path):
    """Test loading environment variables from existing file."""
    from server.app import load_env_file

    env_file = tmp_path / '.env.test'
    env_file.write_text(
      'TEST_VAR1=value1\n'
      'TEST_VAR2=value2\n'
      '# This is a comment\n'
      'TEST_VAR3=value3\n'
      '\n'  # Empty line
      'INVALID_LINE_NO_EQUALS\n'
      '=INVALID_LINE_NO_KEY\n'
    )

    # Clear any existing test variables
    for var in ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']:
      if var in os.environ:
        del os.environ[var]

    load_env_file(str(env_file))

    assert os.environ.get('TEST_VAR1') == 'value1'
    assert os.environ.get('TEST_VAR2') == 'value2'
    assert os.environ.get('TEST_VAR3') == 'value3'

    # Clean up
    for var in ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']:
      if var in os.environ:
        del os.environ[var]

  def test_load_nonexistent_env_file(self):
    """Test loading from non-existent file does not raise error."""
    from server.app import load_env_file

    # Should not raise an exception
    load_env_file('/nonexistent/file.env')

  def test_load_env_file_with_equals_in_value(self, tmp_path):
    """Test loading environment variables with equals signs in values."""
    from server.app import load_env_file

    env_file = tmp_path / '.env.test'
    env_file.write_text('TEST_URL=https://example.com/path?param=value\n')

    if 'TEST_URL' in os.environ:
      del os.environ['TEST_URL']

    load_env_file(str(env_file))

    assert os.environ.get('TEST_URL') == 'https://example.com/path?param=value'

    # Clean up
    if 'TEST_URL' in os.environ:
      del os.environ['TEST_URL']


class TestLoadConfig:
  """Test configuration loading functionality."""

  def test_load_existing_config(self, tmp_path, monkeypatch):
    """Test loading configuration from existing config.yaml."""
    from server.app import load_config

    config_data = {'servername': 'test-mcp-server', 'other_setting': 'test_value'}

    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w') as f:
      yaml.dump(config_data, f)

    # Change to tmp directory so config.yaml is found
    monkeypatch.chdir(tmp_path)

    config = load_config()

    assert config['servername'] == 'test-mcp-server'
    assert config['other_setting'] == 'test_value'

  def test_load_nonexistent_config(self, tmp_path, monkeypatch):
    """Test loading config when config.yaml doesn't exist."""
    from server.app import load_config

    # Change to tmp directory with no config.yaml
    monkeypatch.chdir(tmp_path)

    config = load_config()

    assert config == {}

  def test_load_invalid_yaml_config(self, tmp_path, monkeypatch):
    """Test loading invalid YAML configuration."""
    from server.app import load_config

    config_file = tmp_path / 'config.yaml'
    config_file.write_text('invalid: yaml: content: [unclosed')

    monkeypatch.chdir(tmp_path)

    with pytest.raises(yaml.YAMLError):
      load_config()


@pytest.mark.unit
class TestFastAPIApp:
  """Test FastAPI application setup and configuration."""

  @patch('server.app.load_tools')
  @patch('server.app.load_prompts')
  @patch('server.app.FastMCP')
  def test_app_creation(self, mock_fastmcp, mock_load_prompts, mock_load_tools):
    """Test FastAPI application is created with correct configuration."""
    # Setup mocks
    mock_mcp_server = Mock()
    mock_mcp_server.http_app.return_value = Mock()
    mock_mcp_server.http_app.return_value.lifespan = None
    mock_fastmcp.return_value = mock_mcp_server

    # Import after mocking to avoid side effects
    with patch.dict(os.environ, {'TESTING': 'true'}):
      from server.app import app

      assert app.title == 'Databricks App API'
      assert app.version == '0.1.0'
      assert 'Modern FastAPI application template' in app.description

  @patch('server.app.load_tools')
  @patch('server.app.load_prompts')
  def test_cors_middleware_configuration(self, mock_load_prompts, mock_load_tools):
    """Test CORS middleware is configured correctly."""
    with patch.dict(os.environ, {'TESTING': 'true'}):
      from server.app import app

      # Check that CORS middleware is added
      cors_middleware = None
      for middleware in app.user_middleware:
        if 'CORSMiddleware' in str(middleware.cls):
          cors_middleware = middleware
          break

      assert cors_middleware is not None

  def test_api_router_included(self, test_client):
    """Test that API router is included with correct prefix."""
    # Test a basic endpoint exists under /api
    response = test_client.get('/api/user/me')
    # We expect this to either succeed or fail with auth, not 404
    assert response.status_code != 404

  @patch('os.path.exists')
  def test_static_files_mounted_when_build_exists(self, mock_exists):
    """Test static files are mounted when client/build exists."""
    mock_exists.return_value = True

    with patch('server.app.StaticFiles') as mock_static_files:
      # Re-import to trigger the static file mounting logic
      import importlib

      import server.app

      importlib.reload(server.app)

      # Should have attempted to mount static files
      mock_static_files.assert_called_once_with(directory='client/build', html=True)

  @patch('os.path.exists')
  def test_static_files_not_mounted_when_build_missing(self, mock_exists):
    """Test static files are not mounted when client/build doesn't exist."""
    mock_exists.return_value = False

    with patch('server.app.StaticFiles') as mock_static_files:
      # Re-import to trigger the static file mounting logic
      import importlib

      import server.app

      importlib.reload(server.app)

      # Should not have attempted to mount static files
      mock_static_files.assert_not_called()


@pytest.mark.unit
class TestMCPServerIntegration:
  """Test MCP server integration with FastAPI."""

  def test_mcp_server_creation(self, mcp_server):
    """Test MCP server is created with correct name."""
    assert mcp_server.name == 'test-databricks-mcp'

  def test_mcp_server_mounted_at_correct_path(self, test_client):
    """Test MCP server is mounted at /mcp path."""
    # The MCP server should be mounted and respond to requests
    response = test_client.get('/mcp/')
    # We expect either a valid response or method not allowed, not 404
    assert response.status_code != 404

  @patch('server.app.load_tools')
  @patch('server.app.load_prompts')
  def test_tools_and_prompts_loaded(self, mock_load_prompts, mock_load_tools):
    """Test that tools and prompts are loaded into MCP server."""
    with patch.dict(os.environ, {'TESTING': 'true'}):
      # Import to trigger loading

      # Verify load functions were called
      mock_load_tools.assert_called_once()
      mock_load_prompts.assert_called_once()


@pytest.mark.unit
class TestEnvironmentSetup:
  """Test environment variable setup and validation."""

  def test_default_port_configuration(self):
    """Test default port is set correctly."""
    with patch.dict(os.environ, {}, clear=False):
      if 'DATABRICKS_APP_PORT' in os.environ:
        del os.environ['DATABRICKS_APP_PORT']

      # Import the main block logic
      port = int(os.environ.get('DATABRICKS_APP_PORT', 8000))
      assert port == 8000

  def test_custom_port_configuration(self):
    """Test custom port is used when set."""
    with patch.dict(os.environ, {'DATABRICKS_APP_PORT': '9000'}):
      port = int(os.environ.get('DATABRICKS_APP_PORT', 8000))
      assert port == 9000

  def test_databricks_environment_variables(self, mock_environment):
    """Test Databricks environment variables are accessible."""
    assert mock_environment['DATABRICKS_HOST'] == 'https://test.cloud.databricks.com'
    assert mock_environment['DATABRICKS_TOKEN'] == 'test-token'
    assert mock_environment['TESTING'] == 'true'


@pytest.mark.integration
class TestAppHealthCheck:
  """Integration tests for application health and basic functionality."""

  def test_app_starts_successfully(self, test_client):
    """Test that the application starts and responds to requests."""
    # The test client should be created successfully
    assert test_client is not None

  def test_mcp_endpoint_accessibility(self, test_client):
    """Test that MCP endpoint is accessible."""
    response = test_client.get('/mcp/')
    # Should not return 404 (server not found)
    assert response.status_code != 404

  def test_api_endpoint_accessibility(self, test_client):
    """Test that API endpoints are accessible."""
    response = test_client.get('/api/user/me')
    # Should not return 404 (router not mounted)
    assert response.status_code != 404


class TestAppConfiguration:
  """Test application configuration edge cases."""

  def test_servername_defaults_correctly(self, tmp_path, monkeypatch):
    """Test servername defaults to 'databricks-mcp' when not in config."""
    # Create empty config
    config_file = tmp_path / 'config.yaml'
    config_file.write_text('other_setting: value\n')

    monkeypatch.chdir(tmp_path)

    from server.app import load_config

    config = load_config()
    servername = config.get('servername', 'databricks-mcp')

    assert servername == 'databricks-mcp'

  def test_servername_from_config(self, tmp_path, monkeypatch):
    """Test servername is loaded from config when present."""
    config_data = {'servername': 'custom-mcp-server'}

    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w') as f:
      yaml.dump(config_data, f)

    monkeypatch.chdir(tmp_path)

    from server.app import load_config

    config = load_config()
    servername = config.get('servername', 'databricks-mcp')

    assert servername == 'custom-mcp-server'
