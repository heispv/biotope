"""Test the read command functionality."""

import pytest
from click.testing import CliRunner

from biotope.commands.read import read


def test_read_command():
    """Test basic read command functionality."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(read, ["--text", "test input"])
        assert result.exit_code == 0
        assert "Extracted knowledge: test input" in result.output


def test_read_command_no_text():
    """Test read command fails without any input."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(read)
        assert result.exit_code != 0
        assert "Either --text or --file must be provided" in result.output


def test_read_command_from_file():
    """Test read command with file input."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('test.txt', 'w') as f:
            f.write('test content')
        result = runner.invoke(read, ["--file", "test.txt"])
        assert result.exit_code == 0
        assert "Extracted knowledge: test content" in result.output


def test_read_command_both_inputs():
    """Test read command with both text and file input."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('test.txt', 'w') as f:
            f.write('file content')
        result = runner.invoke(read, ["--text", "text input", "--file", "test.txt"])
        assert result.exit_code == 0
        # File input should take precedence
        assert "Extracted knowledge: file content" in result.output
