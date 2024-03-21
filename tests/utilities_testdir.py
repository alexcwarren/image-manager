import pathlib


def copy_test_directory(source_dir: pathlib.Path, target_dir: pathlib.Path):
    """Copy contents of source directory into target directory."""

    for path_item in source_dir.iterdir():
        if path_item.is_file():
            copy = pathlib.Path(f"{target_dir}/{path_item.name}")
            copy.write_bytes(path_item.read_bytes())


def cleanup(directory: pathlib.Path):
    """Delete the temporary test directory."""

    remove_dir_contents(directory)
    directory.rmdir()


def remove_dir_contents(directory: pathlib.Path):
    """Remove all contents (files/directories) in given directory."""

    for path_item in directory.iterdir():
        if path_item.is_dir():
            remove_dir_contents(path_item)
            path_item.rmdir()
        else:
            path_item.unlink()
