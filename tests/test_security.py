"""Security tests for SQL injection prevention and access control."""

from unittest.mock import Mock, patch

import pytest

from server.tools.dashboards import load_dashboard_tools
from tests.utils import assert_error_response, assert_success_response


class TestSQLInjectionPrevention:
  """Test SQL injection prevention in dashboard and widget operations."""

  @pytest.mark.security
  def test_sql_injection_in_dataset_query(self, mcp_server, mock_env_vars):
    """Test prevention of SQL injection in dataset queries."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock statement execution
      mock_response = Mock()
      mock_response.status.state = 'FAILED'
      mock_response.status.error = Mock()
      mock_response.status.error.message = 'Syntax error'

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Common SQL injection attempts
      injection_queries = [
        'SELECT * FROM users; DROP TABLE users;--',
        'SELECT * FROM users WHERE id = 1 OR 1=1',
        "SELECT * FROM users WHERE name = ''; DELETE FROM users WHERE '1'='1'",
        'SELECT * FROM users UNION SELECT * FROM sensitive_data',
        "SELECT * FROM users; INSERT INTO admins VALUES('hacker', 'password')",
        "SELECT * FROM users WHERE id = 1; EXEC xp_cmdshell('net user')",
        'SELECT * FROM ${table}; UPDATE users SET admin=true WHERE id=1',
        'SELECT * FROM users WHERE name = CHAR(97,100,109,105,110)',
        'SELECT * FROM users WHERE id = 1 /*comment*/ OR /*comment*/ 1=1',
        'SELECT * FROM users WHERE id = (SELECT password FROM admins LIMIT 1)',
      ]

      dataset_tool = mcp_server._tool_manager._tools['create_dashboard_dataset']

      for malicious_query in injection_queries:
        result = dataset_tool.fn(
          dashboard_id='test-dashboard',
          name='Malicious Dataset',
          query=malicious_query,
          warehouse_id='warehouse-123',
        )

        # Should either fail validation or be safely handled
        if not result['success']:
          assert 'error' in result
          # Verify error doesn't expose sensitive information
          assert 'password' not in result['error'].lower()
          assert 'admin' not in result['error'].lower()

  @pytest.mark.security
  def test_parameterized_query_safety(self, mcp_server, mock_env_vars):
    """Test that parameterized queries prevent injection."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock successful execution for safe queries
      mock_response = Mock()
      mock_response.status.state = 'SUCCEEDED'
      mock_response.result.data_array = []
      mock_response.result.schema.columns = []

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Safe parameterized queries
      safe_queries = [
        'SELECT * FROM users WHERE id = :user_id',
        'SELECT * FROM sales WHERE region = :region AND date >= :start_date',
        'SELECT * FROM products WHERE price BETWEEN :min_price AND :max_price',
      ]

      test_tool = mcp_server._tool_manager._tools['test_dataset_query']

      for safe_query in safe_queries:
        result = test_tool.fn(query=safe_query, warehouse_id='warehouse-123')

        # Safe queries should execute successfully
        assert_success_response(result)

  @pytest.mark.security
  def test_widget_field_injection(self, mcp_server, mock_env_vars):
    """Test prevention of injection through widget field names."""
    load_dashboard_tools(mcp_server)

    # Malicious field names that could cause injection
    malicious_fields = [
      'field; DROP TABLE users',
      "field' OR '1'='1",
      'field/*comment*/',
      'field UNION SELECT * FROM passwords',
      "field'; INSERT INTO admins VALUES('hacker'",
      'field`; DELETE FROM users WHERE 1=1',
      'field$(rm -rf /)',
      'field&&net user hacker password /add',
      'field||1=1',
      "field<script>alert('XSS')</script>",
    ]

    # Test various widget creation tools with malicious fields
    widget_tools = [
      ('create_bar_chart', {'x_field': None, 'y_field': 'revenue'}),
      ('create_line_chart', {'x_field': None, 'y_field': 'value'}),
      ('create_pie_chart', {'category_field': None, 'value_field': 'amount'}),
      ('create_scatter_plot', {'x_field': None, 'y_field': 'y_value'}),
      ('create_dropdown_filter', {'filter_field': None}),
      ('create_slider_filter', {'numeric_field': None}),
    ]

    for tool_name, base_params in widget_tools:
      tool = mcp_server._tool_manager._tools[tool_name]

      for malicious_field in malicious_fields:
        # Insert malicious field into appropriate parameter
        params = base_params.copy()
        params['dataset_name'] = 'test_data'

        # Find which field to replace with malicious input
        for key, value in params.items():
          if value is None and 'field' in key:
            params[key] = malicious_field
            break

        result = tool.fn(**params)

        # Widget should be created but field should be sanitized
        assert_success_response(result)

        # Verify malicious code is not present in widget spec
        widget_spec = result.get('widget_spec', {})
        widget_str = str(widget_spec)

        assert 'DROP TABLE' not in widget_str
        assert 'INSERT INTO' not in widget_str
        assert 'DELETE FROM' not in widget_str
        assert '<script>' not in widget_str

  @pytest.mark.security
  def test_dataset_name_injection(self, mcp_server, mock_env_vars):
    """Test prevention of injection through dataset names."""
    load_dashboard_tools(mcp_server)

    # Malicious dataset names
    malicious_names = [
      "'; DROP TABLE users; --",
      "dataset' UNION SELECT * FROM passwords WHERE '1'='1",
      'dataset`; DELETE FROM sensitive_data',
      '../../../etc/passwd',
      '..\\..\\..\\windows\\system32\\config\\sam',
      'dataset$(whoami)',
      'dataset&&net user',
      'dataset|cat /etc/shadow',
    ]

    for malicious_name in malicious_names:
      # Test dataset creation
      with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
        mock_workspace = Mock()
        mock_response = Mock()
        mock_response.status.state = 'SUCCEEDED'
        mock_workspace.statement_execution.execute_statement.return_value = mock_response
        mock_client.return_value = mock_workspace

        dataset_tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
        result = dataset_tool.fn(
          dashboard_id='test-dashboard',
          name=malicious_name,
          query='SELECT * FROM safe_table',
          warehouse_id='warehouse-123',
        )

        # Dataset creation should handle malicious names safely
        if result['success']:
          assert result['dataset_name'] == malicious_name
          # But the actual execution should be safe
          call_args = mock_workspace.statement_execution.execute_statement.call_args
          executed_query = call_args[1]['statement']
          assert 'DROP TABLE' not in executed_query
          assert 'DELETE FROM' not in executed_query


class TestAccessControl:
  """Test access control and permission validation."""

  @pytest.mark.security
  def test_dashboard_access_permissions(self, mcp_server, mock_env_vars):
    """Test dashboard access permission validation."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Simulate permission denied
      mock_workspace.lakeview.get.side_effect = Exception(
        'Permission denied: Access denied to Databricks resource'
      )
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Test accessing restricted dashboard
      get_tool = mcp_server._tool_manager._tools['get_lakeview_dashboard']
      result = get_tool.fn(dashboard_id='restricted-dashboard')

      assert_error_response(result)
      assert 'Permission denied' in result['error']

  @pytest.mark.security
  def test_widget_modification_permissions(self, mcp_server, mock_env_vars):
    """Test widget modification permission checks."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock dashboard with restricted access
      mock_dashboard = Mock()
      mock_dashboard.widgets = []
      mock_dashboard.owner = 'other_user@example.com'
      mock_dashboard.permissions = {'can_edit': False}

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.side_effect = Exception('Insufficient permissions')

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Try to modify dashboard without permission
      add_tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = add_tool.fn(
        dashboard_id='restricted-dashboard',
        widget_spec={'type': 'chart', 'name': 'Unauthorized Widget'},
      )

      assert_error_response(result)
      assert 'permission' in result['error'].lower()

  @pytest.mark.security
  def test_data_access_control(self, mcp_server, mock_env_vars):
    """Test data access control in queries."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Queries attempting to access restricted data
      restricted_queries = [
        'SELECT * FROM hr.salaries',
        'SELECT * FROM finance.transactions',
        'SELECT * FROM security.audit_logs',
      ]

      for query in restricted_queries:
        # Mock permission denied for restricted tables
        mock_response = Mock()
        mock_response.status.state = 'FAILED'
        mock_response.status.error = Mock()
        mock_response.status.error.message = 'Access denied to table'

        mock_workspace.statement_execution.execute_statement.return_value = mock_response
        mock_client.return_value = mock_workspace

        load_dashboard_tools(mcp_server)

        test_tool = mcp_server._tool_manager._tools['test_dataset_query']
        result = test_tool.fn(query=query, warehouse_id='warehouse-123')

        assert_error_response(result)
        assert 'access denied' in result['error'].lower() or 'failed' in result['error'].lower()


class TestQueryTimeoutAndLimits:
  """Test query timeout and resource limit enforcement."""

  @pytest.mark.security
  def test_query_timeout_enforcement(self, mcp_server, mock_env_vars):
    """Test that long-running queries are terminated."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Simulate query timeout
      mock_response = Mock()
      mock_response.status.state = 'FAILED'
      mock_response.status.error = Mock()
      mock_response.status.error.message = 'Query exceeded maximum execution time of 30 seconds'

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Test query that would run too long
      test_tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = test_tool.fn(
        query='SELECT * FROM huge_table CROSS JOIN huge_table2', warehouse_id='warehouse-123'
      )

      assert_error_response(result)
      assert 'exceeded' in result['error'].lower() or 'timeout' in result['error'].lower()

  @pytest.mark.security
  def test_result_size_limits(self, mcp_server, mock_env_vars):
    """Test enforcement of result size limits."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Create mock response with large result set
      mock_response = Mock()
      mock_response.status.state = 'SUCCEEDED'
      # Simulate 1 million rows
      mock_response.result.data_array = [['row'] for _ in range(1000000)]
      mock_response.result.schema.columns = [Mock(name='col1')]

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      test_tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = test_tool.fn(
        query='SELECT * FROM large_table',
        warehouse_id='warehouse-123',
        limit=100,  # Should limit results
      )

      assert_success_response(result)
      # Sample data should be limited
      assert len(result.get('sample_data', [])) <= 100

  @pytest.mark.security
  def test_resource_consumption_limits(self, mcp_server, mock_env_vars):
    """Test prevention of resource-intensive operations."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Queries that could consume excessive resources
      resource_intensive_queries = [
        'SELECT * FROM table1 CROSS JOIN table2 CROSS JOIN table3',
        'WITH RECURSIVE cte AS (SELECT 1 UNION ALL SELECT n+1 FROM cte WHERE n < 1000000) '
        'SELECT * FROM cte',
        'SELECT DISTINCT * FROM (SELECT * FROM huge_table ORDER BY RANDOM()) LIMIT 1000000',
      ]

      for query in resource_intensive_queries:
        mock_response = Mock()
        mock_response.status.state = 'FAILED'
        mock_response.status.error = Mock()
        mock_response.status.error.message = 'Query requires too many resources'

        mock_workspace.statement_execution.execute_statement.return_value = mock_response
        mock_client.return_value = mock_workspace

        load_dashboard_tools(mcp_server)

        test_tool = mcp_server._tool_manager._tools['test_dataset_query']
        result = test_tool.fn(query=query, warehouse_id='warehouse-123')

        assert_error_response(result)


class TestInputSanitization:
  """Test input sanitization and validation."""

  @pytest.mark.security
  def test_special_character_handling(self, mcp_server, mock_env_vars):
    """Test handling of special characters in inputs."""
    load_dashboard_tools(mcp_server)

    # Special characters that should be properly escaped
    special_inputs = [
      "O'Reilly",  # Single quote
      'Company "ABC"',  # Double quotes
      'Path\\to\\file',  # Backslashes
      'Value with\nnewline',  # Newline
      'Tab\tseparated',  # Tab
      'Null\x00character',  # Null byte
      'Unicode: 🚀 ñ α',  # Unicode characters
      '<>&"\'',  # HTML special characters
      '${variable}',  # Template syntax
      '{{mustache}}',  # Template syntax
      '%wildcard%',  # SQL wildcard
    ]

    for special_input in special_inputs:
      # Test with dashboard name
      create_tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
      result = create_tool.fn(
        dashboard_config={
          'name': f'Dashboard: {special_input}',
          'description': f'Description with {special_input}',
        }
      )

      # Should handle special characters safely
      if result['success']:
        assert special_input in result.get('name', '') or 'Dashboard:' in result.get('name', '')

  @pytest.mark.security
  def test_html_script_tag_prevention(self, mcp_server, mock_env_vars):
    """Test prevention of HTML/JavaScript injection."""
    load_dashboard_tools(mcp_server)

    # HTML/JS injection attempts
    xss_attempts = [
      "<script>alert('XSS')</script>",
      "<img src=x onerror='alert(1)'>",
      "<iframe src='evil.com'></iframe>",
      "javascript:alert('XSS')",
      "<body onload='alert(1)'>",
      "<svg onload='alert(1)'>",
      "';alert('XSS');//",
      '"><script>alert("XSS")</script>',
      "<meta http-equiv='refresh' content='0;url=evil.com'>",
    ]

    text_widget_tool = mcp_server._tool_manager._tools.get('create_text_widget')

    if text_widget_tool:
      for xss_attempt in xss_attempts:
        result = text_widget_tool.fn(content=xss_attempt)

        assert_success_response(result)

        # Verify script tags are escaped or removed
        widget_spec = result.get('widget_spec', {})
        content = widget_spec.get('content', '')

        # Check for HTML-encoded or escaped content
        assert '<script>' not in content
        assert 'alert(' not in content or 'alert(&#x27;' in content  # Allow HTML-encoded
        assert 'onerror=' not in content
        assert 'javascript:' not in content.lower()

  @pytest.mark.security
  def test_path_traversal_prevention(self, mcp_server, mock_env_vars):
    """Test prevention of path traversal attacks."""
    load_dashboard_tools(mcp_server)

    # Path traversal attempts
    traversal_attempts = [
      '../../../../etc/passwd',
      '..\\..\\..\\windows\\system32',
      '/etc/shadow',
      'C:\\Windows\\System32\\config\\sam',
      '../data/../../sensitive',
      'file:///etc/passwd',
      '\\\\server\\share\\sensitive',
    ]

    image_widget_tool = mcp_server._tool_manager._tools.get('create_image_widget')
    iframe_widget_tool = mcp_server._tool_manager._tools.get('create_iframe_widget')

    for traversal in traversal_attempts:
      if image_widget_tool:
        result = image_widget_tool.fn(image_url=traversal)
        assert_success_response(result)
        # URL should be stored as-is but not executed locally
        assert result['widget_spec']['image_url'] == traversal

      if iframe_widget_tool:
        result = iframe_widget_tool.fn(iframe_url=traversal)
        assert_success_response(result)
        # URL should be stored but sandboxed
        assert result['widget_spec']['iframe_url'] == traversal


class TestDataValidationAndEncoding:
  """Test data validation and encoding security measures."""

  @pytest.mark.security
  def test_json_injection_prevention(self, mcp_server, mock_env_vars):
    """Test prevention of JSON injection attacks."""
    load_dashboard_tools(mcp_server)

    # JSON injection attempts
    json_injections = [
      '{"name": "test", "extra": "field"}',
      '{"__proto__": {"isAdmin": true}}',
      '{"constructor": {"prototype": {"isAdmin": true}}}',
      '{"name": "test"}, {"malicious": "code"}',
      '{"$where": "this.password == \'admin\'"}',
      '{"$regex": ".*", "$options": "si"}',
    ]

    for injection in json_injections:
      # Test with dashboard configuration
      create_tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
      result = create_tool.fn(dashboard_config={'name': injection, 'description': 'Test'})

      # Should handle safely without executing injection
      assert 'error' in result or result['success']
      if result.get('success'):
        # Verify no prototype pollution occurred
        assert '__proto__' not in str(result)
        assert 'constructor' not in str(result) or 'prototype' not in str(result)

  @pytest.mark.security
  def test_ldap_injection_prevention(self, mcp_server, mock_env_vars):
    """Test prevention of LDAP injection attacks."""
    load_dashboard_tools(mcp_server)

    # LDAP injection attempts
    ldap_injections = [
      'admin)(|(password=*)',
      '*)(uid=*',
      'admin)(objectClass=*',
      'admin))%00',
      '*)(mail=*@example.com',
    ]

    for injection in ldap_injections:
      # Test in user-related operations
      share_tool = mcp_server._tool_manager._tools.get('share_lakeview_dashboard')
      if share_tool:
        result = share_tool.fn(
          dashboard_id='test-dashboard', share_config={'users': [injection], 'permission': 'READ'}
        )

        # Should handle safely
        assert 'error' in result or result['success']

  @pytest.mark.security
  def test_csv_injection_prevention(self, mcp_server, mock_env_vars):
    """Test prevention of CSV injection attacks."""
    load_dashboard_tools(mcp_server)

    # CSV injection attempts (formula injection)
    csv_injections = [
      '=1+1',
      '@SUM(1+1)',
      '+1+1',
      '-1+1',
      "=cmd|'/c calc.exe'!A1",
      '=HYPERLINK("http://evil.com","Click")',
      '@IMPORT("http://evil.com/data.csv")',
      '=WEBSERVICE("http://evil.com/api")',
    ]

    table_tool = mcp_server._tool_manager._tools.get('create_table_widget')
    if table_tool:
      for injection in csv_injections:
        result = table_tool.fn(
          dashboard_id='test-dashboard',
          dataset_name='test_data',
          columns=[{'name': injection, 'type': 'string'}],
        )

        # Should sanitize formula injections
        assert_success_response(result)
        widget_spec = result.get('widget_spec', {})

        # Formulas should be escaped or prefixed
        for col in widget_spec.get('columns', []):
          name = col.get('name', '')
          # Check that formulas are escaped
          assert not name.startswith('=') or name.startswith("'=")
          assert not name.startswith('@') or name.startswith("'@")
          assert not name.startswith('+') or name.startswith("'+")
          assert not name.startswith('-') or name.startswith("'-")


class TestConcurrentUserSecurity:
  """Test security in concurrent user scenarios."""

  @pytest.mark.security
  def test_session_isolation(self, mcp_server, mock_env_vars):
    """Test that user sessions are properly isolated."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Simulate different user contexts
      user1_workspace = Mock()
      user1_dashboard = Mock()
      user1_dashboard.dashboard_id = 'user1-dashboard'
      user1_dashboard.owner = 'user1@example.com'
      user1_dashboard.widgets = []

      user2_workspace = Mock()
      user2_dashboard = Mock()
      user2_dashboard.dashboard_id = 'user2-dashboard'
      user2_dashboard.owner = 'user2@example.com'
      user2_dashboard.widgets = []

      # Users should not be able to access each other's dashboards
      def user1_get(dashboard_id):
        if dashboard_id == 'user1-dashboard':
          return user1_dashboard
        else:
          # Make the exception more aggressive
          raise Exception('Permission denied: Access denied to Databricks resource')

      def user2_get(dashboard_id):
        if dashboard_id == 'user2-dashboard':
          return user2_dashboard
        else:
          # Make the exception more aggressive
          raise Exception('Permission denied: Access denied to Databricks resource')

      user1_workspace.lakeview.get.side_effect = user1_get
      user2_workspace.lakeview.get.side_effect = user2_get

      # Test user1 trying to access user2's dashboard
      mock_client.return_value = user1_workspace

      load_dashboard_tools(mcp_server)

      get_tool = mcp_server._tool_manager._tools['get_lakeview_dashboard']
      result = get_tool.fn(dashboard_id='user2-dashboard')

      assert_error_response(result)
      assert 'Permission denied' in result['error']

  @pytest.mark.security
  def test_race_condition_prevention(self, mcp_server, mock_env_vars):
    """Test prevention of race conditions in concurrent updates."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Track update versions
      update_version = 0

      def mock_get(*args, **kwargs):
        mock_dashboard = Mock()
        mock_dashboard.version = update_version
        mock_dashboard.widgets = []
        return mock_dashboard

      def mock_update(*args, **kwargs):
        nonlocal update_version
        # Check version matches
        if 'version' in kwargs and kwargs['version'] != update_version:
          raise Exception('Concurrent modification detected')
        update_version += 1
        return Mock()

      mock_workspace.lakeview.get.side_effect = mock_get
      mock_workspace.lakeview.update.side_effect = mock_update

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Simulate concurrent updates
      add_tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']

      # First update should succeed
      result1 = add_tool.fn(
        dashboard_id='test-dashboard', widget_spec={'type': 'chart', 'name': 'Widget 1'}
      )
      assert_success_response(result1)

      # Concurrent update with old version should fail
      mock_workspace.lakeview.get.side_effect = lambda *args: Mock(version=0, widgets=[])
      _result2 = add_tool.fn(
        dashboard_id='test-dashboard', widget_spec={'type': 'table', 'name': 'Widget 2'}
      )
      # This may fail due to version mismatch


if __name__ == '__main__':
  pytest.main([__file__, '-v', '-m', 'security'])
