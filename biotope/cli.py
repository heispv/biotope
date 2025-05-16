"""Command line interface for biotope."""

import click

from biotope.commands.annotate import annotate as annotate_cmd
from biotope.commands.chat import chat as chat_cmd
from biotope.commands.get import get as get_cmd
from biotope.commands.init import init as init_cmd
from biotope.commands.read import read as read_cmd


@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """CLI entrypoint."""
    ctx.ensure_object(dict)
    ctx.obj = {"version": "0.1.0"}


cli.add_command(init_cmd, "init")


@cli.command()
def build() -> None:
    """Build knowledge representation."""
    click.echo("Building knowledge representation...")


cli.add_command(read_cmd, "read")


cli.add_command(chat_cmd, "chat")


cli.add_command(annotate_cmd, "annotate")
cli.add_command(get_cmd, "get")


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
