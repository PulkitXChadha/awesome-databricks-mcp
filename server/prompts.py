"""MCP Prompts loader for Databricks operations."""

import glob
import os


def load_prompts(mcp_server):
  """Dynamically load prompts from the prompts directory.

  Args:
      mcp_server: The FastMCP server instance to register prompts with
  """
  prompt_files = glob.glob('prompts/*.md')

  for prompt_file in prompt_files:
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]

    # Read the prompt file
    with open(prompt_file, 'r') as f:
      content = f.read()
      lines = content.strip().split('\n')

      # First line is the title (skip the # prefix)
      title = lines[0].strip().lstrip('#').strip() if lines else prompt_name
      # Full content is what gets returned

    # Create a closure to capture the current values
    def make_prompt_handler(prompt_content, prompt_name, prompt_title):
      @mcp_server.prompt(name=prompt_name, description=prompt_title)
      async def handle_prompt():
        return prompt_content

      return handle_prompt

    # Register the prompt
    make_prompt_handler(content, prompt_name, title)
