"""Command for creating dataset metadata definitions in Croissant format."""

from __future__ import annotations

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


def get_standard_context() -> dict:
    """Get the standard Croissant context."""
    return {
        "@vocab": "https://schema.org/",
        "cr": "https://mlcommons.org/croissant/",
        "ml": "http://ml-schema.org/",
        "sc": "https://schema.org/",
        "dct": "http://purl.org/dc/terms/",
        "data": "https://mlcommons.org/croissant/data/",
        "rai": "https://mlcommons.org/croissant/rai/",
        "format": "https://mlcommons.org/croissant/format/",
        "citeAs": "https://mlcommons.org/croissant/citeAs/",
        "conformsTo": "https://mlcommons.org/croissant/conformsTo/",
        "@language": "en",
        "repeated": "https://mlcommons.org/croissant/repeated/",
        "field": "https://mlcommons.org/croissant/field/",
        "examples": "https://mlcommons.org/croissant/examples/",
        "recordSet": "https://mlcommons.org/croissant/recordSet/",
        "fileObject": "https://mlcommons.org/croissant/fileObject/",
        "fileSet": "https://mlcommons.org/croissant/fileSet/",
        "source": "https://mlcommons.org/croissant/source/",
        "references": "https://mlcommons.org/croissant/references/",
        "key": "https://mlcommons.org/croissant/key/",
        "parentField": "https://mlcommons.org/croissant/parentField/",
        "isLiveDataset": "https://mlcommons.org/croissant/isLiveDataset/",
        "separator": "https://mlcommons.org/croissant/separator/",
        "extract": "https://mlcommons.org/croissant/extract/",
        "subField": "https://mlcommons.org/croissant/subField/",
        "regex": "https://mlcommons.org/croissant/regex/",
        "column": "https://mlcommons.org/croissant/column/",
        "path": "https://mlcommons.org/croissant/path/",
        "fileProperty": "https://mlcommons.org/croissant/fileProperty/",
        "md5": "https://mlcommons.org/croissant/md5/",
        "jsonPath": "https://mlcommons.org/croissant/jsonPath/",
        "transform": "https://mlcommons.org/croissant/transform/",
        "replace": "https://mlcommons.org/croissant/replace/",
        "dataType": "https://mlcommons.org/croissant/dataType/",
        "includes": "https://mlcommons.org/croissant/includes/",
        "excludes": "https://mlcommons.org/croissant/excludes/",
    }


def merge_metadata(dynamic_metadata: dict) -> dict:
    """Merge dynamic metadata with standard context and structure."""
    # Start with standard context
    metadata = {
        "@context": get_standard_context(),
        "@type": "Dataset",
    }

    # Update with dynamic content
    metadata.update(dynamic_metadata)

    return metadata


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
    # Create a basic metadata structure with proper Croissant context
    metadata = {
        "@context": {
            "@vocab": "https://schema.org/",
            "cr": "https://mlcommons.org/croissant/",
            "ml": "http://ml-schema.org/",
            "sc": "https://schema.org/",
            "dct": "http://purl.org/dc/terms/",
            "data": "https://mlcommons.org/croissant/data/",
            "rai": "https://mlcommons.org/croissant/rai/",
            "format": "https://mlcommons.org/croissant/format/",
            "citeAs": "https://mlcommons.org/croissant/citeAs/",
            "conformsTo": "https://mlcommons.org/croissant/conformsTo/",
            "@language": "en",
            "repeated": "https://mlcommons.org/croissant/repeated/",
            "field": "https://mlcommons.org/croissant/field/",
            "examples": "https://mlcommons.org/croissant/examples/",
            "recordSet": "https://mlcommons.org/croissant/recordSet/",
            "fileObject": "https://mlcommons.org/croissant/fileObject/",
            "fileSet": "https://mlcommons.org/croissant/fileSet/",
            "source": "https://mlcommons.org/croissant/source/",
            "references": "https://mlcommons.org/croissant/references/",
            "key": "https://mlcommons.org/croissant/key/",
            "parentField": "https://mlcommons.org/croissant/parentField/",
            "isLiveDataset": "https://mlcommons.org/croissant/isLiveDataset/",
            "separator": "https://mlcommons.org/croissant/separator/",
            "extract": "https://mlcommons.org/croissant/extract/",
            "subField": "https://mlcommons.org/croissant/subField/",
            "regex": "https://mlcommons.org/croissant/regex/",
            "column": "https://mlcommons.org/croissant/column/",
            "path": "https://mlcommons.org/croissant/path/",
            "fileProperty": "https://mlcommons.org/croissant/fileProperty/",
            "md5": "https://mlcommons.org/croissant/md5/",
            "jsonPath": "https://mlcommons.org/croissant/jsonPath/",
            "transform": "https://mlcommons.org/croissant/transform/",
            "replace": "https://mlcommons.org/croissant/replace/",
            "dataType": "https://mlcommons.org/croissant/dataType/",
        },
        "@type": "Dataset",
        "name": name,
        "description": description,
        "url": data_source,  # Changed from dataSource to url for schema.org compatibility
        "creator": {
            "@type": "Person",
            "name": contact,
        },
        "dateCreated": date,
        # Add recommended properties
        "datePublished": date,  # Use creation date as publication date by default
        "version": "1.0",  # Default version
        "license": "https://creativecommons.org/licenses/by/4.0/",  # Default license
        "citation": f"Please cite this dataset as: {name} ({date.split('-')[0]})",  # Simple citation
    }

    # Add custom fields with proper namespacing
    metadata["cr:accessRestrictions"] = access_restrictions

    # Add optional fields if provided
    if format:
        metadata["encodingFormat"] = format  # Using schema.org standard property
    if legal_obligations:
        metadata["cr:legalObligations"] = legal_obligations
    if collaboration_partner:
        metadata["cr:collaborationPartner"] = collaboration_partner

    # Add distribution property with empty array for FileObjects/FileSets
    metadata["distribution"] = []

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
            # Filter out informational log messages
            filtered_output = "\n".join(
                line for line in result.stdout.splitlines() if not line.startswith("I") or not line.endswith("Done.")
            )
            if filtered_output:
                click.echo(f"Output: {filtered_output}")
        if result.stderr:
            # Filter out informational log messages
            filtered_stderr = "\n".join(
                line for line in result.stderr.splitlines() if not line.startswith("I") or not line.endswith("Done.")
            )
            if filtered_stderr:
                click.echo(f"Warnings: {filtered_stderr}")
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
@click.option(
    "--file-path",
    "-f",
    type=click.Path(exists=True),
    help="Path to the file to annotate",
)
@click.option(
    "--prefill-metadata",
    "-p",
    type=str,
    help="JSON string containing pre-filled metadata",
)
def interactive(file_path: str | None = None, prefill_metadata: str | None = None) -> None:
    """Interactive annotation process for files."""
    console = Console()

    # Initialize metadata with pre-filled values if provided
    dynamic_metadata = json.loads(prefill_metadata) if prefill_metadata else {}

    # Merge with standard context and structure
    metadata = merge_metadata(dynamic_metadata)

    # If file path is provided, use it
    if file_path:
        metadata["file_path"] = file_path

    # Create a nice header
    console.print(
        Panel(
            "[bold blue]Biotope Dataset Metadata Creator[/]",
            subtitle="Create scientific dataset metadata in Croissant format",
        ),
    )

    console.print(Markdown("This wizard will help you document your scientific dataset with standardized metadata."))
    console.print()

    # Section: Basic Information
    console.print("[bold green]Basic Dataset Information[/]")
    console.print("─" * 50)

    # Use pre-filled name if available, otherwise prompt
    dataset_name = metadata.get("name", "")
    if not dataset_name:
        dataset_name = click.prompt(
            "Dataset name (a short, descriptive title; no spaces allowed)",
            default="",
        )
    else:
        dataset_name = click.prompt(
            "Dataset name (a short, descriptive title; no spaces allowed)",
            default=dataset_name,
        )

    description = click.prompt(
        "Dataset description (what does this dataset contain and what is it used for?)",
        default=metadata.get("description", ""),
    )

    # Section: Source Information
    console.print("\n[bold green]Data Source Information[/]")
    console.print("─" * 50)
    console.print("Where did this data come from? (e.g., a URL, database name, or experiment)")
    data_source = click.prompt("Data source", default=metadata.get("url", ""))

    # Section: Ownership and Dates
    console.print("\n[bold green]Ownership and Dates[/]")
    console.print("─" * 50)

    project_name = click.prompt(
        "Project name",
        default=metadata.get("cr:projectName", Path.cwd().name),
    )

    contact = click.prompt(
        "Contact person (email preferred)",
        default=metadata.get("creator", {}).get("name", getpass.getuser()),
    )

    date = click.prompt(
        "Creation date (YYYY-MM-DD)",
        default=metadata.get("dateCreated", datetime.date.today().isoformat()),
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
        default=bool(metadata.get("cr:accessRestrictions")),
    )

    access_restrictions = None
    if has_access_restrictions:
        access_restrictions = Prompt.ask(
            "Please describe the access restrictions",
            default=metadata.get("cr:accessRestrictions", ""),
        )
        if not access_restrictions.strip():
            access_restrictions = None

    # Section: Additional Information
    console.print("\n[bold green]Additional Information[/]")
    console.print("─" * 50)
    console.print("[italic]The following fields are optional but recommended for scientific datasets[/]")

    format = click.prompt(
        "File format (MIME type, e.g., text/csv, application/json, application/x-hdf5, application/fastq)",
        default=metadata.get("encodingFormat")
        or metadata.get("format")
        or (metadata.get("distribution", [{}])[0].get("encodingFormat", "")),
    )

    legal_obligations = click.prompt(
        "Legal obligations (e.g., citation requirements, licenses)",
        default=metadata.get("cr:legalObligations", ""),
    )

    collaboration_partner = click.prompt(
        "Collaboration partner and institute",
        default=metadata.get("cr:collaborationPartner", ""),
    )

    # Section: Publication Information
    console.print("\n[bold green]Publication Information[/]")
    console.print("─" * 50)
    console.print("[italic]The following fields are recommended for proper dataset citation[/]")

    publication_date = click.prompt(
        "Publication date (YYYY-MM-DD)",
        default=metadata.get("datePublished", date),  # Use creation date as default
    )

    version = click.prompt(
        "Dataset version",
        default=metadata.get("version", "1.0"),
    )

    license_url = click.prompt(
        "License URL",
        default=metadata.get("license", "https://creativecommons.org/licenses/by/4.0/"),
    )

    citation = click.prompt(
        "Citation text",
        default=metadata.get("citation", f"Please cite this dataset as: {dataset_name} ({date.split('-')[0]})"),
    )

    # Update metadata with new values while preserving any existing fields
    new_metadata = {
        "@context": get_standard_context(),  # Use the standard context
        "@type": "Dataset",
        "name": dataset_name,
        "description": description,
        "url": data_source,
        "creator": {
            "@type": "Person",
            "name": contact,
        },
        "dateCreated": date,
        "cr:projectName": project_name,
        "datePublished": publication_date,
        "version": version,
        "license": license_url,
        "citation": citation,
    }

    # Only add access restrictions if they exist
    if access_restrictions:
        new_metadata["cr:accessRestrictions"] = access_restrictions

    # Add optional fields if provided
    if format:
        new_metadata["encodingFormat"] = format
    if legal_obligations:
        new_metadata["cr:legalObligations"] = legal_obligations
    if collaboration_partner:
        new_metadata["cr:collaborationPartner"] = collaboration_partner

    # Update metadata while preserving pre-filled values
    for key, value in new_metadata.items():
        if key not in ["distribution"]:  # Don't overwrite distribution
            metadata[key] = value

    # Initialize distribution array for FileObjects/FileSets if it doesn't exist
    if "distribution" not in metadata:
        metadata["distribution"] = []

    # Section: File Resources
    console.print("\n[bold green]File Resources[/]")
    console.print("─" * 50)
    console.print("Croissant datasets can include file resources (FileObject) and file collections (FileSet).")

    # If we have pre-filled distribution, use it
    if prefill_metadata and "distribution" in dynamic_metadata:
        # Create a table to display pre-filled file information
        table = Table(title="Pre-filled File Resources")
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Format", style="yellow")
        table.add_column("Hash", style="magenta")

        for resource in dynamic_metadata["distribution"]:
            resource_type = resource.get("@type", "").replace("sc:", "").replace("cr:", "")
            name = resource.get("name", "")
            format = resource.get("encodingFormat", "")
            hash = resource.get("sha256", "")[:8] + "..." if resource.get("sha256") else ""

            table.add_row(resource_type, name, format, hash)

        console.print(table)

        if click.confirm("Would you like to use these pre-filled file resources?", default=True):
            metadata["distribution"] = dynamic_metadata["distribution"]
            console.print("[bold green]Using pre-filled file resources[/]")
        else:
            console.print("[yellow]You can now add new file resources manually[/]")
            metadata["distribution"] = []
    elif click.confirm("Would you like to add file resources to your dataset?", default=True):
        while True:
            resource_type = click.prompt(
                "Resource type",
                type=click.Choice(["FileObject", "FileSet"]),
                default="FileObject",
            )

            if resource_type == "FileObject":
                file_id = click.prompt("File ID (unique identifier for this file)")
                file_name = click.prompt("File name (including extension)")
                content_url = click.prompt("Content URL (where the file can be accessed)")
                encoding_format = click.prompt(
                    "Encoding format (MIME type, e.g., text/csv, application/json, application/x-hdf5, application/fastq)",
                )

                file_object = {
                    "@type": "sc:FileObject",
                    "@id": file_id,
                    "name": file_name,
                    "contentUrl": content_url,
                    "encodingFormat": encoding_format,
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                }

                # Optional SHA256 checksum
                if click.confirm("Add SHA256 checksum?", default=False):
                    sha256 = click.prompt("SHA256 checksum")
                    file_object["sha256"] = sha256

                # Optional containedIn property
                if click.confirm("Is this file contained in another file (e.g., in an archive)?", default=False):
                    container_id = click.prompt("Container file ID")
                    file_object["containedIn"] = {"@id": container_id}

                metadata["distribution"].append(file_object)

            else:  # FileSet
                fileset_id = click.prompt("FileSet ID (unique identifier for this file set)")

                # Container information
                container_id = click.prompt("Container file ID (archive or directory)")

                fileset = {
                    "@type": "cr:FileSet",
                    "@id": fileset_id,
                    "containedIn": {"@id": container_id},
                }

                # File pattern information
                encoding_format = click.prompt(
                    "Encoding format of files in this set (MIME type, e.g., text/csv, application/json, application/x-hdf5, application/fastq)",
                    default="",
                )
                if encoding_format:
                    fileset["encodingFormat"] = encoding_format

                includes_pattern = click.prompt("Include pattern (e.g., *.jpg, data/*.csv)", default="")
                if includes_pattern:
                    fileset["includes"] = includes_pattern

                # Optional exclude pattern
                if click.confirm("Add exclude pattern?", default=False):
                    excludes_pattern = click.prompt("Exclude pattern")
                    fileset["excludes"] = excludes_pattern

                metadata["distribution"].append(fileset)

            if not click.confirm("Add another file resource?", default=False):
                break

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
        metadata["cr:recordSet"] = []

        while True:
            record_set_name = click.prompt("Record set name (e.g., 'patients', 'samples')")
            record_set_description = click.prompt(f"Description of the '{record_set_name}' record set", default="")

            # Create record set with proper Croissant format
            record_set = {
                "@type": "cr:RecordSet",
                "@id": f"#{record_set_name}",
                "name": record_set_name,
                "description": record_set_description,
            }

            # Ask about data type
            if click.confirm(
                f"Would you like to specify a data type for the '{record_set_name}' record set?",
                default=False,
            ):
                data_type = click.prompt("Data type (e.g., sc:GeoCoordinates, sc:Person)")
                record_set["dataType"] = data_type

            # Ask about fields with examples
            console.print(f"\n[bold]Fields in '{record_set_name}'[/]")
            console.print("Fields describe the data columns or attributes in this record set.")

            if click.confirm(f"Would you like to add fields to the '{record_set_name}' record set?", default=True):
                record_set["cr:field"] = []

                while True:
                    field_name = click.prompt("Field name (column or attribute name)")
                    field_description = click.prompt(f"Description of '{field_name}'", default="")

                    # Create field with proper Croissant format
                    field = {
                        "@type": "cr:Field",
                        "@id": f"#{record_set_name}/{field_name}",
                        "name": field_name,
                        "description": field_description,
                    }

                    # Ask about data type
                    if click.confirm(
                        f"Would you like to specify a data type for the '{field_name}' field?",
                        default=False,
                    ):
                        data_type = click.prompt("Data type (e.g., sc:Text, sc:Integer, sc:Float, sc:ImageObject)")
                        field["dataType"] = data_type

                    # Ask about source
                    if click.confirm(
                        f"Would you like to specify a data source for the '{field_name}' field?",
                        default=False,
                    ):
                        source_type = click.prompt(
                            "Source type",
                            type=click.Choice(["FileObject", "FileSet"]),
                            default="FileObject",
                        )
                        source_id = click.prompt(f"{source_type} ID")

                        source = {"source": {}}
                        if source_type == "FileObject":
                            source["source"]["fileObject"] = {"@id": source_id}
                        else:
                            source["source"]["fileSet"] = {"@id": source_id}

                        # Ask about extraction method
                        extract_type = click.prompt(
                            "Extraction method",
                            type=click.Choice(["column", "jsonPath", "fileProperty", "none"]),
                            default="none",
                        )

                        if extract_type != "none":
                            source["source"]["extract"] = {}
                            if extract_type == "column":
                                column_name = click.prompt("Column name")
                                source["source"]["extract"]["column"] = column_name
                            elif extract_type == "jsonPath":
                                json_path = click.prompt("JSONPath expression")
                                source["source"]["extract"]["jsonPath"] = json_path
                            elif extract_type == "fileProperty":
                                file_property = click.prompt(
                                    "File property",
                                    type=click.Choice(["fullpath", "filename", "content", "lines", "lineNumbers"]),
                                )
                                source["source"]["extract"]["fileProperty"] = file_property

                        # Add source to field
                        for key, value in source["source"].items():
                            field[key] = value

                    # Ask if the field is repeated (array)
                    if click.confirm(f"Is '{field_name}' a repeated field (array/list)?", default=False):
                        field["repeated"] = True

                    # Ask if the field references another field
                    if click.confirm(f"Does '{field_name}' reference another field (foreign key)?", default=False):
                        ref_record_set = click.prompt("Referenced record set name")
                        ref_field = click.prompt("Referenced field name")
                        field["references"] = {"@id": f"#{ref_record_set}/{ref_field}"}

                    # Add field to record set
                    record_set["cr:field"].append(field)

                    if not click.confirm("Add another field?", default=True):
                        break

            # Ask about key fields
            if click.confirm(
                f"Would you like to specify key fields for the '{record_set_name}' record set?",
                default=False,
            ):
                record_set["key"] = []
                while True:
                    key_field = click.prompt("Key field name")
                    record_set["key"].append({"@id": f"#{record_set_name}/{key_field}"})

                    if not click.confirm("Add another key field?", default=False):
                        break

            # Add record set to metadata
            metadata["cr:recordSet"].append(record_set)

            if not click.confirm("Add another record set?", default=False):
                break

    # Save metadata with a suggested filename
    default_filename = f"{dataset_name.lower().replace(' ', '_')}_metadata.json"
    output_path = click.prompt("Output file path", default=default_filename)

    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Final success message with rich formatting
    console.print()
    console.print(
        Panel(
            f"[bold green]✅ Created Croissant metadata file at:[/] [blue]{output_path}[/]",
            title="Success",
            border_style="green",
        ),
    )

    console.print("[italic]Validate this file with:[/]")
    console.print(f"[bold yellow]biotope annotate validate --jsonld {output_path}[/]")
