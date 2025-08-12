"""Repositories and Git MCP tools for Databricks."""

import os
from databricks.sdk import WorkspaceClient


def load_repo_tools(mcp_server):
    """Register repositories and Git MCP tools with the server.
    
    Args:
        mcp_server: The FastMCP server instance to register tools with
    """
    
    # @mcp_server.tool
    # def list_repos() -> dict:
    #     """List all Git repositories in the Databricks workspace.

    #     Returns:
    #         Dictionary containing list of repositories with their details
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # List all repositories
    #         repos = w.repos.list()
            
    #         repo_list = []
    #         for repo in repos:
    #             repo_list.append({
    #                 'repo_id': repo.id,
    #                 'path': repo.path,
    #                 'url': repo.url,
    #                 'provider': repo.provider,
    #                 'head_commit_id': repo.head_commit_id,
    #                 'status': repo.status,
    #             })

    #         return {
    #             'success': True,
    #             'repositories': repo_list,
    #             'count': len(repo_list),
    #             'message': f'Found {len(repo_list)} repository(ies)',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error listing repositories: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}', 'repositories': [], 'count': 0}

    # @mcp_server.tool
    # def get_repo(repo_id: str) -> dict:
    #     """Get details of a specific Git repository.

    #     Args:
    #         repo_id: The ID of the repository to get details for

    #     Returns:
    #         Dictionary with repository details or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get repository details
    #         repo = w.repos.get(repo_id)
            
    #         return {
    #             'success': True,
    #             'repository': {
    #                 'repo_id': repo.id,
    #                 'path': repo.path,
    #                 'url': repo.url,
    #                 'provider': repo.provider,
    #                 'head_commit_id': repo.head_commit_id,
    #                 'status': repo.status,
    #                 'branch': repo.branch,
    #                 'tag': repo.tag,
    #             },
    #             'message': f'Repository {repo_id} details retrieved successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting repository details: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def create_repo(url: str, provider: str = 'github') -> dict:
    #     """Create a new Git repository in the Databricks workspace.

    #     Args:
    #         url: The Git repository URL
    #         provider: The Git provider (default: 'github')

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Create repository
    #         repo = w.repos.create(
    #             url=url,
    #             provider=provider,
    #         )
            
    #         return {
    #             'success': True,
    #             'repo_id': repo.id,
    #             'path': repo.path,
    #             'url': repo.url,
    #             'message': f'Repository created successfully with ID {repo.id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error creating repository: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def delete_repo(repo_id: str) -> dict:
    #     """Delete a Git repository from the Databricks workspace.

    #     Args:
    #         repo_id: The ID of the repository to delete

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Delete repository
    #         w.repos.delete(repo_id)
            
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'message': f'Repository {repo_id} deleted successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error deleting repository: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def update_repo(repo_id: str, updates: dict) -> dict:
    #     """Update a Git repository in the Databricks workspace.

    #     Args:
    #         repo_id: The ID of the repository to update
    #         updates: Dictionary containing updates to apply

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Update repository
    #         repo = w.repos.update(
    #             repo_id=repo_id,
    #             **updates,
    #         )
            
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'path': repo.path,
    #             'message': f'Repository {repo_id} updated successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error updating repository: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def pull_repo(repo_id: str) -> dict:
    #     """Pull latest changes from a Git repository.

    #     Args:
    #         repo_id: The ID of the repository to pull from

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Pull repository
    #         w.repos.update(repo_id)
            
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'message': f'Repository {repo_id} pulled successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error pulling repository: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def create_branch(repo_id: str, branch_name: str, source_branch: str = 'main') -> dict:
    #     """Create a new branch in a Git repository.

    #     Args:
    #         repo_id: The ID of the repository
    #         branch_name: The name of the new branch
    #         source_branch: The source branch to create from (default: 'main')

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Create branch
    #         w.repos.update(
    #             repo_id=repo_id,
    #             branch=branch_name,
    #         )
            
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'branch_name': branch_name,
    #             'source_branch': source_branch,
    #             'message': f'Branch {branch_name} created successfully from {source_branch}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error creating branch: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def list_branches(repo_id: str) -> dict:
    #     """List all branches in a Git repository.

    #     Args:
    #         repo_id: The ID of the repository

    #     Returns:
    #         Dictionary with list of branches or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get repository details to see current branch
    #         repo = w.repos.get(repo_id)
            
    #         # Note: Databricks SDK doesn't directly expose branch listing
    #         # This is a limitation of the current SDK
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'current_branch': repo.branch,
    #             'message': f'Current branch is {repo.branch}. Full branch listing not available via SDK.',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error listing branches: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def switch_branch(repo_id: str, branch_name: str) -> dict:
    #     """Switch to a different branch in a Git repository.

    #     Args:
    #         repo_id: The ID of the repository
    #         branch_name: The name of the branch to switch to

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Switch branch
    #         w.repos.update(
    #             repo_id=repo_id,
    #             branch=branch_name,
    #         )
            
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'branch_name': branch_name,
    #             'message': f'Switched to branch {branch_name} successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error switching branch: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def get_commit_history(repo_id: str, limit: int = 10) -> dict:
    #     """Get commit history for a Git repository.

    #     Args:
    #         repo_id: The ID of the repository
    #         limit: Maximum number of commits to return (default: 10)

    #     Returns:
    #         Dictionary with commit history or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get repository details
    #         repo = w.repos.get(repo_id)
            
    #         # Note: Databricks SDK doesn't directly expose commit history
    #         # This is a limitation of the current SDK
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'head_commit_id': repo.head_commit_id,
    #             'message': f'Head commit is {repo.head_commit_id}. Full commit history not available via SDK.',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting commit history: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def get_repo_status(repo_id: str) -> dict:
    #     """Get the current status of a Git repository.

    #     Args:
    #         repo_id: The ID of the repository

    #     Returns:
    #         Dictionary with repository status or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get repository status
    #         repo = w.repos.get(repo_id)
            
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'status': {
    #                 'path': repo.path,
    #                 'url': repo.url,
    #                 'provider': repo.provider,
    #                 'head_commit_id': repo.head_commit_id,
    #                 'status': repo.status,
    #                 'branch': repo.branch,
    #                 'tag': repo.tag,
    #             },
    #             'message': f'Repository status retrieved successfully for {repo_id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting repository status: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def sync_repo(repo_id: str) -> dict:
    #     """Sync a Git repository with the remote.

    #     Args:
    #         repo_id: The ID of the repository to sync

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Sync repository (pull + push if needed)
    #         w.repos.update(repo_id)
            
    #         return {
    #             'success': True,
    #             'repo_id': repo_id,
    #             'message': f'Repository {repo_id} synced successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error syncing repository: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    pass  # All tools are commented out
