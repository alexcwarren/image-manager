from pathlib import Path
from PIL import Image # pillow


def convert_to_pngs(directory: Path, do_keep=True, depth=0):
    print(f"{"  " * depth}[{directory.name}] ({do_keep}, {depth})")
    depth += 1
    for path_item in directory.iterdir():
        if path_item.is_dir():
            convert_to_pngs(path_item, do_keep, depth)
        else:
            print(f"{"  " * depth}{path_item.name}", end="")

            new_filename = f"{sanitize_name(path_item.stem)}.png"
            do_rename = False
            if path_item.name != new_filename:
                do_rename = True
                print(f" -> {new_filename}", end="")
            
            new_path = f"{str(path_item.parent)}/{new_filename}"
            
            if is_jpg(path_item):
                img = Image.open(path_item, "r", ["JPEG"])
                img.save(new_path, "PNG")
                img.close()

                print(f" (converted)", end="")

                if not do_keep:
                    print(f" (old file deleted)")
                    path_item.unlink()
                else:
                    print()
            elif do_rename:
                new_file = Path(new_path)
                path_item.replace(new_file)
                print(f" (renamed)")
            else:
                print()



def is_jpg(file: Path) -> bool:
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
    if not(text[0].isalpha() or text[0] == "_"):
        text = replacement + text[1:]
    return text


def replace_special_characters(text: str) -> str:
    replacement="_"
    special_characters = "()"
    for char in special_characters:
        text = text.replace(char, replacement)
    
    if text.endswith(replacement):
        text = text[:-1]

    return text


def prompt_directory_path() -> str:
    return Path(input("Please enter directory path: "))


def prompt_keep_old_files() -> bool:
    keep = None
    while keep is None or not (keep == "" or keep.lower().startswith("y") or keep.lower().startswith("n")):
        keep = input("Keep old JPG/JPEG files? [Y]/[n]: ")
    if keep == "" or keep.lower().startswith("y"):
        return True
    return False


if __name__ == "__main__":
    convert_to_pngs(prompt_directory_path(), prompt_keep_old_files())
