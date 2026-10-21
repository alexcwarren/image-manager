from __future__ import annotations

import argparse
import math
import pathlib

from PIL import Image as PillowImage
from PIL import UnidentifiedImageError


def convert_jpgs_to_pngs(path: pathlib.Path) -> None:
    """Convert all JPEG images to PNG contained in given directory path."""

    # Confirm path is a valid directory or file
    if not (path.is_file() or path.is_dir()):
        if not path.is_file():
            raise FileNotFoundError(f"path provided is not a file: '{path.absolute()}'")
        if not path.is_dir():
            raise NotADirectoryError(
                f"path provided is not a directory: '{path.absolute()}'"
            )

    # Recursively iterate through contents of directory
    for path_item in path.iterdir():
        if path_item.is_dir():
            convert_jpgs_to_pngs(path_item)
        elif path_item.is_file():
            convert_jpg_to_png(path_item)


def convert_jpg_to_png(filepath: pathlib.Path) -> None:
    """Convert given JPEG image to PNG."""
    if not is_jpg(filepath):
        return

    # Create new filepath with 'png' extension
    new_filepath = pathlib.Path(f"{filepath.parent}/{filepath.stem}.png")

    if new_filepath.exists():
        raise FileExistsError(
            f"destination file already exists: '{new_filepath}'"
        )

    # Create new PNG file from JPEG file
    with PillowImage.open(filepath, "r", ["JPEG"]) as img:
        try:
            img.save(new_filepath, "PNG")
        except Exception:
            # A JPEG that decodes mid-way leaves the source untouched and no
            # half-written destination behind; the error reaches the caller.
            new_filepath.unlink(missing_ok=True)
            raise

    # Remove the original JPEF file
    filepath.unlink()


def OLDconvert_jpg_to_png(directory: pathlib.Path, do_keep=True, depth=0) -> None:
    print(f"{' ' * depth}[{directory.name}]")
    depth += 1
    for path_item in directory.iterdir():
        if path_item.is_dir():
            convert_jpg_to_png(path_item)
        else:
            print(f"{' ' * depth}{path_item.name}", end="")

            new_filename = f"{sanitize_name(path_item.stem)}.png"
            do_rename = False
            if path_item.name != new_filename:
                do_rename = True
                print(f" -> {new_filename}", end="")

            new_path = f"{path_item.parent!s}/{new_filename}"
            new_file = pathlib.Path(new_path)

            if is_jpg(path_item):
                img = PillowImage.open(path_item, "r", ["JPEG"])
                img.save(new_path, "PNG")
                img.close()
                print(" (converted)", end="")

                if not do_keep:
                    print(" (old file deleted)", end="")
                    path_item.unlink()
            elif do_rename:
                path_item.replace(new_file)
                print(" (renamed)", end="")
            print()


def is_jpg(file: pathlib.Path) -> bool:
    """Whether the file's actual content is a JPEG image, whatever its name says.

    Pillow's format detection reads the image signature, so JFIF and EXIF JPEGs
    are both recognised, while empty files, text, other image formats and
    unidentifiable data are simply not JPEGs. Content a signature cannot
    identify raises UnidentifiedImageError and counts as not a JPEG; anything
    else (a missing file, a directory, a permission problem) reaches the caller.
    """
    try:
        with PillowImage.open(file, "r") as image:
            return image.format == "JPEG"
    except UnidentifiedImageError:
        return False


def sanitize_name(name: str) -> str:
    name = check_starting_character(name)
    name = check_prefix(name, "spr")
    name = replace_special_characters(name)
    return name


def check_prefix(text: str, prefix: str) -> str:
    if not text.startswith(prefix):
        if text.startswith("_"):
            text = prefix + text
        else:
            text = prefix + "_" + text
    return text


def check_starting_character(text: str) -> str:
    replacement = "_"
    if not (text[0].isalpha() or text[0] == "_"):
        text = replacement + text[1:]
    return text


def replace_special_characters(text: str) -> str:
    replacement = "_"
    special_characters = "()"
    for char in special_characters:
        text = text.replace(char, replacement)

    if text.endswith(replacement):
        text = text[:-1]

    return text


def prompt_directory_path() -> str:
    return str(pathlib.Path(input("Please enter directory path: ")))


def prompt_keep_old_files() -> bool:
    keep = None
    while keep is None or not (
        keep == "" or keep.lower().startswith("y") or keep.lower().startswith("n")
    ):
        keep = input("Keep old JPG/JPEG files? [Y]/[n]: ")
    return bool(keep == "" or keep.lower().startswith("y"))


def prompt_resize() -> tuple[int, int] | None:
    resize = None
    while resize is None or not (resize.lower() in ("", "y", "n")):
        resize = input("Resize files? [y]/[N]: ")
    if resize == "":
        return None

    width: str = ""
    height: str = ""
    while "" in (width, height) or not (width.isdigit() and height.isdigit()):
        width_height = input("Enter width and height: ")
        delimeter = " "
        if "," in width_height:
            delimeter = ","
            width_height.replace(" ", "")
        width, height = width_height.split(delimeter)

    return (int(width), int(height))


def resize_images(
    directory: pathlib.Path, resize: tuple[int, int], resize_suffix="_small"
) -> None:
    for path_item in directory.iterdir():
        if path_item.is_dir():
            resize_images(path_item, resize)
        else:
            img = PillowImage.open(path_item)

            # # Maintain orientation - TODO - Doesn't work all the time
            # o_width, o_height = img.size
            # if o_width > o_height:
            #     resize = (resize[1], resize[0])

            resized = img.resize(resize)
            new_path_item = path_item
            if not path_item.stem.endswith(resize_suffix):
                new_path_item = pathlib.Path(
                    f"{path_item.parent!s}/"
                    + f"{path_item.stem}{resize_suffix}{path_item.suffix}"
                )
            resized.save(new_path_item)
            img.close()
            resized.close()


def remove_corners(directory: pathlib.Path, corner_radius: int) -> None:
    lengths: tuple[int, ...] = (corner_radius,)
    lengths += tuple(
        round(corner_radius - math.sqrt(corner_radius**2 - (corner_radius - y) ** 2))
        + 1
        for y in range(1, corner_radius)
    )

    top_coordinates: tuple = ()
    for X, y in zip(lengths, range(corner_radius)):
        top_coordinates += tuple((x, y) for x in range(X))

    bottom_coordinates: tuple = ()
    for X, y in zip(reversed(lengths), range(corner_radius)):
        bottom_coordinates += tuple((x, y) for x in range(X))

    color = (0, 0, 0, 0)

    for path_item in directory.iterdir():
        if path_item.is_dir():
            remove_corners(path_item, corner_radius)
        else:
            img = PillowImage.open(path_item)
            w = img.width
            h = img.height

            for x, y in top_coordinates:
                # Top-left
                img.putpixel((x, y), color)

                # Top-right
                img.putpixel((w - x - 1, y), color)

            for x, y in bottom_coordinates:
                # Bottom-left
                img.putpixel((x, h - corner_radius + y), color)

                # Bottom-right
                img.putpixel((w - x - 1, h - corner_radius + y), color)

            img.save(path_item)
            img.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ImageManager", description="Modify image files in a given directory."
    )
    parser.add_argument(
        "path", type=pathlib.Path, help="the path to directory of images to modify"
    )
    args = parser.parse_args()

    try:
        convert_jpgs_to_pngs(args.path)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(e)
    print()
