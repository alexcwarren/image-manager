"""Check Path

This script contains functionality to check path validity.

This file can also be imported as a module and contains the following function:

    * raise_if_invalid_path
"""


import pathlib


def raise_if_invalid_path(path: pathlib.Path) -> None:
    """Confirm path is a valid directory or file.

    Raises FileNotFoundError or NotADirectoryError.
    """

    if not (path.is_file() or path.is_dir()):
        if not path.is_file():
            raise FileNotFoundError(
                f"path provided is not a file: '{path.absolute()}'"
            )
        if not path.is_dir():
            raise NotADirectoryError(
                f"path provided is not a directory: '{path.absolute()}'"
            )
