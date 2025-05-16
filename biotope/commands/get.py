"""Command for downloading files and automatically triggering annotation."""

from __future__ import annotations

import hashlib
import json
import mimetypes
from pathlib import Path
from urllib.parse import urlparse

import click
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn


def calculate_md5(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def detect_file_type(file_path: Path) -> str:
    """Detect file type using mime types and file extension."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type:
        return mime_type
    return file_path.suffix[1:] if file_path.suffix else "unknown"


def download_file(url: str, output_dir: Path) -> Path | None:
    """Download a file from URL with progress bar."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Get filename from URL or Content-Disposition header
        filename = Path(urlparse(url).path).name
        if not filename:
            filename = "downloaded_file"

        output_path = output_dir / filename

        total_size = int(response.headers.get("content-length", 0))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"Downloading {filename}...", total=total_size)

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

        return output_path
    except Exception as e:
        click.echo(f"Error downloading file: {e}", err=True)
        return None


def get_file_and_annotate(url: str, output_dir: str, skip_annotation: bool, console=None) -> dict | None:
    """
    Core logic for downloading a file and optionally triggering annotation process.
    Returns the metadata dict if annotation is triggered, else None.
    """
    if console is None:
        from rich.console import Console

        console = Console()

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Download the file
    console.print(f"[bold blue]Downloading file from {url}[/]")
    file_path = download_file(url, output_path)

    if not file_path:
        console.print("[bold red]Download failed[/]")
        return None

    console.print(f"[bold green]Successfully downloaded to {file_path}[/]")

    if skip_annotation:
        return None

    # Prepare metadata for annotation in Croissant ML format
    file_md5 = calculate_md5(file_path)
    file_type = detect_file_type(file_path)
    filename = file_path.name

    # Create pre-filled metadata following Croissant ML schema
    prefill_metadata = {
        "@context": {
            "@vocab": "https://schema.org/",
            "cr": "https://mlcommons.org/croissant/",
            "ml": "http://ml-schema.org/",
            "sc": "https://schema.org/",
        },
        "@type": "Dataset",
        "name": filename,  # Default to filename, can be changed in interactive mode
        "description": f"Downloaded file from {url}",
        "url": url,
        "encodingFormat": file_type,
        "distribution": [
            {
                "@type": "sc:FileObject",
                "@id": f"file_{file_md5}",
                "name": filename,
                "contentUrl": str(file_path),
                "encodingFormat": file_type,
                "sha256": file_md5,  # Using MD5 as SHA256 for now
            },
        ],
        "cr:recordSet": [
            {
                "@type": "cr:RecordSet",
                "@id": "#main",
                "name": "main",
                "description": f"Records from {filename}",
                "cr:field": [
                    {
                        "@type": "cr:Field",
                        "@id": "#main/content",
                        "name": "content",
                        "description": "File content",
                        "dataType": "sc:Text",
                        "source": {
                            "fileObject": {"@id": f"file_{file_md5}"},
                            "extract": {"fileProperty": "content"},
                        },
                    },
                ],
            },
        ],
    }

    # Trigger annotation process
    console.print("[bold blue]Starting annotation process...[/]")
    try:
        import click

        from biotope.commands.annotate import annotate

        ctx = click.get_current_context()
        ctx.invoke(
            annotate.get_command(ctx, "interactive"),
            prefill_metadata=json.dumps(prefill_metadata),
        )
    except Exception as e:
        console.print(f"[bold red]Error during annotation: {e}[/]")
        return None

    return prefill_metadata


@click.command()
@click.argument("url")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False),
    default="downloads",
    help="Directory to save downloaded files",
)
@click.option(
    "--skip-annotation",
    "-s",
    is_flag=True,
    help="Skip automatic annotation after download",
)
def get(url: str, output_dir: str, skip_annotation: bool) -> None:
    """
    Download a file and optionally trigger annotation process.

    URL can be any valid HTTP/HTTPS URL pointing to a file.
    """
    get_file_and_annotate(url, output_dir, skip_annotation)
