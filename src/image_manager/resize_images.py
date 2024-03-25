"""Resize Images

This script resizes all images in a given directory.

This file can also be imported as a module and contains the following function:

    * resize_images
"""

import argparse
import pathlib
import sys
from . import check_path

from PIL import Image as PillowImage


def resize_images(
    path: pathlib.Path,
    ratio: float = None,
    width: int = None,
    height: int = None,
    keep_originals: bool = False,
) -> None:
    """Resize all images in given directory path.

    If only width or only height are provided, images are resized with same aspect
    ratio.
    """

    check_path.raise_if_invalid_path(path)

    # Recursively iterate through contents of directory
    for path_item in path.iterdir():
        if path_item.is_dir():
            resize_images(path_item)
        elif path_item.is_file():
            img = PillowImage.open(path_item)

            # # Maintain orientation - TODO - Doesn't work all the time
            # o_width, o_height = img.size
            # if o_width > o_height:
            #     resize = (resize[1], resize[0])

            if ratio:
                width = int(ratio * img.width)
                height = int(ratio * img.height)
            else:
                # Keep aspect ratio if other dimension not provided
                if width and not height:
                    height = img.height * width // img.width

                if height and not width:
                    width = img.width * height // img.height

                if not (width or height):
                    raise TypeError(
                        f"{resize_images.__name__}() missing 2 argument: 'width' and 'height'"
                    )

            resized_img = img.resize((width, height))

            # If keep != True, remove the original file
            if keep_originals:
                new_path = pathlib.Path(
                    f"{path_item.parent}/{path_item.stem}_resized{path_item.suffix}"
                )
                resized_img.save(new_path)
            else:
                resized_img.save(path_item)

            resized_img.close()
            img.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ResizeImages", description="Resize all image files in a given directory."
    )
    parser.add_argument(
        "path", type=pathlib.Path, help="the path to directory of images to modify"
    )
    parser.add_argument("-r", "--ratio")
    parser.add_argument("-w", "--width")
    parser.add_argument("-h", "--height")
    parser.add_argument(
        "-k",
        "--keep-originals",
        action="store_true",
        dest="keep",
        help="use if you want to keep original files",
    )
    args = parser.parse_args()

    # Verify at least one option selected
    if not (args.ratio or args.width or args.height):
        print("Please choose at least one of the options:\n  -r -w -h\n")
        parser.print_help()
    else:
        try:
            # Make keep=args.keep if set or keep=False if args.keep wasn't set
            keep = args.keep or False

            if args.resize:
                resize_images(args.path, ratio=0.5, keep_originals=keep)
            if args.corner:
                pass
        except (FileNotFoundError, NotADirectoryError, TypeError):
            print(sys.exception())
    print()
