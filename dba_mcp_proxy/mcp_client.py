#!/usr/bin/env -S uv run python
"""Pure MCP Protocol Proxy for Databricks App.

This implements the MCP protocol directly to create a true transparent proxy
that forwards all requests to the remote Databricks App MCP server.

Usage:
    mcp_databricks_client.py --databricks-host <HOST> --databricks-app-url <URL>

    --databricks-host: Your Databricks workspace URL (e.g., https://workspace.cloud.databricks.com)
    --databricks-app-url: The Databricks App URL
    - Full URL like http://localhost:8000/mcp/sse/
    - Or base URL like https://app.databricksapps.com (will append /mcp/sse/)
"""

import argparse
import json
import subprocess
import sys

import requests


def validate_token(token, databricks_host):
  """Validate if a specific token is still valid."""
  try:
    # Use a lightweight endpoint that just checks auth
    response = requests.get(
      f'{databricks_host}/api/2.0/preview/scim/v2/Me',
      headers={'Authorization': f'Bearer {token}'},
      timeout=5,
    )
    return response.status_code == 200
  except Exception:
    return False


def get_oauth_token(databricks_host):
  """Get OAuth token from Databricks CLI, handling expired tokens automatically."""
  try:
    # First try to get token directly from Databricks CLI
    result = subprocess.run(
      ['uvx', '--from', 'databricks-cli', 'databricks', 'auth', 'token', '--host', databricks_host],
      capture_output=True,
      text=True,
      check=True,
    )
    token = json.loads(result.stdout).get('access_token')
    if token:
      return token
    else:
      raise Exception('No access token in response')
  except Exception:
    # Token might be expired or not exist, try OAuth login which handles token generation
    print(f'Getting fresh OAuth token for {databricks_host}...', file=sys.stderr)
    try:
      # OAuth login should handle token generation automatically
      subprocess.run(
        ['uvx', '--from', 'databricks-cli', 'databricks', 'auth', 'login', '--host', databricks_host],
        capture_output=True,
        text=True,
        check=True,
      )

      # Get the token that was generated during login
      result = subprocess.run(
        ['uvx', '--from', 'databricks-cli', 'databricks', 'auth', 'token', '--host', databricks_host],
        capture_output=True,
        text=True,
        check=True,
      )
      token = json.loads(result.stdout).get('access_token')
      if token:
        print('OAuth authentication successful', file=sys.stderr)
        return token
      else:
        raise Exception('No access token after login')
    except Exception as login_error:
      raise Exception(f'Failed to authenticate: {login_error}')


class MCPProxy:
  """Pure MCP Protocol Proxy."""

  def __init__(self, databricks_host, url):
    if not url:
      raise ValueError('URL argument is required')

    # Store databricks_host for OAuth token retrieval
    self.databricks_host = databricks_host

    # Ensure URL ends with /mcp/ for the MCP endpoint
    if not url.endswith('/mcp/'):
      if url.endswith('/'):
        url = url + 'mcp/'
      else:
        url = url + '/mcp/'
    self.app_url = url

    self.session_id = None
    self.initialized = False
    self.session = requests.Session()
    self.is_local = self.app_url.startswith('http://localhost')
    self._oauth_token = None  # Cache the OAuth token

  def _initialize_session(self):
    """Initialize MCP session with proper handshake."""
    if self.initialized:
      return

    # Get appropriate token based on environment
    if self.is_local:
      self._oauth_token = 'local-test-token'
    else:
      # Check if we have a valid cached token
      if not self._oauth_token or not validate_token(self._oauth_token, self.databricks_host):
        self._oauth_token = get_oauth_token(self.databricks_host)
    oauth_token = self._oauth_token

    headers = {
      'Authorization': f'Bearer {oauth_token}',
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream',
    }

    # Get session ID
    response = self.session.get(self.app_url, headers=headers)
    self.session_id = response.headers.get('mcp-session-id')

    if self.session_id:
      headers['mcp-session-id'] = self.session_id

    # Initialize MCP session
    init_request = {
      'jsonrpc': '2.0',
      'id': 'initialize',
      'method': 'initialize',
      'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {'roots': {'listChanged': True}, 'sampling': {}},
        'clientInfo': {'name': 'databricks-mcp-proxy', 'version': '1.0.0'},
      },
    }

    self.session.post(self.app_url, headers=headers, json=init_request)

    # Send initialized notification
    initialized_request = {'jsonrpc': '2.0', 'method': 'notifications/initialized'}

    self.session.post(self.app_url, headers=headers, json=initialized_request)
    self.initialized = True

  def proxy_request(self, request_data):
    """Proxy an MCP request to the remote server."""
    try:
      # Initialize session if needed
      self._initialize_session()

      # Use cached token
      oauth_token = self._oauth_token

      headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      }

      if self.session_id:
        headers['mcp-session-id'] = self.session_id

      response = self.session.post(self.app_url, headers=headers, json=request_data)

      if response.status_code == 200:
        # Handle SSE response
        if 'event: message' in response.text:
          for line in response.text.split('\n'):
            if line.startswith('data: '):
              try:
                return json.loads(line[6:])
              except json.JSONDecodeError:
                continue
        else:
          return response.json()

      return {
        'jsonrpc': '2.0',
        'id': request_data.get('id'),
        'error': {
          'code': response.status_code,
          'message': f'HTTP {response.status_code}: {response.text[:100]}',
        },
      }

    except Exception as e:
      return {
        'jsonrpc': '2.0',
        'id': request_data.get('id'),
        'error': {'code': -32000, 'message': str(e)},
      }

  def run(self):
    """Run the MCP proxy server using stdio transport."""
    # Main loop - read from stdin, proxy to remote, write to stdout
    try:
      for line in sys.stdin:
        line = line.strip()
        if not line:
          continue

        try:
          request = json.loads(line)
          response = self.proxy_request(request)
          print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
          error_response = {
            'jsonrpc': '2.0',
            'id': None,
            'error': {'code': -32700, 'message': 'Parse error'},
          }
          print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
      pass
    except Exception as e:
      error_response = {
        'jsonrpc': '2.0',
        'id': None,
        'error': {'code': -32000, 'message': f'Proxy error: {e}'},
      }
      print(json.dumps(error_response), flush=True)


def main():
  """Main entry point for the MCP proxy."""
  parser = argparse.ArgumentParser(
    description='MCP Proxy for Databricks Apps',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  # Connect to local development server
  %(prog)s --databricks-host https://workspace.cloud.databricks.com --databricks-app-url http://localhost:8000

  # Connect to deployed Databricks App
  %(prog)s --databricks-host https://workspace.cloud.databricks.com --databricks-app-url https://myapp.databricksapps.com
    """,
  )

  parser.add_argument(
    '--databricks-host',
    required=True,
    help='Your Databricks workspace URL (e.g., https://workspace.cloud.databricks.com)',
  )

  parser.add_argument(
    '--databricks-app-url',
    required=True,
    help='The Databricks App URL (e.g., https://myapp.databricksapps.com)',
  )

  args = parser.parse_args()

  try:
    proxy = MCPProxy(args.databricks_host, args.databricks_app_url)
    print(f'Connected to MCP server at: {proxy.app_url}', file=sys.stderr)
    proxy.run()
  except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
  main()
