import os

import pytest
from PIL import Image

import image_manager


@pytest.mark.parametrize(
    "filename",
    [
        "photo.jpg",
        "photo.jpeg",
        "photo.JPG",
        "photo.JPEG",
        "my photo (1).jpg",
        "photo.dat",
    ],
)
def test_convert_jpg_to_png(tmp_path, filename):
    source = tmp_path / filename
    with Image.new("RGB", (3, 2), "red") as image:
        image.save(source, "JPEG")
    with Image.open(source) as image:
        expected_pixels = image.tobytes()

    image_manager.convert_jpg_to_png(source)

    assert not source.exists()
    output = source.with_suffix(".png")
    assert list(tmp_path.iterdir()) == [output]
    with Image.open(output) as image:
        assert image.format == "PNG"
        assert image.size == (3, 2)
        assert image.mode == "RGB"
        assert image.tobytes() == expected_pixels


@pytest.mark.parametrize("filename", ["notes.txt", "not_an_image.jpg", "existing.png"])
def test_convert_jpg_to_png_leaves_non_jpeg_untouched(tmp_path, filename):
    source = tmp_path / filename
    if source.suffix == ".png":
        with Image.new("RGB", (2, 2), "blue") as image:
            image.save(source, "PNG")
    else:
        source.write_text("This is not a JPEG.")
    original_bytes = source.read_bytes()

    image_manager.convert_jpg_to_png(source)

    assert source.read_bytes() == original_bytes
    assert list(tmp_path.iterdir()) == [source]


def test_convert_jpg_to_png_does_not_overwrite_existing_png(tmp_path):
    """Known bug: conversion silently replaces an existing same-stem PNG."""
    source = tmp_path / "photo.jpg"
    output = tmp_path / "photo.png"
    with Image.new("RGB", (2, 2), "red") as image:
        image.save(source, "JPEG")
    with Image.new("RGB", (2, 2), "blue") as image:
        image.save(output, "PNG")
    original_bytes = output.read_bytes()

    # Catch expected FileExistsError
    try:
        image_manager.convert_jpg_to_png(source)
    except FileExistsError:
        pass

    assert output.read_bytes() == original_bytes
    assert source.exists()


def test_convert_jpgs_to_pngs_mixed_directory_recursively(tmp_path):
    nested = tmp_path / "nested" / "deeper"
    nested.mkdir(parents=True)
    sources = [
        tmp_path / "photo.jpg",
        tmp_path / "another.jpeg",
        nested / "my photo (1).JPG",
    ]
    for source in sources:
        with Image.new("RGB", (2, 3), "green") as image:
            image.save(source, "JPEG")
    text = nested / "notes.txt"
    text.write_text("Keep these notes.")
    png = tmp_path / "existing.png"
    with Image.new("RGB", (1, 1), "blue") as image:
        image.save(png, "PNG")
    empty = nested / "empty.jpg"
    empty.touch()
    originals = {path: path.read_bytes() for path in (text, png, empty)}

    image_manager.convert_jpgs_to_pngs(tmp_path)

    for source in sources:
        assert not source.exists()
        with Image.open(source.with_suffix(".png")) as image:
            assert image.format == "PNG"
            assert image.size == (2, 3)
    for path, original_bytes in originals.items():
        assert path.read_bytes() == original_bytes
    expected_files = {source.with_suffix(".png") for source in sources}
    expected_files.update([text, png, empty])
    assert {path for path in tmp_path.rglob("*") if path.is_file()} == expected_files


def test_convert_jpgs_to_pngs_empty_directory(tmp_path):
    image_manager.convert_jpgs_to_pngs(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_convert_jpgs_to_pngs_nonexistent_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        image_manager.convert_jpgs_to_pngs(tmp_path / "missing")


def test_convert_jpgs_to_pngs_file_path_is_rejected(tmp_path):
    """Validation accepts files, but directory iteration rejects them."""
    source = tmp_path / "photo.jpg"
    with Image.new("RGB", (2, 2), "red") as image:
        image.save(source, "JPEG")
    original_bytes = source.read_bytes()

    with pytest.raises(NotADirectoryError):
        image_manager.convert_jpgs_to_pngs(source)

    assert source.read_bytes() == original_bytes
    assert not source.with_suffix(".png").exists()


def test_is_jpg_checks_contents_instead_of_extension(tmp_path):
    jpeg = tmp_path / "photo.txt"
    text = tmp_path / "notes.jpg"
    with Image.new("RGB", (1, 1), "red") as image:
        image.save(jpeg, "JPEG")
    text.write_text("Not an image.")
    assert image_manager.is_jpg(jpeg) is True
    assert image_manager.is_jpg(text) is False


def test_is_jpg_empty_text_png_and_unidentifiable_data_are_not_jpegs(tmp_path):
    source = tmp_path / "empty.txt"
    source.touch()
    assert image_manager.is_jpg(source) is False
    assert source.read_bytes() == b""

    text = tmp_path / "notes.jpg"
    text.write_text("Not an image.")
    assert image_manager.is_jpg(text) is False
    assert text.read_bytes() == b"Not an image."

    png = tmp_path / "picture.jpg"
    with Image.new("RGB", (1, 1), "blue") as image:
        image.save(png, "PNG")
    assert image_manager.is_jpg(png) is False

    binary = tmp_path / "random.bin"
    binary.write_bytes(bytes(range(256)) * 4)
    assert image_manager.is_jpg(binary) is False


def test_is_jpg_finds_exif_jpegs_and_ignores_extensions(tmp_path):
    """An EXIF JPEG carries no JFIF marker, so the old heuristic missed it."""
    non_jfif = tmp_path / "non-jfif.txt"
    with Image.new("RGB", (2, 2), "green") as image:
        image.save(non_jfif, "JPEG")
    data = non_jfif.read_bytes()
    jfif_at = data.index(b"JFIF")
    # drop the APP0 segment (marker + length + payload) so no JFIF marker remains
    non_jfif.write_bytes(data[: jfif_at - 4] + data[jfif_at + 14 :])
    assert b"JFIF" not in non_jfif.read_bytes()
    assert image_manager.is_jpg(non_jfif) is True

    with Image.new("RGB", (2, 2), "red") as image:
        image.save(tmp_path / "plain.TXT", "JPEG")
    assert image_manager.is_jpg(tmp_path / "plain.TXT") is True


def test_is_jpg_does_not_take_a_textual_jfif_marker_for_a_jpeg(tmp_path):
    """Data mentioning JFIF is not a JPEG on that account alone."""
    source = tmp_path / "about.jpg"
    source.write_text("The JFIF APP0 marker is described here.")
    assert image_manager.is_jpg(source) is False


@pytest.mark.skipif(os.name == "nt", reason="POSIX file permissions")
def test_is_jpg_propagates_permission_errors(tmp_path):
    """A file that cannot be read is an error, not a silent non-JPEG."""
    locked = tmp_path / "locked.jpg"
    with Image.new("RGB", (1, 1), "red") as image:
        image.save(locked, "JPEG")
    locked.chmod(0o000)
    try:
        with pytest.raises(PermissionError):
            image_manager.is_jpg(locked)
    finally:
        locked.chmod(0o644)


def test_convert_jpg_to_png_preserves_the_source_when_decoding_fails(tmp_path):
    """A truncated JPEG keeps its original file and leaves no partial PNG."""
    source = tmp_path / "truncated.jpg"
    with Image.new("RGB", (2, 2), "red") as image:
        image.save(source, "JPEG")
    original_bytes = source.read_bytes()
    source.write_bytes(original_bytes[: len(original_bytes) // 2])

    with pytest.raises(OSError):
        image_manager.convert_jpg_to_png(source)

    assert source.read_bytes() == source.read_bytes()[: len(original_bytes) // 2]
    assert not source.with_suffix(".png").exists()


@pytest.mark.parametrize(
    "name, expected",
    [
        ("photo", "spr_photo"),
        ("spr_photo", "spr_photo"),
        ("1photo", "spr_photo"),
        ("my photo (1)", "spr_my photo _1"),
    ],
)
def test_sanitize_name(name, expected):
    assert image_manager.sanitize_name(name) == expected


@pytest.mark.parametrize(
    "text, prefix, expected",
    [
        ("photo", "spr", "spr_photo"),
        ("_photo", "spr", "spr_photo"),
        ("spr_photo", "spr", "spr_photo"),
        ("sprout", "spr", "sprout"),
        ("", "img", "img_"),
        ("photo", "img", "img_photo"),
    ],
)
def test_check_prefix(text, prefix, expected):
    assert image_manager.check_prefix(text, prefix) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("photo", "photo"),
        ("_photo", "_photo"),
        ("1photo", "_photo"),
        (" photo", "_photo"),
    ],
)
def test_check_starting_character(text, expected):
    assert image_manager.check_starting_character(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("photo", "photo"),
        ("photo (1)", "photo _1"),
        ("(photo)", "_photo"),
        ("photo__", "photo_"),
        ("photo !-", "photo !-"),
        ("", ""),
    ],
)
def test_replace_special_characters(text, expected):
    assert image_manager.replace_special_characters(text) == expected


@pytest.mark.parametrize(
    "function", [image_manager.check_starting_character, image_manager.sanitize_name]
)
def test_name_helpers_reject_empty_names(function):
    with pytest.raises(IndexError):
        function("")
