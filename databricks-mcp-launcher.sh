#!/bin/bash
# MCP launcher script for Claude CLI

exec uvx --refresh --from git+https://git@github.com/databricks-solutions/custom-mcp-databricks-app.git dba-mcp-proxy "$@"