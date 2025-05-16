# Downloading and Annotating Files with `get`

The `get` command in Biotope provides a convenient way to download files and
automatically start the annotation process. It combines file downloading
capabilities with Biotope's powerful annotation system. Check also the
[annotation tutorial](annotate-omics.md) for more information on how to annotate
your data.

## Basic Usage

The simplest way to use the `get` command is to provide a URL:

```bash
biotope get https://raw.githubusercontent.com/biocypher/biotope/refs/heads/main/tests/example_gene_expression.csv
```

or 

```bash
biotope get https://raw.githubusercontent.com/biocypher/biotope/refs/heads/main/tests/example_protein_sequences.fasta
```

This will:
1. Download the file to the `downloads` directory
2. Calculate its MD5 hash
3. Detect the file type
4. Create pre-filled metadata
5. Automatically start the interactive annotation process

## Command Options

The `get` command supports the following option:

```bash
biotope get [OPTIONS] URL
```

### Available Options

- `--output-dir`, `-o`: Specify a custom directory for downloaded files
  ```bash
  biotope get https://example.com/data/file.txt --output-dir /path/to/dir
  ```

## Automatic Metadata Generation

When downloading a file, the `get` command automatically generates initial
metadata in Croissant ML format. This includes:

- File identification (name, path, MD5 hash)
- File type detection
- Source URL
- Creator information
- Creation date
- Basic record set structure

The generated metadata follows the schema.org and Croissant ML standards, making
it compatible with the rest of the Biotope ecosystem.

### Example Generated Metadata

```json
{
    "name": "Dataset_file.txt",
    "description": "Dataset containing file downloaded from https://example.com/data/file.txt",
    "url": "https://example.com/data/file.txt",
    "creator": {
        "@type": "Person",
        "name": "username"
    },
    "dateCreated": "2024-03-21",
    "distribution": [
        {
            "@type": "sc:FileObject",
            "@id": "file_md5hash",
            "name": "file.txt",
            "contentUrl": "https://example.com/data/file.txt",
            "encodingFormat": "text/plain",
            "sha256": "md5hash"
        }
    ]
}
```

## Interactive Annotation

After downloading, the command automatically starts the interactive annotation
process. You can:

1. Review and modify the pre-filled metadata
2. Add additional fields and record sets
3. Specify access restrictions and legal obligations
4. Add collaboration information

The interactive process follows the same workflow as the `annotate` command, but
with pre-filled information to save time.

## Error Handling

The command handles various error cases gracefully:

- Download failures: Displays an error message and exits
- Annotation failures: Shows the error and allows you to retry
- Invalid URLs: Provides clear error messages
- File system issues: Handles permission problems and disk space issues

## Best Practices

1. **Use Meaningful URLs**: When possible, use URLs that reflect the content or purpose of the file
2. **Organize Downloads**: Use the `--output-dir` option to keep downloaded files organized
3. **Review Metadata**: Always review the pre-filled metadata before saving

## Examples

### Download and Annotate a CSV File

```bash
biotope get https://example.com/data/expression.csv
```

### Download to a Specific Directory

```bash
biotope get https://example.com/data/expression.csv --output-dir ./data/raw
```

## Integration with Other Commands

The `get` command integrates well with other Biotope commands:

- Use `biotope annotate validate` to validate the generated metadata
- Use `biotope read` to read the downloaded and annotated files
- Use `biotope chat` to ask questions about the downloaded data

## Troubleshooting

### Common Issues

1. **Download Fails**
   - Check your internet connection
   - Verify the URL is accessible
   - Ensure you have write permissions in the output directory

2. **Annotation Fails**
   - Check if the file is corrupted
   - Verify you have sufficient disk space
   - Ensure you have the required permissions

3. **Metadata Issues**
   - Use `biotope annotate validate` to check metadata validity
   - Review the pre-filled metadata carefully
   - Make sure all required fields are filled

### Getting Help

For additional help, use:

```bash
biotope get --help
```

This will show all available options and usage examples. 