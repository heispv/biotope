"""Tests for status command annotation validation display."""

import json
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner
import os

from biotope.commands.status import status


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def biotope_project(tmp_path):
    """Create a mock biotope project structure."""
    # Create .biotope directory
    biotope_dir = tmp_path / ".biotope"
    biotope_dir.mkdir()
    
    # Create config directory
    config_dir = biotope_dir / "config"
    config_dir.mkdir()
    
    # Create datasets directory
    datasets_dir = biotope_dir / "datasets"
    datasets_dir.mkdir()
    
    return tmp_path


@pytest.fixture
def git_repo(biotope_project):
    """Create a mock Git repository."""
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        yield biotope_project


def test_status_shows_annotation_status_for_add_metadata(runner, git_repo):
    """Test that status shows incomplete annotation for biotope add metadata."""
    
    # Create biotope config with default validation
    config = {
        "annotation_validation": {
            "enabled": True,
            "minimum_required_fields": [
                "name",
                "description", 
                "creator",
                "dateCreated",
                "distribution"
            ],
            "field_validation": {
                "name": {"type": "string", "min_length": 1},
                "description": {"type": "string", "min_length": 10},
                "creator": {"type": "object", "required_keys": ["name"]},
                "dateCreated": {"type": "string", "format": "date"},
                "distribution": {"type": "array", "min_length": 1}
            }
        }
    }
    
    config_file = git_repo / ".biotope" / "config" / "biotope.yaml"
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    
    # Create metadata file like biotope add would (incomplete)
    incomplete_metadata = {
        "@context": {"@vocab": "https://schema.org/"},
        "@type": "Dataset",
        "name": "experiment3",
        "description": "Dataset for experiment3.csv",
        "distribution": [
            {
                "@type": "sc:FileObject",
                "@id": "file_e3b0c442",
                "name": "experiment3.csv",
                "contentUrl": "data/raw/experiment3.csv",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "contentSize": 0,
                "dateCreated": "2025-07-15T14:57:55.699579+00:00"
            }
        ]
    }
    
    metadata_file = git_repo / ".biotope" / "datasets" / "experiment3.jsonld"
    with open(metadata_file, "w") as f:
        json.dump(incomplete_metadata, f)
    
    # Mock Git status to show this file as tracked
    with mock.patch("biotope.utils.find_biotope_root", return_value=git_repo), \
         mock.patch("biotope.commands.status._get_git_status", return_value={
             "staged": [],
             "modified": [],
             "untracked": []
         }):
        with runner.isolated_filesystem():
            os.chdir(git_repo)
            # Run status command in the correct working directory
            result = runner.invoke(status)
            # Should show the file as unannotated (⚠️)
            assert result.exit_code == 0
            assert "experiment3" in result.output
            assert "⚠️" in result.output or "Incomplete" in result.output


def test_status_shows_annotation_status_for_complete_metadata(runner, git_repo):
    """Test that status shows complete annotation for properly annotated metadata."""
    
    # Create biotope config with default validation
    config = {
        "annotation_validation": {
            "enabled": True,
            "minimum_required_fields": [
                "name",
                "description", 
                "creator",
                "dateCreated",
                "distribution"
            ],
            "field_validation": {
                "name": {"type": "string", "min_length": 1},
                "description": {"type": "string", "min_length": 10},
                "creator": {"type": "object", "required_keys": ["name"]},
                "dateCreated": {"type": "string", "format": "date"},
                "distribution": {"type": "array", "min_length": 1}
            }
        }
    }
    
    config_file = git_repo / ".biotope" / "config" / "biotope.yaml"
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    
    # Create complete metadata file
    complete_metadata = {
        "@context": {"@vocab": "https://schema.org/"},
        "@type": "Dataset",
        "name": "experiment3",
        "description": "Dataset for experiment3.csv with complete annotation",
        "creator": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "dateCreated": "2025-07-15T14:57:55.699579+00:00",
        "distribution": [
            {
                "@type": "sc:FileObject",
                "@id": "file_e3b0c442",
                "name": "experiment3.csv",
                "contentUrl": "data/raw/experiment3.csv",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "contentSize": 0,
                "dateCreated": "2025-07-15T14:57:55.699579+00:00"
            }
        ]
    }
    
    metadata_file = git_repo / ".biotope" / "datasets" / "experiment3.jsonld"
    with open(metadata_file, "w") as f:
        json.dump(complete_metadata, f)
    
    # Mock Git status to show this file as tracked
    with mock.patch("biotope.utils.find_biotope_root", return_value=git_repo), \
         mock.patch("biotope.commands.status._get_git_status", return_value={
             "staged": [],
             "modified": [],
             "untracked": []
         }):
        with runner.isolated_filesystem():
            os.chdir(git_repo)
            # Run status command in the correct working directory
            result = runner.invoke(status)
            # Should show the file as annotated (✅)
            assert result.exit_code == 0
            assert "experiment3" in result.output
            assert "✅" in result.output or "Complete" in result.output 