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
