import pytest

from image_manager import round_corners


@pytest.mark.skip
def test_round_corners(test_dir):
    round_corners(test_dir)
    pass


@pytest.mark.skip
def test_round_corners_keep_originals(test_dir):
    # TODO
    pass
