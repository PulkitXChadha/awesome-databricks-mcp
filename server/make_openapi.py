"""Generate OpenAPI schema from FastAPI app."""

import json

import click

from .app import app


@click.command()
@click.option('--output', default='openapi.json', help='Output file for OpenAPI schema')
def main(output: str):
  """Generate OpenAPI schema from FastAPI app."""
  schema = app.openapi()
  with open(output, 'w') as f:
    json.dump(schema, f, indent=2)
  print(f'OpenAPI schema written to {output}')


if __name__ == '__main__':
  main()
