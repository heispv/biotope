# Git Integration for Developers

This document explains the technical implementation of biotope's Git-on-Top strategy for metadata version control.

## Architecture Overview

Biotope implements a **Git-on-Top** strategy where all version control operations delegate to Git via `subprocess.run()` calls. No custom version control is implemented.

### Key Principles

1. **Git Wrapper Pattern**: All biotope commands wrap Git operations with metadata-specific logic
2. **No Custom Version Control**: Zero custom commit history, branching, or remote handling
3. **Separation of Concerns**: Data files in `data/`, metadata in `.biotope/datasets/`
4. **Croissant ML Integration**: Metadata follows Croissant ML standard with validation

### Project Structure

```
your-project/
├── .git/                  # Git repository (handled by Git)
├── .biotope/              # Git-tracked metadata
│   ├── datasets/          # Croissant ML JSON-LD files
│   ├── config/            # Biotope configuration
│   ├── workflows/         # Bioinformatics workflows
│   └── logs/              # Command execution logs
├── data/                  # Data files (not in Git)
│   ├── raw/
│   └── processed/
├── config/                # User configuration
├── schemas/               # Knowledge schemas
└── outputs/               # Generated outputs
```

## Implementation Details

### Core Commands

#### `biotope init` (`biotope/commands/init.py`)

```python
def _init_git_repo(directory: Path) -> None:
    """Initialize a Git repository in the directory."""
    subprocess.run(["git", "init"], cwd=directory, check=True)
    subprocess.run(["git", "add", "."], cwd=directory, check=True)
    subprocess.run(["git", "commit", "-m", "Initial biotope project setup"], cwd=directory, check=True)
```

- Creates `.biotope/` directory structure
- Initializes Git repository with `subprocess.run(["git", "init"])`
- Creates initial commit with project setup

#### `biotope commit` (`biotope/commands/commit.py`)

```python
def _create_git_commit(biotope_root: Path, message: str, author: Optional[str], amend: bool) -> Optional[str]:
    """Create a Git commit for .biotope/ changes."""
    cmd = ["git", "commit"]
    if amend:
        cmd.append("--amend")
    if author:
        cmd.extend(["--author", author])
    cmd.extend(["-m", message])
    
    result = subprocess.run(cmd, cwd=biotope_root, capture_output=True, text=True, check=True)
    # Extract commit hash from output
```

- Validates Croissant ML metadata before committing
- Stages `.biotope/` directory with `git add .biotope/`
- Delegates actual commit to Git via `subprocess.run()`
- Supports standard Git options (`--amend`, `--author`)

#### `biotope status` (`biotope/commands/status.py`)

```python
def _get_git_status(biotope_root: Path, biotope_only: bool) -> Dict[str, List]:
    """Get Git status for .biotope/ directory."""
    cmd = ["git", "status", "--porcelain"]
    if biotope_only:
        cmd.append(".biotope/")
    
    result = subprocess.run(cmd, cwd=biotope_root, capture_output=True, text=True, check=True)
    # Parse Git's porcelain output format
```

- Uses `git status --porcelain` for machine-readable output
- Parses Git's status format (A, M, D, ??)
- Focuses on `.biotope/` directory changes

#### `biotope log` (`biotope/commands/log.py`)

```python
def _get_git_log(biotope_root: Path, max_count: Optional[int] = None, since: Optional[str] = None, author: Optional[str] = None, biotope_only: bool = False) -> List[Dict]:
    """Get Git log with optional filtering."""
    cmd = ["git", "log", "--pretty=format:%H|%an|%ad|%s", "--date=short"]
    if biotope_only:
        cmd.append("--")
        cmd.append(".biotope/")
    
    result = subprocess.run(cmd, cwd=biotope_root, capture_output=True, text=True, check=True)
    # Parse commit lines: hash|author|date|message
```

- Uses `git log` with custom format for parsing
- Supports all standard Git log options
- Filters for `.biotope/` directory with `-- .biotope/`

#### `biotope push` / `biotope pull` (`biotope/commands/push.py`, `biotope/commands/pull.py`)

```python
def _push_changes(biotope_root: Path, remote: str, branch: str, force: bool) -> bool:
    """Push changes to remote repository."""
    cmd = ["git", "push"]
    if force:
        cmd.append("--force")
    cmd.extend([remote, branch])
    
    result = subprocess.run(cmd, cwd=biotope_root, capture_output=True, text=True, check=True)
    return True
```

- Direct delegation to `git push` and `git pull`
- Supports standard Git options (`--force`, `--rebase`)
- No custom remote handling

### Supporting Commands

#### `biotope add` (`biotope/commands/add.py`)

```python
def _stage_git_changes(biotope_root: Path) -> None:
    """Stage .biotope/ changes in Git."""
    subprocess.run(["git", "add", ".biotope/"], cwd=biotope_root, check=True)
```

- Creates Croissant ML metadata files in `.biotope/datasets/`
- Calculates SHA256 checksums for data integrity
- Stages changes with `git add .biotope/`

#### `biotope check-data` (`biotope/commands/check_data.py`)

```python
def _get_recorded_checksum(file_path: Path, biotope_root: Path) -> Optional[str]:
    """Get the recorded checksum for a file."""
    datasets_dir = biotope_root / ".biotope" / "datasets"
    for dataset_file in datasets_dir.glob("*.jsonld"):
        with open(dataset_file) as f:
            metadata = json.load(f)
            for distribution in metadata.get("distribution", []):
                if distribution.get("@type") == "sc:FileObject":
                    content_url = distribution.get("contentUrl")
                    if content_url and (biotope_root / content_url) == file_path:
                        return distribution.get("sha256")
```

- Reads checksums from Croissant ML metadata files
- Validates data integrity against recorded checksums
- No version control functionality

## Git Integration Patterns

### Common Helper Functions

All commands use these shared helper functions:

```python
def _is_git_repo(directory: Path) -> bool:
    """Check if directory is a Git repository."""
    try:
        result = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=directory, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def find_biotope_root() -> Optional[Path]:
    """Find the biotope project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".biotope").exists():
            return current
        current = current.parent
    return None
```

### Error Handling

All commands follow consistent error handling:

```python
try:
    result = subprocess.run(cmd, cwd=biotope_root, capture_output=True, text=True, check=True)
    return result.stdout.strip()
except subprocess.CalledProcessError as e:
    click.echo(f"❌ Git error: {e}")
    if e.stderr:
        click.echo(f"Error details: {e.stderr}")
    return None
```

### Metadata Validation

Before committing, metadata is validated:

```python
def _validate_metadata_files(biotope_root: Path) -> bool:
    """Validate all Croissant ML files in .biotope/datasets/."""
    datasets_dir = biotope_root / ".biotope" / "datasets"
    for dataset_file in datasets_dir.glob("*.jsonld"):
        with open(dataset_file) as f:
            metadata = json.load(f)
            # Basic validation - check required fields
            if not metadata.get("@type") == "Dataset":
                click.echo(f"⚠️  Warning: {dataset_file.name} missing @type: Dataset")
```

## Croissant ML Integration

### Metadata Structure

All metadata follows Croissant ML standard:

```json
{
  "@context": {"@vocab": "https://schema.org/"},
  "@type": "Dataset",
  "name": "experiment-dataset",
  "description": "RNA-seq experiment data",
  "distribution": [
    {
      "@type": "sc:FileObject",
      "@id": "file_abc123",
      "name": "experiment.csv",
      "contentUrl": "data/raw/experiment.csv",
      "sha256": "abc123...",
      "contentSize": 1024
    }
  ]
}
```

### Data Integrity

- SHA256 checksums embedded in metadata
- Automatic validation before commits
- Data integrity checking via `biotope check-data`

## Testing

### Test Structure

Tests verify Git integration without mocking Git:

```python
def test_commit_success(self, runner, biotope_project):
    """Test successful commit."""
    with patch("biotope.commands.commit.find_biotope_root", return_value=biotope_project):
        # Create a change
        with open(biotope_project / ".biotope" / "datasets" / "new.jsonld", "w") as f:
            json.dump({"name": "new-dataset"}, f)
        
        result = runner.invoke(commit, ["-m", "Add new dataset"])
        assert result.exit_code == 0
        assert "Commit" in result.output
```

### Git Command Testing

Tests use actual Git commands:

```python
# Initialize Git repository
subprocess.run(["git", "init"], cwd=tmp_path, check=True)
subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, check=True)
```

## Configuration

### Biotope Configuration

`.biotope/config/biotope.yaml`:

```yaml
version: "1.0"
croissant_schema_version: "1.0"
default_metadata_template: "scientific"
data_storage:
  type: "local"
  path: "data"
checksum_algorithm: "sha256"
auto_stage: true
commit_message_template: "Update metadata: {description}"
```

### Git Configuration

Standard Git configuration applies - no biotope-specific Git config.

## Security Considerations

- No custom version control reduces attack surface
- Git's battle-tested security model applies
- Checksums provide data integrity verification
- Metadata validation prevents malformed commits

## Performance

- Git operations are delegated to native Git binary
- No custom parsing or storage overhead
- Metadata files are small JSON-LD files
- Checksum calculation only on file changes

## Future Enhancements

Planned improvements while maintaining Git-on-Top:

- Enhanced Croissant ML validation
- Metadata conflict resolution tools
- Integration with external metadata repositories
- Workflow automation features

## Conclusion

The Git-on-Top implementation provides:

- **Reliability**: Battle-tested Git infrastructure
- **Simplicity**: No custom version control complexity
- **Familiarity**: Standard Git workflows and tools
- **Maintainability**: Minimal custom code to maintain
- **Performance**: Native Git performance

This approach eliminates the need for custom version control while providing robust metadata management capabilities. 

# Developer & Admin Guide: Annotation Validation

This document describes the internals and configuration of the annotation validation system in Biotope (git-on-top mode).

## Configuration Structure

Annotation validation is configured in `.biotope/config/biotope.yaml` under the `annotation_validation` key:

```yaml
annotation_validation:
  enabled: true
  minimum_required_fields:
    - name
    - description
    - creator
    - dateCreated
    - distribution
  field_validation:
    name:
      type: string
      min_length: 1
    description:
      type: string
      min_length: 10
    creator:
      type: object
      required_keys: [name]
    dateCreated:
      type: string
      format: date
    distribution:
      type: array
      min_length: 1
```

- **enabled**: Toggle validation on/off.
- **minimum_required_fields**: List of fields that must be present in each metadata file.
- **field_validation**: Per-field validation rules (type, min_length, required_keys, etc).

## Validation Logic

Validation is implemented in `biotope/validation.py`:
- `is_metadata_annotated(metadata, config)` checks if a metadata dict meets requirements.
- `_validate_field(value, field_name, validation_rules)` applies per-field rules.
- `get_annotation_status_for_files(biotope_root, file_paths)` returns annotation status for a list of files.

The system supports:
- Type checks (`string`, `object`, `array`)
- Minimum length for strings/arrays
- Required keys for objects
- ISO date format for date fields

## Extending Validation

To add new validation rules:
- Update the `field_validation` structure in the config (via CLI or manually).
- Extend `_validate_field` in `biotope/validation.py` to support new rule types.
- Add tests for new rules in `tests/commands/test_annotate.py` or a new test file.

## Status Command Integration

- The status command (`biotope/commands/status.py`) uses `get_annotation_status_for_files` to display annotation status for both staged and tracked metadata files.
- The summary counts annotated/unannotated datasets for quick project health assessment.

## Best Practices

- Set clear, project-appropriate requirements for annotation fields.
- Use the CLI (`biotope config set-validation`, etc) to manage requirements for reproducibility.
- Encourage users to check `biotope status` regularly to ensure all datasets are properly annotated before committing.
- For advanced validation (e.g., regex, cross-field checks), extend the validation module and document new rules for your team.

## Code References
- `biotope/validation.py`: Validation logic
- `biotope/commands/status.py`: Status reporting
- `biotope/commands/config.py`: Admin CLI for validation
- `docs/git-integration.md`: User-facing documentation

For questions or contributions, see the [CONTRIBUTING.md](../CONTRIBUTING.md). 