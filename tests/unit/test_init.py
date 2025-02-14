"""Test the init command functionality."""

from pathlib import Path

import click
import yaml
from click.testing import CliRunner

from biotope.commands.init import init


@click.group()
def cli_test():
    """Test CLI group."""


def test_init_basic():
    """Test basic initialization with default values."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            init,
            input="test-project\nn\nneo4j\nn\n",
            obj={"version": "0.1.0"},
        )
        assert result.exit_code == 0
        assert "Biotope established successfully!" in result.output

        # Check directory structure
        assert Path("config").exists()
        assert Path("data/raw").exists()
        assert Path("data/processed").exists()
        assert Path("schemas").exists()
        assert Path("outputs").exists()
        assert Path(".biotope").exists()

        # Check config file
        with open("config/biotope.yaml") as f:
            config = yaml.safe_load(f)
            assert config["project"]["name"] == "test-project"
            assert config["project"]["output_format"] == "neo4j"
            assert config["knowledge_sources"] == []


def test_init_with_knowledge_source():
    """Test initialization with a knowledge source."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Add one knowledge source then finish
        result = runner.invoke(
            init,
            input="test-project\ny\nPubMed\ndatabase\n\nneo4j\nn\n",
            obj={"version": "0.1.0"},
        )
        assert result.exit_code == 0

        with open("config/biotope.yaml") as f:
            config = yaml.safe_load(f)
            assert len(config["knowledge_sources"]) == 1
            assert config["knowledge_sources"][0]["name"] == "PubMed"
            assert config["knowledge_sources"][0]["type"] == "database"


def test_init_with_llm():
    """Test initialization with LLM configuration."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Configure with OpenAI
        result = runner.invoke(
            init,
            input="test-project\nn\nneo4j\ny\nopenai\nsk-test123\n",
            obj={"version": "0.1.0"},
        )
        assert result.exit_code == 0

        with open("config/biotope.yaml") as f:
            config = yaml.safe_load(f)
            assert "llm" in config
            assert config["llm"]["provider"] == "openai"
            assert config["llm"]["api_key"] == "sk-test123"


def test_init_existing_biotope():
    """Test initialization fails when .biotope directory exists."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create .biotope directory
        Path(".biotope").mkdir()

        result = runner.invoke(init, obj={"version": "0.1.0"})
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_init_custom_directory():
    """Test initialization in a custom directory."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            init,
            ["--dir", "custom_dir"],
            input="test-project\nn\nneo4j\nn\n",
            obj={"version": "0.1.0"},
        )
        assert result.exit_code == 0
        assert Path("custom_dir/config").exists()
        assert Path("custom_dir/.biotope").exists()


def test_init_metadata():
    """Test metadata file creation and content."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            init,
            input="test-project\nn\nneo4j\nn\n",
            obj={"version": "0.1.0"},
        )
        assert result.exit_code == 0

        with open(".biotope/metadata.yaml") as f:
            metadata = yaml.safe_load(f)
            assert metadata["project_name"] == "test-project"
            assert "created_at" in metadata
            assert "biotope_version" in metadata
            assert "last_modified" in metadata
            assert isinstance(metadata["builds"], list)
