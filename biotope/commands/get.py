"""Command for downloading files and automatically triggering annotation."""

from __future__ import annotations

import datetime
import getpass
import hashlib
import json
import mimetypes
import os
from pathlib import Path
from urllib.parse import urlparse

import click
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn


# Add custom MIME type mappings
mimetypes.add_type("chemical/seq-na-fasta", ".fasta")
mimetypes.add_type("chemical/seq-aa-fasta", ".faa")
mimetypes.add_type("chemical/seq-na-fasta", ".fna")


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


def get_file_and_annotate(url: str, output_dir: str | None = None) -> None:
    """
    Download a file and create metadata for it.

    Args:
        url: URL of the file to download
        output_dir: Directory to save the file to (defaults to current directory)

    """
    import click  # Import click at the top of the function

    try:
        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Get filename from URL or Content-Disposition header
        filename = None
        if "Content-Disposition" in response.headers:
            content_disposition = response.headers["Content-Disposition"]
            if "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')
        if not filename:
            filename = url.split("/")[-1]

        # Save the file
        file_path = os.path.join(output_dir or "", filename)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Calculate MD5 hash for unique identification
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        file_hash = md5_hash.hexdigest()

        # Create a unique dataset name by combining a prefix with the file name
        dataset_name = f"Dataset_{filename}"

        # Create pre-filled metadata
        prefill_metadata = {
            "name": dataset_name,  # Use the unique dataset name
            "description": f"Dataset containing file downloaded from {url}",
            "url": url,
            "creator": {"@type": "Person", "name": getpass.getuser()},
            "dateCreated": datetime.datetime.now(tz=datetime.timezone.utc).date().isoformat(),
            "distribution": [
                {
                    "@type": "sc:FileObject",
                    "@id": f"file_{file_hash}",  # Use hash-based unique ID
                    "name": filename,
                    "contentUrl": url,
                    "encodingFormat": detect_file_type(Path(file_path)),
                    "sha256": file_hash,
                },
            ],
        }

        # Start interactive annotation using Click's context
        from biotope.commands.annotate import annotate

        ctx = click.get_current_context()
        ctx.invoke(
            annotate.get_command(ctx, "interactive"),
            file_path=file_path,
            prefill_metadata=json.dumps(prefill_metadata),
        )
    except requests.exceptions.RequestException as e:
        click.echo(f"Error downloading file: {e}", err=True)
        return


@click.command()
@click.argument("url")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False),
    default="downloads",
    help="Directory to save downloaded files",
)
def get(url: str, output_dir: str) -> None:
    """
    Download a file and trigger annotation process.

    URL can be any valid HTTP/HTTPS URL pointing to a file.
    """
    get_file_and_annotate(url, output_dir)
