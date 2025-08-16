"""Unit tests for user router endpoints."""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
@pytest.mark.api
class TestUserRouter:
  """Test user router endpoints."""

  def test_get_current_user_success(self, test_client):
    """Test successful user info retrieval."""
    mock_user_info = {
      'userName': 'test@example.com',
      'displayName': 'Test User',
      'active': True,
      'emails': ['test@example.com'],
    }

    with patch('server.services.user_service.UserService') as mock_service_class:
      mock_service = Mock()
      mock_service.get_user_info.return_value = mock_user_info
      mock_service_class.return_value = mock_service

      response = test_client.get('/api/user/me')

    assert response.status_code == 200
    data = response.json()
    assert data['userName'] == 'test@example.com'
    assert data['displayName'] == 'Test User'
    assert data['active'] is True
    assert data['emails'] == ['test@example.com']

  def test_get_current_user_minimal_info(self, test_client):
    """Test user info retrieval with minimal data."""
    mock_user_info = {
      'userName': 'minimal@example.com',
      'displayName': None,
      'active': False,
      'emails': [],
    }

    with patch('server.services.user_service.UserService') as mock_service_class:
      mock_service = Mock()
      mock_service.get_user_info.return_value = mock_user_info
      mock_service_class.return_value = mock_service

      response = test_client.get('/api/user/me')

    assert response.status_code == 200
    data = response.json()
    assert data['userName'] == 'minimal@example.com'
    assert data['displayName'] is None
    assert data['active'] is False
    assert data['emails'] == []

  def test_get_current_user_service_error(self, test_client):
    """Test user info retrieval when service fails."""
    with patch('server.services.user_service.UserService') as mock_service_class:
      mock_service = Mock()
      mock_service.get_user_info.side_effect = Exception('Service unavailable')
      mock_service_class.return_value = mock_service

      response = test_client.get('/api/user/me')

    assert response.status_code == 500
    data = response.json()
    assert 'Failed to fetch user info' in data['detail']
    assert 'Service unavailable' in data['detail']

  def test_get_user_workspace_info_success(self, test_client):
    """Test successful user and workspace info retrieval."""
    mock_workspace_info = {
      'user': {'userName': 'test@example.com', 'displayName': 'Test User', 'active': True},
      'workspace': {
        'workspaceId': '12345',
        'workspaceName': 'Test Workspace',
        'region': 'us-west-2',
      },
    }

    with patch('server.services.user_service.UserService') as mock_service_class:
      mock_service = Mock()
      mock_service.get_user_workspace_info.return_value = mock_workspace_info
      mock_service_class.return_value = mock_service

      response = test_client.get('/api/user/me/workspace')

    assert response.status_code == 200
    data = response.json()
    assert data['user']['userName'] == 'test@example.com'
    assert data['user']['displayName'] == 'Test User'
    assert data['user']['active'] is True
    assert data['workspace']['workspaceId'] == '12345'
    assert data['workspace']['workspaceName'] == 'Test Workspace'

  def test_get_user_workspace_info_error(self, test_client):
    """Test workspace info retrieval when service fails."""
    with patch('server.services.user_service.UserService') as mock_service_class:
      mock_service = Mock()
      mock_service.get_user_workspace_info.side_effect = Exception('Workspace not accessible')
      mock_service_class.return_value = mock_service

      response = test_client.get('/api/user/me/workspace')

    assert response.status_code == 500
    data = response.json()
    assert 'Failed to fetch workspace info' in data['detail']
    assert 'Workspace not accessible' in data['detail']


@pytest.mark.unit
@pytest.mark.api
class TestUserModels:
  """Test user router Pydantic models."""

  def test_user_info_model_creation(self):
    """Test UserInfo model with all fields."""
    from server.routers.user import UserInfo

    user = UserInfo(
      userName='test@example.com',
      displayName='Test User',
      active=True,
      emails=['test@example.com', 'test2@example.com'],
    )

    assert user.userName == 'test@example.com'
    assert user.displayName == 'Test User'
    assert user.active is True
    assert user.emails == ['test@example.com', 'test2@example.com']

  def test_user_info_model_minimal(self):
    """Test UserInfo model with minimal required fields."""
    from server.routers.user import UserInfo

    user = UserInfo(userName='minimal@example.com', active=False)

    assert user.userName == 'minimal@example.com'
    assert user.displayName is None
    assert user.active is False
    assert user.emails == []

  def test_user_workspace_info_model(self):
    """Test UserWorkspaceInfo model."""
    from server.routers.user import UserInfo, UserWorkspaceInfo

    user = UserInfo(userName='test@example.com', displayName='Test User', active=True)

    workspace_info = UserWorkspaceInfo(
      user=user, workspace={'workspaceId': '12345', 'name': 'Test Workspace'}
    )

    assert workspace_info.user.userName == 'test@example.com'
    assert workspace_info.workspace['workspaceId'] == '12345'


@pytest.mark.integration
@pytest.mark.api
class TestUserRouterIntegration:
  """Integration tests for user router."""

  def test_user_router_endpoints_exist(self, test_client):
    """Test that user router endpoints are properly mounted."""
    # Test that endpoints exist (even if they fail due to missing services)
    response = test_client.get('/api/user/me')
    # Should not be 404 (not found)
    assert response.status_code != 404

    response = test_client.get('/api/user/me/workspace')
    # Should not be 404 (not found)
    assert response.status_code != 404

  def test_user_router_error_handling_consistency(self, test_client):
    """Test that error responses are consistent across endpoints."""
    with patch('server.services.user_service.UserService') as mock_service_class:
      mock_service = Mock()
      mock_service.get_user_info.side_effect = Exception('Test error')
      mock_service.get_user_workspace_info.side_effect = Exception('Test error')
      mock_service_class.return_value = mock_service

      # Both endpoints should return 500 errors with similar structure
      response1 = test_client.get('/api/user/me')
      response2 = test_client.get('/api/user/me/workspace')

      assert response1.status_code == 500
      assert response2.status_code == 500

      data1 = response1.json()
      data2 = response2.json()

      # Both should have 'detail' field with error message
      assert 'detail' in data1
      assert 'detail' in data2
      assert 'Test error' in data1['detail']
      assert 'Test error' in data2['detail']
