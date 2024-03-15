import argparse
import math
import pathlib
import sys

from PIL import Image as PillowImage


def convert_jpgs_to_pngs(path: pathlib.Path, keep_originals: bool = False) -> None:
    """Convert all JPEG images to PNG contained in given directory path."""

    raise_if_invalid_path(path)
    
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


def resize_images(path: pathlib.Path, ratio: float = None, width: int = None, height: int = None, keep_originals: bool = False) -> None:
    """Resize all images in given directory path.

    If only width or only height are provided, images are resized with same aspect
    ratio.
    """

    raise_if_invalid_path(path)
    
    # Recursively iterate through contents of directory
    for path_item in path.iterdir():
        if path_item.is_dir():
            convert_jpgs_to_pngs(path_item)
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
                    raise TypeError(f"{resize_images.__name__}() missing 2 argument: 'width' and 'height'")

            resized_img = img.resize((width, height))

            # If keep != True, remove the original file
            if keep_originals:
                new_path = pathlib.Path(f"{path_item.parent}/{path_item.stem}_resized{path_item.suffix}")
                resized_img.save(new_path)
            else:
                resized_img.save(path_item)
            
            resized_img.close()
            img.close()


def raise_if_invalid_path(path: pathlib.Path) -> None:
    """Confirm path is a valid directory or file."""

    if not (path.is_file() or path.is_dir()):
        if not path.is_file():
            raise FileNotFoundError(
                f"path provided is not a file: '{path.absolute()}'"
            )
        if not path.is_dir():
            raise NotADirectoryError(
                f"path provided is not a directory: '{path.absolute()}'"
            )


def OLDconvert_jpg_to_png(directory: pathlib.Path, do_keep=True, depth=0) -> None:
    print(f"{" " * depth}[{directory.name}]")
    depth += 1
    for path_item in directory.iterdir():
        if path_item.is_dir():
            convert_jpg_to_png(path_item, do_keep, depth)
        else:
            print(f"{" " * depth}{path_item.name}", end="")

            new_filename = f"{sanitize_name(path_item.stem)}.png"
            do_rename = False
            if path_item.name != new_filename:
                do_rename = True
                print(f" -> {new_filename}", end="")

            new_path = f"{str(path_item.parent)}/{new_filename}"
            new_file = pathlib.Path(new_path)

            if is_jpg(path_item):
                img = PIL.Image.open(path_item, "r", ["JPEG"])
                img.save(new_path, "PNG")
                img.close()
                print(f" (converted)", end="")

                if not do_keep:
                    print(f" (old file deleted)", end="")
                    path_item.unlink()
            elif do_rename:
                path_item.replace(new_file)
                print(f" (renamed)", end="")
            print()


def is_jpg(file: pathlib.Path) -> bool:
    contents = file.read_bytes().splitlines()
    first_line = contents[0]
    return bytes("JFIF", "iso-8859-1") in first_line


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
    return pathlib.Path(input("Please enter directory path: "))


def prompt_keep_old_files() -> bool:
    keep = None
    while keep is None or not (
        keep == "" or keep.lower().startswith("y") or keep.lower().startswith("n")
    ):
        keep = input("Keep old JPG/JPEG files? [Y]/[n]: ")
    if keep == "" or keep.lower().startswith("y"):
        return True
    return False


def prompt_resize() -> tuple[int, int]:
    resize = None
    while resize is None or not (resize.lower() in ("", "y", "n")):
        resize = input("Resize files? [y]/[N]: ")
    if resize == "":
        return None

    width = height = None
    while None in (width, height) or not (width.isdigit() and height.isdigit()):
        width_height = input("Enter width and height: ")
        delimeter = " "
        if "," in width_height:
            delimeter = ","
            width_height.replace(" ", "")
        width, height = width_height.split(delimeter)

    return (int(width), int(height))


def OLDresize_images(
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
                    f"{str(path_item.parent)}/"
                    + f"{path_item.stem}{resize_suffix}{path_item.suffix}"
                )
            resized.save(new_path_item)
            img.close()
            resized.close()


def remove_corners(directory: pathlib.Path, corner_radius: int) -> None:
    lengths = (corner_radius,)
    lengths += tuple(
        int(
            round(
                corner_radius - math.sqrt(corner_radius**2 - (corner_radius - y) ** 2)
            )
        ) + 1
        for y in range(1, corner_radius)
    )

    top_coordinates = tuple()
    for X, y in zip(lengths, range(corner_radius)):
        top_coordinates += tuple((x, y) for x in range(X))

    bottom_coordinates = tuple()
    for X, y in zip(reversed(lengths), range(corner_radius)):
        bottom_coordinates += tuple((x, y) for x in range(X))

    color = (0, 0, 0, 0)

    for path_item in directory.iterdir():
        if path_item.is_dir():
            remove_corners(path_item)
        else:
            img = PIL.Image.open(path_item)
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
        prog="ImageManager",
        description="Modify image files in a given directory."
    )
    parser.add_argument("path", type=pathlib.Path, help="the path to directory of images to modify")
    parser.add_argument("-p", "--png-convert", action="store_true", dest="png")
    parser.add_argument("-r", "--resize", action="store_true")
    parser.add_argument("-c", "--corner-round", action="store_true", dest="corner")
    parser.add_argument("-k", "--keep-originals", action="store_true", dest="keep")
    args = parser.parse_args()

    # Verify at least one option selected
    if not (args.png or args.resize or args.corner):
        print("Please choose at least one of the options:\n  -p -r -c\n")
        parser.print_help()
    else:
        try:
            # Make keep=args.keep if set or keep=False if args.keep wasn't set
            keep = args.keep or False

            if args.png:
                convert_jpgs_to_pngs(args.path, keep_originals=keep)
            if args.resize:
                resize_images(args.path, ratio=0.5, keep_originals=keep)
            if args.corner:
                pass
        except (FileNotFoundError, NotADirectoryError, TypeError):
            print(sys.exception())
    print()

    # remove_corners(directory, 14)
