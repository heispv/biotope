# Biotope

*CLI integration for BioCypher ecosystem packages*

!!! info "Biotope is still under development"

    Biotope is still under development and the API is subject to change.

## Metadata annotation using Croissant, short guide

The `biotope` package features a metadata annotation assistant using the
recently introduced
[Croissant](https://research.google/blog/croissant-a-metadata-format-for-ml-ready-datasets/)
schema. It is available as the `biotope annotate` module. Usage:

```
pip install biotope
biotope annotate interactive
```

After creation, `biotope` can also be used to validate the JSON-LD (CAVE: being
a prototype, biotope does not yet implement all croissant fields):

```
biotope annotate validate –jsonld <file_name.json>
```

`biotope` also has the method `biotope annotate create` to create metadata files
from CLI parameters (no interactive mode) and `biotope annotate load` to load an
existing record (the use of this is not well-defined yet). Obvious improvements
would be to integrate file download (something like `biotope annotate get`) with
automatic annotation functionalities, and the integration of LLMs for the
further automation of metadata annotations from file contents (using the
`biochatter` module of `biotope`).

Unit tests to inform about further functions and details can be found at
https://github.com/biocypher/biotope/blob/main/tests/commands/test_annotate.py

## Copyright

- Copyright © 2025 Sebastian Lobentanzer.
- Free software distributed under the [MIT License](../LICENSE).
