"""Tests for the get command."""

import hashlib
from unittest import mock

import pytest
import requests
from click.testing import CliRunner

from biotope.commands.get import calculate_md5, detect_file_type, download_file, get_file_and_annotate


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample file for testing."""
    file_path = tmp_path / "test.txt"
    content = "This is a test file content"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def mock_response():
    """Create a mock response for requests.get."""
    mock_resp = mock.Mock()
    mock_resp.headers = {"content-length": "100"}
    mock_resp.iter_content.return_value = [b"test content"]
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_calculate_md5(sample_file):
    """Test MD5 hash calculation."""
    expected_hash = hashlib.md5(sample_file.read_bytes()).hexdigest()
    assert calculate_md5(sample_file) == expected_hash


def test_detect_file_type(sample_file):
    """Test file type detection."""
    # Test with a text file
    assert detect_file_type(sample_file) == "text/plain"

    # Test with unknown extension
    unknown_file = sample_file.parent / "test.unknown"
    unknown_file.touch()
    assert detect_file_type(unknown_file) == "unknown"


@mock.patch("requests.get")
def test_download_file_success(mock_get, tmp_path, mock_response):
    """Test successful file download."""
    mock_get.return_value = mock_response
    url = "https://example.com/test.txt"
    output_dir = tmp_path / "downloads"
    output_dir.mkdir()

    result = download_file(url, output_dir)
    assert result is not None
    assert result.exists()
    assert result.name == "test.txt"
    assert result.parent == output_dir

    mock_get.assert_called_once_with(url, stream=True, timeout=10)


@mock.patch("requests.get")
def test_download_file_failure(mock_get, tmp_path):
    """Test file download failure."""
    mock_get.side_effect = requests.RequestException("Download failed")
    url = "https://example.com/test.txt"
    output_dir = tmp_path / "downloads"
    output_dir.mkdir()

    result = download_file(url, output_dir)
    assert result is None


@mock.patch("biotope.commands.get.requests.get")
def test_get_command_download_failure(mock_get, runner):
    """Test get command when download fails."""
    from biotope.commands.get import get

    # Mock requests.get to raise an HTTPError
    mock_get.side_effect = requests.exceptions.HTTPError(
        "404 Client Error: Not Found for url: https://example.com/test.txt",
    )

    result = runner.invoke(get, ["https://example.com/test.txt"])

    assert result.exit_code == 0  # Command should exit gracefully
    assert "Error downloading file" in result.output


def test_get_file_and_annotate_successful_flow(tmp_path, sample_file):
    """Test successful file download and annotation flow."""
    from unittest import mock

    # Setup mocks
    with (
        mock.patch("biotope.commands.get.requests.get") as mock_get,
        mock.patch("click.get_current_context") as mock_get_context,
    ):
        # Setup the context mock
        mock_context = mock.Mock()
        mock_context.invoke = mock.Mock()
        mock_get_context.return_value = mock_context

        # Setup mock response
        mock_response = mock.Mock()
        mock_response.headers = {}
        mock_response.iter_content.return_value = [b"test content"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the function
        get_file_and_annotate(
            url="https://example.com/test.txt",
            output_dir=str(tmp_path),
        )

        # Verify mocks were called correctly
        mock_get.assert_called_once_with("https://example.com/test.txt", stream=True)
        mock_context.invoke.assert_called_once()


@pytest.fixture
def test_files_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    csv_content = """GeneID,Sample1,Sample2,Sample3,Sample4,Sample5
BRCA1,12.5,15.2,8.7,10.3,14.1
TP53,9.8,11.4,7.2,8.9,10.5
EGFR,14.2,13.8,15.1,12.7,13.9"""

    fasta_content = """>BRCA1_HUMAN BRCA1, early onset breast cancer 1
MSTESMNRVAVGDMLRLLHEVEGVRTLRQRVKDSQPLGDFYDRVRKELQLLRQRMKKT
FQLVDFSRRLEDLLMKLLNQKAKLPGLLNTDPRLLEVLQDMGHARALAVLLTAGDGLG"""

    # Write files
    csv_file = tmp_path / "test_gene_expression.csv"
    fasta_file = tmp_path / "test_protein_sequences.fasta"

    csv_file.write_text(csv_content)
    fasta_file.write_text(fasta_content)

    return tmp_path


@mock.patch("biotope.commands.get.requests.get")
def test_get_file_and_annotate_csv(mock_get, test_files_dir, runner):
    """Test metadata extraction from CSV file."""
    csv_file = test_files_dir / "test_gene_expression.csv"
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL
    file_url = f"file://{csv_file.absolute()}"

    # Setup mock response
    mock_response = mock.Mock()
    mock_response.headers = {}
    mock_response.iter_content.return_value = [csv_file.read_bytes()]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Mock click context
    with mock.patch("click.get_current_context") as mock_context:
        mock_ctx = mock.Mock()
        mock_ctx.invoke = mock.Mock()
        mock_context.return_value = mock_ctx

        # Call the function
        get_file_and_annotate(file_url, str(output_dir))

        # Verify mocks were called correctly
        mock_get.assert_called_once_with(file_url, stream=True)
        mock_ctx.invoke.assert_called_once()


@mock.patch("biotope.commands.get.requests.get")
def test_get_file_and_annotate_fasta(mock_get, test_files_dir, runner):
    """Test metadata extraction from FASTA file."""
    fasta_file = test_files_dir / "test_protein_sequences.fasta"
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL
    file_url = f"file://{fasta_file.absolute()}"

    # Setup mock response
    mock_response = mock.Mock()
    mock_response.headers = {}
    mock_response.iter_content.return_value = [fasta_file.read_bytes()]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Mock click context
    with mock.patch("click.get_current_context") as mock_context:
        mock_ctx = mock.Mock()
        mock_ctx.invoke = mock.Mock()
        mock_context.return_value = mock_ctx

        # Call the function
        get_file_and_annotate(file_url, str(output_dir))

        # Verify mocks were called correctly
        mock_get.assert_called_once_with(file_url, stream=True)
        mock_ctx.invoke.assert_called_once()


@mock.patch("biotope.commands.get.requests.get")
def test_get_file_and_annotate_invalid_url(mock_get, test_files_dir, runner):
    """Test handling of invalid URL."""
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Mock requests.get to raise an error
    mock_get.side_effect = requests.exceptions.RequestException("Invalid URL")

    # Call the function with invalid URL
    get_file_and_annotate("invalid://url", str(output_dir))

    # Verify error was handled
    mock_get.assert_called_once_with("invalid://url", stream=True)


@mock.patch("biotope.commands.get.requests.get")
def test_get_file_and_annotate_nonexistent_file(mock_get, test_files_dir, runner):
    """Test handling of nonexistent file."""
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL for nonexistent file
    file_url = f"file://{test_files_dir}/nonexistent.txt"

    # Mock requests.get to raise an error
    mock_get.side_effect = requests.exceptions.RequestException("File not found")

    # Call the function
    get_file_and_annotate(file_url, str(output_dir))

    # Verify error was handled
    mock_get.assert_called_once_with(file_url, stream=True)


@mock.patch("biotope.commands.get.requests.get")
def test_get_file_and_annotate_with_annotation(mock_get, test_files_dir, runner):
    """Test metadata extraction with annotation process."""
    csv_file = test_files_dir / "test_gene_expression.csv"
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL
    file_url = f"file://{csv_file.absolute()}"

    # Setup mock response
    mock_response = mock.Mock()
    mock_response.headers = {}
    mock_response.iter_content.return_value = [csv_file.read_bytes()]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Mock click context
    with mock.patch("click.get_current_context") as mock_context:
        mock_ctx = mock.Mock()
        mock_ctx.invoke = mock.Mock()
        mock_context.return_value = mock_ctx

        # Call the function
        get_file_and_annotate(file_url, str(output_dir))

        # Verify mocks were called correctly
        mock_get.assert_called_once_with(file_url, stream=True)
        mock_ctx.invoke.assert_called_once()
