"""Test utilities and helpers."""

import json
from pathlib import Path
from unittest.mock import Mock

from databricks.sdk.errors import (
  InvalidParameterValue,
  NotFound,
  OperationTimeout,
  PermissionDenied,
  RequestLimitExceeded,
  ResourceDoesNotExist,
  TooManyRequests,
  Unauthenticated,
)


def load_mock_response(key):
  """Load mock response from fixtures using the flat structure."""
  fixture_path = Path(__file__).parent / 'fixtures' / 'mock_responses.json'
  with open(fixture_path) as f:
    data = json.load(f)
  return data.get(key, [])


def create_mock_catalog(name='test_catalog'):
  """Create a mock catalog object."""
  mock = Mock()
  mock.name = name
  mock.owner = 'test@example.com'
  mock.created_at = 1234567890
  return mock


def create_mock_schema(catalog='main', name='default'):
  """Create a mock schema object."""
  mock = Mock()
  mock.catalog_name = catalog
  mock.name = name
  mock.full_name = f'{catalog}.{name}'
  return mock


def create_mock_table(catalog='main', schema='default', name='table1'):
  """Create a mock table object."""
  mock = Mock()
  mock.catalog_name = catalog
  mock.schema_name = schema
  mock.name = name
  mock.full_name = f'{catalog}.{schema}.{name}'
  mock.table_type = 'MANAGED'
  mock.data_source_format = 'DELTA'
  mock.comment = f'Test table {name}'
  mock.owner = 'test@example.com'
  mock.created_at = 1234567890
  mock.updated_at = 1234567890
  mock.properties = {'table_type': 'test'}
  mock.columns = []
  mock.partitioning = []
  mock.storage_location = None
  return mock


def assert_success_response(result):
  """Common assertion for successful MCP responses."""
  assert result is not None
  assert result.get('success') is True
  assert 'error' not in result
  return result


def assert_error_response(result):
  """Common assertion for error MCP responses."""
  assert result is not None
  assert result.get('success') is False
  assert 'error' in result
  return result


# Common error patterns to test across all tools
ERROR_SCENARIOS = [
  ('Network timeout', OperationTimeout),
  ('Permission denied', PermissionDenied),
  ('Resource not found', NotFound),
  ('Rate limiting', TooManyRequests),
  ('Authentication failed', Unauthenticated),
  ('Invalid parameters', InvalidParameterValue),
  ('Resource does not exist', ResourceDoesNotExist),
  ('Request limit exceeded', RequestLimitExceeded),
]


def create_error_test_cases(tool_names, client_patch_path):
  """Create error test cases for multiple tools.

  Args:
      tool_names: List of tool names to test
      client_patch_path: Path to patch the WorkspaceClient
                        (e.g., 'server.tools.unity_catalog.WorkspaceClient')

  Returns:
      List of test case dictionaries
  """
  test_cases = []

  for tool_name in tool_names:
    for error_description, error_class in ERROR_SCENARIOS:
      test_cases.append(
        {
          'tool_name': tool_name,
          'error_description': error_description,
          'error_class': error_class,
          'client_patch_path': client_patch_path,
        }
      )

  return test_cases


def simulate_databricks_error(error_class, message):
  """Simulate a Databricks SDK error with proper message."""
  if error_class in [PermissionDenied, Unauthenticated]:
    return error_class(f'{message}: Access denied to Databricks resource')
  elif error_class in [NotFound, ResourceDoesNotExist]:
    return error_class(f'{message}: Resource not found in workspace')
  elif error_class in [TooManyRequests, RequestLimitExceeded]:
    return error_class(f'{message}: Rate limit exceeded for API calls')
  elif error_class == OperationTimeout:
    return error_class(f'{message}: Request timed out')
  elif error_class == InvalidParameterValue:
    return error_class(f'{message}: Invalid parameter provided')
  else:
    return error_class(message)
