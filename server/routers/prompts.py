"""API endpoints for MCP prompts."""

from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get('')
async def list_prompts() -> List[Dict[str, str]]:
  """List all available prompts."""
  prompts_dir = Path('prompts')
  prompts = []

  if prompts_dir.exists():
    for prompt_file in prompts_dir.glob('*.md'):
      prompt_name = prompt_file.stem
      # Read first line for description
      try:
        content = prompt_file.read_text()
        lines = content.strip().split('\n')
        description = prompt_name.replace('_', ' ').title()

        if lines and lines[0].startswith('#'):
          description = lines[0].strip('#').strip()

        prompts.append(
          {'name': prompt_name, 'description': description, 'filename': prompt_file.name}
        )
      except Exception:
        # If error reading, still include the prompt
        prompts.append(
          {
            'name': prompt_name,
            'description': prompt_name.replace('_', ' ').title(),
            'filename': prompt_file.name,
          }
        )

  return prompts


@router.get('/{prompt_name}')
async def get_prompt(prompt_name: str) -> Dict[str, str]:
  """Get the content of a specific prompt."""
  prompt_file = Path(f'prompts/{prompt_name}.md')

  if not prompt_file.exists():
    # Try without .md extension if it was included
    prompt_file = Path(f'prompts/{prompt_name}')
    if not prompt_file.exists():
      raise HTTPException(status_code=404, detail='Prompt not found')

  try:
    content = prompt_file.read_text()
    return {'name': prompt_file.stem, 'content': content}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f'Failed to read prompt: {str(e)}')
