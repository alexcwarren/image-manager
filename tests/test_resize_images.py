import pytest

from image_manager import resize_images


@pytest.mark.skip
def test_resize_images(test_dir):
    resize_images.resize_images(test_dir)
    pass


@pytest.mark.skip
def test_resize_images_keep_originals(test_dir):
    # TODO
    pass
