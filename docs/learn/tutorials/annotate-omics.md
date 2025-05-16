
The `biotope annotate` module provides tools for creating and managing metadata annotations using the Croissant ML schema. This document provides detailed examples and instructions for working with different layers of Croissant ML.

## Installation

```bash
pip install biotope
```

## Basic Usage

The annotation module can be used in several ways:

```bash
# Interactive mode
biotope annotate interactive

# Create metadata from CLI parameters
biotope annotate create

# Validate existing metadata
biotope annotate validate --jsonld <file_name.json>

# Load existing record
biotope annotate load
```

## Croissant ML Layers

Croissant ML organizes metadata in several layers, each serving a specific purpose in describing your dataset.

### 1. Dataset Layer

The dataset layer provides high-level information about your entire dataset.

Example:
```json
{
  "@type": "sc:Dataset",
  "name": "Example Dataset",
  "description": "A sample dataset for demonstration",
  "license": "MIT",
  "version": "1.0.0",
  "datePublished": "2024-03-20",
  "creator": {
    "@type": "Person",
    "name": "John Doe"
  }
}
```

### 2. Distribution Layer

The distribution layer describes how the dataset is distributed and accessed.

Example:
```json
{
  "@type": "sc:DataDownload",
  "name": "Dataset Distribution",
  "contentUrl": "https://example.com/dataset.zip",
  "encodingFormat": "application/zip",
  "contentSize": "1.2GB",
  "sha256": "abc123..."
}
```

### 3. Record Set Layer

The record set layer defines the structure of your data records.

Example:
```json
{
  "@type": "sc:RecordSet",
  "name": "Main Records",
  "description": "Primary data records",
  "field": [
    {
      "@type": "sc:Field",
      "name": "id",
      "description": "Unique identifier",
      "dataType": "string"
    },
    {
      "@type": "sc:Field",
      "name": "value",
      "description": "Numerical value",
      "dataType": "float"
    }
  ]
}
```

### 4. Field Layer

The field layer provides detailed information about individual data fields.

Example:
```json
{
  "@type": "sc:Field",
  "name": "temperature",
  "description": "Temperature measurement in Celsius",
  "dataType": "float",
  "unit": "celsius",
  "minimum": -273.15,
  "maximum": 100.0
}
```

## Best Practices

1. **Completeness**: Always provide as much metadata as possible for each layer
2. **Consistency**: Use consistent naming conventions and data types
3. **Validation**: Regularly validate your metadata using `biotope annotate validate`
4. **Versioning**: Include version information for both the dataset and metadata

## Common Use Cases

### Creating a New Dataset Annotation

1. Start with the interactive mode:
```bash
biotope annotate interactive
```

2. Follow the prompts to enter:
   - Dataset information (name, description, license)
   - Distribution details (format, size, URL)
   - Record structure (fields, data types)
   - Field-specific metadata (units, ranges, descriptions)

### Validating Existing Annotations

```bash
biotope annotate validate --jsonld my_dataset.json
```

This will check your metadata against the Croissant ML schema and report any issues.

## Future Improvements

The following features are planned for future releases:
- Automatic metadata extraction from file contents
- Integration with LLMs for automated annotation
- File download and automatic annotation
- Enhanced validation capabilities
- Support for additional Croissant ML fields

## Related Resources

- [Croissant ML Documentation](https://research.google/blog/croissant-a-metadata-format-for-ml-ready-datasets/)
- [BioCypher Documentation](https://biocypher.org)
- [Unit Tests](https://github.com/biocypher/biotope/blob/main/tests/commands/test_annotate.py) 
