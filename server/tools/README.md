# Databricks MCP Tools - Modular Structure

This directory contains the modularized MCP tools for Databricks operations. The original `tools.py` file (4231 lines) has been broken down into logical, manageable modules.

## Structure

```
server/tools/
├── __init__.py              # Main entry point that imports and registers all tools
├── core.py                  # Core/health tools (1 tool)
├── sql_operations.py        # SQL warehouse and query management (15 tools)
├── unity_catalog.py         # Unity Catalog operations (20 tools)
├── data_management.py       # DBFS, volumes, and data operations (10 tools)
├── jobs_pipelines.py        # Job and pipeline management (20 tools)
├── workspace_files.py       # Workspace file operations (5 tools)
├── dashboards.py            # Dashboard and monitoring tools (8 tools)
├── repositories.py          # Git repository management (10 tools)
├── governance.py            # Governance rules and data lineage (15 tools)
└── test_imports.py         # Test file for verifying imports
```

## Tool Distribution

| Module | Tools | Description |
|--------|-------|-------------|
| **core.py** | 1 | Basic health checks and core functionality |
| **sql_operations.py** | 15 | SQL warehouse management, query execution, and monitoring |
| **unity_catalog.py** | 20 | Catalog, schema, table, and metadata operations |
| **data_management.py** | 10 | DBFS operations, external locations, storage credentials |
| **jobs_pipelines.py** | 20 | Job and DLT pipeline management |
| **workspace_files.py** | 5 | Workspace file and directory operations |
| **dashboards.py** | 8 | Lakeview and legacy dashboard management |
| **repositories.py** | 10 | Git repository operations and branch management |
| **governance.py** | 15 | Audit logs, governance rules, and data lineage |

**Total: 104 tools** organized into 9 logical modules

## Benefits of Modularization

1. **Maintainability**: Each module focuses on a specific domain, making code easier to understand and maintain
2. **Readability**: Smaller files are easier to navigate and debug
3. **Collaboration**: Multiple developers can work on different modules simultaneously
4. **Testing**: Individual modules can be tested in isolation
5. **Scalability**: New tools can be added to appropriate modules without cluttering the main file
6. **Documentation**: Each module has clear purpose and can be documented independently

## Usage

The main `load_tools()` function in `__init__.py` automatically imports and registers all tools from each module. No changes are needed in the calling code - the interface remains the same.

## Adding New Tools

To add new tools:

1. Identify the appropriate module based on functionality
2. Add the tool function to that module
3. Ensure the tool is properly decorated with `@mcp_server.tool`
4. The tool will automatically be available when the module is loaded

## Migration Notes

- Original `tools.py` has been backed up as `tools.py.backup`
- All existing functionality is preserved
- No breaking changes to the API
- Tools are organized by domain rather than alphabetically for better logical grouping
