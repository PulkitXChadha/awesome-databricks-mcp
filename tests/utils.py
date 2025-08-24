"""Test utilities and helpers."""
import json
from pathlib import Path
from unittest.mock import Mock

def load_mock_response(key):
    """Load mock response from fixtures using the flat structure."""
    fixture_path = Path(__file__).parent / "fixtures" / "mock_responses.json"
    with open(fixture_path) as f:
        data = json.load(f)
    return data.get(key, [])

def create_mock_catalog(name="test_catalog"):
    """Create a mock catalog object."""
    mock = Mock()
    mock.name = name
    mock.owner = "test@example.com"
    mock.created_at = 1234567890
    return mock

def create_mock_schema(catalog="main", name="default"):
    """Create a mock schema object."""
    mock = Mock()
    mock.catalog_name = catalog
    mock.name = name
    mock.full_name = f"{catalog}.{name}"
    return mock

def create_mock_table(catalog="main", schema="default", name="table1"):
    """Create a mock table object."""
    mock = Mock()
    mock.catalog_name = catalog
    mock.schema_name = schema
    mock.name = name
    mock.full_name = f"{catalog}.{schema}.{name}"
    mock.table_type = "MANAGED"
    mock.data_source_format = "DELTA"
    mock.columns = []
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
