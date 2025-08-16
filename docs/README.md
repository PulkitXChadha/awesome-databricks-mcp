# Databricks MCP Server Documentation

Welcome to the comprehensive documentation for the Databricks MCP (Model Context Protocol) Server. This server provides AI assistants with programmatic access to Databricks services through a unified interface.

## 📚 Documentation Overview

This documentation is organized into logical sections that cover all aspects of the Databricks MCP server:

### 🚀 [Getting Started](getting-started.md)
- Quick start guide
- Installation and setup
- Authentication configuration
- Basic usage examples

### 🔧 [Core Tools & APIs](core-tools.md)
- **Databricks SDK Integration**: Direct SDK usage patterns and examples
- **Unity Catalog Tools**: Complete data catalog management capabilities
- **SQL Operations**: Warehouse management and query execution
- **Compute Management**: Clusters, jobs, and workflows
- **File Management**: DBFS and workspace file operations

### 🏗️ [Architecture & Design](architecture.md)
- System architecture overview
- Tool implementation patterns
- Error handling and validation
- Performance considerations

### 📖 [API Reference](api-reference.md)
- Complete tool reference
- Parameter specifications
- Return value documentation
- Usage examples for each tool

### 🧪 [Testing & Development](testing.md)
- Testing strategies and tools
- Development setup
- Debugging and troubleshooting
- Contributing guidelines

## 🎯 What This Server Provides

The Databricks MCP Server exposes over **100+ tools** covering:

- **Data Management**: Unity Catalog, tables, schemas, volumes
- **Compute Resources**: Clusters, SQL warehouses, instance pools
- **Workflows**: Jobs, pipelines, Delta Live Tables
- **Machine Learning**: Model serving, experiments, feature store
- **File Operations**: DBFS, workspace files, external storage
- **Governance**: Permissions, audit logs, data quality monitoring
- **Development**: Git integration, notebooks, repositories

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/awesome-databricks-mcp.git
cd awesome-databricks-mcp

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Set environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-personal-access-token"
```

### 3. Start the Server
```bash
# Run locally
./run_app_local.sh

# Or deploy to production
./deploy.sh
```

## 🔑 Key Features

- **Comprehensive Coverage**: Access to all major Databricks services
- **Unified Interface**: Consistent tool patterns across all services
- **Error Handling**: Robust error handling with detailed feedback
- **Performance Optimized**: Pagination, caching, and async operations
- **Security Focused**: Proper authentication and permission handling
- **Developer Friendly**: Clear documentation and examples

## 📊 Tool Categories

| Category | Tools | Status |
|----------|-------|---------|
| **Unity Catalog** | 15+ tools | ✅ Complete |
| **SQL Operations** | 10+ tools | ✅ Complete |
| **Compute Management** | 20+ tools | 🔄 In Progress |
| **Jobs & Workflows** | 15+ tools | ✅ Complete |
| **File Management** | 12+ tools | ✅ Complete |
| **ML & AI** | 25+ tools | 🔄 In Progress |
| **Governance** | 10+ tools | ✅ Complete |

## 🛠️ Technology Stack

- **Backend**: FastAPI + Python
- **Databricks Integration**: Official Python SDK
- **Authentication**: Personal Access Tokens, Service Principals
- **Documentation**: Markdown + Auto-generated API docs
- **Testing**: pytest + Integration tests

## 📖 Detailed Documentation

### [Databricks SDK Guide](databricks_apis/databricks_sdk.md)
Comprehensive guide to using the Databricks SDK directly, including:
- Authentication and setup
- Core API patterns
- FastAPI integration examples
- Error handling best practices

### [Unity Catalog Tools](unity_catalog_tools.md)
Complete reference for Unity Catalog operations:
- Catalog, schema, and table management
- Volume and function operations
- Data discovery and search
- Governance and permissions

### [Model Serving APIs](databricks_apis/model_serving.md)
Detailed guide to ML model serving:
- Endpoint management
- Real-time and batch inference
- Chat model integration
- Error handling and monitoring

### [SDK Tools Implementation](databricks_sdk_tools.md)
Implementation plan and reference for all SDK tools:
- Tool categorization and priorities
- Implementation status tracking
- Testing strategies
- Future enhancements

## 🔍 Search & Navigation

Use the table of contents above to navigate to specific sections, or search for specific topics:

- **For SDK usage**: See [Databricks SDK Guide](databricks_apis/databricks_sdk.md)
- **For Unity Catalog**: See [Unity Catalog Tools](unity_catalog_tools.md)
- **For ML models**: See [Model Serving APIs](databricks_apis/model_serving.md)
- **For tool development**: See [SDK Tools Implementation](databricks_sdk_tools.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Development setup

## 📞 Support

- **Documentation Issues**: Open an issue in this repository
- **Code Problems**: Check the [Troubleshooting Guide](troubleshooting.md)
- **Feature Requests**: Use the issue tracker with the "enhancement" label

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Databricks SDK Version**: 0.59.0
