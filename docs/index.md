# Biotope

*CLI integration for BioCypher ecosystem packages*

!!! info "Biotope is still under development"

    Biotope is still under development and the API is subject to change.
    The package is currently only meant for developer use and prototyping.

The *Biotope* CLI integration is our attempt to integrate BioCypher ecosystem
packages into an accessible suite for scientific knowledge management. We are
first approaching the project from a CLI perspective, as this is the most basic
technology for prototyping automated workflows. We aim to extend this towards
other user-interfaces, such as web apps, in the future.

*Biotope* contains various modules for different tasks, some of which are
straightfoward applications of existing BioCypher packages, while others
are prototypes for new features. See more information in the API documentation.

- `biotope init`: Initialize a new project in the BioCypher suite
- `biotope build`: Build a BioCypher knowledge representation
- `biotope chat`: Chat with a BioCypher project (BioChatter)
- `biotope read`: Extract information from unstructured modalities (BioGather)
- `biotope view`: Use visual analysis tools to interpret your data and metadata
- `biotope get`: Download files and automatically start annotation
- `biotope annotate`: Annotate your data with consistent metadata in Croissant ML

## Git Integration for Metadata Version Control

Biotope uses a **Git-on-Top** strategy for metadata version control, providing:

- **Version control** for all metadata changes using Git
- **Collaboration** through standard Git workflows
- **Data integrity** through checksum verification
- **Familiar tooling** - all Git tools work seamlessly

### Core Git-Integrated Commands

- `biotope add`: Stage data files for metadata creation
- `biotope status`: Show current project status
- `biotope commit`: Commit metadata changes using Git
- `biotope log`: View commit history
- `biotope push/pull`: Share metadata with remote repositories
- `biotope check-data`: Verify data integrity against checksums

### Basic Workflow

```bash
# Initialize project (with Git)
biotope init

# Add data files
biotope add data/raw/experiment.csv

# Create metadata
biotope annotate interactive --staged

# Commit changes
biotope commit -m "Add experiment dataset"

# View history
biotope log --oneline
```

### Documentation

- **[Git Integration for Users](git-integration.md)**: Learn how to use biotope's Git integration, leveraging your existing Git knowledge
- **[Git Integration for Developers](git-integration-dev.md)**: Understand the technical implementation and architecture

## Metadata annotation using Croissant, short guide

The `biotope` package features a metadata annotation assistant using the
recently introduced
[Croissant](https://research.google/blog/croissant-a-metadata-format-for-ml-ready-datasets/)
schema. It is available as the `biotope annotate` module. Usage:

```
pip install biotope
biotope annotate interactive
```

You can also use the `biotope get` command to download files and automatically start the annotation process:

```
biotope get https://example.com/data/file.txt
```

This will download the file and pre-fill metadata fields based on the file's properties.

After creation, `biotope` can also be used to validate the JSON-LD (CAVE: being
a prototype, biotope does not yet implement all croissant fields):

```
biotope annotate validate –jsonld <file_name.json>
```

`biotope` also has the method `biotope annotate create` to create metadata files
from CLI parameters (no interactive mode) and `biotope annotate load` to load an
existing record (the use of this is not well-defined yet). Further improvements
would be the integration of LLMs for the automation of metadata annotations from
file contents (using the `biochatter` module of `biotope`).

Unit tests to inform about further functions and details can be found at
https://github.com/biocypher/biotope/blob/main/tests/commands/test_annotate.py
and https://github.com/biocypher/biotope/blob/main/tests/commands/test_get.py

## Copyright

- Copyright © 2025 Sebastian Lobentanzer.
- Free software distributed under the MIT License.
