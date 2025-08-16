"""Unit tests for prompts router endpoints."""

from pathlib import Path

import pytest


@pytest.mark.unit
@pytest.mark.api
class TestPromptsRouter:
  """Test prompts router endpoints."""

  def test_list_prompts_empty_directory(self, test_client, tmp_path, monkeypatch):
    """Test listing prompts when prompts directory is empty."""
    # Create empty prompts directory
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

  def test_list_prompts_no_directory(self, test_client, tmp_path, monkeypatch):
    """Test listing prompts when prompts directory doesn't exist."""
    # No prompts directory created
    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

  def test_list_prompts_with_markdown_files(self, test_client, tmp_path, monkeypatch):
    """Test listing prompts with valid markdown files."""
    # Create prompts directory with test files
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    # Create test prompt files
    prompt1 = prompts_dir / 'test_prompt.md'
    prompt1.write_text('# Test Prompt\n\nThis is a test prompt.')

    prompt2 = prompts_dir / 'another_prompt.md'
    prompt2.write_text('# Another Prompt\n\nThis is another test prompt.')

    prompt3 = prompts_dir / 'no_header.md'
    prompt3.write_text('This prompt has no header.\n\nJust content.')

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    # Check that all prompts are included
    prompt_names = [prompt['name'] for prompt in data]
    assert 'test_prompt' in prompt_names
    assert 'another_prompt' in prompt_names
    assert 'no_header' in prompt_names

    # Check descriptions
    test_prompt_data = next(p for p in data if p['name'] == 'test_prompt')
    assert test_prompt_data['description'] == 'Test Prompt'
    assert test_prompt_data['filename'] == 'test_prompt.md'

    another_prompt_data = next(p for p in data if p['name'] == 'another_prompt')
    assert another_prompt_data['description'] == 'Another Prompt'

    no_header_data = next(p for p in data if p['name'] == 'no_header')
    assert no_header_data['description'] == 'No Header'  # Auto-generated from filename

  def test_list_prompts_ignores_non_markdown_files(self, test_client, tmp_path, monkeypatch):
    """Test that non-markdown files are ignored when listing prompts."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    # Create various file types
    (prompts_dir / 'valid_prompt.md').write_text('# Valid Prompt\n\nContent.')
    (prompts_dir / 'not_a_prompt.txt').write_text('This is not a prompt.')
    (prompts_dir / 'config.json').write_text('{"key": "value"}')
    (prompts_dir / 'README.rst').write_text('README content')

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # Only the .md file should be included
    assert data[0]['name'] == 'valid_prompt'

  def test_list_prompts_handles_read_errors(self, test_client, tmp_path, monkeypatch):
    """Test that prompts with read errors are still included in the list."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    # Create a valid prompt
    (prompts_dir / 'valid_prompt.md').write_text('# Valid Prompt\n\nContent.')

    # Create a file that will cause read error (empty filename will be included)
    (prompts_dir / 'unreadable_prompt.md').write_text('# Unreadable\n\nContent.')

    monkeypatch.chdir(tmp_path)

    # Mock pathlib.Path.read_text to raise exception for one file
    original_read_text = Path.read_text

    def mock_read_text(self, *args, **kwargs):
      if 'unreadable_prompt' in str(self):
        raise OSError('Permission denied')
      return original_read_text(self, *args, **kwargs)

    Path.read_text = mock_read_text

    try:
      response = test_client.get('/api/prompts')

      assert response.status_code == 200
      data = response.json()
      assert len(data) == 2  # Both prompts should be included

      # Valid prompt should have correct description
      valid_prompt = next(p for p in data if p['name'] == 'valid_prompt')
      assert valid_prompt['description'] == 'Valid Prompt'

      # Unreadable prompt should have auto-generated description
      unreadable_prompt = next(p for p in data if p['name'] == 'unreadable_prompt')
      assert unreadable_prompt['description'] == 'Unreadable Prompt'

    finally:
      # Restore original method
      Path.read_text = original_read_text

  def test_get_prompt_success(self, test_client, tmp_path, monkeypatch):
    """Test successful prompt retrieval."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    prompt_content = (
      '# Test Prompt\n\nThis is the content of the test prompt.\n\n## Section\n\nMore content here.'
    )
    (prompts_dir / 'test_prompt.md').write_text(prompt_content)

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts/test_prompt')

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'test_prompt'
    assert data['content'] == prompt_content

  def test_get_prompt_with_md_extension(self, test_client, tmp_path, monkeypatch):
    """Test prompt retrieval when .md extension is included in request."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    prompt_content = '# Test Prompt\n\nContent with extension handling.'
    (prompts_dir / 'test_prompt.md').write_text(prompt_content)

    monkeypatch.chdir(tmp_path)

    # Request with .md extension should also work
    response = test_client.get('/api/prompts/test_prompt.md')

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'test_prompt'
    assert data['content'] == prompt_content

  def test_get_prompt_not_found(self, test_client, tmp_path, monkeypatch):
    """Test prompt retrieval for non-existent prompt."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts/nonexistent_prompt')

    assert response.status_code == 404
    data = response.json()
    assert 'not found' in data['detail']

  def test_get_prompt_no_prompts_directory(self, test_client, tmp_path, monkeypatch):
    """Test prompt retrieval when prompts directory doesn't exist."""
    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts/any_prompt')

    assert response.status_code == 404
    data = response.json()
    assert 'not found' in data['detail']

  def test_get_prompt_read_error(self, test_client, tmp_path, monkeypatch):
    """Test prompt retrieval when file read fails."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    (prompts_dir / 'test_prompt.md').write_text('# Test Content')

    monkeypatch.chdir(tmp_path)

    # Mock pathlib.Path.read_text to raise exception
    original_read_text = Path.read_text

    def mock_read_text(self, *args, **kwargs):
      if 'test_prompt' in str(self):
        raise OSError('Permission denied')
      return original_read_text(self, *args, **kwargs)

    Path.read_text = mock_read_text

    try:
      response = test_client.get('/api/prompts/test_prompt')

      assert response.status_code == 500
      data = response.json()
      assert 'Failed to read prompt' in data['detail']
      assert 'Permission denied' in data['detail']

    finally:
      # Restore original method
      Path.read_text = original_read_text


@pytest.mark.unit
@pytest.mark.api
class TestPromptsRouterEdgeCases:
  """Test edge cases for prompts router."""

  def test_prompt_with_special_characters_in_filename(self, test_client, tmp_path, monkeypatch):
    """Test prompts with special characters in filenames."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    # Create prompts with various filename patterns
    (prompts_dir / 'prompt_with_underscores.md').write_text('# Underscore Prompt')
    (prompts_dir / 'prompt-with-hyphens.md').write_text('# Hyphen Prompt')
    (prompts_dir / 'prompt123.md').write_text('# Number Prompt')

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    prompt_names = [p['name'] for p in data]
    assert 'prompt_with_underscores' in prompt_names
    assert 'prompt-with-hyphens' in prompt_names
    assert 'prompt123' in prompt_names

  def test_empty_prompt_file(self, test_client, tmp_path, monkeypatch):
    """Test handling of empty prompt files."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    (prompts_dir / 'empty_prompt.md').write_text('')

    monkeypatch.chdir(tmp_path)

    # List should include empty prompt
    response = test_client.get('/api/prompts')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'empty_prompt'
    assert data[0]['description'] == 'Empty Prompt'  # Auto-generated

    # Get should return empty content
    response = test_client.get('/api/prompts/empty_prompt')
    assert response.status_code == 200
    data = response.json()
    assert data['content'] == ''

  def test_prompt_with_complex_markdown(self, test_client, tmp_path, monkeypatch):
    """Test prompts with complex markdown content."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    complex_content = """# Complex Prompt

This prompt has **bold** and *italic* text.

## Code Blocks

```python
def hello():
    print("Hello, world!")
```

## Lists

- Item 1
- Item 2
  - Nested item
  - Another nested item

## Tables

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

## Links

[Link to Databricks](https://databricks.com)

---

End of prompt.
"""

    (prompts_dir / 'complex_prompt.md').write_text(complex_content)

    monkeypatch.chdir(tmp_path)

    response = test_client.get('/api/prompts/complex_prompt')

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'complex_prompt'
    assert data['content'] == complex_content


@pytest.mark.integration
@pytest.mark.api
class TestPromptsRouterIntegration:
  """Integration tests for prompts router."""

  def test_prompts_router_endpoints_exist(self, test_client):
    """Test that prompts router endpoints are properly mounted."""
    # List endpoint should exist
    response = test_client.get('/api/prompts')
    assert response.status_code == 200

    # Get endpoint should exist (will return 404 for non-existent prompt)
    response = test_client.get('/api/prompts/nonexistent')
    assert response.status_code == 404  # Not 405 (method not allowed)

  def test_prompts_workflow_with_real_files(self, test_client, tmp_path, monkeypatch):
    """Test complete workflow: list prompts then get specific prompt."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    # Create test prompts
    (prompts_dir / 'workflow_test.md').write_text('# Workflow Test\n\nTest content.')
    (prompts_dir / 'another_test.md').write_text('# Another Test\n\nAnother content.')

    monkeypatch.chdir(tmp_path)

    # First, list all prompts
    list_response = test_client.get('/api/prompts')
    assert list_response.status_code == 200
    prompts = list_response.json()
    assert len(prompts) == 2

    # Then get each prompt
    for prompt in prompts:
      get_response = test_client.get(f'/api/prompts/{prompt["name"]}')
      assert get_response.status_code == 200
      prompt_data = get_response.json()
      assert prompt_data['name'] == prompt['name']
      assert len(prompt_data['content']) > 0

  def test_prompts_router_response_format_consistency(self, test_client, tmp_path, monkeypatch):
    """Test that response formats are consistent across endpoints."""
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()

    (prompts_dir / 'format_test.md').write_text('# Format Test\n\nContent.')

    monkeypatch.chdir(tmp_path)

    # List response should be array of objects
    list_response = test_client.get('/api/prompts')
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert isinstance(list_data, list)

    if list_data:
      prompt_item = list_data[0]
      assert 'name' in prompt_item
      assert 'description' in prompt_item
      assert 'filename' in prompt_item

    # Get response should be single object
    get_response = test_client.get('/api/prompts/format_test')
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert isinstance(get_data, dict)
    assert 'name' in get_data
    assert 'content' in get_data
