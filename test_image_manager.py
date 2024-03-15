import pathlib

import pytest

import image_manager

TEST_ROOT_DIR = pathlib.Path(".test_root")
TEST_SAMPLE_DIR = pathlib.Path(f"{TEST_ROOT_DIR}/.test_sample")
TEST_DIR_STR = ".test"


@pytest.fixture(autouse=True)
def test_dir():
    # Create test_dir path
    test_dir = pathlib.Path(f"{TEST_ROOT_DIR}/{TEST_DIR_STR}")

    # Remove test_dir if it exists
    if test_dir.exists():
        cleanup(test_dir)

    # Create a new test directory
    test_dir.mkdir()

    # Copy test directory
    copy_test_directory(TEST_SAMPLE_DIR, test_dir)

    return test_dir


# TODO
def test_convert_jpg_to_png():
    pass


# TODO
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
