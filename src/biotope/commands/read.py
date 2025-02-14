"""Read command implementation."""

import click


@click.command()
@click.option(
    "--text",
    "-t",
    type=str,
    help="Text to extract knowledge from",
    required=False,
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="File to extract knowledge from",
    required=False,
)
def read(text: str | None, file: str | None) -> None:
    """
    Extract knowledge from input text or file using NLP.
    
    Args:
        text: Input text to process
        file: Input file to process
    """
    if text is None and file is None:
        raise click.UsageError("Either --text or --file must be provided")
    
    if file is not None:
        with open(file, 'r') as f:
            text = f.read()
    
    if text is not None:  # This will now be true in both cases
        result = extract_knowledge(text)
        click.echo(result)


def extract_knowledge(text: str) -> str:
    """
    Extract knowledge using NLP and other methods.
    
    Args:
        text: Input text to process
        
    Returns:
        Extracted knowledge (currently just returns input)
    """
    return f"Extracted knowledge: {text}"
