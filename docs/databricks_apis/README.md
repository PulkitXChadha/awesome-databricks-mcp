# Databricks APIs Documentation

> **Note**: This documentation has been consolidated into the main documentation structure. For the most up-to-date information, see the [main documentation](../README.md).

## Overview

The Databricks SDK provides direct access to all Databricks APIs. This documentation shows you how to call these APIs directly in your FastAPI application.

## 🔗 Quick Navigation

- **[Main Documentation](../README.md)** - Complete overview and navigation
- **[Getting Started](../getting-started.md)** - Setup and quick start guide
- **[Core Tools](../core-tools.md)** - All available tools and APIs
- **[API Reference](../api-reference.md)** - Complete tool reference

## 📚 Available Documentation

### [Databricks SDK](databricks_sdk.md)
- Comprehensive SDK usage patterns
- Authentication and configuration
- Core APIs overview
- FastAPI integration examples

### [Model Serving](model_serving.md)
- AI agent tracing and observability
- Automated quality evaluation
- Feedback and continuous improvement
- Application lifecycle management

## 🔐 Authentication

All APIs use the same authentication configured in your app:

```python
from databricks.sdk import WorkspaceClient

# Automatically uses your configured authentication
client = WorkspaceClient()
```

## 🚀 Quick Start

For complete setup instructions, see [Getting Started](../getting-started.md).

```bash
# Set environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-personal-access-token"

# Start the server
./run_app_local.sh
```

## 📖 Next Steps

1. **Start with [Getting Started](../getting-started.md)** for setup instructions
2. **Explore [Core Tools](../core-tools.md)** for available functionality
3. **Check [API Reference](../api-reference.md)** for detailed documentation
4. **Review [Architecture](../architecture.md)** for implementation details

## 🔍 Search & Navigation

Use the main documentation for comprehensive coverage:
- **For SDK usage**: See [Core Tools](../core-tools.md) → Databricks SDK Integration
- **For ML models**: See [Core Tools](../core-tools.md) → Machine Learning & AI
- **For tool development**: See [API Reference](../api-reference.md)

---

**This documentation is maintained for reference. For the most current information, please use the [main documentation](../README.md).**