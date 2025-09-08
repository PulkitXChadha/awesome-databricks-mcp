# Architecture & Design

This document provides an overview of the Databricks MCP Server architecture and design principles.

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client   │    │   FastAPI App    │    │  Databricks    │
│   (Claude,     │◄──►│   (MCP Server)   │◄──►│     SDK        │
│    etc.)       │    │                  │    │                │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   MCP Tools     │
                       │   (100+ tools)  │
                       └──────────────────┘
```

### Core Components

1. **FastAPI Application**: Main server that handles HTTP requests and MCP protocol
2. **MCP Tools**: Tool implementations that wrap Databricks SDK functionality
3. **Databricks SDK**: Official Python SDK for Databricks services
4. **Authentication Layer**: Handles Databricks authentication and token management

## 🔧 Tool Implementation Pattern

### Standard Tool Structure

```python
def tool_name(param1: str, param2: int = None) -> dict:
    """
    Tool description.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (optional)
    
    Returns:
        Standard response format with success/error indicators
    """
    try:
        # Initialize Databricks client
        client = WorkspaceClient()
        
        # Perform operation using SDK
        result = client.service.operation(param1, param2)
        
        # Return standardized response
        return {
            "success": True,
            "data": result,
            "count": len(result) if hasattr(result, '__len__') else 1
        }
        
    except Exception as e:
        # Handle errors consistently
        return {
            "success": False,
            "error": str(e),
            "error_code": get_error_code(e)
        }
```

### Response Format Standardization

All tools return responses in a consistent format:

```python
# Success Response
{
    "success": True,
    "data": {...},           # Actual result data
    "count": 5,              # Number of items (if applicable)
    "message": "Success"     # Optional success message
}

# Error Response
{
    "success": False,
    "error": "Error message",    # Human-readable error
    "error_code": "ERROR_CODE",  # Machine-readable error code
    "details": {...}             # Additional error details
}
```

## 🔐 Authentication Architecture

### Authentication Flow

1. **Environment Variables**: Server reads `DATABRICKS_HOST` and `DATABRICKS_TOKEN`
2. **Client Initialization**: `WorkspaceClient()` automatically uses configured credentials
3. **Token Validation**: SDK validates token with Databricks workspace
4. **Permission Checking**: Each tool respects Unity Catalog and workspace permissions

### Supported Authentication Methods

- **Personal Access Token**: `DATABRICKS_HOST` + `DATABRICKS_TOKEN`
- **CLI Profile**: `DATABRICKS_CONFIG_PROFILE`
- **Service Principal**: When deployed to Databricks Apps

## 📊 Tool Categories

### 1. Unity Catalog Tools
- **Purpose**: Data catalog management and discovery
- **Implementation**: Direct SDK calls to Unity Catalog APIs
- **Status**: ✅ Complete (15+ tools)

### 2. SQL Operations
- **Purpose**: Warehouse management and query execution
- **Implementation**: SDK statement execution and warehouse APIs
- **Status**: ✅ Complete (10+ tools)

### 3. Compute Management
- **Purpose**: Cluster and instance pool management
- **Implementation**: SDK cluster and compute APIs
- **Status**: 🔄 In Progress (20+ tools)

### 4. Jobs & Workflows
- **Purpose**: Job management and execution
- **Implementation**: SDK jobs and pipelines APIs
- **Status**: ✅ Complete (15+ tools)

### 5. File Management
- **Purpose**: DBFS and workspace file operations
- **Implementation**: SDK workspace and DBFS APIs
- **Status**: ✅ Complete (12+ tools)

### 6. Machine Learning
- **Purpose**: Model serving and ML operations
- **Implementation**: SDK ML and serving APIs
- **Status**: 🔄 In Progress (25+ tools)

## 🚀 Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Detailed information only fetched when requested
2. **Pagination**: Large result sets handled with pagination
3. **Caching**: Frequently accessed metadata cached when possible
4. **Async Operations**: Long-running operations support async patterns
5. **Batch Operations**: Multiple operations batched where possible

### Rate Limiting

- **API Limits**: Respect Databricks API rate limits
- **Backoff Strategy**: Exponential backoff for retries
- **Request Batching**: Group related API calls when possible

## 🛡️ Security & Permissions

### Security Model

1. **Authentication**: All requests authenticated via Databricks
2. **Authorization**: Tools respect Unity Catalog access controls
3. **Audit Logging**: All operations logged for compliance
4. **Error Masking**: Sensitive information not exposed in errors

### Permission Handling

```python
def secure_tool_operation(resource_id: str):
    try:
        client = WorkspaceClient()
        
        # Check if user has access to resource
        if not has_permission(client, resource_id):
            return {
                "success": False,
                "error": "Permission denied",
                "error_code": "PERMISSION_DENIED"
            }
        
        # Perform operation
        result = perform_operation(client, resource_id)
        return {"success": True, "data": result}
        
    except PermissionDenied:
        return {
            "success": False,
            "error": "Insufficient permissions",
            "error_code": "PERMISSION_DENIED"
        }
```

## 🔍 Error Handling Strategy

### Error Categories

1. **Authentication Errors**: Invalid or expired credentials
2. **Permission Errors**: Insufficient access rights
3. **Validation Errors**: Invalid input parameters
4. **Resource Errors**: Resources not found or unavailable
5. **System Errors**: Internal server or Databricks errors

### Error Handling Pattern

```python
def robust_tool_operation(params):
    try:
        # Validate parameters
        validate_params(params)
        
        # Perform operation
        result = perform_operation(params)
        
        return {"success": True, "data": result}
        
    except ValidationError as e:
        return {
            "success": False,
            "error": f"Invalid parameters: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except NotFound as e:
        return {
            "success": False,
            "error": f"Resource not found: {e}",
            "error_code": "NOT_FOUND"
        }
    except PermissionDenied as e:
        return {
            "success": False,
            "error": f"Permission denied: {e}",
            "error_code": "PERMISSION_DENIED"
        }
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in tool_operation: {e}")
        return {
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
```

## 🧪 Testing Architecture

### Testing Strategy

1. **Unit Tests**: Individual tool function testing
2. **Integration Tests**: End-to-end workflow testing
3. **Mock Testing**: Databricks API responses mocked
4. **Performance Testing**: Load and stress testing

### Test Structure

```python
# Example test structure
def test_describe_uc_catalog():
    # Arrange
    mock_client = MockWorkspaceClient()
    
    # Act
    result = describe_uc_catalog("hive_metastore")
    
    # Assert
    assert result["success"] == True
    assert "catalogs" in result
    assert result["count"] >= 0
```

## 📈 Scalability Considerations

### Horizontal Scaling

- **Stateless Design**: Server can be scaled horizontally
- **Load Balancing**: Multiple instances behind load balancer
- **Database Independence**: No persistent state to manage

### Resource Management

- **Connection Pooling**: Efficient Databricks client management
- **Memory Management**: Large result sets handled efficiently
- **Timeout Handling**: Configurable timeouts for long operations

## 🔄 Deployment Architecture

### Deployment Options

1. **Local Development**: Direct Python execution
2. **Docker**: Containerized deployment
3. **Cloud Platforms**: Google Cloud Run, AWS App Runner
4. **Databricks Apps**: Native Databricks deployment

### Environment Configuration

```bash
# Required
DATABRICKS_HOST=https://workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token

# Optional
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

## 📚 Related Documentation

- **[Getting Started](getting-started.md)** - Setup and configuration
- **[Core Tools](core-tools.md)** - Tool categories and usage
- **[API Reference](api-reference.md)** - Complete tool reference
- **[Testing](testing.md)** - Testing strategies and examples

---

**This architecture provides a solid foundation for a scalable, secure, and maintainable Databricks MCP Server.**
