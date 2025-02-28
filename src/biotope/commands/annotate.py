"""Command for creating dataset metadata definitions in Croissant format."""

import datetime
import getpass
import json
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table


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
    console = Console()

    # Create a nice header
    console.print(
        Panel(
            "[bold blue]Biotope Dataset Metadata Creator[/]",
            subtitle="Create scientific dataset metadata in Croissant format",
        )
    )

    console.print(Markdown("This wizard will help you document your scientific dataset with standardized metadata."))
    console.print()

    # Section: Basic Information
    console.print("[bold green]Basic Dataset Information[/]")
    console.print("─" * 50)

    name = click.prompt("Dataset name (a short, descriptive title)")
    description = click.prompt(
        "Dataset description (what does this dataset contain and what is it used for?)",
        default="",
    )

    # Section: Source Information
    console.print("\n[bold green]Data Source Information[/]")
    console.print("─" * 50)
    console.print("Where did this data come from? (e.g., a URL, database name, or experiment)")
    data_source = click.prompt("Data source")

    # Section: Ownership and Dates
    console.print("\n[bold green]Ownership and Dates[/]")
    console.print("─" * 50)

    project_name = click.prompt(
        "Project name",
        default=Path.cwd().name,
    )

    contact = click.prompt(
        "Contact person (email preferred)",
        default=getpass.getuser(),
    )

    date = click.prompt(
        "Creation date (YYYY-MM-DD)",
        default=datetime.date.today().isoformat(),
    )

    # Section: Access Information
    console.print("\n[bold green]Access Information[/]")
    console.print("─" * 50)

    # Create a table for examples
    table = Table(title="Access Restriction Examples")
    table.add_column("Type", style="cyan")
    table.add_column("Description", style="green")
    table.add_row("Public", "Anyone can access and use the data")
    table.add_row("Academic", "Restricted to academic/research use only")
    table.add_row("Approval", "Requires explicit approval from data owner")
    table.add_row("Embargo", "Will become public after a specific date")
    console.print(table)

    has_access_restrictions = Confirm.ask(
        "Does this dataset have access restrictions?",
        default=False,
    )

    access_restrictions = None
    if has_access_restrictions:
        access_restrictions = Prompt.ask(
            "Please describe the access restrictions",
            default="",
        )
        if not access_restrictions.strip():
            access_restrictions = None

    # Section: Additional Information
    console.print("\n[bold green]Additional Information[/]")
    console.print("─" * 50)
    console.print("[italic]The following fields are optional but recommended for scientific datasets[/]")

    format = click.prompt(
        "File format (e.g., CSV, JSON, HDF5, FASTQ)",
        default="",
    )

    legal_obligations = click.prompt(
        "Legal obligations (e.g., citation requirements, licenses)",
        default="",
    )

    collaboration_partner = click.prompt(
        "Collaboration partner and institute",
        default="",
    )

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
    }

    # Only add access restrictions if they exist
    if access_restrictions:
        metadata["accessRestrictions"] = access_restrictions

    # Add optional fields if provided
    if format:
        metadata["fileFormat"] = format
    if legal_obligations:
        metadata["legalObligations"] = legal_obligations
    if collaboration_partner:
        metadata["collaborationPartner"] = collaboration_partner

    # Section: Data Structure
    console.print("\n[bold green]Data Structure[/]")
    console.print("─" * 50)

    # Create a table for record set examples
    table = Table(title="Record Set Examples")
    table.add_column("Dataset Type", style="cyan")
    table.add_column("Record Sets", style="green")
    table.add_row("Genomics", "patients, samples, gene_expressions")
    table.add_row("Climate", "locations, time_series, measurements")
    table.add_row("Medical", "patients, visits, treatments, outcomes")
    console.print(table)

    console.print("Record sets describe the structure of your data.")

    if click.confirm("Would you like to add a record set to describe your data structure?", default=True):
        metadata["ml:recordSet"] = []

        while True:
            record_set_name = click.prompt("Record set name (e.g., 'patients', 'samples')")
            record_set_description = click.prompt(f"Description of the '{record_set_name}' record set", default="")

            # Create record set
            record_set = {
                "@type": "ml:RecordSet",
                "@id": record_set_name,
                "name": record_set_name,
                "description": record_set_description,
            }

            # Ask about fields with examples
            console.print(f"\n[bold]Fields in '{record_set_name}'[/]")
            console.print("Fields describe the data columns or attributes in this record set.")

            if click.confirm(f"Would you like to add fields to the '{record_set_name}' record set?", default=True):
                record_set["ml:field"] = []

                while True:
                    field_name = click.prompt("Field name (column or attribute name)")
                    field_description = click.prompt(f"Description of '{field_name}'", default="")

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

    # Save metadata with a suggested filename
    default_filename = f"{name.lower().replace(' ', '_')}_metadata.json"
    output_path = click.prompt("Output file path", default=default_filename)

    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Final success message with rich formatting
    console.print()
    console.print(
        Panel(
            f"[bold green]✅ Created Croissant metadata file at:[/]\n[blue]{output_path}[/]",
            title="Success",
            border_style="green",
        )
    )

    console.print("[italic]Validate this file with:[/]")
    console.print(f"[bold yellow]biotope annotate validate --jsonld {output_path}[/]")
