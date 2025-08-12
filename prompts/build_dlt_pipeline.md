# Build DLT Medallion Architecture Pipeline

I can help you build a Delta Live Tables (DLT) pipeline using the medallion architecture pattern. This tool will guide you through the complete deployment lifecycle, from initial deployment to resolving all failures and ensuring successful pipeline execution. This tool will create a DLT pipeline with Bronze, Silver, and Gold layers, including:

## Features
- **Bronze Layer**: Raw data ingestion with audit columns and schema evolution
- **Silver Layer**: Cleaned, validated data with comprehensive data quality rules
- **Gold Layer**: Business-ready star schema with fact and dimension tables optimized for analytics and BI tools
- **Serverless Compute**: Configured for cost-effective, autoscaling compute.
- **Data Quality Rules**: Built-in expectations that handle real-world data issues gracefully
- **Multiple Source Types**: Supports Parquet, Delta, CSV, JSON, Kafka, and Auto Loader
- **Asset Bundle Deployment**: Complete Databricks Asset Bundle for CI/CD deployment
- **Star Schema Design**: Optimized dimensional model for analytics and reporting

## Databricks Documentation

### Core Concepts
- **[Delta Live Tables Overview](https://docs.databricks.com/en/delta-live-tables/index.html)**: Complete guide to DLT concepts and architecture
- **[Medallion Architecture](https://docs.databricks.com/en/lakehouse/medallion.html)**: Best practices for data lakehouse design patterns
- **[Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)**: Data governance and catalog management
- **[Delta Lake](https://docs.databricks.com/en/delta/index.html)**: ACID transactions and schema evolution

### DLT Development
- **[DLT Python API](https://docs.databricks.com/en/delta-live-tables/python-ref.html)**: Python functions and decorators reference
- **[DLT Expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html)**: Data quality rules and validation
- **[DLT Pipeline Configuration](https://docs.databricks.com/en/delta-live-tables/configuration.html)**: Pipeline settings and compute configuration
- **[DLT Best Practices](https://docs.databricks.com/en/delta-live-tables/best-practices.html)**: Performance and reliability guidelines

### Deployment & Operations
- **[Databricks Asset Bundles](https://docs.databricks.com/en/dev-tools/bundles/index.html)**: Infrastructure as code for Databricks
- **[Asset Bundle CLI](https://docs.databricks.com/en/dev-tools/bundles/cli.html)**: Command-line interface for deployment
- **[DLT Pipeline Management](https://docs.databricks.com/en/delta-live-tables/manage.html)**: Monitoring, troubleshooting, and maintenance
- **[Serverless Compute](https://docs.databricks.com/en/compute/serverless.html)**: On-demand compute for cost optimization

### Data Engineering
- **[Auto Loader](https://docs.databricks.com/en/ingestion/auto-loader/index.html)**: Incremental data ingestion
- **[Streaming with DLT](https://docs.databricks.com/en/delta-live-tables/streaming.html)**: Real-time data processing
- **[Schema Evolution](https://docs.databricks.com/en/delta-live-tables/schema-evolution.html)**: Handling changing data structures
- **[Data Quality Monitoring](https://docs.databricks.com/en/delta-live-tables/quality-monitoring.html)**: Tracking data quality metrics

## How to Use

To build your DLT pipeline, I'll need information about your source tables and configuration preferences:

### Required Information
- **name**: Table name (e.g., "customers", "orders")

### Pipeline Configuration
- **pipeline_name**: Name for your DLT pipeline
- **catalog**: Unity Catalog name (will create new catalog if specified)
- **schema**: Schema for DLT tables (will create new schema if specified)
- **databricks_cli_profile**: Databricks CLI profile to use (defaults to "DEFAULT" if not provided)
- **sql_warehouse**: SQL warehouse ID or name to run SQL queries. The DLT pipeline will be serverless.

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
4. **Asset Bundle Structure**: Complete Databricks Asset Bundle with:
   - `databricks.yml` configuration file
   - `resources/` directory with pipeline definitions
5. **Implementation Guide**: Step-by-step deployment instructions

## Deployment Process

### Phase 1: Asset Bundle Deployment
- Deploy pipeline using `databricks bundle deploy`
- Verify pipeline creation in Databricks workspace
- Validate compute configuration and permissions

### Phase 2: Pipeline Execution
- Start pipeline with `databricks pipeline start`
- Monitor initial execution for any configuration issues
- Verify all three layers (Bronze, Silver, Gold) process successfully

### Phase 3: Validation & Monitoring
- Confirm data quality expectations are met
- Verify star schema structure in Gold layer
- Set up monitoring and alerting for production use

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

## Additional Resources

### Learning Paths
- **[Data Engineering Learning Path](https://docs.databricks.com/en/learn/data-engineering.html)**: Comprehensive data engineering tutorials
- **[DLT Tutorials](https://docs.databricks.com/en/delta-live-tables/tutorial.html)**: Step-by-step DLT examples
- **[Unity Catalog Tutorials](https://docs.databricks.com/en/data-governance/unity-catalog/workspace-setup.html)**: Setting up data governance

### Community & Support
- **[Databricks Community](https://community.databricks.com/)**: Ask questions and share solutions
- **[Databricks Academy](https://academy.databricks.com/)**: Free online courses and certifications
- **[GitHub Examples](https://github.com/databricks/tech-talks)**: Code samples and best practices

Just describe your source tables and requirements, and I'll build a complete DLT pipeline with star schema design and Asset Bundle deployment for you!