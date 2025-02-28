"""Tests for the annotate command."""

import datetime
import getpass
import json
import os
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner

from biotope.commands.annotate import annotate, create, interactive, load, validate


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def sample_metadata_file(tmp_path):
    """Create a sample metadata file for testing."""
    metadata_path = tmp_path / "metadata.json"

    # Create a simple metadata structure for a scientific dataset
    metadata = {
        "@context": {
            "@vocab": "https://schema.org/",
            "ml": "https://ml-schema.org/",
        },
        "@type": "ml:Dataset",
        "name": "Gene Expression Dataset",
        "description": "RNA-seq data from cancer patients",
        "dataSource": "https://example.com/gene_data",
        "projectName": "Cancer Genomics",
        "contactPerson": "researcher@university.edu",
        "creationDate": "2023-01-15",
        "accessRestrictions": "Restricted to research use only",
        "fileFormat": "CSV",
        "legalObligations": "Data usage agreement required",
        "collaborationPartner": "University Medical Center",
        "ml:recordSet": [
            {
                "@type": "ml:RecordSet",
                "@id": "samples",
                "name": "samples",
                "description": "Patient samples with gene expression data",
                "ml:field": [
                    {
                        "@type": "ml:Field",
                        "name": "patient_id",
                        "description": "Unique identifier for each patient",
                    },
                    {
                        "@type": "ml:Field",
                        "name": "gene_expression",
                        "description": "Normalized gene expression values",
                    },
                ],
            },
        ],
    }

    with Path(metadata_path).open("w") as f:
        json.dump(metadata, f)

    return metadata_path


def test_create_command_with_required_fields(runner, tmp_path):
    """Test creating a new metadata file with all required scientific metadata fields."""
    output_path = tmp_path / "output.json"

    # Run the create command with all required fields
    result = runner.invoke(
        create,
        [
            "--name",
            "Single-cell RNA-seq Dataset",
            "--description",
            "Single-cell RNA sequencing data from tumor microenvironment",
            "--data-source",
            "https://example.org/scRNA-seq",
            "--contact",
            "researcher@university.edu",
            "--date",
            "2023-05-20",
            "--access-restrictions",
            "Restricted to academic use",
            "--format",
            "H5AD",
            "--legal-obligations",
            "Citation required",
            "--collaboration-partner",
            "Cancer Research Institute",
            "--output",
            str(output_path),
        ],
    )

    # Check that the command executed successfully
    assert result.exit_code == 0
    assert f"Created Croissant metadata file at {output_path}" in result.output

    # Verify the file was created
    assert os.path.exists(output_path)

    # Check the content of the file
    with Path(output_path).open() as f:
        metadata = json.load(f)

    # Check basic fields
    assert metadata["name"] == "Single-cell RNA-seq Dataset"
    assert metadata["description"] == "Single-cell RNA sequencing data from tumor microenvironment"

    # Check required scientific metadata fields
    assert metadata["dataSource"] == "https://example.org/scRNA-seq"
    assert metadata["contactPerson"] == "researcher@university.edu"
    assert metadata["creationDate"] == "2023-05-20"
    assert metadata["accessRestrictions"] == "Restricted to academic use"

    # Check optional fields
    assert metadata["fileFormat"] == "H5AD"
    assert metadata["legalObligations"] == "Citation required"
    assert metadata["collaborationPartner"] == "Cancer Research Institute"


def test_create_command_with_defaults(runner, tmp_path):
    """Test creating a new metadata file with default values for some fields."""
    output_path = tmp_path / "output.json"
    today = datetime.datetime.now(tz=datetime.timezone.utc).date().isoformat()
    username = getpass.getuser()

    # Run the create command with minimal required fields
    result = runner.invoke(
        create,
        [
            "--name",
            "Proteomics Dataset",
            "--data-source",
            "https://example.org/proteomics",
            "--access-restrictions",
            "Public",
            "--output",
            str(output_path),
        ],
    )

    # Check that the command executed successfully
    assert result.exit_code == 0

    # Check the content of the file
    with Path(output_path).open() as f:
        metadata = json.load(f)

    # Check that defaults were applied
    assert metadata["name"] == "Proteomics Dataset"
    assert metadata["description"] == ""  # Default empty string
    assert metadata["dataSource"] == "https://example.org/proteomics"
    assert metadata["contactPerson"] == username  # Default to current user
    assert metadata["creationDate"] == today  # Default to today
    assert metadata["accessRestrictions"] == "Public"

    # Optional fields should not be present
    assert "fileFormat" not in metadata
    assert "legalObligations" not in metadata
    assert "collaborationPartner" not in metadata


@mock.patch("subprocess.run")
def test_validate_command_success(mock_run, runner, sample_metadata_file):
    """Test validating a correctly formatted metadata file."""
    # Configure the mock to return a successful result
    mock_process = mock.Mock()
    mock_process.stdout = "Done"
    mock_process.stderr = ""
    mock_run.return_value = mock_process

    # Run the validate command
    result = runner.invoke(validate, ["--jsonld", str(sample_metadata_file)])

    # Check that the command executed successfully
    assert result.exit_code == 0
    assert "Validation successful!" in result.output

    # Verify that subprocess.run was called with the correct arguments
    mock_run.assert_called_once_with(
        ["mlcroissant", "validate", "--jsonld", str(sample_metadata_file)],
        capture_output=True,
        text=True,
        check=True,
    )


@mock.patch("subprocess.run")
def test_validate_command_failure(mock_run, runner, sample_metadata_file):
    """Test validating an incorrectly formatted metadata file."""
    # Configure the mock to raise an exception
    error_message = "Invalid schema: missing required field"
    mock_run.side_effect = subprocess.CalledProcessError(
        1,
        ["mlcroissant", "validate"],
        stderr=error_message,
    )

    # Run the validate command
    result = runner.invoke(validate, ["--jsonld", str(sample_metadata_file)])

    # Check that the command failed with the expected error
    assert result.exit_code == 1
    assert "Validation failed" in result.output
    assert error_message in result.output


@mock.patch("subprocess.run")
def test_load_command(mock_run, runner, sample_metadata_file):
    """Test loading records from a dataset."""
    # Configure the mock to return sample data
    sample_output = "\n".join(
        [f"Record {i + 1}: {{'patient_id': 'P{i}', 'gene_expression': [0.1, 0.2, 0.3]}}" for i in range(5)],
    )
    mock_process = mock.Mock()
    mock_process.stdout = sample_output
    mock_process.stderr = ""
    mock_run.return_value = mock_process

    # Run the load command
    result = runner.invoke(
        load,
        [
            "--jsonld",
            str(sample_metadata_file),
            "--record-set",
            "samples",
            "--num-records",
            "5",
        ],
    )

    # Check that the command executed successfully
    assert result.exit_code == 0
    assert "Loaded 5 records from record set 'samples'" in result.output

    # Verify that subprocess.run was called with the correct arguments
    mock_run.assert_called_once_with(
        [
            "mlcroissant",
            "load",
            "--jsonld",
            str(sample_metadata_file),
            "--record_set",
            "samples",
            "--num_records",
            "5",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    # Verify that the output was displayed
    assert sample_output in result.output


@mock.patch("click.prompt")
@mock.patch("click.confirm")
@mock.patch("getpass.getuser")
@mock.patch("datetime.date")
def test_interactive_command_with_scientific_fields(
    mock_date,
    mock_getuser,
    mock_confirm,
    mock_prompt,
    runner,
    tmp_path,
):
    """Test interactively creating a metadata file with scientific metadata fields."""
    mock_date.today.return_value = datetime.date(2023, 6, 15)
    mock_getuser.return_value = "researcher"

    # Configure the mocks for a typical scientific dataset creation flow
    mock_prompt.side_effect = [
        "Proteomics Dataset",  # Dataset name
        "Mass spectrometry data from protein samples",  # Dataset description
        "https://example.org/proteomics",  # Data source URL
        "Protein Analysis",  # Project name
        "dr.researcher@university.edu",  # Contact person
        "2023-06-15",  # Creation date
        "Restricted to project members",  # Access restrictions
        "mzML",  # File format
        "Data sharing agreement required",  # Legal obligations
        "Proteomics Center, University Hospital",  # Collaboration partner
        "protein_samples",  # Record set name
        "Protein samples with abundance measurements",  # Record set description
        "protein_id",  # Field name
        "Unique identifier for each protein",  # Field description
        "abundance",  # Field name
        "Normalized protein abundance",  # Field description
        str(tmp_path / "proteomics_metadata.json"),  # Output path
    ]

    # Configure confirm responses
    mock_confirm.side_effect = [True, True, True, False, False]

    # Run the interactive command
    result = runner.invoke(interactive)

    # Check that the command executed successfully
    assert result.exit_code == 0

    # Verify the expected prompts were made
    assert mock_prompt.call_count == 17
    assert mock_confirm.call_count == 5

    # Check for success message
    expected_output_path = str(tmp_path / "proteomics_metadata.json")
    assert f"Created Croissant metadata file at {expected_output_path}" in result.output

    # Verify the file was created and contains the expected content
    assert Path(expected_output_path).exists()
    with Path(expected_output_path).open() as f:
        metadata = json.load(f)

    # Check that all the scientific metadata fields are present
    assert metadata["name"] == "Proteomics Dataset"
    assert metadata["description"] == "Mass spectrometry data from protein samples"
    assert metadata["dataSource"] == "https://example.org/proteomics"
    assert metadata["projectName"] == "Protein Analysis"
    assert metadata["contactPerson"] == "dr.researcher@university.edu"
    assert metadata["creationDate"] == "2023-06-15"
    assert metadata["accessRestrictions"] == "Restricted to project members"
    assert metadata["fileFormat"] == "mzML"
    assert metadata["legalObligations"] == "Data sharing agreement required"
    assert metadata["collaborationPartner"] == "Proteomics Center, University Hospital"


def test_annotate_group(runner):
    """Test the annotate command group."""
    # Run the annotate command without subcommands to see help
    result = runner.invoke(annotate)

    # Check that the command executed successfully
    assert result.exit_code == 0

    # Verify that the help text includes all subcommands
    assert "create" in result.output
    assert "validate" in result.output
    assert "load" in result.output
    assert "interactive" in result.output

    # Check that the description mentions Croissant format
    assert "Croissant format" in result.output
