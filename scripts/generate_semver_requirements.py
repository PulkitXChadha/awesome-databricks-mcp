#!/usr/bin/env python3
"""Generate requirements.txt with semantic versioning ranges from pyproject.toml.

This script helps avoid conflicts with pre-installed packages in Databricks Apps.
"""

import sys
from pathlib import Path

try:
  import tomllib  # Python 3.11+
except ImportError:
  try:
    import tomli as tomllib  # Fallback for older Python
  except ImportError:
    # Fallback to manual parsing if no toml library available
    tomllib = None  # type: ignore


def parse_dependencies_manual(content):
  """Manually parse dependencies from pyproject.toml content."""
  dependencies = []
  in_dependencies = False

  for line in content.split('\n'):
    line = line.strip()
    if line == 'dependencies = [':
      in_dependencies = True
      continue
    elif in_dependencies and line == ']':
      break
    elif in_dependencies and line.startswith('"') and line.endswith('",'):
      # Extract dependency string
      dep = line[1:-2]  # Remove quotes and comma
      dependencies.append(dep)
    elif in_dependencies and line.startswith('"') and line.endswith('"'):
      # Last dependency without comma
      dep = line[1:-1]  # Remove quotes
      dependencies.append(dep)

  return dependencies


def generate_semver_requirements():
  """Extract dependencies from pyproject.toml and write requirements.txt with semver ranges."""
  # Read pyproject.toml
  pyproject_path = Path('pyproject.toml')
  if not pyproject_path.exists():
    print('Error: pyproject.toml not found', file=sys.stderr)
    sys.exit(1)

  # Try to parse with tomllib, fallback to manual parsing
  if tomllib:
    with open(pyproject_path, 'rb') as f:
      pyproject = tomllib.load(f)
    dependencies = pyproject.get('project', {}).get('dependencies', [])
  else:
    # Manual parsing fallback
    with open(pyproject_path, 'r') as f:
      content = f.read()
    dependencies = parse_dependencies_manual(content)

  if not dependencies:
    print('Warning: No dependencies found in pyproject.toml', file=sys.stderr)

  # Write requirements.txt
  with open('requirements.txt', 'w') as f:
    f.write('# Generated from pyproject.toml for Databricks Apps deployment\n')
    f.write('# Avoids editable installs and hash conflicts\n\n')

    for dep in dependencies:
      # Write each dependency on its own line
      f.write(f'{dep}\n')

  print(f'Generated requirements.txt with {len(dependencies)} dependencies')


if __name__ == '__main__':
  generate_semver_requirements()
