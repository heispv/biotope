"""Initialize command implementation."""

from datetime import datetime, timezone
from pathlib import Path

import click
import yaml


@click.command()
@click.option(
    "--dir",
    "-d",
    type=click.Path(file_okay=False, path_type=Path),
    default=".",
    help="Directory to initialize biotope project in",
)
def init(dir: Path) -> None:  # noqa: A002
    """
    Initialize a new biotope with interactive configuration.

    Args:
        dir: Directory to initialize the project in

    """
    # Check if .biotope directory already exists
    biotope_dir = dir / ".biotope"
    if biotope_dir.exists():
        click.echo("❌ A biotope project already exists in this directory.")
        click.echo("To start fresh, remove the .biotope directory first.")
        raise click.Abort

    click.echo("Establishing biotope! Let's set up your project.\n")

    # Project name
    project_name = click.prompt(
        "What's your project name?",
        type=str,
        default=dir.absolute().name,
    )

    # Knowledge sources
    knowledge_sources = []
    if click.confirm("Would you like to add knowledge sources now?", default=True):
        while True:
            source = click.prompt(
                "\nEnter knowledge source (or press enter to finish)",
                type=str,
                default="",
                show_default=False,
            )
            if not source:
                break
            source_type = click.prompt(
                "What type of source is this?",
                type=click.Choice(["database", "file", "api"], case_sensitive=False),
                default="database",
            )
            knowledge_sources.append({"name": source, "type": source_type})

    # Output preferences
    output_format = click.prompt(
        "\nPreferred output format",
        type=click.Choice(["neo4j", "csv", "json"], case_sensitive=False),
        default="neo4j",
    )

    # LLM integration
    use_llm = click.confirm("\nWould you like to set up LLM integration?", default=True)
    if use_llm:
        llm_provider = click.prompt(
            "Which LLM provider would you like to use?",
            type=click.Choice(["openai", "anthropic", "local"], case_sensitive=False),
            default="openai",
        )

        if llm_provider in ["openai", "anthropic"]:
            api_key = click.prompt(
                f"Please enter your {llm_provider} API key",
                type=str,
                hide_input=True,
            )

    # Create user configuration
    user_config = {
        "project": {
            "name": project_name,
            "output_format": output_format,
        },
        "knowledge_sources": knowledge_sources,
    }

    if use_llm:
        user_config["llm"] = {
            "provider": llm_provider,
            "api_key": api_key if llm_provider in ["openai", "anthropic"] else None,
        }

    # Create internal metadata
    metadata = {
        "project_name": project_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "biotope_version": click.get_current_context().obj.get("version", "unknown"),
        "last_modified": datetime.now(timezone.utc).isoformat(),
        "builds": [],
        "knowledge_sources": knowledge_sources,
    }

    # Create project structure
    try:
        dir.mkdir(parents=True, exist_ok=True)
        create_project_structure(dir, user_config, metadata)
        click.echo("\n✨ Biotope established successfully! ✨")
        click.echo(
            f"\nYour biotope '{project_name}' has been established. "
            "Make sure to water regularly.",
        )
        click.echo("\nNext steps:")
        click.echo("1. Review the configuration in config/biotope.yaml")
        click.echo("2. Add your knowledge sources")
        click.echo("3. Run 'biotope build' to create your knowledge graph")
    except (OSError, yaml.YAMLError) as e:
        click.echo(f"\n❌ Error initializing project: {e!s}", err=True)
        raise click.Abort from e


def create_project_structure(directory: Path, config: dict, metadata: dict) -> None:
    """
    Create the project directory structure and configuration files.

    Args:
        directory: Project directory path
        config: User-facing configuration dictionary
        metadata: Internal metadata dictionary

    """
    # Create directory structure
    dirs = [
        ".biotope",
        ".biotope/logs",
        "config",
        "data",
        "data/raw",
        "data/processed",
        "schemas",
        "outputs",
    ]

    for d in dirs:
        (directory / d).mkdir(parents=True, exist_ok=True)

    # Create files
    (directory / "config" / "biotope.yaml").write_text(
        yaml.dump(config, default_flow_style=False),
    )

    (directory / ".biotope" / "metadata.yaml").write_text(
        yaml.dump(metadata, default_flow_style=False),
    )

    # Create README
    readme_content = f"""# {config["project"]["name"]}

A BioCypher knowledge graph project.

## Project Structure

- `config/`: User configuration files
- `data/`: Data files
  - `raw/`: Raw input data
  - `processed/`: Processed data
- `schemas/`: Knowledge schema definitions
- `outputs/`: Generated knowledge graphs
"""
    (directory / "README.md").write_text(readme_content)
