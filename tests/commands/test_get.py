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


@mock.patch("biotope.commands.get.download_file")
def test_get_command_skip_annotation(mock_download, runner, tmp_path, sample_file):
    from biotope.commands.get import get

    """Test get command with skip annotation flag."""
    mock_download.return_value = sample_file

    result = runner.invoke(get, ["https://example.com/test.txt", "--skip-annotation"])

    assert result.exit_code == 0
    assert "Downloading file from" in result.output
    assert "Successfully downloaded" in result.output
    assert "Starting annotation process" not in result.output


@mock.patch("biotope.commands.get.download_file")
def test_get_command_download_failure(mock_download, runner):
    from biotope.commands.get import get

    """Test get command when download fails."""
    mock_download.return_value = None

    result = runner.invoke(get, ["https://example.com/test.txt"])

    assert result.exit_code == 0  # Command should exit gracefully
    assert "Download failed" in result.output


def test_get_file_and_annotate_successful_flow(tmp_path, sample_file):
    from unittest import mock

    # Setup mocks
    with (
        mock.patch("biotope.commands.get.download_file") as mock_download,
        mock.patch("biotope.commands.get.calculate_md5") as mock_calculate_md5,
        mock.patch("biotope.commands.get.detect_file_type") as mock_detect_type,
        mock.patch("click.get_current_context") as mock_get_context,
    ):
        # Setup the context mock
        mock_context = mock.Mock()
        mock_context.invoke = mock.Mock()
        mock_get_context.return_value = mock_context

        mock_download.return_value = sample_file
        mock_calculate_md5.return_value = "test_md5"
        mock_detect_type.return_value = "text/plain"

        # Use a mock console to avoid printing
        mock_console = mock.Mock()

        # Call the logic function directly
        metadata = get_file_and_annotate(
            url="https://example.com/test.txt",
            output_dir=str(tmp_path),
            skip_annotation=False,
            console=mock_console,
        )

        # Verify all mocks were called correctly
        mock_download.assert_called_once()
        mock_calculate_md5.assert_called_once_with(sample_file)
        mock_detect_type.assert_called_once_with(sample_file)
        mock_context.invoke.assert_called_once()

        # Verify the metadata structure
        assert metadata["@type"] == "Dataset"
        assert metadata["name"] == sample_file.name
        assert metadata["encodingFormat"] == "text/plain"
        assert len(metadata["distribution"]) == 1
        assert metadata["distribution"][0]["sha256"] == "test_md5"
        assert len(metadata["cr:recordSet"]) == 1


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


def test_get_file_and_annotate_csv(test_files_dir, runner):
    """Test metadata extraction from CSV file."""
    csv_file = test_files_dir / "test_gene_expression.csv"
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL
    file_url = f"file://{csv_file.absolute()}"

    # Mock all required functions
    with (
        mock.patch("biotope.commands.get.download_file") as mock_download,
        mock.patch("biotope.commands.get.calculate_md5") as mock_md5,
        mock.patch("biotope.commands.get.detect_file_type") as mock_type,
        mock.patch("click.get_current_context") as mock_context,
    ):
        # Setup mocks
        mock_download.return_value = csv_file
        mock_md5.return_value = "test_md5"
        mock_type.return_value = "text/csv"

        # Setup context mock
        mock_ctx = mock.Mock()
        mock_ctx.invoke = mock.Mock()
        mock_context.return_value = mock_ctx

        # Call the function without skipping annotation
        metadata = get_file_and_annotate(file_url, str(output_dir), skip_annotation=False)

        # Verify metadata structure
        assert metadata is not None
        assert "@context" in metadata
        assert "@type" in metadata
        assert metadata["@type"] == "Dataset"
        assert "name" in metadata
        assert metadata["name"] == "test_gene_expression.csv"
        assert "encodingFormat" in metadata
        assert metadata["encodingFormat"] == "text/csv"
        assert "distribution" in metadata
        assert len(metadata["distribution"]) == 1

        # Verify file object metadata
        file_obj = metadata["distribution"][0]
        assert file_obj["@type"] == "sc:FileObject"
        assert "name" in file_obj
        assert "contentUrl" in file_obj
        assert "encodingFormat" in file_obj
        assert file_obj["encodingFormat"] == "text/csv"
        assert "sha256" in file_obj
        assert file_obj["sha256"] == "test_md5"

        # Verify record set
        assert "cr:recordSet" in metadata
        assert len(metadata["cr:recordSet"]) == 1
        record_set = metadata["cr:recordSet"][0]
        assert record_set["@type"] == "cr:RecordSet"
        assert record_set["name"] == "main"
        assert "cr:field" in record_set
        assert len(record_set["cr:field"]) == 1


def test_get_file_and_annotate_fasta(test_files_dir, runner):
    """Test metadata extraction from FASTA file."""
    fasta_file = test_files_dir / "test_protein_sequences.fasta"
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL
    file_url = f"file://{fasta_file.absolute()}"

    # Mock all required functions
    with (
        mock.patch("biotope.commands.get.download_file") as mock_download,
        mock.patch("biotope.commands.get.calculate_md5") as mock_md5,
        mock.patch("biotope.commands.get.detect_file_type") as mock_type,
        mock.patch("click.get_current_context") as mock_context,
    ):
        # Setup mocks
        mock_download.return_value = fasta_file
        mock_md5.return_value = "test_md5"
        mock_type.return_value = "text/x-fasta"

        # Setup context mock
        mock_ctx = mock.Mock()
        mock_ctx.invoke = mock.Mock()
        mock_context.return_value = mock_ctx

        # Call the function without skipping annotation
        metadata = get_file_and_annotate(file_url, str(output_dir), skip_annotation=False)

        # Verify metadata structure
        assert metadata is not None
        assert "@context" in metadata
        assert "@type" in metadata
        assert metadata["@type"] == "Dataset"
        assert "name" in metadata
        assert metadata["name"] == "test_protein_sequences.fasta"
        assert "encodingFormat" in metadata
        assert metadata["encodingFormat"] == "text/x-fasta"
        assert "distribution" in metadata
        assert len(metadata["distribution"]) == 1

        # Verify file object metadata
        file_obj = metadata["distribution"][0]
        assert file_obj["@type"] == "sc:FileObject"
        assert "name" in file_obj
        assert "contentUrl" in file_obj
        assert "encodingFormat" in file_obj
        assert file_obj["encodingFormat"] == "text/x-fasta"
        assert "sha256" in file_obj
        assert file_obj["sha256"] == "test_md5"

        # Verify record set
        assert "cr:recordSet" in metadata
        assert len(metadata["cr:recordSet"]) == 1
        record_set = metadata["cr:recordSet"][0]
        assert record_set["@type"] == "cr:RecordSet"
        assert record_set["name"] == "main"
        assert "cr:field" in record_set
        assert len(record_set["cr:field"]) == 1


def test_get_file_and_annotate_invalid_url(test_files_dir, runner):
    """Test handling of invalid URL."""
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Call the function with invalid URL
    metadata = get_file_and_annotate("invalid://url", str(output_dir), skip_annotation=True)

    # Verify that metadata is None for invalid URL
    assert metadata is None


def test_get_file_and_annotate_nonexistent_file(test_files_dir, runner):
    """Test handling of nonexistent file."""
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL for nonexistent file
    file_url = f"file://{test_files_dir}/nonexistent.txt"

    # Call the function
    metadata = get_file_and_annotate(file_url, str(output_dir), skip_annotation=True)

    # Verify that metadata is None for nonexistent file
    assert metadata is None


def test_get_file_and_annotate_with_annotation(test_files_dir, runner, monkeypatch):
    """Test metadata extraction with annotation process."""
    csv_file = test_files_dir / "test_gene_expression.csv"
    output_dir = test_files_dir / "downloads"
    output_dir.mkdir(exist_ok=True)

    # Create a file URL
    file_url = f"file://{csv_file.absolute()}"

    # Mock all required functions
    def mock_download_file(url, output_dir):
        return csv_file

    def mock_calculate_md5(file_path):
        return "test_md5"

    def mock_detect_file_type(file_path):
        return "text/csv"

    def mock_annotate(*args, **kwargs):
        return None

    # Create a mock command object with get_command method
    mock_command = mock.Mock()
    mock_command.get_command = mock.Mock(return_value=mock_annotate)

    # Mock click context
    mock_context = mock.Mock()
    mock_context.invoke = mock.Mock()
    monkeypatch.setattr("click.get_current_context", lambda: mock_context)

    # Mock all the required functions
    monkeypatch.setattr("biotope.commands.get.download_file", mock_download_file)
    monkeypatch.setattr("biotope.commands.get.calculate_md5", mock_calculate_md5)
    monkeypatch.setattr("biotope.commands.get.detect_file_type", mock_detect_file_type)
    monkeypatch.setattr("biotope.commands.annotate.annotate", mock_command)

    # Call the function without skipping annotation
    metadata = get_file_and_annotate(file_url, str(output_dir), skip_annotation=False)

    # Verify metadata structure
    assert metadata is not None
    assert "@context" in metadata
    assert "@type" in metadata
    assert metadata["@type"] == "Dataset"
    assert "name" in metadata
    assert metadata["name"] == "test_gene_expression.csv"
    assert "encodingFormat" in metadata
    assert metadata["encodingFormat"] == "text/csv"
    assert "distribution" in metadata
    assert len(metadata["distribution"]) == 1
