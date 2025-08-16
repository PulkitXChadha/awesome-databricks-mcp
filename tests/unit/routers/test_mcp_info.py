"""Unit tests for MCP info router endpoints."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
@pytest.mark.api
class TestMCPInfoRouter:
  """Test MCP info router endpoints."""

  def test_get_mcp_info_local_development(self, test_client):
    """Test MCP info endpoint in local development mode."""
    with patch.dict(os.environ, {}, clear=False):
      # Ensure DATABRICKS_APP_PORT is not set (local development)
      if 'DATABRICKS_APP_PORT' in os.environ:
        del os.environ['DATABRICKS_APP_PORT']

      response = test_client.get('/api/mcp_info/info')

    assert response.status_code == 200
    data = response.json()

    assert data['mcp_url'] == 'http://localhost:8001/mcp/'
    assert data['server_name'] == 'mcp-commands'
    assert data['transport'] == 'http'
    assert 'capabilities' in data
    assert data['capabilities']['prompts'] is True
    assert data['capabilities']['tools'] is True
    assert 'client_path' in data

  def test_get_mcp_info_databricks_app(self, test_client):
    """Test MCP info endpoint in Databricks app mode."""
    with patch.dict(os.environ, {'DATABRICKS_APP_PORT': '8000'}):
      response = test_client.get('/api/mcp_info/info')

    assert response.status_code == 200
    data = response.json()

    assert data['mcp_url'] == '/mcp/'  # Relative URL for same-origin
    assert data['server_name'] == 'mcp-commands'
    assert data['transport'] == 'http'
    assert data['capabilities']['prompts'] is True
    assert data['capabilities']['tools'] is True

  def test_get_mcp_discovery_success(self, test_client):
    """Test MCP discovery endpoint with mocked MCP server."""
    # Mock the MCP server objects
    mock_prompt = Mock()
    mock_prompt.key = 'test_prompt'
    mock_prompt.description = 'Test prompt description'

    mock_tool = Mock()
    mock_tool.key = 'test_tool'
    mock_tool.description = 'Test tool description'

    mock_prompt_manager = Mock()
    mock_prompt_manager.list_prompts = Mock(return_value=[mock_prompt])

    mock_tool_manager = Mock()
    mock_tool_manager.list_tools = Mock(return_value=[mock_tool])

    with (
      patch('server.routers.mcp_info.mcp') as mock_mcp,
      patch('server.routers.mcp_info.servername', 'test-server'),
    ):
      mock_mcp._prompt_manager = mock_prompt_manager
      mock_mcp._tool_manager = mock_tool_manager

      response = test_client.get('/api/mcp_info/discovery')

    assert response.status_code == 200
    data = response.json()

    assert 'prompts' in data
    assert 'tools' in data
    assert 'servername' in data
    assert data['servername'] == 'test-server'

    assert len(data['prompts']) == 1
    assert data['prompts'][0]['name'] == 'test_prompt'
    assert data['prompts'][0]['description'] == 'Test prompt description'

    assert len(data['tools']) == 1
    assert data['tools'][0]['name'] == 'test_tool'
    assert data['tools'][0]['description'] == 'Test tool description'

  def test_get_mcp_discovery_no_managers(self, test_client):
    """Test MCP discovery when managers are not available."""
    with (
      patch('server.routers.mcp_info.mcp') as mock_mcp,
      patch('server.routers.mcp_info.servername', 'test-server'),
    ):
      # MCP server without _prompt_manager and _tool_manager
      delattr(mock_mcp, '_prompt_manager') if hasattr(mock_mcp, '_prompt_manager') else None
      delattr(mock_mcp, '_tool_manager') if hasattr(mock_mcp, '_tool_manager') else None

      response = test_client.get('/api/mcp_info/discovery')

    assert response.status_code == 200
    data = response.json()

    assert data['prompts'] == []
    assert data['tools'] == []
    assert data['servername'] == 'test-server'

  def test_get_mcp_discovery_auto_generated_descriptions(self, test_client):
    """Test MCP discovery with auto-generated descriptions."""
    # Mock objects without descriptions
    mock_prompt = Mock()
    mock_prompt.key = 'test_prompt_name'
    mock_prompt.description = None

    mock_tool = Mock()
    mock_tool.key = 'another_tool_name'
    mock_tool.description = None

    mock_prompt_manager = Mock()
    mock_prompt_manager.list_prompts = Mock(return_value=[mock_prompt])

    mock_tool_manager = Mock()
    mock_tool_manager.list_tools = Mock(return_value=[mock_tool])

    with (
      patch('server.routers.mcp_info.mcp') as mock_mcp,
      patch('server.routers.mcp_info.servername', 'test-server'),
    ):
      mock_mcp._prompt_manager = mock_prompt_manager
      mock_mcp._tool_manager = mock_tool_manager

      response = test_client.get('/api/mcp_info/discovery')

    assert response.status_code == 200
    data = response.json()

    # Descriptions should be auto-generated from keys
    assert data['prompts'][0]['description'] == 'Test Prompt Name'
    assert data['tools'][0]['description'] == 'Another Tool Name'

  def test_get_mcp_config_local_development(self, test_client):
    """Test MCP config endpoint in local development."""
    with patch.dict(os.environ, {'DATABRICKS_HOST': 'https://test.databricks.com'}, clear=False):
      # Ensure DATABRICKS_APP_PORT is not set
      if 'DATABRICKS_APP_PORT' in os.environ:
        del os.environ['DATABRICKS_APP_PORT']

      with patch('server.routers.mcp_info.servername', 'test-mcp-server'):
        response = test_client.get('/api/mcp_info/config')

    assert response.status_code == 200
    data = response.json()

    assert data['servername'] == 'test-mcp-server'
    assert data['databricks_host'] == 'https://test.databricks.com'
    assert data['is_databricks_app'] is False
    assert 'client_path' in data

  def test_get_mcp_config_databricks_app(self, test_client):
    """Test MCP config endpoint in Databricks app mode."""
    with patch.dict(
      os.environ,
      {'DATABRICKS_HOST': 'https://production.databricks.com', 'DATABRICKS_APP_PORT': '8000'},
    ):
      with patch('server.routers.mcp_info.servername', 'production-mcp'):
        response = test_client.get('/api/mcp_info/config')

    assert response.status_code == 200
    data = response.json()

    assert data['servername'] == 'production-mcp'
    assert data['databricks_host'] == 'https://production.databricks.com'
    assert data['is_databricks_app'] is True
    assert 'client_path' in data

  def test_get_mcp_prompt_content_success(self, test_client, tmp_path, monkeypatch):
    """Test successful prompt content retrieval."""
    # Create a temporary prompts directory with a test prompt
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    test_prompt = prompts_dir / 'test_prompt.md'
    test_prompt.write_text('# Test Prompt\n\nThis is a test prompt content.')

    # Change to the temp directory so prompts are found
    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/mcp_info/prompt/test_prompt')

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'test_prompt'
    assert 'Test Prompt' in data['content']
    assert 'test prompt content' in data['content']

  def test_get_mcp_prompt_content_not_found(self, test_client, tmp_path, monkeypatch):
    """Test prompt content retrieval for non-existent prompt."""
    # Create empty prompts directory
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/mcp_info/prompt/nonexistent')

    assert response.status_code == 404
    data = response.json()
    assert 'not found' in data['detail']

  def test_get_mcp_prompt_content_no_prompts_dir(self, test_client, tmp_path, monkeypatch):
    """Test prompt content retrieval when prompts directory doesn't exist."""
    # No prompts directory created
    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/mcp_info/prompt/any_prompt')

    assert response.status_code == 404
    data = response.json()
    assert 'not found' in data['detail']


@pytest.mark.unit
@pytest.mark.api
class TestMCPInfoHelpers:
  """Test helper functionality in MCP info router."""

  def test_client_path_generation(self, test_client):
    """Test that client path is correctly generated."""
    response = test_client.get('/api/mcp_info/info')

    assert response.status_code == 200
    data = response.json()

    client_path = data['client_path']
    assert client_path.endswith('mcp_databricks_client.py')
    assert Path(client_path).name == 'mcp_databricks_client.py'

  def test_environment_detection_logic(self):
    """Test environment detection logic for Databricks apps."""
    # Test local development detection
    with patch.dict(os.environ, {}, clear=False):
      if 'DATABRICKS_APP_PORT' in os.environ:
        del os.environ['DATABRICKS_APP_PORT']

      is_databricks_app = os.environ.get('DATABRICKS_APP_PORT') is not None
      assert is_databricks_app is False

    # Test Databricks app detection
    with patch.dict(os.environ, {'DATABRICKS_APP_PORT': '8000'}):
      is_databricks_app = os.environ.get('DATABRICKS_APP_PORT') is not None
      assert is_databricks_app is True


@pytest.mark.integration
@pytest.mark.api
class TestMCPInfoRouterIntegration:
  """Integration tests for MCP info router."""

  def test_all_mcp_info_endpoints_accessible(self, test_client):
    """Test that all MCP info endpoints are accessible."""
    endpoints = ['/api/mcp_info/info', '/api/mcp_info/discovery', '/api/mcp_info/config']

    for endpoint in endpoints:
      response = test_client.get(endpoint)
      assert response.status_code == 200
      assert response.headers['content-type'] == 'application/json'

  def test_mcp_info_responses_have_required_fields(self, test_client):
    """Test that MCP info responses contain required fields."""
    # Test info endpoint
    response = test_client.get('/api/mcp_info/info')
    data = response.json()
    required_fields = ['mcp_url', 'server_name', 'transport', 'capabilities']
    for field in required_fields:
      assert field in data

    # Test discovery endpoint
    response = test_client.get('/api/mcp_info/discovery')
    data = response.json()
    required_fields = ['prompts', 'tools', 'servername']
    for field in required_fields:
      assert field in data

    # Test config endpoint
    response = test_client.get('/api/mcp_info/config')
    data = response.json()
    required_fields = ['servername', 'databricks_host', 'is_databricks_app']
    for field in required_fields:
      assert field in data

  def test_mcp_info_consistency_across_environments(self, test_client):
    """Test MCP info consistency across different environment configurations."""
    # Test in local development mode
    with patch.dict(os.environ, {'DATABRICKS_HOST': 'https://local.databricks.com'}, clear=False):
      if 'DATABRICKS_APP_PORT' in os.environ:
        del os.environ['DATABRICKS_APP_PORT']

      local_info = test_client.get('/api/mcp_info/info').json()
      local_config = test_client.get('/api/mcp_info/config').json()

    # Test in Databricks app mode
    with patch.dict(
      os.environ, {'DATABRICKS_HOST': 'https://prod.databricks.com', 'DATABRICKS_APP_PORT': '8000'}
    ):
      app_info = test_client.get('/api/mcp_info/info').json()
      app_config = test_client.get('/api/mcp_info/config').json()

    # Server name and transport should be consistent
    assert local_info['server_name'] == app_info['server_name']
    assert local_info['transport'] == app_info['transport']

    # But URLs and app detection should differ
    assert local_info['mcp_url'] != app_info['mcp_url']
    assert local_config['is_databricks_app'] != app_config['is_databricks_app']
