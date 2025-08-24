"""Test jobs and pipeline tools."""

from unittest.mock import Mock, patch

import pytest

from server.tools.jobs_pipelines import load_job_tools
from tests.utils import assert_error_response, assert_success_response


class TestJobsAndPipelines:
  """Test job and pipeline operations."""

  @pytest.mark.unit
  def test_list_jobs(self, mcp_server, mock_env_vars):
    """Test listing jobs."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      # Create mock job
      mock_job = Mock()
      mock_job.job_id = 123
      mock_job.settings.name = 'Test Job'
      mock_job.created_time = 1234567890
      mock_job.creator_user_name = 'test@example.com'

      mock_client.return_value.jobs.list.return_value = [mock_job]

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_jobs']
      result = tool.fn()

      assert_success_response(result)
      assert result['count'] == 1
      assert result['jobs'][0]['name'] == 'Test Job'

  @pytest.mark.unit
  def test_submit_job_run(self, mcp_server, mock_env_vars):
    """Test submitting a job run."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      # Mock job run
      mock_run = Mock()
      mock_run.run_id = '456'

      mock_client.return_value.jobs.submit_run.return_value = mock_run

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['submit_job_run']
      result = tool.fn(job_id='123')

      assert_success_response(result)
      assert result['run_id'] == '456'

  @pytest.mark.unit
  def test_list_pipelines(self, mcp_server, mock_env_vars):
    """Test listing pipelines."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      # Create mock pipeline
      mock_pipeline = Mock()
      mock_pipeline.pipeline_id = 'pipeline-123'
      mock_pipeline.name = 'Test Pipeline'
      mock_pipeline.state = 'IDLE'
      mock_pipeline.creator_user_name = 'test@example.com'
      mock_pipeline.created_time = 1234567890

      mock_client.return_value.pipelines.list_pipelines.return_value = [mock_pipeline]

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_pipelines']
      result = tool.fn()

      assert_success_response(result)
      assert result['count'] == 1
      assert result['pipelines'][0]['name'] == 'Test Pipeline'

  @pytest.mark.unit
  def test_get_job(self, mcp_server, mock_env_vars):
    """Test getting job details."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      # Mock job details
      mock_job = Mock()
      mock_job.job_id = 123
      mock_job.settings.name = 'Test Job'
      mock_job.settings.timeout_seconds = 3600
      mock_job.settings.max_concurrent_runs = 1
      mock_job.created_time = 1234567890
      mock_job.creator_user_name = 'test@example.com'

      mock_client.return_value.jobs.get.return_value = mock_job

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_job']
      result = tool.fn(job_id='123')

      assert_success_response(result)
      assert result['job']['job_id'] == 123
      assert result['job']['name'] == 'Test Job'

  @pytest.mark.unit
  def test_get_pipeline(self, mcp_server, mock_env_vars):
    """Test getting pipeline details."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      # Mock pipeline details
      mock_pipeline = Mock()
      mock_pipeline.pipeline_id = 'pipeline-123'
      mock_pipeline.name = 'Test Pipeline'
      mock_pipeline.state = 'IDLE'
      mock_pipeline.creator_user_name = 'test@example.com'
      mock_pipeline.created_time = 1234567890

      mock_client.return_value.pipelines.get.return_value = mock_pipeline

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_pipeline']
      result = tool.fn(pipeline_id='pipeline-123')

      assert_success_response(result)
      assert result['pipeline']['pipeline_id'] == 'pipeline-123'
      assert result['pipeline']['name'] == 'Test Pipeline'

  @pytest.mark.unit
  def test_list_job_runs(self, mcp_server, mock_env_vars):
    """Test listing job runs."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      # Mock job runs
      mock_run = Mock()
      mock_run.run_id = 456
      mock_run.job_id = 123
      mock_run.state = 'SUCCESS'
      mock_run.start_time = 1234567890
      mock_run.end_time = 1234567990

      mock_client.return_value.jobs.list_runs.return_value = [mock_run]

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_job_runs']
      result = tool.fn(job_id=123)

      assert_success_response(result)
      assert result['count'] == 1
      assert result['runs'][0]['run_id'] == 456
      assert result['runs'][0]['state'] == 'SUCCESS'

  @pytest.mark.unit
  def test_list_pipeline_runs(self, mcp_server, mock_env_vars):
    """Test listing pipeline runs."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      # Mock pipeline runs
      mock_run = Mock()
      mock_run.pipeline_id = 'pipeline-123'
      mock_run.run_id = 'run-456'
      mock_run.state = 'COMPLETED'
      mock_run.start_time = 1234567890
      mock_run.end_time = 1234567990

      mock_client.return_value.pipelines.list_pipeline_runs.return_value = [mock_run]

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_pipeline_runs']
      result = tool.fn(pipeline_id='pipeline-123')

      assert_success_response(result)
      assert result['count'] == 1
      assert result['runs'][0]['run_id'] == 'run-456'
      assert result['runs'][0]['state'] == 'COMPLETED'

  @pytest.mark.unit
  def test_cancel_job_run(self, mcp_server, mock_env_vars):
    """Test canceling a job run."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      mock_client.return_value.jobs.cancel_run.return_value = None

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['cancel_job_run']
      result = tool.fn(run_id='456')

      assert_success_response(result)
      assert result['run_id'] == '456'
      assert result['message'] == 'Job run 456 cancelled successfully'

  @pytest.mark.unit
  def test_stop_pipeline_update(self, mcp_server, mock_env_vars):
    """Test stopping a pipeline update."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      mock_client.return_value.pipelines.stop.return_value = None

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['stop_pipeline_update']
      result = tool.fn(pipeline_id='pipeline-123')

      assert_success_response(result)
      assert result['pipeline_id'] == 'pipeline-123'
      assert result['message'] == 'Pipeline update stopped successfully for pipeline-123'

  @pytest.mark.unit
  def test_job_lifecycle(self, mcp_server, mock_env_vars):
    """Test job creation, running, monitoring."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_job, mock_workspace_client

      client = mock_workspace_client()

      # Setup job lifecycle data
      job_data = mock_job()
      mock_job_obj = Mock()
      for key, value in job_data.items():
        if key == 'job_id':
          setattr(mock_job_obj, key, value)
        elif key == 'name':
          mock_job_obj.settings = Mock()
          mock_job_obj.settings.name = value
        else:
          setattr(mock_job_obj, key, value)

      # Setup job runs
      mock_run = Mock()
      mock_run.run_id = 456
      mock_run.job_id = job_data['job_id']
      mock_run.state = 'RUNNING'
      mock_run.start_time = 1234567890
      mock_run.run_name = 'Test Run'

      # Setup job run monitoring states
      completed_run = Mock()
      completed_run.run_id = 456
      completed_run.job_id = job_data['job_id']
      completed_run.state = 'SUCCESS'
      completed_run.start_time = 1234567890
      completed_run.end_time = 1234567990
      completed_run.execution_duration = 100000
      completed_run.state_message = 'Completed successfully'

      client.jobs.list.return_value = [mock_job_obj]
      client.jobs.get.return_value = mock_job_obj
      client.jobs.submit_run.return_value = mock_run
      client.jobs.list_runs.return_value = [completed_run]
      client.jobs.get_run.return_value = completed_run

      mock_client.return_value = client

      load_job_tools(mcp_server)

      # Test job listing
      list_tool = mcp_server._tool_manager._tools['list_jobs']
      list_result = list_tool.fn()

      assert_success_response(list_result)
      assert list_result['count'] == 1
      assert list_result['jobs'][0]['job_id'] == 123

      # Test job running
      submit_tool = mcp_server._tool_manager._tools['submit_job_run']
      submit_result = submit_tool.fn(job_id='123')

      assert_success_response(submit_result)
      assert submit_result['run_id'] == 456

      # Test job monitoring
      runs_tool = mcp_server._tool_manager._tools['list_job_runs']
      runs_result = runs_tool.fn(job_id=123)

      assert_success_response(runs_result)
      assert runs_result['count'] == 1
      assert runs_result['runs'][0]['state'] == 'SUCCESS'
      assert runs_result['runs'][0]['end_time'] is not None

  @pytest.mark.unit
  def test_pipeline_operations(self, mcp_server, mock_env_vars):
    """Test DLT pipeline management."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_pipeline, mock_workspace_client

      client = mock_workspace_client()

      # Setup pipeline data
      pipeline_data = mock_pipeline()
      mock_pipeline_obj = Mock()
      for key, value in pipeline_data.items():
        setattr(mock_pipeline_obj, key, value)

      # Setup pipeline runs
      mock_run = Mock()
      mock_run.pipeline_id = pipeline_data['pipeline_id']
      mock_run.run_id = 'run-789'
      mock_run.state = 'COMPLETED'
      mock_run.start_time = 1234567890
      mock_run.end_time = 1234567990

      # Setup pipeline events
      mock_event = Mock()
      mock_event.event_type = 'FLOW_PROGRESS'
      mock_event.timestamp = 1234567900
      mock_event.message = 'Pipeline processing started'

      client.pipelines.list_pipelines.return_value = [mock_pipeline_obj]
      client.pipelines.get.return_value = mock_pipeline_obj
      client.pipelines.list_pipeline_runs.return_value = [mock_run]
      client.pipelines.list_pipeline_events.return_value = [mock_event]

      mock_client.return_value = client

      load_job_tools(mcp_server)

      # Test pipeline listing
      list_tool = mcp_server._tool_manager._tools['list_pipelines']
      list_result = list_tool.fn()

      assert_success_response(list_result)
      assert list_result['count'] == 1
      assert list_result['pipelines'][0]['pipeline_id'] == 'pipeline-123'

      # Test pipeline state management
      get_tool = mcp_server._tool_manager._tools['get_pipeline']
      get_result = get_tool.fn(pipeline_id='pipeline-123')

      assert_success_response(get_result)
      assert get_result['pipeline']['state'] == 'IDLE'

      # Test pipeline runs
      runs_tool = mcp_server._tool_manager._tools['list_pipeline_runs']
      runs_result = runs_tool.fn(pipeline_id='pipeline-123')

      assert_success_response(runs_result)
      assert runs_result['count'] == 1
      assert runs_result['runs'][0]['state'] == 'COMPLETED'

  @pytest.mark.unit
  def test_job_error_handling(self, mcp_server, mock_env_vars):
    """Test error handling for failed jobs."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_workspace_client

      client = mock_workspace_client()

      # Setup failed job run
      failed_run = Mock()
      failed_run.run_id = 999
      failed_run.job_id = 123
      failed_run.state = 'FAILED'
      failed_run.start_time = 1234567890
      failed_run.end_time = 1234567990
      failed_run.state_message = 'Task failed due to cluster startup timeout'

      client.jobs.get_run.return_value = failed_run
      client.jobs.list_runs.return_value = [failed_run]

      mock_client.return_value = client

      load_job_tools(mcp_server)

      # Test failed job run monitoring
      runs_tool = mcp_server._tool_manager._tools['list_job_runs']
      runs_result = runs_tool.fn(job_id=123)

      assert_success_response(runs_result)
      assert runs_result['count'] == 1
      assert runs_result['runs'][0]['state'] == 'FAILED'

  @pytest.mark.unit
  def test_job_filtering(self, mcp_server, mock_env_vars):
    """Test job listing and filtering."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_workspace_client

      client = mock_workspace_client()

      # Setup multiple jobs with different states
      jobs = []
      for i, name in enumerate(['ETL Job', 'ML Training', 'Data Quality Check']):
        job = Mock()
        job.job_id = 100 + i
        job.settings = Mock()
        job.settings.name = name
        job.settings.timeout_seconds = 3600
        job.created_time = 1234567890 + i * 1000
        job.creator_user_name = f'user{i}@example.com'
        jobs.append(job)

      client.jobs.list.return_value = jobs

      mock_client.return_value = client

      load_job_tools(mcp_server)

      # Test job filtering by listing all
      list_tool = mcp_server._tool_manager._tools['list_jobs']
      list_result = list_tool.fn()

      assert_success_response(list_result)
      assert list_result['count'] == 3
      assert any(job['name'] == 'ETL Job' for job in list_result['jobs'])
      assert any(job['name'] == 'ML Training' for job in list_result['jobs'])
      assert any(job['name'] == 'Data Quality Check' for job in list_result['jobs'])


class TestJobsPipelinesErrorScenarios:
  """Test Jobs and Pipelines error handling across different failure scenarios."""

  @pytest.mark.unit
  def test_job_network_failures(self, mcp_server, mock_env_vars):
    """Test job operations network failure handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test job listing timeout
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Network timeout'), 'Network timeout'
      )

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_jobs']
      result = tool.fn()

      assert_error_response(result)
      assert 'timeout' in result['error'].lower() or 'network' in result['error'].lower()

  @pytest.mark.unit
  def test_job_authentication_errors(self, mcp_server, mock_env_vars):
    """Test job access authentication errors."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test job access denied
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      mock_client.return_value.jobs.get.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Permission denied'),
        'Permission denied',
      )

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_job']
      result = tool.fn(job_id='restricted-job-123')

      assert_error_response(result)
      assert 'access denied' in result['error'].lower() or 'permission' in result['error'].lower()

  @pytest.mark.unit
  def test_pipeline_rate_limiting(self, mcp_server, mock_env_vars):
    """Test pipeline operations rate limiting."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test pipeline listing rate limiting
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      mock_client.return_value.pipelines.list_pipelines.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Rate limiting'), 'Rate limiting'
      )

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_pipelines']
      result = tool.fn()

      assert_error_response(result)
      assert (
        'rate limit' in result['error'].lower() or 'too many requests' in result['error'].lower()
      )

  @pytest.mark.unit
  def test_job_malformed_input_handling(self, mcp_server, mock_env_vars):
    """Test malformed job parameter handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_job_tools(mcp_server)

    # Test invalid job configuration
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
      mock_client.return_value.jobs.create.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Invalid parameters'),
        'Invalid parameters',
      )

      create_tool = mcp_server._tool_manager._tools['create_job']

      # Test malformed job configurations
      malformed_configs = [
        {},  # Empty configuration
        {'name': ''},  # Empty name
        {'name': 'Test Job'},  # Missing required fields
        {'name': 'Test Job', 'tasks': []},  # Empty tasks
        {'name': 'Test Job', 'tasks': 'invalid'},  # Invalid tasks format
      ]

      for config in malformed_configs:
        result = create_tool.fn(job_config=config)
        assert_error_response(result)
        assert 'invalid' in result['error'].lower() or 'parameter' in result['error'].lower()

  @pytest.mark.unit
  def test_job_resource_not_found(self, mcp_server, mock_env_vars):
    """Test job resource not found scenarios."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_job_tools(mcp_server)

    # Test job not found operations
    job_operations = [
      ('get_job', {'job_id': 'nonexistent-job-999'}),
      ('delete_job', {'job_id': 'nonexistent-job-999'}),
      ('list_job_runs', {'job_id': 'nonexistent-job-999'}),
      ('cancel_job_run', {'run_id': 'nonexistent-run-999'}),
    ]

    for tool_name, params in job_operations:
      with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
        # Mock all job methods that could be called
        error_exception = simulate_databricks_error(
          next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Resource not found'),
          'Resource not found',
        )
        mock_client.return_value.jobs.get.side_effect = error_exception
        mock_client.return_value.jobs.delete.side_effect = error_exception
        mock_client.return_value.jobs.list_runs.side_effect = error_exception
        mock_client.return_value.jobs.get_run.side_effect = error_exception
        mock_client.return_value.jobs.cancel_run.side_effect = error_exception

        tool = mcp_server._tool_manager._tools[tool_name]
        result = tool.fn(**params)

        assert_error_response(result)
        assert 'not found' in result['error'].lower() or 'resource' in result['error'].lower()

  @pytest.mark.unit
  def test_pipeline_resource_not_found(self, mcp_server, mock_env_vars):
    """Test pipeline resource not found scenarios."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_job_tools(mcp_server)

    # Test pipeline not found operations
    pipeline_operations = [
      ('get_pipeline', {'pipeline_id': 'nonexistent-pipeline-999'}),
      ('delete_pipeline', {'pipeline_id': 'nonexistent-pipeline-999'}),
      ('list_pipeline_runs', {'pipeline_id': 'nonexistent-pipeline-999'}),
    ]

    for tool_name, params in pipeline_operations:
      with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
        # Mock all pipeline methods that could be called
        error_exception = simulate_databricks_error(
          next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Resource not found'),
          'Resource not found',
        )
        mock_client.return_value.pipelines.get.side_effect = error_exception
        mock_client.return_value.pipelines.delete.side_effect = error_exception
        mock_client.return_value.pipelines.list_pipeline_runs.side_effect = error_exception

        tool = mcp_server._tool_manager._tools[tool_name]
        result = tool.fn(**params)

        assert_error_response(result)
        assert 'not found' in result['error'].lower() or 'resource' in result['error'].lower()
