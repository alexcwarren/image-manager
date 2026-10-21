# image-manager

A small Python command-line utility for batch image processing.

The current CLI supports recursively converting JPEG images to PNG files within a directory.

## Current Functionality

- Convert `.jpg` / `.jpeg` images to `.png`
- Process images recursively through nested directories
- Preserve non-JPEG files
- Refuse to overwrite an existing PNG with the same filename

## Usage

Install the runtime dependency:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python image_manager.py <directory>
```

Example:

```bash
python image_manager.py ./images
```

JPEG files found in the directory and its subdirectories will be converted to PNG files.

The original JPEG is removed after a successful conversion.

If a PNG with the same filename already exists, the conversion will stop rather than overwrite the existing file.

## Exit status

- `0` — the conversion succeeded (an empty directory is a success), or `--help` was used
- `1` — the run stopped on a user-facing failure: the path is missing or not a directory, a file
cannot be read or written, a destination PNG already exists, or a JPEG cannot be decoded.
  The error message naming the affected path is written to stderr; nothing is printed to stdout on failure.

## Development

Install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the tests:

```bash
pytest -v
```

## Planned Functionality

Additional image-processing functionality already exists in the codebase but is not yet exposed through the CLI.

Planned features include:

- resizing images
- rounding image corners
- additional filename/image-processing utilities

These features should currently be considered experimental or incomplete from a user-facing perspective.

## About This Project

This is a small learning project focused on working with image files, filesystem operations, command-line interfaces, and automated testing in Python.

## License

Licensed under the MIT License. See [`LICENSE`](LICENSE).
