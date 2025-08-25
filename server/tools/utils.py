"""Simple utility functions for MCP tools."""

import re


def sanitize_error_message(error_msg: str) -> str:
  """Remove sensitive information from error messages.

  Args:
      error_msg: The raw error message

  Returns:
      Sanitized error message with sensitive data removed
  """
  # Remove Databricks tokens (dapi... format)
  error_msg = re.sub(r'dapi[a-zA-Z0-9\-_]+', '[TOKEN_REDACTED]', error_msg)

  # Remove bearer tokens
  error_msg = re.sub(r'Bearer [a-zA-Z0-9\-_\.]+', 'Bearer [TOKEN_REDACTED]', error_msg)

  # Remove general token patterns
  error_msg = re.sub(r'token [a-zA-Z0-9\-_]+', 'token [REDACTED]', error_msg)

  # Remove file paths that might contain usernames
  error_msg = re.sub(r'/Users/[^/\s]+', '/Users/[USER]', error_msg)
  error_msg = re.sub(r'/home/[^/\s]+', '/home/[USER]', error_msg)

  # Remove server.tools internal paths
  error_msg = re.sub(r'server\.tools\.[a-zA-Z_\.]+', 'server.tools.[MODULE]', error_msg)

  return error_msg
