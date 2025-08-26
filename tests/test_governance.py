"""Test governance and lineage tools."""

from unittest.mock import Mock, patch

import pytest

from server.tools.governance import load_governance_tools
from tests.utils import assert_success_response


class TestGovernanceTools:
  """Test governance and lineage operations."""

  @pytest.mark.unit
  def test_list_audit_logs(self, mcp_server, mock_env_vars):
    """Test listing audit logs."""
    with patch('server.tools.governance.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_governance_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_audit_logs']
      result = tool.fn(start_time='2024-01-01', end_time='2024-01-31')

      assert_success_response(result)
      assert result['start_time'] == '2024-01-01'
      assert result['end_time'] == '2024-01-31'
      assert result['message'] == 'Audit log listing initiated'
      assert result['count'] == 0
      assert 'note' in result

  @pytest.mark.unit
  def test_get_audit_log(self, mcp_server, mock_env_vars):
    """Test getting specific audit log."""
    with patch('server.tools.governance.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_governance_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_audit_log']
      result = tool.fn(event_id='event-123')

      assert_success_response(result)
      assert result['event_id'] == 'event-123'
      assert result['message'] == 'Audit log event-123 details retrieval initiated'

  @pytest.mark.unit
  def test_list_governance_rules(self, mcp_server, mock_env_vars):
    """Test listing governance rules."""
    with patch('server.tools.governance.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_governance_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_governance_rules']
      result = tool.fn()

      assert_success_response(result)
      assert result['message'] == 'Governance rule listing initiated'
      assert result['count'] == 0
      assert 'note' in result

  @pytest.mark.unit
  def test_create_governance_rule(self, mcp_server, mock_env_vars):
    """Test creating governance rule."""
    with patch('server.tools.governance.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      rule_config = {'name': 'test-rule', 'type': 'data_quality'}

      load_governance_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_governance_rule']
      result = tool.fn(rule_config=rule_config)

      assert_success_response(result)
      assert result['rule_config'] == rule_config
      assert result['message'] == 'Governance rule creation initiated'

  @pytest.mark.unit
  def test_get_table_lineage(self, mcp_server, mock_env_vars):
    """Test getting table lineage."""
    with patch('server.tools.governance.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_governance_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_table_lineage']
      result = tool.fn(table_name='main.default.users', depth=2)

      assert_success_response(result)
      assert result['table_name'] == 'main.default.users'
      assert result['depth'] == 2
      assert result['message'] == 'Table lineage retrieval initiated for main.default.users'

  @pytest.mark.unit
  def test_search_catalog(self, mcp_server, mock_env_vars):
    """Test catalog search."""
    with patch('server.tools.governance.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_governance_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['search_catalog']
      result = tool.fn(query='users', object_type='table')

      assert_success_response(result)
      assert result['query'] == 'users'
      assert result['object_type'] == 'table'
      assert result['message'] == 'Catalog search initiated'
      assert result['count'] == 0

  # Note: Data quality tools are implemented in Unity Catalog module, not governance
  # These tests will be added to test_unity_catalog.py when appropriate

  # Note: Access control tools (list_access_controls, grant_access, revoke_access)
  # are not implemented yet
  # These tests will be added when those tools are implemented
