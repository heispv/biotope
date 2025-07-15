"""Validation utilities for biotope metadata."""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_biotope_config(biotope_root: Path) -> Dict:
    """Load biotope configuration from .biotope/config/biotope.yaml."""
    config_path = biotope_root / ".biotope" / "config" / "biotope.yaml"
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, IOError):
        return {}


def is_metadata_annotated(metadata: Dict, config: Dict) -> Tuple[bool, List[str]]:
    """
    Check if metadata meets the minimum annotation requirements.
    
    Args:
        metadata: The metadata dictionary to validate
        config: Biotope configuration dictionary
        
    Returns:
        Tuple of (is_annotated, list_of_validation_errors)
    """
    validation_config = config.get("annotation_validation", {})
    
    # If validation is disabled, consider everything annotated
    if not validation_config.get("enabled", True):
        return True, []
    
    required_fields = validation_config.get("minimum_required_fields", [])
    field_validation = validation_config.get("field_validation", {})
    
    errors = []
    
    # Check for required fields
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
            continue
        
        # Validate field according to field_validation rules
        field_errors = _validate_field(metadata[field], field, field_validation.get(field, {}))
        errors.extend(field_errors)
    
    return len(errors) == 0, errors


def _validate_field(value: any, field_name: str, validation_rules: Dict) -> List[str]:
    """Validate a single field according to validation rules."""
    errors = []
    
    # Type validation
    expected_type = validation_rules.get("type")
    if expected_type:
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"Field '{field_name}' must be a string")
        elif expected_type == "object" and not isinstance(value, dict):
            errors.append(f"Field '{field_name}' must be an object")
        elif expected_type == "array" and not isinstance(value, list):
            errors.append(f"Field '{field_name}' must be an array")
    
    # String-specific validations
    if isinstance(value, str) and expected_type == "string":
        min_length = validation_rules.get("min_length")
        if min_length and len(value.strip()) < min_length:
            errors.append(f"Field '{field_name}' must be at least {min_length} characters")
    
    # Object-specific validations
    if isinstance(value, dict) and expected_type == "object":
        required_keys = validation_rules.get("required_keys", [])
        for key in required_keys:
            if key not in value:
                errors.append(f"Field '{field_name}' must contain key: {key}")
    
    # Array-specific validations
    if isinstance(value, list) and expected_type == "array":
        min_length = validation_rules.get("min_length")
        if min_length and len(value) < min_length:
            errors.append(f"Field '{field_name}' must contain at least {min_length} items")
    
    # Date format validation
    if field_name == "dateCreated" and isinstance(value, str):
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            errors.append(f"Field '{field_name}' must be a valid ISO date format")
    
    return errors


def get_annotation_status_for_files(biotope_root: Path, file_paths: List[str]) -> Dict[str, Tuple[bool, List[str]]]:
    """
    Get annotation status for multiple metadata files.
    
    Args:
        biotope_root: Path to biotope project root
        file_paths: List of file paths relative to biotope_root
        
    Returns:
        Dictionary mapping file paths to (is_annotated, validation_errors)
    """
    config = load_biotope_config(biotope_root)
    results = {}
    
    for file_path in file_paths:
        if not file_path.endswith('.jsonld'):
            continue
            
        metadata_file = biotope_root / file_path
        if not metadata_file.exists():
            results[file_path] = (False, ["Metadata file not found"])
            continue
        
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            is_annotated, errors = is_metadata_annotated(metadata, config)
            results[file_path] = (is_annotated, errors)
            
        except (json.JSONDecodeError, IOError) as e:
            results[file_path] = (False, [f"Error reading metadata: {str(e)}"])
    
    return results


def get_all_tracked_files(biotope_root: Path) -> List[str]:
    """Get all tracked metadata files in the biotope project."""
    datasets_dir = biotope_root / ".biotope" / "datasets"
    if not datasets_dir.exists():
        return []
    
    tracked_files = []
    for metadata_file in datasets_dir.glob("*.jsonld"):
        # Get the relative path from biotope_root
        relative_path = metadata_file.relative_to(biotope_root)
        tracked_files.append(str(relative_path))
    
    return tracked_files


def get_staged_metadata_files(biotope_root: Path) -> List[str]:
    """Get all staged metadata files using Git."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=biotope_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        staged_files = []
        for file_path in result.stdout.splitlines():
            if file_path.startswith(".biotope/datasets/") and file_path.endswith(".jsonld"):
                staged_files.append(file_path)
        
        return staged_files
        
    except subprocess.CalledProcessError:
        return [] 