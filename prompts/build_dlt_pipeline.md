# Build DLT Medallion Architecture Pipeline

I can help you build a comprehensive Delta Live Tables (DLT) pipeline using the medallion architecture pattern. This tool will create a complete DLT pipeline with Bronze, Silver, and Gold layers, including:

## Features
- **Bronze Layer**: Raw data ingestion with audit columns and schema evolution
- **Silver Layer**: Cleaned, validated data with comprehensive data quality rules
- **Gold Layer**: Business-ready aggregated data optimized for analytics
- **Serverless Compute**: Configured for cost-effective, auto-scaling compute
- **Data Quality Rules**: Built-in expectations and monitoring
- **Multiple Source Types**: Supports Parquet, Delta, JSON, CSV, Kafka, and Auto Loader
- **Asset Bundle Deployment**: Complete Databricks Asset Bundle for CI/CD deployment

## How to Use

To build your DLT pipeline, I'll need information about your source tables. For each table, please provide:

### Required Information
- **name**: Table name (e.g., "customers", "orders")


### Optional Information
- **primary_key**: List of primary key columns (for data validation)
- **business_keys**: List of business key columns (for deduplication)
- **description**: Description of the table's purpose

### Pipeline Configuration
- **pipeline_name**: Name for your DLT pipeline
- **catalog**: Unity Catalog name
- **schema**: Schema for DLT tables 

## What You'll Get

The tool will generate:

1. **Complete DLT Python Code**: Ready-to-deploy pipeline code with all layers
2. **Pipeline Configuration**: JSON configuration for Databricks DLT
3. **Data Quality Rules**: Built-in expectations and validation logic
4. **Serverless Configuration**: Optimized for cost and performance
5. **Asset Bundle Structure**: Complete Databricks Asset Bundle with:
   - `databricks.yml` configuration file
   - `resources/` directory with pipeline definitions
   - `bundles/` directory for environment-specific configurations
   - Deployment scripts and CI/CD integration
6. **Implementation Guide**: Step-by-step deployment instructions
7. **Best Practice Recommendations**: Customization suggestions

## Data Quality Features

The generated pipeline includes:
- **Primary key validation**: Ensures key fields are not null
- **Data freshness checks**: Validates recent data ingestion
- **Deduplication logic**: Handles duplicate records based on business keys
- **Schema evolution**: Automatic handling of schema changes
- **Audit trails**: Tracking columns for lineage and debugging

## Architecture Layers

- **Bronze**: Raw data with minimal processing, audit columns, schema evolution
- **Silver**: Cleaned data with quality rules, deduplication, standardization
- **Gold**: Aggregated business metrics, dimensional models, analytics-ready data

## Deployment Options

The generated Asset Bundle supports:
- **Local Development**: Deploy to development workspace for testing
- **CI/CD Integration**: Automated deployment through GitHub Actions, GitLab CI, or Azure DevOps
- **Environment Management**: Separate configurations for dev, staging, and production
- **Version Control**: Track pipeline changes and rollback capabilities
- **Infrastructure as Code**: Reproducible deployments across environments

Just describe your source tables and requirements, and I'll build a complete DLT pipeline with Asset Bundle deployment for you!