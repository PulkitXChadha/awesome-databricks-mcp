# Build DLT Medallion Architecture Pipeline

I can help you build a Delta Live Tables (DLT) pipeline using the medallion architecture pattern. This tool will create a DLT pipeline with Bronze, Silver, and Gold layers, including:

## Features
- **Bronze Layer**: Raw data ingestion with audit columns and schema evolution
- **Silver Layer**: Cleaned, validated data with comprehensive data quality rules
- **Gold Layer**: Business-ready star schema with fact and dimension tables optimized for analytics and BI tools
- **Serverless Compute**: Configured for cost-effective, autoscaling compute.
- **Data Quality Rules**: Built-in expectations that handle real-world data issues gracefully
- **Multiple Source Types**: Supports Parquet, Delta, JSON, CSV, Kafka, and Auto Loader
- **Asset Bundle Deployment**: Complete Databricks Asset Bundle for CI/CD deployment
- **Star Schema Design**: Optimized dimensional model for analytics and reporting

## How to Use

To build your DLT pipeline, I'll need information about your source tables and configuration preferences:

### Required Information
- **name**: Table name (e.g., "customers", "orders")

### Pipeline Configuration
- **pipeline_name**: Name for your DLT pipeline
- **catalog**: Unity Catalog name (will create new catalog if specified)
- **schema**: Schema for DLT tables (will create new schema if specified)
- **databricks_cli_profile**: Databricks CLI profile to use (defaults to "DEFAULT" if not provided)
- **sql_warehouse**: SQL warehouse ID or name to run SQL queries.  The DLT pipeline will be serverless.


### Star Schema Design
The gold layer will be designed as a star schema with:
- **Fact Tables**: Central tables containing business metrics and measures
- **Dimension Tables**: Descriptive attributes and hierarchies for analysis
- **Optimized for Analytics**: Proper indexing, partitioning, and clustering for BI tools
- **Business Intelligence Ready**: Structured for easy querying and reporting

## What You'll Get

The tool will generate:

1. **Complete DLT Python Code**: Ready-to-deploy ELT pipeline code with appropriate Expectations that handle real-world data issues gracefully.
2. **Star Schema Design**: Optimized dimensional model in the gold layer
3. **Pipeline Configuration**: JSON configuration for Databricks DLT with serverless compute
6. **Asset Bundle Structure**: Complete Databricks Asset Bundle with:
   - `databricks.yml` configuration file
   - `resources/` directory with pipeline definitions
7. **Implementation Guide**: Step-by-step deployment instructions


## Configuration Details

- **New Catalog/Schema**: Will create specified catalog and schema if they don't exist
- **Single Schema**: All medallion tables will be created in one schema.
- **Serverless Compute**: All layers configured to use serverless compute for cost optimization
- **CLI Profile**: Uses specified Databricks CLI profile for deployment
- **SQL Warehouse**: Configured to use the specified warehouse for SQL queries only. The DLT pipeline will be serverless.

## Critical Code Generation Rules

### Data Type Safety (MANDATORY)
- **ALWAYS** use `float()` for numeric values in schemas with `DoubleType()`
- **ALWAYS** use `datetime.now()` instead of `F.current_timestamp()` for data values
- **ALWAYS** use `.0` suffix for numeric literals (e.g., `0.0` not `0`)
- **NEVER** pass PySpark Column objects as data values

### Unity Catalog Configuration (MANDATORY)
- **ALWAYS** use `target: {schema_name}` (schema name only)
- **ALWAYS** specify `catalog: {catalog_name}` as separate field
- **ALWAYS** include comprehensive permission grants

### Error Prevention Patterns
- Handle division by zero: `value if total > 0 else 0.0`
- Null-safe counting: `df.count() or 0`
- Type conversion: `float(count)` for all numeric metrics

## Required Permission Setup

### Pre-deployment Permissions Script
```sql
-- Create catalog and schema
CREATE CATALOG IF NOT EXISTS {catalog_name} 
COMMENT 'Retail analytics catalog for medallion architecture';

CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name} 
COMMENT 'Medallion architecture schema for bronze, silver, and gold tables';

-- Grant comprehensive permissions
GRANT USE CATALOG ON CATALOG {catalog_name} TO `{user_email}`;
GRANT CREATE SCHEMA ON CATALOG {catalog_name} TO `{user_email}`;
GRANT USE SCHEMA ON SCHEMA {catalog_name}.{schema_name} TO `{user_email}`;
GRANT CREATE TABLE ON SCHEMA {catalog_name}.{schema_name} TO `{user_email}`;
GRANT CREATE MATERIALIZED VIEW ON SCHEMA {catalog_name}.{schema_name} TO `{user_email}`;
GRANT CREATE FUNCTION ON SCHEMA {catalog_name}.{schema_name} TO `{user_email}`;
GRANT ALL PRIVILEGES ON SCHEMA {catalog_name}.{schema_name} TO `{user_email}`;

-- Grant source data access
GRANT SELECT ON SCHEMA {source_catalog}.{source_schema} TO `{user_email}`;
```


Just describe your source tables and requirements, and I'll build a complete DLT pipeline with star schema design and Asset Bundle deployment for you!