"""Convert to PNG

This script converts all JPEG image files to PNG in the given directory.

This file can also be imported as a module and contains the following functions:

    * convert_jpgs_to_pngs
    * is_jpg
"""

import argparse
import pathlib
import sys

import check_path
from PIL import Image as PillowImage


def convert_jpgs_to_pngs(path: pathlib.Path, keep_originals: bool = False) -> None:
    """Convert all JPEG images to PNG contained in given directory path."""

    check_path.raise_if_invalid_path(path)

    # Recursively iterate through contents of directory
    for path_item in path.iterdir():
        if path_item.is_dir():
            convert_jpgs_to_pngs(path_item)
        elif path_item.is_file() and is_jpg(path_item):
            # Create new filepath with 'png' extension
            new_filepath = pathlib.Path(f"{path_item.parent}/{path_item.stem}.png")

            # Create new PNG file from JPEG file
            img = PillowImage.open(path_item, "r", ["JPEG"])
            img.save(new_filepath, "PNG")
            img.close()

            # If keep_originals != True, remove the original JPEF file
            if not keep_originals:
                path_item.unlink()


def is_jpg(file: pathlib.Path) -> bool:
    contents = file.read_bytes().splitlines()
    first_line = contents[0]
    return bytes("JFIF", "iso-8859-1") in first_line


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ConvertToPNG",
        description="Convert image files to PNG format in a given directory.",
    )
    parser.add_argument(
        "path", type=pathlib.Path, help="the path to directory of images to modify"
    )
    parser.add_argument(
        "-k",
        "--keep-originals",
        action="store_true",
        dest="keep",
        help="use if you want to keep original files",
    )
    args = parser.parse_args()

    try:
        # Make keep=args.keep if set or keep=False if args.keep wasn't set
        keep = args.keep or False
        convert_jpgs_to_pngs(args.path, keep_originals=keep)
    except (FileNotFoundError, NotADirectoryError):
        print(sys.exception())
    print()
