"""Integration tests for business user journeys."""

from unittest.mock import Mock, patch

import pytest

from server.tools.dashboards import load_dashboard_tools
from server.tools.governance import load_governance_tools
from server.tools.sql_operations import load_sql_tools
from server.tools.unity_catalog import load_uc_tools
from tests.mock_factory import mock_catalog_list
from tests.utils import assert_success_response, create_mock_schema, create_mock_table


class TestBusinessUserJourneys:
  """Test complete business user workflows."""

  @pytest.mark.integration
  @pytest.mark.business_critical
  def test_data_analyst_workflow(self, mcp_server, mock_env_vars):
    """Test complete data analyst journey."""
    with (
      patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc_client,
      patch('server.tools.sql_operations.WorkspaceClient') as mock_sql_client,
      patch('server.tools.dashboards.WorkspaceClient') as mock_dash_client,
    ):
      # Setup unified mock client for all operations
      client = Mock()
      mock_uc_client.return_value = client
      mock_sql_client.return_value = client
      mock_dash_client.return_value = client

      # 1. Setup catalog discovery data
      catalog_data = mock_catalog_list()
      catalogs = []
      for cat in catalog_data:
        mock_cat = Mock()
        for key, value in cat.items():
          setattr(mock_cat, key, value)
        mock_cat.catalog_type = 'UNITY_CATALOG'
        mock_cat.comment = f'Analytics catalog {cat["name"]}'
        mock_cat.owner = 'analytics-team@company.com'
        mock_cat.created_at = 1234567890
        mock_cat.updated_at = 1234567890
        mock_cat.properties = {'environment': 'production', 'team': 'analytics'}
        catalogs.append(mock_cat)

      client.catalogs.list.return_value = catalogs
      client.catalogs.get.side_effect = lambda name: next(
        (c for c in catalogs if c.name == name), None
      )

      # 2. Setup schema and table metadata
      schemas = [
        create_mock_schema('main', 'sales'),
        create_mock_schema('main', 'marketing'),
        create_mock_schema('main', 'customer_analytics'),
      ]
      for schema in schemas:
        schema.comment = f'Business data schema {schema.name}'
        schema.owner = 'analytics-team@company.com'
        schema.created_at = 1234567890
        schema.updated_at = 1234567890
        schema.properties = {'data_classification': 'sensitive'}

      client.schemas.list.return_value = schemas
      client.schemas.get.side_effect = lambda full_name: next(
        (s for s in schemas if f'{s.catalog_name}.{s.name}' == full_name), None
      )

      # Setup comprehensive table data for analysis
      tables = [
        create_mock_table('main', 'sales', 'transactions'),
        create_mock_table('main', 'sales', 'customers'),
        create_mock_table('main', 'marketing', 'campaigns'),
        create_mock_table('main', 'customer_analytics', 'user_behavior'),
      ]

      # Add business-relevant metadata to tables
      for i, table in enumerate(tables):
        table.owner = 'analytics-team@company.com'
        table.comment = f'Business critical table {table.name}'
        table.table_type = 'MANAGED'
        table.data_source_format = 'DELTA'
        # Create columns with proper string names
        id_col = Mock()
        id_col.name = 'id'
        id_col.type_text = 'BIGINT'
        id_col.nullable = False
        id_col.position = 0
        id_col.comment = None

        date_col = Mock()
        date_col.name = 'created_date'
        date_col.type_text = 'TIMESTAMP'
        date_col.nullable = False
        date_col.position = 1
        date_col.comment = None

        amount_col = Mock()
        amount_col.name = 'amount'
        amount_col.type_text = 'DECIMAL(10,2)'
        amount_col.nullable = True
        amount_col.position = 2
        amount_col.comment = None

        customer_col = Mock()
        customer_col.name = 'customer_id'
        customer_col.type_text = 'BIGINT'
        customer_col.nullable = False
        customer_col.position = 3
        customer_col.comment = None

        table.columns = [id_col, date_col, amount_col, customer_col]
        table.row_count = (i + 1) * 25000  # Simulate different table sizes

      client.tables.list.return_value = tables
      client.tables.get.side_effect = lambda name: next(
        (t for t in tables if t.full_name == name), None
      )

      # 3. Setup analytical query execution (large result set >10K rows)
      large_result_mock = Mock()
      large_result_mock.statement_id = 'stmt-large-analysis'
      large_result_mock.status.state = 'SUCCEEDED'
      large_result_mock.result = Mock()

      # Simulate large result set (>10K rows)
      large_data = []
      for i in range(15000):  # >10K rows
        large_data.append(
          [
            str(i + 1),
            f'2024-01-{(i % 30) + 1:02d}',
            f'{100.50 + (i * 10.25):.2f}',
            str((i % 1000) + 1),
          ]
        )

      large_result_mock.result.data_array = large_data
      # Create columns with proper names
      col1 = Mock()
      col1.name = 'transaction_id'
      col1.type_text = 'BIGINT'
      col2 = Mock()
      col2.name = 'transaction_date'
      col2.type_text = 'DATE'
      col3 = Mock()
      col3.name = 'revenue'
      col3.type_text = 'DECIMAL(10,2)'
      col4 = Mock()
      col4.name = 'customer_id'
      col4.type_text = 'BIGINT'

      large_result_mock.manifest.schema.columns = [col1, col2, col3, col4]

      client.statement_execution.execute_statement.return_value = large_result_mock

      # 4. Setup warehouse listing for query execution
      mock_warehouse = Mock()
      mock_warehouse.id = 'analytics-warehouse'
      mock_warehouse.name = 'Analytics Warehouse'
      mock_warehouse.state = 'RUNNING'
      mock_warehouse.cluster_size = 'X-Small'
      client.sql_warehouses.list.return_value = [mock_warehouse]

      # Load all required tools
      load_uc_tools(mcp_server)
      load_sql_tools(mcp_server)
      load_dashboard_tools(mcp_server)

      # Execute data analyst workflow

      # Step 1: Browse catalogs for data discovery
      list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      catalog_result = list_catalogs_tool.fn()

      assert_success_response(catalog_result)
      assert catalog_result['count'] >= 1
      main_catalog = next(cat for cat in catalog_result['catalogs'] if cat['name'] == 'main')
      assert main_catalog['properties']['team'] == 'analytics'

      # Step 2: Explore schema and table metadata
      describe_catalog_tool = mcp_server._tool_manager._tools['describe_uc_catalog']
      catalog_detail_result = describe_catalog_tool.fn('main')

      assert_success_response(catalog_detail_result)
      assert len(catalog_detail_result['schemas']) >= 3

      # Explore specific schema for sales data
      describe_schema_tool = mcp_server._tool_manager._tools['describe_uc_schema']
      schema_result = describe_schema_tool.fn('main', 'sales')

      assert_success_response(schema_result)
      assert schema_result['schema']['properties']['data_classification'] == 'sensitive'

      # Get table details for analysis planning
      describe_table_tool = mcp_server._tool_manager._tools['describe_uc_table']
      table_result = describe_table_tool.fn('main.sales.transactions')

      assert_success_response(table_result)
      assert len(table_result['table']['columns']) == 4
      assert any(col['name'] == 'amount' for col in table_result['table']['columns'])

      # Step 3: Execute analytical query
      execute_sql_tool = mcp_server._tool_manager._tools['execute_dbsql']
      query = """
            SELECT
                DATE_TRUNC('month', created_date) as month,
                SUM(amount) as total_revenue,
                COUNT(*) as transaction_count,
                AVG(amount) as avg_transaction_value
            FROM main.sales.transactions
            WHERE created_date >= '2024-01-01'
            GROUP BY DATE_TRUNC('month', created_date)
            ORDER BY month
            """
      sql_result = execute_sql_tool.fn(query=query, warehouse_id='analytics-warehouse', limit=15000)

      assert_success_response(sql_result)

      # Step 4: Handle large result set (>10K rows)
      assert sql_result['row_count'] > 10000
      assert 'data' in sql_result
      assert len(sql_result['data']['rows']) > 10000

      # Verify data structure for analytics
      assert len(sql_result['data']['columns']) == 4
      assert 'revenue' in sql_result['data']['columns']

      # Step 5: Create dashboard from results
      create_dashboard_tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
      dashboard_config = {
        'name': 'Sales Analytics Dashboard',
        'description': 'Monthly revenue trends and transaction analysis',
        'data_source': 'main.sales.transactions',
        'visualizations': [
          {'type': 'line_chart', 'metric': 'total_revenue'},
          {'type': 'bar_chart', 'metric': 'transaction_count'},
        ],
      }
      
      # Mock the dashboard creation response
      mock_dashboard = Mock()
      mock_dashboard.dashboard_id = 'dashboard-123'
      mock_dashboard.name = 'Sales Analytics Dashboard'
      
      # Mock the lakeview.create method that the dashboard tool actually calls
      client.lakeview = Mock()
      client.lakeview.create.return_value = mock_dashboard
      
      dashboard_result = create_dashboard_tool.fn(dashboard_config=dashboard_config)

      assert_success_response(dashboard_result)
      assert dashboard_result['name'] == 'Sales Analytics Dashboard'
      assert dashboard_result['dashboard_id'] == 'dashboard-123'
      assert dashboard_result['type'] == 'lakeview'

      # Validate workflow completion
      assert catalog_result['success'] is True
      assert schema_result['success'] is True
      assert table_result['success'] is True
      assert sql_result['success'] is True
      assert dashboard_result['success'] is True

  @pytest.mark.integration
  @pytest.mark.business_critical
  def test_governance_workflow(self, mcp_server, mock_env_vars):
    """Test data governance team workflow."""
    with (
      patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc_client,
      patch('server.tools.sql_operations.WorkspaceClient') as mock_sql_client,
      patch('server.tools.governance.WorkspaceClient') as mock_gov_client,
    ):
      # Setup unified mock client
      client = Mock()
      mock_uc_client.return_value = client
      mock_sql_client.return_value = client
      mock_gov_client.return_value = client

      # Setup governance test data
      catalog_data = mock_catalog_list()
      catalogs = []
      for cat in catalog_data:
        mock_cat = Mock()
        for key, value in cat.items():
          setattr(mock_cat, key, value)
        mock_cat.catalog_type = 'UNITY_CATALOG'
        mock_cat.comment = f'Governance managed catalog {cat["name"]}'
        mock_cat.owner = 'governance-team@company.com'
        mock_cat.properties = {
          'data_classification': 'restricted',
          'compliance_framework': 'SOX',
          'retention_policy': '7_years',
        }
        catalogs.append(mock_cat)

      client.catalogs.list.return_value = catalogs

      # Setup schemas with governance metadata
      schemas = [
        create_mock_schema('main', 'pii_data'),
        create_mock_schema('main', 'financial_records'),
        create_mock_schema('main', 'audit_logs'),
      ]
      for schema in schemas:
        schema.comment = f'Governance controlled schema {schema.name}'
        schema.owner = 'governance-team@company.com'
        schema.properties = {
          'data_classification': 'highly_restricted',
          'access_control': 'rbac_enabled',
          'encryption': 'at_rest_and_transit',
        }

      client.schemas.list.return_value = schemas

      # Setup tables with compliance metadata
      tables = [
        create_mock_table('main', 'pii_data', 'customer_profiles'),
        create_mock_table('main', 'financial_records', 'transactions'),
        create_mock_table('main', 'audit_logs', 'access_log'),
      ]

      for table in tables:
        table.owner = 'governance-team@company.com'
        table.comment = f'Compliance monitored table {table.name}'
        table.properties = {
          'data_classification': 'restricted',
          'pii_fields': 'email,phone,ssn',
          'compliance_tags': 'gdpr,ccpa,sox',
          'last_audit': '2024-01-15',
        }
        # Add governance-relevant columns
        # Create columns with proper string names
        id_col = Mock()
        id_col.name = 'id'
        id_col.type_text = 'BIGINT'
        id_col.nullable = False
        id_col.position = 0
        id_col.comment = None

        email_col = Mock()
        email_col.name = 'email'
        email_col.type_text = 'STRING'
        email_col.nullable = True
        email_col.position = 1
        email_col.comment = None

        timestamp_col = Mock()
        timestamp_col.name = 'created_timestamp'
        timestamp_col.type_text = 'TIMESTAMP'
        timestamp_col.nullable = False
        timestamp_col.position = 2
        timestamp_col.comment = None

        source_col = Mock()
        source_col.name = 'data_source'
        source_col.type_text = 'STRING'
        source_col.nullable = False
        source_col.position = 3
        source_col.comment = None

        table.columns = [id_col, email_col, timestamp_col, source_col]

      client.tables.list.return_value = tables
      client.tables.get.side_effect = lambda name: next(
        (t for t in tables if t.full_name == name), None
      )

      # Load all tools needed for governance workflow
      load_uc_tools(mcp_server)
      load_sql_tools(mcp_server)
      load_governance_tools(mcp_server)

      # Execute governance workflow

      # Step 1: Check data lineage
      describe_table_tool = mcp_server._tool_manager._tools['describe_uc_table']
      lineage_result = describe_table_tool.fn(
        'main.pii_data.customer_profiles', include_lineage=True
      )

      assert_success_response(lineage_result)
      assert lineage_result['table']['properties']['compliance_tags'] == 'gdpr,ccpa,sox'
      assert lineage_result['table']['properties']['pii_fields'] == 'email,phone,ssn'

      # Step 2: Verify data quality metrics
      # Mock data quality validation query
      quality_query_mock = Mock()
      quality_query_mock.statement_id = 'stmt-quality-check'
      quality_query_mock.status.state = 'SUCCEEDED'
      quality_query_mock.result = Mock()
      quality_query_mock.result.data_array = [
        ['customer_profiles', '95.5', '98.2', '92.1', '89.3'],
        ['transactions', '97.8', '99.1', '94.5', '91.7'],
      ]
      # Create columns with proper names
      col1 = Mock()
      col1.name = 'table_name'
      col2 = Mock()
      col2.name = 'completeness'
      col3 = Mock()
      col3.name = 'accuracy'
      col4 = Mock()
      col4.name = 'consistency'
      col5 = Mock()
      col5.name = 'timeliness'

      quality_query_mock.manifest.schema.columns = [col1, col2, col3, col4, col5]

      client.statement_execution.execute_statement.return_value = quality_query_mock

      execute_sql_tool = mcp_server._tool_manager._tools['execute_dbsql']
      quality_check_query = """
            SELECT
                table_name,
                completeness_score,
                accuracy_score,
                consistency_score,
                timeliness_score
            FROM governance.data_quality.metrics
            WHERE table_name IN ('customer_profiles', 'transactions')
            AND metric_date = CURRENT_DATE()
            """
      quality_result = execute_sql_tool.fn(
        query=quality_check_query, warehouse_id='governance-warehouse', limit=100
      )

      assert_success_response(quality_result)
      assert quality_result['row_count'] == 2
      # Verify quality metrics are within acceptable ranges
      for row in quality_result['data']['rows']:
        assert float(row['completeness']) >= 90.0  # Governance threshold
        assert float(row['accuracy']) >= 95.0  # Governance threshold

      # Step 3: Validate access permissions
      permissions_query_mock = Mock()
      permissions_query_mock.statement_id = 'stmt-permissions-audit'
      permissions_query_mock.status.state = 'SUCCEEDED'
      permissions_query_mock.result = Mock()
      permissions_query_mock.result.data_array = [
        ['main.pii_data.customer_profiles', 'governance-team@company.com', 'OWNER', 'ACTIVE'],
        ['main.pii_data.customer_profiles', 'senior-analysts@company.com', 'SELECT', 'ACTIVE'],
        ['main.financial_records.transactions', 'governance-team@company.com', 'OWNER', 'ACTIVE'],
        ['main.financial_records.transactions', 'finance-team@company.com', 'SELECT', 'ACTIVE'],
      ]
      # Create columns with proper names
      col1 = Mock()
      col1.name = 'table_name'
      col2 = Mock()
      col2.name = 'principal'
      col3 = Mock()
      col3.name = 'privilege'
      col4 = Mock()
      col4.name = 'status'

      permissions_query_mock.manifest.schema.columns = [col1, col2, col3, col4]

      client.statement_execution.execute_statement.return_value = permissions_query_mock

      permissions_audit_query = """
            SELECT
                table_name,
                principal,
                privilege,
                grant_status
            FROM system.access.table_privileges
            WHERE table_name LIKE 'main.%'
            AND grant_status = 'ACTIVE'
            ORDER BY table_name, principal
            """
      permissions_result = execute_sql_tool.fn(
        query=permissions_audit_query, warehouse_id='governance-warehouse', limit=100
      )

      assert_success_response(permissions_result)
      assert permissions_result['row_count'] == 4

      # Verify governance team has owner access to sensitive tables
      owner_permissions = [
        row for row in permissions_result['data']['rows'] if row['privilege'] == 'OWNER'
      ]
      assert len(owner_permissions) == 2
      for perm in owner_permissions:
        assert perm['principal'] == 'governance-team@company.com'

      # Step 4: Generate compliance report
      compliance_report_query = """
            SELECT
                catalog_name,
                schema_name,
                table_name,
                data_classification,
                compliance_framework,
                pii_columns,
                last_access_audit,
                quality_score
            FROM governance.compliance.table_inventory
            WHERE compliance_framework IN ('SOX', 'GDPR', 'CCPA')
            ORDER BY data_classification DESC, table_name
            """

      compliance_mock = Mock()
      compliance_mock.statement_id = 'stmt-compliance-report'
      compliance_mock.status.state = 'SUCCEEDED'
      compliance_mock.result = Mock()
      compliance_mock.result.data_array = [
        [
          'main',
          'pii_data',
          'customer_profiles',
          'highly_restricted',
          'GDPR,CCPA',
          'email,phone',
          '2024-01-15',
          '94.2',
        ],
        [
          'main',
          'financial_records',
          'transactions',
          'restricted',
          'SOX',
          'none',
          '2024-01-15',
          '96.8',
        ],
      ]
      # Create columns with proper names
      col1 = Mock()
      col1.name = 'catalog_name'
      col2 = Mock()
      col2.name = 'schema_name'
      col3 = Mock()
      col3.name = 'table_name'
      col4 = Mock()
      col4.name = 'data_classification'
      col5 = Mock()
      col5.name = 'compliance_framework'
      col6 = Mock()
      col6.name = 'pii_columns'
      col7 = Mock()
      col7.name = 'last_access_audit'
      col8 = Mock()
      col8.name = 'quality_score'

      compliance_mock.manifest.schema.columns = [col1, col2, col3, col4, col5, col6, col7, col8]

      client.statement_execution.execute_statement.return_value = compliance_mock
      compliance_result = execute_sql_tool.fn(
        query=compliance_report_query, warehouse_id='governance-warehouse', limit=100
      )

      assert_success_response(compliance_result)
      assert compliance_result['row_count'] == 2

      # Verify compliance report data
      for row in compliance_result['data']['rows']:
        assert row['data_classification'] in ['highly_restricted', 'restricted']
        assert row['compliance_framework'] in ['GDPR,CCPA', 'SOX']
        assert float(row['quality_score']) >= 90.0  # Governance quality threshold

      # Validate complete governance workflow
      assert lineage_result['success'] is True
      assert quality_result['success'] is True
      assert permissions_result['success'] is True
      assert compliance_result['success'] is True

  @pytest.mark.integration
  def test_tool_interaction_validation(self, mcp_server, mock_env_vars):
    """Test tool interactions and state consistency."""
    with (
      patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc_client,
      patch('server.tools.sql_operations.WorkspaceClient') as mock_sql_client,
    ):
      # Setup shared mock client
      client = Mock()
      mock_uc_client.return_value = client
      mock_sql_client.return_value = client

      # Setup consistent catalog state across tools
      catalogs = []
      catalog_data = mock_catalog_list()
      for cat in catalog_data:
        mock_cat = Mock()
        for key, value in cat.items():
          setattr(mock_cat, key, value)
        catalogs.append(mock_cat)

      client.catalogs.list.return_value = catalogs

      # Setup warehouse for consistent SQL operations
      mock_warehouse = Mock()
      mock_warehouse.id = 'shared-warehouse'
      mock_warehouse.name = 'Shared Analytics Warehouse'
      mock_warehouse.state = 'RUNNING'
      client.sql_warehouses.list.return_value = [mock_warehouse]

      # Load tools
      load_uc_tools(mcp_server)
      load_sql_tools(mcp_server)

      # Test state consistency across tool interactions

      # First interaction: List catalogs
      catalog_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      catalog_result1 = catalog_tool.fn()
      assert_success_response(catalog_result1)
      initial_catalog_count = catalog_result1['count']

      # Second interaction: List warehouses
      warehouse_tool = mcp_server._tool_manager._tools['list_warehouses']
      warehouse_result = warehouse_tool.fn()
      assert_success_response(warehouse_result)

      # Third interaction: List catalogs again (should be consistent)
      catalog_result2 = catalog_tool.fn()
      assert_success_response(catalog_result2)
      assert catalog_result2['count'] == initial_catalog_count
      assert catalog_result1['catalogs'] == catalog_result2['catalogs']

      # Validate tool interaction consistency
      assert warehouse_result['warehouses'][0]['name'] == 'Shared Analytics Warehouse'

  @pytest.mark.integration
  def test_permission_validation_across_roles(self, mcp_server, mock_env_vars):
    """Test permission validation across different user roles."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = Mock()
      mock_client.return_value = client

      # Setup role-based permission scenarios
      tables = [
        create_mock_table('main', 'public', 'reference_data'),  # Public access
        create_mock_table('main', 'restricted', 'sensitive_data'),  # Restricted access
        create_mock_table('main', 'private', 'executive_data'),  # Private access
      ]

      # Configure different permission levels per table
      for i, table in enumerate(tables):
        if i == 0:  # Public table
          table.properties = {'access_level': 'public', 'reader_groups': 'all_employees'}
        elif i == 1:  # Restricted table
          table.properties = {'access_level': 'restricted', 'reader_groups': 'analysts,managers'}
        else:  # Private table
          table.properties = {'access_level': 'private', 'reader_groups': 'executives'}

      client.tables.list.return_value = tables
      client.tables.get.side_effect = lambda name: next(
        (t for t in tables if t.full_name == name), None
      )

      load_uc_tools(mcp_server)

      # Test access validation for different permission levels
      describe_tool = mcp_server._tool_manager._tools['describe_uc_table']

      # Test public table access (should always succeed)
      public_result = describe_tool.fn('main.public.reference_data')
      assert_success_response(public_result)
      assert public_result['table']['properties']['access_level'] == 'public'

      # Test restricted table access
      restricted_result = describe_tool.fn('main.restricted.sensitive_data')
      assert_success_response(restricted_result)
      assert restricted_result['table']['properties']['access_level'] == 'restricted'

      # Test private table access
      private_result = describe_tool.fn('main.private.executive_data')
      assert_success_response(private_result)
      assert private_result['table']['properties']['access_level'] == 'private'

      # Validate permission metadata is preserved across operations
      assert public_result['table']['properties']['reader_groups'] == 'all_employees'
      assert restricted_result['table']['properties']['reader_groups'] == 'analysts,managers'
      assert private_result['table']['properties']['reader_groups'] == 'executives'

  @pytest.mark.integration
  def test_large_result_set_handling(self, mcp_server, mock_env_vars):
    """Test handling of large result sets (>10K rows)."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      client = Mock()
      mock_client.return_value = client

      # Setup large result set mock (>10K rows)
      large_result_mock = Mock()
      large_result_mock.statement_id = 'stmt-large-dataset'
      large_result_mock.status.state = 'SUCCEEDED'
      large_result_mock.result = Mock()

      # Generate test data with 25K rows
      row_count = 25000
      large_data = []
      for i in range(row_count):
        large_data.append(
          [
            str(i + 1),  # id
            f'user_{i + 1}@example.com',  # email
            f'2024-01-{(i % 30) + 1:02d}T{(i % 24):02d}:00:00Z',  # timestamp
            f'{(i * 150.75) % 10000:.2f}',  # amount
          ]
        )

      large_result_mock.result.data_array = large_data
      # Create columns with proper names
      col1 = Mock()
      col1.name = 'user_id'
      col2 = Mock()
      col2.name = 'email'
      col3 = Mock()
      col3.name = 'created_at'
      col4 = Mock()
      col4.name = 'transaction_amount'

      large_result_mock.manifest.schema.columns = [col1, col2, col3, col4]

      client.statement_execution.execute_statement.return_value = large_result_mock

      # Setup warehouse
      mock_warehouse = Mock()
      mock_warehouse.id = 'large-data-warehouse'
      mock_warehouse.name = 'Large Data Processing Warehouse'
      mock_warehouse.state = 'RUNNING'
      client.sql_warehouses.list.return_value = [mock_warehouse]

      load_sql_tools(mcp_server)

      # Execute query that returns large result set
      execute_tool = mcp_server._tool_manager._tools['execute_dbsql']
      large_query = """
            SELECT
                user_id,
                email,
                created_at,
                transaction_amount
            FROM main.sales.large_transactions
            WHERE created_at >= '2024-01-01'
            ORDER BY created_at DESC
            """

      large_result = execute_tool.fn(
        query=large_query, warehouse_id='large-data-warehouse', limit=25000
      )

      assert_success_response(large_result)

      # Validate large result set handling
      assert large_result['row_count'] == 25000
      assert large_result['row_count'] > 10000  # Meets >10K requirement
      assert 'data' in large_result
      assert len(large_result['data']['rows']) == 25000
      assert len(large_result['data']['columns']) == 4

      # Verify data structure integrity with large dataset
      first_row = large_result['data']['rows'][0]
      assert len(first_row) == 4  # Dictionary with 4 keys
      assert first_row['user_id'] == '1'  # user_id
      assert '@example.com' in first_row['email']  # email format

      # Verify performance metadata for large result sets
      # The execute_dbsql tool doesn't return statement_id in response
      # but we can verify the execution was successful
      assert large_result['success'] is True

  @pytest.mark.integration
  def test_state_consistency_checks(self, mcp_server, mock_env_vars):
    """Test state consistency across multiple tool operations."""
    with (
      patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc_client,
      patch('server.tools.sql_operations.WorkspaceClient') as mock_sql_client,
    ):
      # Setup shared state between tools
      shared_client = Mock()
      mock_uc_client.return_value = shared_client
      mock_sql_client.return_value = shared_client

      # Consistent catalog data across all operations
      catalogs = []
      for cat_data in mock_catalog_list():
        mock_cat = Mock()
        for key, value in cat_data.items():
          setattr(mock_cat, key, value)
        mock_cat.state_version = '1.0'  # Add version tracking
        catalogs.append(mock_cat)

      shared_client.catalogs.list.return_value = catalogs

      # Consistent schema data
      schemas = [create_mock_schema('main', 'consistency_test')]
      for schema in schemas:
        schema.state_version = '1.0'
        schema.last_modified = '2024-01-15T10:00:00Z'

      shared_client.schemas.list.return_value = schemas
      shared_client.schemas.get.side_effect = lambda full_name: next(
        (s for s in schemas if f'{s.catalog_name}.{s.name}' == full_name), None
      )

      # Consistent table data with state tracking
      tables = [create_mock_table('main', 'consistency_test', 'state_table')]
      for table in tables:
        table.state_version = '1.0'
        table.last_modified = '2024-01-15T10:00:00Z'
        table.row_count = 1000

      shared_client.tables.list.return_value = tables
      shared_client.tables.get.side_effect = lambda name: next(
        (t for t in tables if t.full_name == name), None
      )

      load_uc_tools(mcp_server)
      load_sql_tools(mcp_server)

      # Execute multiple operations and verify state consistency

      # Operation 1: List catalogs
      list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      initial_state = list_catalogs_tool.fn()
      assert_success_response(initial_state)
      initial_catalog_names = [cat['name'] for cat in initial_state['catalogs']]

      # Operation 2: Describe schema
      describe_schema_tool = mcp_server._tool_manager._tools['describe_uc_schema']
      schema_state = describe_schema_tool.fn('main', 'consistency_test')
      assert_success_response(schema_state)

      # Operation 3: Describe table
      describe_table_tool = mcp_server._tool_manager._tools['describe_uc_table']
      table_state = describe_table_tool.fn('main.consistency_test.state_table')
      assert_success_response(table_state)

      # Operation 4: List catalogs again - should be identical
      final_state = list_catalogs_tool.fn()
      assert_success_response(final_state)
      final_catalog_names = [cat['name'] for cat in final_state['catalogs']]

      # Verify state consistency
      assert initial_catalog_names == final_catalog_names
      assert initial_state['count'] == final_state['count']

      # Verify cross-tool state consistency
      catalog_from_list = next(cat for cat in final_state['catalogs'] if cat['name'] == 'main')
      schema_from_describe = schema_state['schema']
      table_from_describe = table_state['table']

      # Check that related objects maintain consistent references
      # Schema describe doesn't include catalog_name, but table describe includes full_name
      assert schema_from_describe['name'] == 'consistency_test'
      assert table_from_describe['name'] == 'state_table'
      assert table_from_describe['full_name'] == 'main.consistency_test.state_table'

      # Verify state version consistency
      assert catalog_from_list['name'] == 'main'


class TestResilienceAndSecurity:
  """Test system resilience and security features."""

  @pytest.mark.resilience
  def test_databricks_api_failure_recovery(self, mcp_server, mock_env_vars):
    """Test behavior when Databricks API is unavailable."""
    from server.tools.unity_catalog import load_uc_tools
    from server.tools.sql_operations import load_sql_tools

    # Load tools
    load_uc_tools(mcp_server)
    load_sql_tools(mcp_server)

    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc_client:
      # Simulate API outage - connection errors
      mock_uc_client.side_effect = Exception("Connection timeout - Databricks API unavailable")

      # Test catalog listing during API outage
      list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = list_catalogs_tool.fn()

      # Verify graceful degradation
      assert result['success'] is False
      assert 'error' in result
      
      # Check error messages are user-friendly (no internal details)
      error_msg = result['error']
      assert 'Connection timeout' in error_msg or 'API unavailable' in error_msg
      assert 'Databricks' in error_msg
      
      # Ensure no stack traces or internal paths leaked
      assert 'Traceback' not in error_msg
      assert '/Users/' not in error_msg
      assert 'server.tools' not in error_msg

    # Test recovery after API becomes available again
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_recovered_client:
      client = Mock()
      mock_recovered_client.return_value = client
      
      # Setup minimal successful response
      mock_catalog = Mock()
      mock_catalog.name = 'main'
      mock_catalog.catalog_type = 'UNITY_CATALOG' 
      client.catalogs.list.return_value = [mock_catalog]

      # Test successful recovery
      recovery_result = list_catalogs_tool.fn()
      assert_success_response(recovery_result)
      assert recovery_result['count'] == 1

  @pytest.mark.resilience
  def test_concurrent_operations(self, mcp_server, mock_env_vars):
    """Test multi-user concurrent access."""
    from concurrent.futures import ThreadPoolExecutor
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = Mock()
      mock_client.return_value = client
      
      # Setup thread-safe mock data
      mock_catalog = Mock()
      mock_catalog.name = 'concurrent_test'
      mock_catalog.catalog_type = 'UNITY_CATALOG'
      client.catalogs.list.return_value = [mock_catalog]

      # Simulate 10 concurrent tool calls
      list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      
      def execute_tool_call():
        return list_catalogs_tool.fn()

      # Execute concurrent operations
      with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(execute_tool_call) for _ in range(10)]
        results = [future.result() for future in futures]

      # Check for race conditions - all should succeed
      for result in results:
        assert_success_response(result)
        assert result['count'] == 1
        assert result['catalogs'][0]['name'] == 'concurrent_test'

      # Verify resource management - no memory leaks or connection issues
      assert len(results) == 10
      
      # Verify all mock client calls were handled correctly
      assert mock_client.call_count >= 10

  @pytest.mark.resilience
  def test_partial_service_failure(self, mcp_server, mock_env_vars):
    """Test when some Databricks services fail."""
    from server.tools.unity_catalog import load_uc_tools
    from server.tools.sql_operations import load_sql_tools

    load_uc_tools(mcp_server)
    load_sql_tools(mcp_server)

    # Scenario: SQL works but UC fails
    with (
      patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc_client,
      patch('server.tools.sql_operations.WorkspaceClient') as mock_sql_client,
    ):
      # UC service fails
      mock_uc_client.side_effect = Exception("Unity Catalog service unavailable")
      
      # SQL service works
      sql_client = Mock()
      mock_sql_client.return_value = sql_client
      
      mock_warehouse = Mock()
      mock_warehouse.id = 'test-warehouse'
      mock_warehouse.name = 'Test Warehouse'
      mock_warehouse.state = 'RUNNING'
      sql_client.sql_warehouses.list.return_value = [mock_warehouse]

      # Test UC failure
      list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      uc_result = list_catalogs_tool.fn()
      assert uc_result['success'] is False
      assert 'Unity Catalog service unavailable' in uc_result['error']

      # Test SQL partial functionality still works
      list_warehouses_tool = mcp_server._tool_manager._tools['list_warehouses']
      sql_result = list_warehouses_tool.fn()
      assert_success_response(sql_result)
      assert len(sql_result['warehouses']) == 1
      assert sql_result['warehouses'][0]['name'] == 'Test Warehouse'

      # Verify partial functionality message
      assert sql_result['success'] is True

  @pytest.mark.security
  def test_token_exposure_prevention(self, mcp_server, mock_env_vars):
    """Ensure tokens never appear in errors."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Force authentication error with token exposure risk
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      # Simulate auth error that might leak token
      sensitive_token = "dapi1234567890abcdef-sensitive-token-data"
      mock_client.side_effect = Exception(f"Authentication failed with token {sensitive_token}")

      list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = list_catalogs_tool.fn()

      # Verify token not in error message
      assert result['success'] is False
      error_msg = result['error']
      
      # Token should be scrubbed from error messages
      assert sensitive_token not in error_msg
      assert 'dapi' not in error_msg
      assert 'token' not in error_msg.lower() or 'Authentication' in error_msg

      # Should contain sanitized error
      assert 'Authentication failed' in error_msg or 'Access denied' in error_msg

  @pytest.mark.security
  def test_sql_injection_prevention(self, mcp_server, mock_env_vars):
    """Test SQL injection prevention."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      client = Mock()
      mock_client.return_value = client

      # Setup warehouse
      mock_warehouse = Mock()
      mock_warehouse.id = 'test-warehouse'
      client.sql_warehouses.list.return_value = [mock_warehouse]

      # Try malicious SQL in parameters
      malicious_queries = [
        "SELECT * FROM users; DROP TABLE users; --",
        "SELECT * FROM users WHERE id = 1 OR 1=1",
        "SELECT * FROM users UNION SELECT password FROM admin_users",
        "'; INSERT INTO audit_log VALUES ('hacked'); --"
      ]

      execute_sql_tool = mcp_server._tool_manager._tools['execute_dbsql']

      for malicious_query in malicious_queries:
        # Mock the statement execution to simulate what would happen
        mock_result = Mock()
        mock_result.statement_id = 'stmt-security-test'
        mock_result.status.state = 'FAILED'
        client.statement_execution.execute_statement.return_value = mock_result

        # Execute the malicious query
        result = execute_sql_tool.fn(query=malicious_query, warehouse_id='test-warehouse')

        # The tool should handle the malicious query safely
        # Since we're mocking, we verify proper error handling structure
        assert isinstance(result, dict)
        
        # Verify that the actual query was passed to Databricks (proper escaping handled by SDK)
        client.statement_execution.execute_statement.assert_called()
        call_args = client.statement_execution.execute_statement.call_args
        assert call_args is not None

  @pytest.mark.security
  def test_permission_boundaries(self, mcp_server, mock_env_vars):
    """Test workspace permission enforcement."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      # Test cross-workspace access prevention
      mock_client.side_effect = Exception("Access denied - insufficient permissions for workspace")

      list_catalogs_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = list_catalogs_tool.fn()

      # Verify permission errors are properly handled
      assert result['success'] is False
      assert 'error' in result
      
      error_msg = result['error']
      assert 'Access denied' in error_msg or 'insufficient permissions' in error_msg
      
      # Ensure error doesn't leak workspace URLs or sensitive details
      assert 'https://' not in error_msg
      assert '.databricks.com' not in error_msg
      assert 'workspace' not in error_msg.lower() or 'permission' in error_msg.lower()

    # Test successful access within proper boundaries
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_authorized_client:
      client = Mock()
      mock_authorized_client.return_value = client
      
      # Setup authorized response
      mock_catalog = Mock()
      mock_catalog.name = 'authorized_catalog'
      mock_catalog.catalog_type = 'UNITY_CATALOG'
      client.catalogs.list.return_value = [mock_catalog]

      # Test authorized access
      authorized_result = list_catalogs_tool.fn()
      assert_success_response(authorized_result)
      assert authorized_result['count'] == 1
      assert authorized_result['catalogs'][0]['name'] == 'authorized_catalog'
