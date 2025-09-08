---
name: build_ldp_pipeline
description: Build Lakeflow Declarative Pipeline with medallion architecture
arguments:
  - name: pipeline_name
    description: Name for your pipeline
    required: true
    schema:
      type: string
      pattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
  
  - name: catalog
    description: Unity Catalog name (will create if specified)
    required: true
    schema:
      type: string
      pattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
  
  - name: schema
    description: Schema for Lakeflow tables (will create if specified)  
    required: true
    schema:
      type: string
      pattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
  
  - name: source_tables
    description: List of source tables to process
    required: true
    schema:
      type: array
      items:
        type: string
      minItems: 1
  
  - name: databricks_cli_profile
    description: Databricks CLI profile to use
    required: false
    schema:
      type: string
      default: "DEFAULT"
  
  - name: sql_warehouse
    description: SQL warehouse ID or name for queries
    required: true
    schema:
      type: string
---

Build a Lakeflow Declarative Pipeline (LDP) using medallion architecture for scalable data processing with built-in quality controls.

## Context

**Configuration Provided:**
- Pipeline Name: ${pipeline_name}
- Catalog: ${catalog}
- Schema: ${schema}
- Source Tables: ${source_tables}
- CLI Profile: ${databricks_cli_profile}
- SQL Warehouse: ${sql_warehouse}

## Objective

Create a production-ready Lakeflow Declarative Pipeline (formerly Delta Live Tables) that:
1. Implements medallion architecture (Bronze → Silver → Gold)
2. Enforces data quality through expectations
3. Optimizes for analytics with star schema design
4. Deploys via Databricks Asset Bundles with serverless compute

## Workflow

### 1. Requirements Analysis
- Analyze source table structures and relationships
- Identify primary keys and business entities
- Define data quality requirements
- Plan star schema design for gold layer

### 2. Pipeline Architecture

**Bronze Layer (Raw Ingestion):**
- Ingest data with minimal transformation
- Add audit columns (ingestion_time, source_file)
- Enable schema evolution for flexibility
- Support multiple formats (Delta, Parquet, CSV, JSON)

**Silver Layer (Cleansed & Validated):**
- Apply data quality expectations
- Standardize data types and formats
- Handle nulls and duplicates
- Create conformed dimensions

**Gold Layer (Business-Ready):**
- Implement star schema design
- Create fact and dimension tables
- Optimize for query performance
- Add business calculations

### 3. Implementation

**Pipeline Structure:**
```python
# Bronze Layer
@dlt.table(
    name="bronze_table",
    comment="Raw data ingestion"
)
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")
def bronze_table():
    return spark.readStream.table("source_table")

# Silver Layer
@dlt.table(
    name="silver_table",
    comment="Cleansed and validated data"
)
def silver_table():
    return dlt.read("bronze_table").select(...)

# Gold Layer
@dlt.table(
    name="gold_fact_table",
    comment="Business metrics fact table"
)
def gold_fact_table():
    return dlt.read("silver_table").join(...)
```

### 4. Data Quality Expectations

**Common Patterns:**
```python
# Required fields
@dlt.expect_or_drop("not_null", "column IS NOT NULL")

# Data validation
@dlt.expect_or_fail("valid_range", "value BETWEEN 0 AND 100")

# Referential integrity
@dlt.expect("foreign_key", "id IN (SELECT id FROM dimension)")

# Data freshness
@dlt.expect("recent_data", "date >= current_date() - 7")
```

### 5. Asset Bundle Configuration

**Directory Structure:**
```
project/
├── databricks.yml
├── resources/
│   └── pipeline.yml
└── src/
    └── pipeline.py
```

**databricks.yml:**
```yaml
bundle:
  name: ${pipeline_name}_bundle

resources:
  pipelines:
    ${pipeline_name}:
      name: ${pipeline_name}
      target: ${schema}
      catalog: ${catalog}
      libraries:
        - file:
            path: ./src/pipeline.py
      configuration:
        pipelines.autoOptimize.managed: true
      serverless: true
```

### 6. Deployment & Monitoring

**Deployment Steps:**
```bash
# Validate bundle
databricks bundle validate --target dev

# Deploy to workspace
databricks bundle deploy --target dev

# Start pipeline
databricks bundle run --target dev ${pipeline_name}
```

**Monitoring Checklist:**
- Pipeline state reaches "IDLE"
- Latest update shows "COMPLETED"
- No ERROR events in history
- All tables created and queryable
- Data quality metrics pass thresholds

## Best Practices

### Performance Optimization
- Use serverless compute for auto-scaling
- Implement incremental processing with Auto Loader
- Partition large tables by date or category
- Z-order clustering for query optimization

### Error Handling
```python
# Safe division
value / total if total > 0 else 0.0

# Null handling
COALESCE(field, default_value)

# Type conversion
CAST(string_col AS DOUBLE)
```

### Star Schema Design
- **Fact Tables**: Transactions, events, measurements
- **Dimension Tables**: Customers, products, time, geography
- **Slowly Changing Dimensions**: Type 2 with effective dates
- **Conformed Dimensions**: Shared across fact tables

## Available Tools

**Pipeline Management:**
- `list_pipelines`, `get_pipeline`, `create_pipeline`
- `start_pipeline_update`, `stop_pipeline_update`
- `get_pipeline_run`, `list_pipeline_runs`

**Unity Catalog:**
- `create_catalog`, `create_schema`
- `describe_uc_table`, `list_uc_tables`

**Monitoring:**
- `execute_dbsql` - Query validation
- `get_job_run_logs` - Pipeline execution logs

## Success Criteria

✓ Pipeline deploys without errors
✓ All medallion layers created successfully
✓ Data quality expectations pass
✓ Star schema tables queryable
✓ Performance meets SLA (<5 min for daily refresh)
✓ Asset Bundle version controlled

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Permission denied | Grant schema privileges before deployment |
| Schema evolution conflicts | Enable `mergeSchema` option |
| Memory errors | Use serverless or increase cluster size |
| Slow queries | Add Z-ordering on filter columns |
| Failed expectations | Review data quality rules, use `expect` instead of `expect_or_fail` |

## Example Star Schema

```yaml
Gold Layer:
  Fact Tables:
    - fact_sales (date_key, product_key, customer_key, amount, quantity)
    - fact_inventory (date_key, product_key, warehouse_key, quantity)
  
  Dimensions:
    - dim_date (date_key, date, year, quarter, month, day_of_week)
    - dim_product (product_key, name, category, price)
    - dim_customer (customer_key, name, segment, geography)
```

## Documentation References

- [Lakeflow/DLT Overview](https://docs.databricks.com/delta-live-tables/)
- [Medallion Architecture](https://docs.databricks.com/lakehouse/medallion)
- [Asset Bundles Guide](https://docs.databricks.com/dev-tools/bundles/)
- [Data Quality Expectations](https://docs.databricks.com/delta-live-tables/expectations)

Ready to build your Lakeflow Declarative Pipeline! Provide any additional requirements or constraints to customize the implementation.