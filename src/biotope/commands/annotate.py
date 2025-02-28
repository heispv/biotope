"""Command for creating dataset metadata definitions in Croissant format."""

import datetime
import getpass
import json
import subprocess
from pathlib import Path

import click


@click.group()
def annotate() -> None:
    """Create dataset metadata definitions in Croissant format."""


@annotate.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="metadata.json",
    help="Output file path for the metadata JSON-LD.",
)
@click.option(
    "--name",
    "-n",
    required=True,
    help="Name of the dataset.",
)
@click.option(
    "--description",
    "-d",
    default="",
    help="Description of the dataset.",
)
@click.option(
    "--data-source",
    "-s",
    required=True,
    help="URL or path to the data source.",
)
@click.option(
    "--contact",
    "-c",
    default=getpass.getuser(),
    help="Responsible contact person for the dataset.",
)
@click.option(
    "--date",
    default=datetime.datetime.now(tz=datetime.timezone.utc).date().isoformat(),
    help="Date of creation (ISO format: YYYY-MM-DD).",
)
@click.option(
    "--access-restrictions",
    "-a",
    required=True,
    help="Note on access restrictions (e.g., public, restricted, private).",
)
@click.option(
    "--format",
    "-f",
    help="Description of file format.",
)
@click.option(
    "--legal-obligations",
    "-l",
    help="Note on legal obligations.",
)
@click.option(
    "--collaboration-partner",
    "-p",
    help="Collaboration partner and institute.",
)
def create(
    output,
    name,
    description,
    data_source,
    contact,
    date,
    access_restrictions,
    format,
    legal_obligations,
    collaboration_partner,
):
    """Create a new Croissant metadata file with required scientific metadata fields."""
    # Create a basic metadata structure
    metadata = {
        "@context": {
            "@vocab": "https://schema.org/",
            "ml": "https://ml-schema.org/",
        },
        "@type": "ml:Dataset",
        "name": name,
        "description": description,
        "dataSource": data_source,
        "contactPerson": contact,
        "creationDate": date,
        "accessRestrictions": access_restrictions,
    }

    # Add optional fields if provided
    if format:
        metadata["fileFormat"] = format
    if legal_obligations:
        metadata["legalObligations"] = legal_obligations
    if collaboration_partner:
        metadata["collaborationPartner"] = collaboration_partner

    # Write to file
    with open(output, "w") as f:
        json.dump(metadata, f, indent=2)

    click.echo(f"Created Croissant metadata file at {output}")


@annotate.command()
@click.option(
    "--jsonld",
    "-j",
    type=click.Path(exists=True),
    required=True,
    help="Path to the JSON-LD metadata file to validate.",
)
def validate(jsonld):
    """Validate a Croissant metadata file."""
    try:
        # Use mlcroissant CLI to validate the file
        result = subprocess.run(
            ["mlcroissant", "validate", "--jsonld", jsonld],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo("Validation successful! The metadata file is valid.")
        if result.stdout:
            click.echo(f"Output: {result.stdout}")
        if result.stderr:
            click.echo(f"Warnings: {result.stderr}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Validation failed: {e.stderr}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"Error running validation: {e!s}", err=True)
        exit(1)


@annotate.command()
@click.option(
    "--jsonld",
    "-j",
    type=click.Path(exists=True),
    required=True,
    help="Path to the JSON-LD metadata file.",
)
@click.option(
    "--record-set",
    "-r",
    required=True,
    help="Name of the record set to load.",
)
@click.option(
    "--num-records",
    "-n",
    type=int,
    default=10,
    help="Number of records to load.",
)
def load(jsonld, record_set, num_records):
    """Load records from a dataset using its Croissant metadata."""
    try:
        # Use mlcroissant CLI to load the dataset
        result = subprocess.run(
            [
                "mlcroissant",
                "load",
                "--jsonld",
                jsonld,
                "--record_set",
                record_set,
                "--num_records",
                str(num_records),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Display the output
        if result.stdout:
            click.echo(result.stdout)

        click.echo(f"Loaded {num_records} records from record set '{record_set}'")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error loading dataset: {e.stderr}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"Error running load command: {e!s}", err=True)
        exit(1)


@annotate.command()
def interactive():
    """Interactively create a Croissant metadata file with required scientific metadata fields."""
    click.echo("Starting interactive Croissant metadata creation...")

    # Get basic metadata with defaults
    name = click.prompt("Dataset name")
    description = click.prompt("Dataset description", default="")

    # Get required metadata fields
    data_source = click.prompt("Data source URL", required=True)

    # Use defaults for some fields
    project_name = click.prompt("Project name", default=Path.cwd().name)
    contact = click.prompt("Responsible contact person", default=getpass.getuser())
    date = click.prompt("Date of creation", default=datetime.date.today().isoformat())

    # Get other required fields
    access_restrictions = click.prompt("Access restrictions", required=True)

    # Get optional fields
    format = click.prompt("File format", default="")
    legal_obligations = click.prompt("Legal obligations", default="")
    collaboration_partner = click.prompt("Collaboration partner and institute", default="")

    # Create metadata structure
    metadata = {
        "@context": {
            "@vocab": "https://schema.org/",
            "ml": "https://ml-schema.org/",
        },
        "@type": "ml:Dataset",
        "name": name,
        "description": description,
        "dataSource": data_source,
        "projectName": project_name,
        "contactPerson": contact,
        "creationDate": date,
        "accessRestrictions": access_restrictions,
    }

    # Add optional fields if provided
    if format:
        metadata["fileFormat"] = format
    if legal_obligations:
        metadata["legalObligations"] = legal_obligations
    if collaboration_partner:
        metadata["collaborationPartner"] = collaboration_partner

    # Ask about record sets
    if click.confirm("Would you like to add a record set?", default=True):
        metadata["ml:recordSet"] = []

        while True:
            record_set_name = click.prompt("Record set name")
            record_set_description = click.prompt("Record set description", default="")

            # Create record set
            record_set = {
                "@type": "ml:RecordSet",
                "@id": record_set_name,
                "name": record_set_name,
                "description": record_set_description,
            }

            # Ask about fields
            if click.confirm("Would you like to add fields to this record set?", default=True):
                record_set["ml:field"] = []

                while True:
                    field_name = click.prompt("Field name")
                    field_description = click.prompt("Field description", default="")

                    # Create field
                    field = {
                        "@type": "ml:Field",
                        "name": field_name,
                        "description": field_description,
                    }

                    # Add field to record set
                    record_set["ml:field"].append(field)

                    if not click.confirm("Add another field?", default=True):
                        break

            # Add record set to metadata
            metadata["ml:recordSet"].append(record_set)

            if not click.confirm("Add another record set?", default=False):
                break

    # Save metadata
    output_path = click.prompt("Output file path", default="metadata.json")
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    click.echo(f"Created Croissant metadata file at {output_path}")
