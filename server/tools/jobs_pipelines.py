"""Jobs and pipelines MCP tools for Databricks."""

import os
from databricks.sdk import WorkspaceClient


def load_job_tools(mcp_server):
    """Register jobs and pipelines MCP tools with the server.
    
    Args:
        mcp_server: The FastMCP server instance to register tools with
    """
    
    # @mcp_server.tool
    # def list_jobs() -> dict:
    #     """List all jobs in the Databricks workspace.

    #     Returns:
    #         Dictionary containing list of jobs with their details
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # List all jobs
    #         jobs = w.jobs.list()
            
    #         job_list = []
    #         for job in jobs:
    #             job_list.append({
    #                 'job_id': job.job_id,
    #                 'name': job.settings.name,
    #                 'creator_user_name': job.creator_user_name,
    #                 'created_time': job.created_time,
    #                 'settings': {
    #                     'timeout_seconds': job.settings.timeout_seconds,
    #                     'max_concurrent_runs': job.settings.max_concurrent_runs,
    #                     'email_notifications': job.settings.email_notifications,
    #                 } if hasattr(job, 'settings') else {},
    #             })

    #         return {
    #             'success': True,
    #             'jobs': job_list,
    #             'count': len(job_list),
    #             'message': f'Found {len(job_list)} job(s)',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error listing jobs: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}', 'jobs': [], 'count': 0}

    # @mcp_server.tool
    # def get_job(job_id: str) -> dict:
    #     """Get detailed information about a specific job.

    #     Args:
    #         job_id: The ID of the job to retrieve

    #     Returns:
    #         Dictionary with detailed job information or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get job details
    #         job = w.jobs.get(job_id)
            
    #         return {
    #             'success': True,
    #             'job': {
    #                 'job_id': job.job_id,
    #                 'name': job.settings.name,
    #                 'creator_user_name': job.creator_user_name,
    #                 'created_time': job.created_time,
    #                 'settings': {
    #                     'timeout_seconds': job.settings.timeout_seconds,
    #                     'max_concurrent_runs': job.settings.max_concurrent_runs,
    #                     'email_notifications': job.settings.email_notifications,
    #                     'tasks': job.settings.tasks,
    #                 } if hasattr(job, 'settings') else {},
    #             },
    #             'message': f'Job {job_id} details retrieved successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting job details: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def create_job(job_config: dict) -> dict:
    #     """Create a new job in the Databricks workspace.

    #     Args:
    #         job_config: Dictionary containing job configuration

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Create job
    #         job = w.jobs.create(
    #             name=job_config.get('name'),
    #             tasks=job_config.get('tasks', []),
    #             timeout_seconds=job_config.get('timeout_seconds', 3600),
    #             max_concurrent_runs=job_config.get('max_concurrent_runs', 1),
    #             email_notifications=job_config.get('email_notifications'),
    #         )
            
    #         return {
    #             'success': True,
    #             'job_id': job.job_id,
    #             'job_name': job.settings.name,
    #             'message': f'Job {job.settings.name} created successfully with ID {job.job_id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error creating job: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def update_job(job_id: str, updates: dict) -> dict:
    #     """Update an existing job in the Databricks workspace.

    #     Args:
    #         job_id: The ID of the job to update
    #         updates: Dictionary containing the updates to apply

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Update job
    #         w.jobs.update(
    #             job_id=job_id,
    #             new_settings=updates,
    #         )
            
    #         return {
    #             'success': True,
    #             'job_id': job_id,
    #             'message': f'Job {job_id} updated successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error updating job: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def delete_job(job_id: str) -> dict:
    #     """Delete a job from the Databricks workspace.

    #     Args:
    #         job_id: The ID of the job to delete

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Delete job
    #         w.jobs.delete(job_id)
            
    #         return {
    #             'success': True,
    #             'job_id': job_id,
    #             'message': f'Job {job_id} deleted successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error deleting job: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def list_job_runs(job_id: str = None) -> dict:
    #     """List job runs, either all runs or runs for a specific job.

    #     Args:
    #         job_id: Optional job ID to filter runs for a specific job

    #     Returns:
    #         Dictionary containing list of job runs with their details
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # List job runs
    #         if job_id:
    #             runs = w.jobs.list_runs(job_id=job_id)
    #         else:
    #             runs = w.jobs.list_runs()
            
    #         run_list = []
    #         for run in runs:
    #             run_list.append({
    #                 'run_id': run.run_id,
    #                 'job_id': run.job_id,
    #                 'run_name': run.run_name,
    #                 'state': run.state,
    #                 'start_time': run.start_time,
    #                 'end_time': run.end_time,
    #                 'creator_user_name': run.creator_user_name,
    #             })

    #         return {
    #             'success': True,
    #             'runs': run_list,
    #             'count': len(run_list),
    #             'job_id': job_id,
    #             'message': f'Found {len(run_list)} job run(s)' + (f' for job {job_id}' if job_id else ''),
    #         }

    #     except Exception as e:
    #         print(f'❌ Error listing job runs: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}', 'runs': [], 'count': 0}

    # @mcp_server.tool
    # def get_job_run(run_id: str) -> dict:
    #     """Get detailed information about a specific job run.

    #     Args:
    #         run_id: The ID of the job run to retrieve

    #     Returns:
    #         Dictionary with detailed job run information or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get job run details
    #         run = w.jobs.get_run(run_id)
            
    #         return {
    #             'success': True,
    #             'run': {
    #                 'run_id': run.run_id,
    #                 'job_id': run.job_id,
    #                 'run_name': run.run_name,
    #                 'state': run.state,
    #                 'start_time': run.start_time,
    #                 'end_time': run.end_time,
    #                 'creator_user_name': run.creator_user_name,
    #                 'run_page_url': run.run_page_url,
    #                 'tasks': run.tasks,
    #             },
    #             'message': f'Job run {run_id} details retrieved successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting job run details: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def submit_job_run(job_id: str, parameters: dict = None) -> dict:
    #     """Submit a new job run.

    #     Args:
    #         job_id: The ID of the job to run
    #         parameters: Optional parameters to pass to the job run

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Submit job run
    #         run = w.jobs.submit_run(
    #             job_id=job_id,
    #             parameters=parameters or {},
    #         )
            
    #         return {
    #             'success': True,
    #             'job_id': job_id,
    #             'run_id': run.run_id,
    #             'message': f'Job run submitted successfully with run ID {run.run_id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error submitting job run: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def cancel_job_run(run_id: str) -> dict:
    #     """Cancel a running job run.

    #     Args:
    #         run_id: The ID of the job run to cancel

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Cancel job run
    #         w.jobs.cancel_run(run_id)
            
    #         return {
    #             'success': True,
    #             'run_id': run_id,
    #             'message': f'Job run {run_id} cancelled successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error cancelling job run: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def get_job_run_logs(run_id: str) -> dict:
    #     """Get logs from a job run.

    #     Args:
    #         run_id: The ID of the job run to get logs for

    #     Returns:
    #         Dictionary with job run logs or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get job run logs
    #         logs = w.jobs.get_run_output(run_id)
            
    #         return {
    #             'success': True,
    #             'run_id': run_id,
    #             'logs': {
    #                 'notebook_output': logs.notebook_output,
    #                 'sql_output': logs.sql_output,
    #                 'dbt_output': logs.dbt_output,
    #                 'run_output': logs.run_output,
    #             },
    #             'message': f'Job run logs retrieved successfully for {run_id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting job run logs: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def list_pipelines() -> dict:
    #     """List all DLT pipelines in the workspace.

    #     Returns:
    #         Dictionary containing list of pipelines with their details
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # List all pipelines
    #         pipelines = w.pipelines.list_pipelines()
            
    #         pipeline_list = []
    #         for pipeline in pipelines:
    #             pipeline_list.append({
    #                 'pipeline_id': pipeline.pipeline_id,
    #                 'name': pipeline.name,
    #                 'state': pipeline.state,
    #                 'creator_user_name': pipeline.creator_user_name,
    #                 'created_time': pipeline.created_time,
    #                 'updated_time': pipeline.updated_time,
    #             })

    #         return {
    #             'success': True,
    #             'pipelines': pipeline_list,
    #             'count': len(pipeline_list),
    #             'message': f'Found {len(pipeline_list)} pipeline(s)',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error listing pipelines: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}', 'pipelines': [], 'count': 0}

    # @mcp_server.tool
    # def get_pipeline(pipeline_id: str) -> dict:
    #     """Get details of a specific DLT pipeline.

    #     Args:
    #         pipeline_id: The ID of the pipeline to get details for

    #     Returns:
    #         Dictionary with pipeline details or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get pipeline details
    #         pipeline = w.pipelines.get(pipeline_id)
            
    #         return {
    #             'success': True,
    #             'pipeline': {
    #                 'pipeline_id': pipeline.pipeline_id,
    #                 'name': pipeline.name,
    #                 'state': pipeline.state,
    #                 'creator_user_name': pipeline.creator_user_name,
    #                 'created_time': pipeline.created_time,
    #                 'updated_time': pipeline.updated_time,
    #                 'specification': pipeline.specification,
    #             },
    #             'message': f'Pipeline {pipeline_id} details retrieved successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting pipeline details: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def create_pipeline(pipeline_config: dict) -> dict:
    #     """Create a new DLT pipeline.

    #     Args:
    #         pipeline_config: Dictionary containing pipeline configuration

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Create pipeline
    #         pipeline = w.pipelines.create(
    #             name=pipeline_config.get('name'),
    #             specification=pipeline_config.get('specification'),
    #         )
            
    #         return {
    #             'success': True,
    #             'pipeline_id': pipeline.pipeline_id,
    #             'pipeline_name': pipeline.name,
    #             'message': f'Pipeline {pipeline.name} created successfully with ID {pipeline.pipeline_id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error creating pipeline: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def update_pipeline(pipeline_id: str, updates: dict) -> dict:
    #     """Update an existing DLT pipeline.

    #     Args:
    #         pipeline_id: The ID of the pipeline to update
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

    #         # Update pipeline
    #         w.pipelines.edit(
    #             pipeline_id=pipeline_id,
    #             **updates,
    #         )
            
    #         return {
    #             'success': True,
    #             'pipeline_id': pipeline_id,
    #             'message': f'Pipeline {pipeline_id} updated successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error updating pipeline: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def delete_pipeline(pipeline_id: str) -> dict:
    #     """Delete a DLT pipeline.

    #     Args:
    #         pipeline_id: The ID of the pipeline to delete

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Delete pipeline
    #         w.pipelines.delete(pipeline_id)
            
    #         return {
    #             'success': True,
    #             'pipeline_id': pipeline_id,
    #             'message': f'Pipeline {pipeline_id} deleted successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error deleting pipeline: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def list_pipeline_runs(pipeline_id: str = None) -> dict:
    #     """List DLT pipeline runs.

    #     Args:
    #         pipeline_id: Optional pipeline ID to filter runs (default: None for all)

    #     Returns:
    #         Dictionary containing list of pipeline runs with their details
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # List pipeline runs
    #         if pipeline_id:
    #             runs = w.pipelines.list_pipeline_runs(pipeline_id=pipeline_id)
    #         else:
    #             runs = w.pipelines.list_pipeline_runs()
            
    #         run_list = []
    #         for run in runs:
    #             run_list.append({
    #                 'run_id': run.run_id,
    #                 'pipeline_id': run.pipeline_id,
    #                 'state': run.state,
    #                 'start_time': run.start_time,
    #                 'end_time': run.end_time,
    #                 'creator_user_name': run.creator_user_name,
    #             })

    #         return {
    #             'success': True,
    #             'runs': run_list,
    #             'count': len(run_list),
    #             'pipeline_id': pipeline_id,
    #             'message': f'Found {len(run_list)} pipeline run(s)' + (f' for pipeline {pipeline_id}' if pipeline_id else ''),
    #         }

    #     except Exception as e:
    #         print(f'❌ Error listing pipeline runs: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}', 'runs': [], 'count': 0}

    # @mcp_server.tool
    # def get_pipeline_run(run_id: str) -> dict:
    #     """Get details of a specific DLT pipeline run.

    #     Args:
    #         run_id: The ID of the pipeline run to get details for

    #     Returns:
    #         Dictionary with pipeline run details or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Get pipeline run details
    #         run = w.pipelines.get_pipeline_run(run_id)
            
    #         return {
    #             'success': True,
    #             'run': {
    #                 'run_id': run.run_id,
    #                 'pipeline_id': run.pipeline_id,
    #                 'state': run.state,
    #                 'start_time': run.start_time,
    #                 'end_time': run.end_time,
    #                 'creator_user_name': run.creator_user_name,
    #                 'run_page_url': run.run_page_url,
    #             },
    #             'message': f'Pipeline run {run_id} details retrieved successfully',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error getting pipeline run details: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def start_pipeline_update(pipeline_id: str, parameters: dict = None) -> dict:
    #     """Start a DLT pipeline update.

    #     Args:
    #         pipeline_id: The ID of the pipeline to start
    #         parameters: Optional parameters for the pipeline update

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Start pipeline update
    #         run = w.pipelines.start_update(
    #             pipeline_id=pipeline_id,
    #             parameters=parameters or {},
    #         )
            
    #         return {
    #             'success': True,
    #             'pipeline_id': pipeline_id,
    #             'run_id': run.run_id,
    #             'message': f'Pipeline update started successfully with run ID {run.run_id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error starting pipeline update: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    # @mcp_server.tool
    # def stop_pipeline_update(pipeline_id: str) -> dict:
    #     """Stop a running DLT pipeline update.

    #     Args:
    #         pipeline_id: The ID of the pipeline to stop

    #     Returns:
    #         Dictionary with operation result or error message
    #     """
    #     try:
    #         # Initialize Databricks SDK
    #         w = WorkspaceClient(
    #             host=os.environ.get('DATABRICKS_HOST'), 
    #             token=os.environ.get('DATABRICKS_TOKEN')
    #         )

    #         # Stop pipeline update
    #         w.pipelines.stop_update(pipeline_id)
            
    #         return {
    #             'success': True,
    #             'pipeline_id': pipeline_id,
    #             'message': f'Pipeline update stopped successfully for {pipeline_id}',
    #         }

    #     except Exception as e:
    #         print(f'❌ Error stopping pipeline update: {str(e)}')
    #         return {'success': False, 'error': f'Error: {str(e)}'}

    pass  # All tools are commented out
