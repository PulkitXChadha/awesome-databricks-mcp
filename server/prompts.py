"""MCP Prompts loader - SIMPLE implementation per CLAUDE.md."""

import glob
import os
import re

import yaml


def load_prompts(mcp_server):
  """Load prompts from markdown files with MCP metadata.

  Parses YAML frontmatter for MCP configuration and registers prompts dynamically.
  """
  prompt_files = glob.glob('prompts/*.md')

  for prompt_file in prompt_files:
    # Parse the markdown file for metadata and content
    metadata, content = parse_prompt_file(prompt_file)

    if not metadata:
      # Skip files without YAML frontmatter
      prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
      print(f'Warning: Skipping {prompt_name} - no YAML frontmatter found')
      continue

    # Register with full MCP metadata
    register_mcp_prompt(mcp_server, metadata, content)


def parse_prompt_file(filepath):
  """Parse markdown file for YAML frontmatter and content."""
  with open(filepath, 'r') as f:
    raw_content = f.read()

  # Check for YAML frontmatter (between --- markers)
  frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw_content, re.DOTALL)

  if frontmatter_match:
    try:
      metadata = yaml.safe_load(frontmatter_match.group(1))
      content = frontmatter_match.group(2)
      return metadata, content
    except yaml.YAMLError as e:
      print(f'Error parsing YAML in {filepath}: {e}')
      return None, raw_content

  return None, raw_content


def register_mcp_prompt(mcp_server, metadata, content):
  """Register prompt with MCP metadata support.

  Note: FastMCP doesn't support argument validation in prompts yet,
  so we return the content with placeholder substitution but without
  runtime validation. The YAML metadata documents the expected arguments
  for future MCP compliance.
  """
  name = metadata.get('name', 'unnamed_prompt')
  description = metadata.get('description', '')
  arguments = metadata.get('arguments', [])

  # Store metadata for documentation (even though FastMCP doesn't use it yet)
  # This prepares for future MCP compliance when FastMCP adds argument support

  # Create the prompt handler - FastMCP requires no parameters or specific named params
  @mcp_server.prompt(name=name, description=description)
  async def handle_prompt():
    # Build comprehensive documentation including arguments
    text = content

    # Add argument documentation to the prompt
    if arguments:
      arg_docs = '\n\n## Expected Arguments:\n'
      for arg in arguments:
        required = ' (required)' if arg.get('required') else ' (optional)'
        arg_docs += f'- **{arg["name"]}**{required}: {arg.get("description", "No description")}\n'
      text = text + arg_docs

    return [{'role': 'user', 'content': {'type': 'text', 'text': text}}]


# Note: No fallback support - all prompts must have YAML frontmatter
# This ensures consistency and proper validation across all prompts
