# Build DLT Medallion Architecture Pipeline

I can help you build a comprehensive Delta Live Tables (DLT) pipeline using the medallion architecture pattern. This tool will create a complete DLT pipeline with Bronze, Silver, and Gold layers, including:

## Features
- **Bronze Layer**: Raw data ingestion with audit columns and schema evolution
- **Silver Layer**: Cleaned, validated data with comprehensive data quality rules
- **Gold Layer**: Business-ready aggregated data optimized for analytics
- **Serverless Compute**: Configured for cost-effective, auto-scaling compute
- **Data Quality Rules**: Built-in expectations and monitoring
- **Multiple Source Types**: Supports Parquet, Delta, JSON, CSV, Kafka, and Auto Loader

## How to Use

To build your DLT pipeline, I'll need information about your source tables. For each table, please provide:

### Required Information
- **name**: Table name (e.g., "customers", "orders")
- **source_path**: Data source location (e.g., "s3://bucket/path/", "dbfs:/data/")
- **source_type**: Data format ("parquet", "delta", "json", "csv", "kafka", "autoloader")

### Optional Information
- **primary_key**: List of primary key columns (for data validation)
- **business_keys**: List of business key columns (for deduplication)
- **description**: Description of the table's purpose

### Pipeline Configuration
- **pipeline_name**: Name for your DLT pipeline
- **catalog**: Unity Catalog name
- **bronze_schema**: Schema for bronze tables (default: "bronze")
- **silver_schema**: Schema for silver tables (default: "silver")  
- **gold_schema**: Schema for gold tables (default: "gold")
- **storage_location**: Storage path for pipeline artifacts (optional)

## Example Usage

Here's an example of how to describe your tables:

```
I want to build a DLT pipeline called "retail_analytics" in the "main" catalog with these tables:

1. customers table:
   - Source: s3://data-lake/customers/
   - Format: parquet
   - Primary key: customer_id
   - Description: Customer master data

2. orders table:
   - Source: s3://streaming-data/orders/
   - Format: autoloader
   - Primary keys: order_id
   - Business keys: order_id, customer_id
   - Description: Order transactions

3. product_events table:
   - Source: kafka-cluster:9092
   - Format: kafka
   - Business keys: event_id
   - Description: Real-time product events
```

## What You'll Get

The tool will generate:

1. **Complete DLT Python Code**: Ready-to-deploy pipeline code with all layers
2. **Pipeline Configuration**: JSON configuration for Databricks DLT
3. **Data Quality Rules**: Built-in expectations and validation logic
4. **Serverless Configuration**: Optimized for cost and performance
5. **Implementation Guide**: Step-by-step deployment instructions
6. **Best Practice Recommendations**: Customization suggestions

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

Just describe your source tables and requirements, and I'll build a complete DLT pipeline for you!