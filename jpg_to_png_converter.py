from pathlib import Path


def convert_to_pngs(directory: Path, depth=0):
    print(f"{" " * depth}[{directory.name}]")
    depth += 1
    for path_item in directory.iterdir():
        if path_item.is_dir():
            convert_to_pngs(path_item, depth)
        else:
            print(f"{" " * depth}{path_item.name}")


def prompt_directory_path():
    return Path(input("Please enter directory path: "))


if __name__ == "__main__":
    convert_to_pngs(prompt_directory_path())
