#!/usr/bin/env python3
"""Test runner script for the Databricks MCP project."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_tests(test_type=None, verbose=False, coverage=False):
  """Run tests with specified options."""
  # Base pytest command
  cmd = ['python', '-m', 'pytest']

  # Add test type filtering
  if test_type:
    if test_type == 'unit':
      cmd.extend(['-m', 'unit'])
    elif test_type == 'integration':
      cmd.extend(['-m', 'integration'])
    elif test_type == 'all':
      pass  # No filtering
    else:
      print(f'Unknown test type: {test_type}')
      print('Available types: unit, integration, all')
      return False

  # Add verbose flag
  if verbose:
    cmd.append('-v')

  # Add coverage
  if coverage:
    cmd.extend(['--cov=server', '--cov-report=html', '--cov-report=term'])

  # Add test discovery
  cmd.append('tests/')

  # Add color output
  cmd.append('--color=yes')

  # Add test summary
  cmd.append('--tb=short')

  print(f'Running tests with command: {" ".join(cmd)}')
  print('-' * 80)

  try:
    result = subprocess.run(cmd, check=False)
    return result.returncode == 0
  except KeyboardInterrupt:
    print('\nTests interrupted by user')
    return False
  except Exception as e:
    print(f'Error running tests: {e}')
    return False


def list_test_files():
  """List all available test files."""
  test_dir = Path(__file__).parent
  test_files = list(test_dir.glob('test_*.py'))

  print('Available test files:')
  print('-' * 40)

  for test_file in sorted(test_files):
    print(f'  {test_file.name}')

  print(f'\nTotal: {len(test_files)} test files')


def main():
  """Main entry point."""
  parser = argparse.ArgumentParser(description='Run tests for Databricks MCP project')
  parser.add_argument(
    '--type',
    choices=['unit', 'integration', 'all'],
    default='all',
    help='Type of tests to run (default: all)',
  )
  parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
  parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
  parser.add_argument('--list', action='store_true', help='List available test files')

  args = parser.parse_args()

  if args.list:
    list_test_files()
    return

  print('Databricks MCP Test Runner')
  print('=' * 50)
  print(f'Test type: {args.type}')
  print(f'Verbose: {args.verbose}')
  print(f'Coverage: {args.coverage}')
  print()

  success = run_tests(args.type, args.verbose, args.coverage)

  if success:
    print('\n✅ All tests passed!')
    sys.exit(0)
  else:
    print('\n❌ Some tests failed!')
    sys.exit(1)


if __name__ == '__main__':
  main()
