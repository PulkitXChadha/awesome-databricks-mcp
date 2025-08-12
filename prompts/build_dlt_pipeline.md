# Build DLT Medallion Architecture Pipeline

I can help you build a comprehensive Delta Live Tables (DLT) pipeline using the medallion architecture pattern. This tool will create a complete DLT pipeline with Bronze, Silver, and Gold layers, including:

## Features
- **Bronze Layer**: Raw data ingestion with audit columns and schema evolution
- **Silver Layer**: Cleaned, validated data with comprehensive data quality rules
- **Gold Layer**: Business-ready star schema with fact and dimension tables optimized for analytics and BI tools
- **ELT Pipeline**: Extract, Load, Transform approach using Databricks DLT
- **Serverless Compute**: Configured for cost-effective, auto-scaling compute throughout all layers
- **Flexible Data Quality Rules**: Built-in expectations that handle real-world data issues gracefully
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
- **sql_warehouse**: SQL warehouse ID or name to run SQL queries. 


### Star Schema Design
The gold layer will be designed as a star schema with:
- **Fact Tables**: Central tables containing business metrics and measures
- **Dimension Tables**: Descriptive attributes and hierarchies for analysis
- **Optimized for Analytics**: Proper indexing, partitioning, and clustering for BI tools
- **Business Intelligence Ready**: Structured for easy querying and reporting

## What You'll Get

The tool will generate:

1. **Complete DLT Python Code**: Ready-to-deploy ELT pipeline code with all layers
2. **Star Schema Design**: Optimized dimensional model in the gold layer
3. **Pipeline Configuration**: JSON configuration for Databricks DLT with serverless compute
4. **Flexible Data Quality Rules**: Expectations that handle real-world data issues gracefully
5. **Serverless Configuration**: Optimized for cost and performance across all layers
6. **Asset Bundle Structure**: Complete Databricks Asset Bundle with:
   - `databricks.yml` configuration file
   - `resources/` directory with pipeline definitions
   - `bundles/` directory for environment-specific configurations
   - Deployment scripts and CI/CD integration
7. **Implementation Guide**: Step-by-step deployment instructions
8. **Best Practice Recommendations**: Customization suggestions for your specific use case

## Data Quality Features

The generated pipeline includes flexible expectations that handle real-world scenarios:
- **Primary key validation**: Ensures key fields are not null
- **Data freshness checks**: Validates recent data ingestion with configurable thresholds
- **Deduplication logic**: Handles duplicate records based on business keys
- **Schema evolution**: Automatic handling of schema changes and new columns
- **Audit trails**: Comprehensive tracking columns for lineage and debugging
- **Graceful failure handling**: Pipeline continues processing even when some expectations fail
- **Configurable thresholds**: Adjustable data quality rules based on business requirements

## Architecture Layers

- **Bronze**: Raw data with minimal processing, audit columns, schema evolution
- **Silver**: Cleaned data with quality rules, deduplication, standardization
- **Gold**: Star schema with fact and dimension tables, business metrics, analytics-ready data

## Star Schema Benefits

The gold layer star schema provides:
- **Fast Query Performance**: Optimized for analytical queries and aggregations
- **Easy Business Understanding**: Intuitive structure for business users
- **BI Tool Compatibility**: Works seamlessly with Tableau, Power BI, and other tools
- **Scalable Design**: Handles growing data volumes efficiently
- **Flexible Analysis**: Supports ad-hoc queries and complex business questions

## Deployment Options

The generated Asset Bundle supports:
- **Local Development**: Deploy to development workspace for testing
- **CI/CD Integration**: Automated deployment through GitHub Actions, GitLab CI, or Azure DevOps
- **Environment Management**: Separate configurations for dev, staging, and production
- **Version Control**: Track pipeline changes and rollback capabilities
- **Infrastructure as Code**: Reproducible deployments across environments

## Configuration Details

- **New Catalog/Schema**: Will create specified catalog and schema if they don't exist
- **Single Schema**: All medallion tables will be created in one schema for simplicity
- **Serverless Compute**: All layers configured to use serverless compute for cost optimization
- **CLI Profile**: Uses specified Databricks CLI profile for deployment
- **SQL Warehouse**: Configured to use the specified warehouse for SQL queries


Just describe your source tables and requirements, and I'll build a complete DLT pipeline with star schema design and Asset Bundle deployment for you!