"""Generate a web client from the OpenAPI spec."""

import os
import subprocess

import click


@click.command()
@click.option(
  '--api_json_from_server',
  is_flag=True,
  help='If true, uses localhost:8000/openapi.json',
  default=False,
  type=bool,
)
def main(api_json_from_server):
  """Generate a web client from the OpenAPI spec."""
  output = f'{os.getcwd()}/client/src/fastapi_client'

  # The API JSON from server is much faster than running the make_openapi script as the
  # make_openapi script needs to import all dependencies and run the FastAPI server.
  if api_json_from_server:
    openapi_input = 'http://localhost:8000/openapi.json'
  else:
    openapi_input = '/tmp/openapi.json'
    # Call the make_openapi script to generate the openapi.json file.
    run(f'uv run python -m server.make_openapi --output={openapi_input}')

  # Generate the web client.
  run(
    f"""
    pushd client/ > /dev/null && \
    npx openapi-typescript-codegen --input {openapi_input} --output {output} --useUnionTypes && \
    popd > /dev/null
  """
  )

  print(f'[make_fastapi_client] Web client written to {output}')


def run(cmd):
  """Run a command and return the result."""
  return subprocess.run(cmd, shell=True, check=True)


if __name__ == '__main__':
  main()
