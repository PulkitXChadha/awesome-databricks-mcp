"""Unit tests for MCP proxy functionality."""

import json
import subprocess
from unittest.mock import Mock, patch

import pytest
import requests


@pytest.mark.unit
@pytest.mark.proxy
class TestTokenValidation:
  """Test token validation functionality."""

  def test_validate_token_success(self, mock_requests):
    """Test successful token validation."""
    from dba_mcp_proxy.mcp_client import validate_token

    mock_requests['get'].return_value.status_code = 200

    result = validate_token('valid-token', 'https://test.databricks.com')

    assert result is True
    mock_requests['get'].assert_called_once_with(
      'https://test.databricks.com/api/2.0/preview/scim/v2/Me',
      headers={'Authorization': 'Bearer valid-token'},
      timeout=5,
    )

  def test_validate_token_invalid(self, mock_requests):
    """Test token validation with invalid token."""
    from dba_mcp_proxy.mcp_client import validate_token

    mock_requests['get'].return_value.status_code = 401

    result = validate_token('invalid-token', 'https://test.databricks.com')

    assert result is False

  def test_validate_token_network_error(self, mock_requests):
    """Test token validation with network error."""
    from dba_mcp_proxy.mcp_client import validate_token

    mock_requests['get'].side_effect = requests.RequestException('Network error')

    result = validate_token('token', 'https://test.databricks.com')

    assert result is False

  def test_validate_token_timeout(self, mock_requests):
    """Test token validation with timeout."""
    from dba_mcp_proxy.mcp_client import validate_token

    mock_requests['get'].side_effect = requests.Timeout('Request timeout')

    result = validate_token('token', 'https://test.databricks.com')

    assert result is False


@pytest.mark.unit
@pytest.mark.proxy
class TestOAuthTokenRetrieval:
  """Test OAuth token retrieval functionality."""

  @patch('subprocess.run')
  def test_get_oauth_token_success(self, mock_subprocess):
    """Test successful OAuth token retrieval."""
    from dba_mcp_proxy.mcp_client import get_oauth_token

    # Mock successful token retrieval
    mock_result = Mock()
    mock_result.stdout = json.dumps({'access_token': 'test-token'})
    mock_subprocess.return_value = mock_result

    result = get_oauth_token('https://test.databricks.com')

    assert result == 'test-token'
    mock_subprocess.assert_called_once_with(
      [
        'uvx',
        '--from',
        'databricks-cli',
        'databricks',
        'auth',
        'token',
        '--host',
        'https://test.databricks.com',
      ],
      capture_output=True,
      text=True,
      check=True,
    )

  @patch('subprocess.run')
  def test_get_oauth_token_missing_token(self, mock_subprocess):
    """Test OAuth token retrieval when token is missing."""
    from dba_mcp_proxy.mcp_client import get_oauth_token

    # Mock response without access_token
    mock_result = Mock()
    mock_result.stdout = json.dumps({'some_other_field': 'value'})
    mock_subprocess.return_value = mock_result

    with pytest.raises(Exception, match='No access token in response'):
      get_oauth_token('https://test.databricks.com')

  @patch('subprocess.run')
  def test_get_oauth_token_with_login_retry(self, mock_subprocess):
    """Test OAuth token retrieval with automatic login retry."""
    from dba_mcp_proxy.mcp_client import get_oauth_token

    # First call fails (expired token), second call succeeds after login
    mock_subprocess.side_effect = [
      subprocess.CalledProcessError(1, 'cmd'),  # First auth token call fails
      Mock(),  # Login call succeeds
      Mock(stdout=json.dumps({'access_token': 'new-token'})),  # Second auth token call succeeds
    ]

    result = get_oauth_token('https://test.databricks.com')

    assert result == 'new-token'
    assert mock_subprocess.call_count == 3

  @patch('subprocess.run')
  def test_get_oauth_token_login_fails(self, mock_subprocess):
    """Test OAuth token retrieval when login fails."""
    from dba_mcp_proxy.mcp_client import get_oauth_token

    # Both auth token and login calls fail
    mock_subprocess.side_effect = [
      subprocess.CalledProcessError(1, 'auth token failed'),
      subprocess.CalledProcessError(1, 'auth login failed'),
    ]

    with pytest.raises(Exception, match='Failed to authenticate'):
      get_oauth_token('https://test.databricks.com')


@pytest.mark.unit
@pytest.mark.proxy
class TestMCPProxyInitialization:
  """Test MCP proxy initialization."""

  def test_mcp_proxy_init_basic(self):
    """Test basic MCP proxy initialization."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'https://app.databricksapps.com')

    assert proxy.databricks_host == 'https://test.databricks.com'
    assert proxy.app_url == 'https://app.databricksapps.com/mcp/'
    assert proxy.session_id is None
    assert proxy.initialized is False
    assert proxy.is_local is False

  def test_mcp_proxy_init_url_normalization(self):
    """Test URL normalization in MCP proxy initialization."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    # Test various URL formats
    test_cases = [
      ('https://app.databricks.com', 'https://app.databricks.com/mcp/'),
      ('https://app.databricks.com/', 'https://app.databricks.com/mcp/'),
      ('https://app.databricks.com/mcp/', 'https://app.databricks.com/mcp/'),
      ('http://localhost:8000', 'http://localhost:8000/mcp/'),
      ('http://localhost:8000/', 'http://localhost:8000/mcp/'),
    ]

    for input_url, expected_url in test_cases:
      proxy = MCPProxy('https://test.databricks.com', input_url)
      assert proxy.app_url == expected_url

  def test_mcp_proxy_init_empty_url(self):
    """Test MCP proxy initialization with empty URL."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    with pytest.raises(ValueError, match='URL argument is required'):
      MCPProxy('https://test.databricks.com', '')

  def test_mcp_proxy_local_detection(self):
    """Test local environment detection."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    # Local URLs
    local_proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')
    assert local_proxy.is_local is True

    # Remote URLs
    remote_proxy = MCPProxy('https://test.databricks.com', 'https://app.databricksapps.com')
    assert remote_proxy.is_local is False


@pytest.mark.unit
@pytest.mark.proxy
class TestMCPProxySessionInitialization:
  """Test MCP proxy session initialization."""

  @patch('dba_mcp_proxy.mcp_client.get_oauth_token')
  def test_initialize_session_remote(self, mock_get_token, mock_requests):
    """Test session initialization for remote environment."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    mock_get_token.return_value = 'test-oauth-token'

    # Mock session GET response
    mock_response = Mock()
    mock_response.headers = {'mcp-session-id': 'test-session-123'}
    mock_requests['get'].return_value = mock_response

    # Mock session POST responses
    mock_requests['post'].return_value = Mock()

    proxy = MCPProxy('https://test.databricks.com', 'https://app.databricksapps.com')

    with (
      patch.object(proxy.session, 'get', return_value=mock_response),
      patch.object(proxy.session, 'post') as mock_post,
    ):
      proxy._initialize_session()

      assert proxy.initialized is True
      assert proxy.session_id == 'test-session-123'
      assert proxy._oauth_token == 'test-oauth-token'

      # Should have made two POST calls (initialize + initialized notification)
      assert mock_post.call_count == 2

  def test_initialize_session_local(self, mock_requests):
    """Test session initialization for local environment."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    # Mock session responses
    mock_response = Mock()
    mock_response.headers = {'mcp-session-id': 'local-session-123'}

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    with patch.object(proxy.session, 'get', return_value=mock_response):
      proxy._initialize_session()

      assert proxy.initialized is True
      assert proxy.session_id == 'local-session-123'
      assert proxy._oauth_token == 'local-test-token'

  def test_initialize_session_idempotent(self, mock_requests):
    """Test that session initialization is idempotent."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')
    proxy.initialized = True  # Mark as already initialized

    with (
      patch.object(proxy.session, 'get') as mock_get,
      patch.object(proxy.session, 'post') as mock_post,
    ):
      proxy._initialize_session()

      # Should not make any requests if already initialized
      mock_get.assert_not_called()
      mock_post.assert_not_called()


@pytest.mark.unit
@pytest.mark.proxy
class TestMCPProxyRequestHandling:
  """Test MCP proxy request handling."""

  def test_proxy_request_success_json(self, mock_requests):
    """Test successful request proxying with JSON response."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')
    proxy.initialized = True
    proxy._oauth_token = 'test-token'
    proxy.session_id = 'test-session'

    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'result': 'success'}
    mock_response.text = '{"result": "success"}'

    with patch.object(proxy.session, 'post', return_value=mock_response):
      request_data = {'jsonrpc': '2.0', 'id': 'test-id', 'method': 'test_method', 'params': {}}

      result = proxy.proxy_request(request_data)

      assert result == {'result': 'success'}

  def test_proxy_request_success_sse(self, mock_requests):
    """Test successful request proxying with SSE response."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')
    proxy.initialized = True
    proxy._oauth_token = 'test-token'

    # Mock SSE response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'event: message\ndata: {"result": "sse_success"}\n\n'

    with patch.object(proxy.session, 'post', return_value=mock_response):
      request_data = {'jsonrpc': '2.0', 'id': 'test-id', 'method': 'test_method'}

      result = proxy.proxy_request(request_data)

      assert result == {'result': 'sse_success'}

  def test_proxy_request_http_error(self, mock_requests):
    """Test request proxying with HTTP error."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')
    proxy.initialized = True
    proxy._oauth_token = 'test-token'

    # Mock error response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'

    with patch.object(proxy.session, 'post', return_value=mock_response):
      request_data = {'jsonrpc': '2.0', 'id': 'test-id', 'method': 'test_method'}

      result = proxy.proxy_request(request_data)

      assert result['jsonrpc'] == '2.0'
      assert result['id'] == 'test-id'
      assert 'error' in result
      assert result['error']['code'] == 500

  def test_proxy_request_exception(self, mock_requests):
    """Test request proxying with exception."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')
    proxy.initialized = True
    proxy._oauth_token = 'test-token'

    with patch.object(proxy.session, 'post', side_effect=Exception('Connection failed')):
      request_data = {'jsonrpc': '2.0', 'id': 'test-id', 'method': 'test_method'}

      result = proxy.proxy_request(request_data)

      assert result['jsonrpc'] == '2.0'
      assert result['id'] == 'test-id'
      assert 'error' in result
      assert result['error']['code'] == -32000
      assert 'Connection failed' in result['error']['message']

  def test_proxy_request_initializes_session(self, mock_requests):
    """Test that proxy_request initializes session when needed."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    with (
      patch.object(proxy, '_initialize_session') as mock_init,
      patch.object(proxy.session, 'post') as mock_post,
    ):
      mock_response = Mock()
      mock_response.status_code = 200
      mock_response.json.return_value = {'result': 'success'}
      mock_response.text = '{"result": "success"}'
      mock_post.return_value = mock_response

      proxy._oauth_token = 'test-token'  # Set token to avoid initialization logic

      request_data = {'jsonrpc': '2.0', 'id': 'test-id', 'method': 'test_method'}
      proxy.proxy_request(request_data)

      # Should have called initialize_session
      mock_init.assert_called_once()


@pytest.mark.unit
@pytest.mark.proxy
class TestMCPProxyMainLoop:
  """Test MCP proxy main loop functionality."""

  def test_run_proxy_single_request(self):
    """Test proxy run with single request."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    test_request = {'jsonrpc': '2.0', 'id': 'test', 'method': 'test_method'}
    test_response = {'jsonrpc': '2.0', 'id': 'test', 'result': 'success'}

    with (
      patch('sys.stdin', [json.dumps(test_request)]),
      patch.object(proxy, 'proxy_request', return_value=test_response) as mock_proxy,
      patch('builtins.print') as mock_print,
    ):
      # Run will continue indefinitely, so we'll test just the iteration logic
      # by mocking stdin to return one line then raise StopIteration
      def mock_stdin():
        yield json.dumps(test_request)

      with patch('sys.stdin', mock_stdin()):
        try:
          proxy.run()
        except StopIteration:
          pass

      mock_proxy.assert_called_once_with(test_request)
      mock_print.assert_called_once_with(json.dumps(test_response), flush=True)

  def test_run_proxy_invalid_json(self):
    """Test proxy run with invalid JSON input."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    with patch('sys.stdin', ['invalid json']), patch('builtins.print') as mock_print:

      def mock_stdin():
        yield 'invalid json'

      with patch('sys.stdin', mock_stdin()):
        try:
          proxy.run()
        except StopIteration:
          pass

      # Should print error response
      mock_print.assert_called_once()
      printed_response = json.loads(mock_print.call_args[0][0])
      assert 'error' in printed_response
      assert printed_response['error']['code'] == -32700  # Parse error


@pytest.mark.unit
@pytest.mark.proxy
class TestMCPProxyCommandLine:
  """Test MCP proxy command line interface."""

  def test_main_function_argument_parsing(self):
    """Test main function argument parsing."""
    from dba_mcp_proxy.mcp_client import main

    test_args = [
      'script_name',
      '--databricks-host',
      'https://test.databricks.com',
      '--databricks-app-url',
      'https://app.databricksapps.com',
    ]

    with (
      patch('sys.argv', test_args),
      patch('dba_mcp_proxy.mcp_client.MCPProxy') as mock_proxy_class,
      patch('builtins.print'),
    ):
      mock_proxy = Mock()
      mock_proxy_class.return_value = mock_proxy

      main()

      mock_proxy_class.assert_called_once_with(
        'https://test.databricks.com', 'https://app.databricksapps.com'
      )
      mock_proxy.run.assert_called_once()

  def test_main_function_missing_arguments(self):
    """Test main function with missing arguments."""
    from dba_mcp_proxy.mcp_client import main

    test_args = ['script_name']  # Missing required arguments

    with patch('sys.argv', test_args), patch('builtins.print'):
      # Should exit due to missing arguments
      with pytest.raises(SystemExit):
        main()

  def test_main_function_proxy_error(self):
    """Test main function when proxy initialization fails."""
    from dba_mcp_proxy.mcp_client import main

    test_args = [
      'script_name',
      '--databricks-host',
      'https://test.databricks.com',
      '--databricks-app-url',
      'https://app.databricksapps.com',
    ]

    with (
      patch('sys.argv', test_args),
      patch('dba_mcp_proxy.mcp_client.MCPProxy', side_effect=Exception('Proxy failed')),
      patch('sys.exit') as mock_exit,
      patch('builtins.print'),
    ):
      main()

      mock_exit.assert_called_once_with(1)


@pytest.mark.integration
@pytest.mark.proxy
class TestMCPProxyIntegration:
  """Integration tests for MCP proxy."""

  def test_proxy_initialization_end_to_end(self, mock_requests):
    """Test complete proxy initialization flow."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    # Setup mocks for successful initialization
    mock_response = Mock()
    mock_response.headers = {'mcp-session-id': 'integration-session'}
    mock_requests['get'].return_value = mock_response
    mock_requests['post'].return_value = Mock()

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    with (
      patch.object(proxy.session, 'get', return_value=mock_response),
      patch.object(proxy.session, 'post'),
    ):
      proxy._initialize_session()

      assert proxy.initialized is True
      assert proxy.session_id == 'integration-session'
      assert proxy._oauth_token == 'local-test-token'

  def test_proxy_request_flow_end_to_end(self, mock_requests):
    """Test complete request proxying flow."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    # Mock initialization
    init_response = Mock()
    init_response.headers = {'mcp-session-id': 'test-session'}

    # Mock request response
    request_response = Mock()
    request_response.status_code = 200
    request_response.json.return_value = {'result': 'end_to_end_success'}
    request_response.text = '{"result": "end_to_end_success"}'

    with (
      patch.object(proxy.session, 'get', return_value=init_response),
      patch.object(proxy.session, 'post', return_value=request_response),
    ):
      test_request = {
        'jsonrpc': '2.0',
        'id': 'integration-test',
        'method': 'test_method',
        'params': {'test': 'data'},
      }

      result = proxy.proxy_request(test_request)

      assert result == {'result': 'end_to_end_success'}
      assert proxy.initialized is True
