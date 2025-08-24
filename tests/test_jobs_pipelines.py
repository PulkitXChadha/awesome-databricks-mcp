"""Test jobs and pipeline tools."""
import pytest
from unittest.mock import patch, Mock
from tests.utils import assert_success_response
from server.tools.jobs_pipelines import load_job_tools

class TestJobsAndPipelines:
    """Test job and pipeline operations."""
    
    @pytest.mark.unit
    def test_list_jobs(self, mcp_server, mock_env_vars):
        """Test listing jobs."""
        with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
            # Create mock job
            mock_job = Mock()
            mock_job.job_id = 123
            mock_job.settings.name = "Test Job"
            mock_job.created_time = 1234567890
            mock_job.creator_user_name = "test@example.com"
            
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
            mock_run.run_id = "456"
            
            mock_client.return_value.jobs.submit_run.return_value = mock_run
            
            load_job_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['submit_job_run']
            result = tool.fn(job_id="123")
            
            assert_success_response(result)
            assert result['run_id'] == "456"
    
    @pytest.mark.unit
    def test_list_pipelines(self, mcp_server, mock_env_vars):
        """Test listing pipelines."""
        with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
            # Create mock pipeline
            mock_pipeline = Mock()
            mock_pipeline.pipeline_id = "pipeline-123"
            mock_pipeline.name = "Test Pipeline"
            mock_pipeline.state = "IDLE"
            mock_pipeline.creator_user_name = "test@example.com"
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
            mock_job.settings.name = "Test Job"
            mock_job.settings.timeout_seconds = 3600
            mock_job.settings.max_concurrent_runs = 1
            mock_job.created_time = 1234567890
            mock_job.creator_user_name = "test@example.com"
            
            mock_client.return_value.jobs.get.return_value = mock_job
            
            load_job_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['get_job']
            result = tool.fn(job_id="123")
            
            assert_success_response(result)
            assert result['job']['job_id'] == 123
            assert result['job']['name'] == "Test Job"
    
    @pytest.mark.unit
    def test_get_pipeline(self, mcp_server, mock_env_vars):
        """Test getting pipeline details."""
        with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
            # Mock pipeline details
            mock_pipeline = Mock()
            mock_pipeline.pipeline_id = "pipeline-123"
            mock_pipeline.name = "Test Pipeline"
            mock_pipeline.state = "IDLE"
            mock_pipeline.creator_user_name = "test@example.com"
            mock_pipeline.created_time = 1234567890
            
            mock_client.return_value.pipelines.get.return_value = mock_pipeline
            
            load_job_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['get_pipeline']
            result = tool.fn(pipeline_id="pipeline-123")
            
            assert_success_response(result)
            assert result['pipeline']['pipeline_id'] == "pipeline-123"
            assert result['pipeline']['name'] == "Test Pipeline"
    
    @pytest.mark.unit
    def test_list_job_runs(self, mcp_server, mock_env_vars):
        """Test listing job runs."""
        with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
            # Mock job runs
            mock_run = Mock()
            mock_run.run_id = 456
            mock_run.job_id = 123
            mock_run.state = "SUCCESS"
            mock_run.start_time = 1234567890
            mock_run.end_time = 1234567990
            
            mock_client.return_value.jobs.list_runs.return_value = [mock_run]
            
            load_job_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_job_runs']
            result = tool.fn(job_id=123)
            
            assert_success_response(result)
            assert result['count'] == 1
            assert result['runs'][0]['run_id'] == 456
            assert result['runs'][0]['state'] == "SUCCESS"
    
    @pytest.mark.unit
    def test_list_pipeline_runs(self, mcp_server, mock_env_vars):
        """Test listing pipeline runs."""
        with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
            # Mock pipeline runs
            mock_run = Mock()
            mock_run.pipeline_id = "pipeline-123"
            mock_run.run_id = "run-456"
            mock_run.state = "COMPLETED"
            mock_run.start_time = 1234567890
            mock_run.end_time = 1234567990
            
            mock_client.return_value.pipelines.list_pipeline_runs.return_value = [mock_run]
            
            load_job_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['list_pipeline_runs']
            result = tool.fn(pipeline_id="pipeline-123")
            
            assert_success_response(result)
            assert result['count'] == 1
            assert result['runs'][0]['run_id'] == "run-456"
            assert result['runs'][0]['state'] == "COMPLETED"
    
    @pytest.mark.unit
    def test_cancel_job_run(self, mcp_server, mock_env_vars):
        """Test canceling a job run."""
        with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
            mock_client.return_value.jobs.cancel_run.return_value = None
            
            load_job_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['cancel_job_run']
            result = tool.fn(run_id="456")
            
            assert_success_response(result)
            assert result['run_id'] == "456"
            assert result['message'] == "Job run 456 cancelled successfully"
    
    @pytest.mark.unit
    def test_stop_pipeline_update(self, mcp_server, mock_env_vars):
        """Test stopping a pipeline update."""
        with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client:
            mock_client.return_value.pipelines.stop.return_value = None
            
            load_job_tools(mcp_server)
            tool = mcp_server._tool_manager._tools['stop_pipeline_update']
            result = tool.fn(pipeline_id="pipeline-123")
            
            assert_success_response(result)
            assert result['pipeline_id'] == "pipeline-123"
            assert result['message'] == "Pipeline update stopped successfully for pipeline-123"
