import pytest

# import image_manager.convert_to_png as convert_to_png
from image_manager import convert_to_png


def test_convert_jpg_to_png(test_dir):
    # Convert all JPEG images to PNG
    convert_to_png.convert_jpgs_to_pngs(test_dir)

    # Confirm no JPEGs remain
    for file in (item for item in test_dir.iterdir() if item.is_file()):
        assert not convert_to_png.is_jpg(file)


@pytest.mark.skip
def test_convert_jpg_to_png_keep_originals(test_dir):
    # TODO
    pass
