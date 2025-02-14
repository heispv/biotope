"""Command line interface for biotope."""

import click

from biotope.commands.read import read as read_cmd

@click.group()
@click.version_option()
def cli() -> None:
    """CLI integration for BioCypher ecosystem packages."""
    pass


@cli.command()
def init() -> None:
    """Initialize a new BioCypher project."""
    click.echo("Establishing biotope...")


@cli.command()
def build() -> None:
    """Build knowledge representation."""
    click.echo("Building knowledge representation...")


cli.add_command(read_cmd, "read")


@cli.command()
def chat() -> None:
    """Manage LLM integration and knowledge application."""
    click.echo("Managing LLM integration...")

@cli.command()
def benchmark() -> None:
    """Run the BioCypher ecosystem benchmarks."""
    click.echo("Running benchmarks...")


@cli.command()
def view() -> None:
    """View and analyze BioCypher knowledge graphs."""
    click.echo("Viewing knowledge graph...")


if __name__ == "__main__":
    cli() 