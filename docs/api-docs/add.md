# Biotope Add

!!! warning "Draft stage"

    Biotope is in draft stage. Functionality may be missing or incomplete.
    The API is subject to change.

The `biotope add` command adds data files to your biotope project and prepares them for metadata creation. It calculates checksums for data integrity and creates basic Croissant ML metadata files.

## Command Signature

```bash
biotope add [OPTIONS] [PATHS]...
```

## Arguments

- `PATHS`: One or more file or directory paths to add. Can be absolute or relative paths.

## Options

- `--recursive, -r`: Add directories recursively (default: False)
- `--force, -f`: Force add even if file already tracked (default: False)

## Examples

### Add a single file
```bash
biotope add data/raw/experiment.csv
```

### Add multiple files
```bash
biotope add data/raw/experiment1.csv data/raw/experiment2.csv
```

### Add directory recursively
```bash
biotope add data/raw/ --recursive
```

### Force add already tracked file
```bash
biotope add data/raw/experiment.csv --force
```

### Add files with absolute paths
```bash
biotope add /absolute/path/to/experiment.csv
```

## What It Does

1. **Validates Environment**: Checks that you're in a biotope project and Git repository
2. **Calculates Checksums**: Computes SHA256 checksums for data integrity
3. **Creates Metadata**: Generates basic Croissant ML metadata files in `.biotope/datasets/`
4. **Stages Changes**: Automatically stages metadata changes in Git
5. **Reports Results**: Shows which files were added and which were skipped

## Output

The command provides detailed feedback:

```
📁 Added data/raw/experiment.csv (SHA256: e471e5fc...)

✅ Added 1 file(s) to biotope project:
  + data/raw/experiment.csv

💡 Next steps:
  1. Run 'biotope status' to see staged files
  2. Run 'biotope annotate interactive --staged' to create metadata
  3. Run 'biotope commit -m "message"' to save changes
```

## Metadata Structure

Creates JSON-LD files in `.biotope/datasets/` with this structure:

```json
{
  "@context": {"@vocab": "https://schema.org/"},
  "@type": "Dataset",
  "name": "experiment",
  "description": "Dataset for experiment.csv",
  "distribution": [
    {
      "@type": "sc:FileObject",
      "@id": "file_e471e5fc",
      "name": "experiment.csv",
      "contentUrl": "data/raw/experiment.csv",
      "sha256": "e471e5fc1234567890abcdef...",
      "contentSize": 1024,
      "dateCreated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Error Handling

### Common Errors

- **"Not in a biotope project"**: Run `biotope init` first
- **"Not in a Git repository"**: Initialize Git with `git init`
- **"File already tracked"**: Use `--force` to override
- **"Path does not exist"**: Check the file path

### Error Messages

```
❌ Not in a biotope project. Run 'biotope init' first.
❌ Not in a Git repository. Initialize Git first with 'git init'.
⚠️  File 'data/raw/experiment.csv' already tracked (use --force to override)
⚠️  Skipping directory 'data/raw/' (use --recursive to add contents)
```

## Integration

### With Other Commands

- **`biotope status`**: See what files are staged
- **`biotope annotate`**: Create detailed metadata
- **`biotope commit`**: Save metadata changes
- **`biotope check-data`**: Verify data integrity

### Workflow Integration

```bash
# 1. Add files
biotope add data/raw/experiment.csv

# 2. Create metadata
biotope annotate interactive --staged

# 3. Commit changes
biotope commit -m "Add experiment dataset"
```

## Technical Details

### File Tracking

Files are tracked by their relative path from the biotope project root. The command handles both absolute and relative paths correctly.

### Checksum Calculation

Uses SHA256 algorithm for data integrity verification:

```python
def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()
```

### Git Integration

Automatically stages metadata changes:

```python
def _stage_git_changes(biotope_root: Path) -> None:
    """Stage .biotope/ changes in Git."""
    subprocess.run(["git", "add", ".biotope/"], cwd=biotope_root, check=True)
```

## Best Practices

1. **Use Relative Paths**: Prefer relative paths for better portability
2. **Organize Data**: Keep data files in structured directories
3. **Check Status**: Use `biotope status` to verify what was added
4. **Review Metadata**: Always review generated metadata before committing

## Limitations

- Only supports local files (not URLs)
- Requires Git repository
- Metadata is basic and should be enhanced with `biotope annotate`
- No support for symbolic links

::: biotope.commands.add 