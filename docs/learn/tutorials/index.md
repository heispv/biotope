# Biotope Tutorials

Welcome to the Biotope tutorials! This guide will help you understand how to
work with Biotope for metadata annotation.

## Workflow Overview

Biotope supports multiple workflows for managing your data and metadata:

### Git-Integrated Workflow (Recommended)

```mermaid
graph LR
    subgraph "biotope add workflow"
        direction TB
        A[Start] --> B[Add Files]
        B --> C[Calculate SHA256 Hash]
        C --> D[Create Basic Metadata]
        D --> E[Stage in Git]
        
        subgraph "Enhanced Metadata"
            direction TB
            E --> F[Interactive Annotation]
            F --> G[Complete Metadata]
        end
        
        G --> H[Commit Changes]
        H --> I[Share with Team]
    end
```

### Download and Annotate Workflow

```mermaid
graph LR
    subgraph "biotope get workflow"
        direction TB
        A[Start] --> B[Download File]
        B --> C[Calculate MD5 Hash]
        C --> D[Create Pre-filled Metadata]
        D --> E[Trigger Interactive Annotation]
        
        subgraph "Interactive Annotation"
            direction TB
            E --> F[Step-by-step Guide]
            F --> G[Complete Metadata]
        end
        
        G --> H[Save Metadata]
        H --> I[Validate Metadata]
        
        subgraph "Validation"
            direction TB
            I --> J[Check Schema]
            J --> K[Report Issues]
        end
    end
```

## Workflow Descriptions

### Git-Integrated Workflow

The `biotope add` command is the foundation of Git-integrated metadata management:

1. **Add Files**: Add local files to your biotope project
2. **Calculate SHA256 Hash**: Generate checksums for data integrity
3. **Create Basic Metadata**: Automatically generate initial Croissant ML metadata
4. **Stage in Git**: Prepare metadata changes for version control
5. **Enhanced Metadata**: Use `biotope annotate` to add detailed metadata
6. **Commit Changes**: Save metadata changes with Git
7. **Share with Team**: Use standard Git workflows for collaboration

### Download and Annotate Workflow

The `biotope get` command provides a streamlined way to download files and annotate them with metadata:

1. **Download File**: Downloads the specified file from a URL
2. **Calculate MD5 Hash**: Generates a unique identifier for the file
3. **Create Pre-filled Metadata**: Automatically generates initial metadata based on the file
4. **Interactive Annotation**: Guides you through completing the metadata with a step-by-step process
5. **Save Metadata**: Stores the final metadata alongside your file
6. **Validation**: Checks the metadata against the schema and reports any issues

## Getting Started

### For Local Files (Recommended)

To get started with local files, use the Git-integrated workflow:

```bash
biotope init
biotope add data/raw/experiment.csv
biotope annotate interactive --staged
biotope commit -m "Add experiment dataset"
```

### For Downloaded Files

To get started with downloaded files, use the download workflow:

```bash
biotope get https://example.com/data/file.csv
```

## Tutorials

For detailed information about each workflow, please refer to the specific tutorial pages:

- **[Adding Files](add-files.md)**: Learn how to add local files to your biotope project
- **[Downloading Files](get-files.md)**: Learn how to download and annotate files from URLs
- **[Annotating Data](annotate-omics.md)**: Learn how to create detailed metadata for your data