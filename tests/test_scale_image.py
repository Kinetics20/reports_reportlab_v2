from pathlib import Path
from unittest.mock import patch

import pytest
from reportlab.platypus import Image

from src.scale_image import scaled_image_flowable


@pytest.fixture
def dummy_image(tmp_path: Path) -> Path:
    """Create a temporary PNG image 10x20 px for testing."""
    from PIL import Image as PILImage

    path = tmp_path / "dummy.png"
    img = PILImage.new("RGB", (10, 20), color="white")
    img.save(path)
    return path


def test_invalid_max_height(dummy_image: Path) -> None:
    """Function should return None if max_height <= 0."""
    result = scaled_image_flowable(dummy_image, max_height=0)
    assert result is None


def test_missing_file(tmp_path: Path) -> None:
    """Function should return None if file does not exist."""
    missing = tmp_path / "no.png"
    result = scaled_image_flowable(missing, max_height=50)
    assert result is None


def test_imagereader_error(dummy_image: Path) -> None:
    """Function should return None if ImageReader raises an exception."""
    with patch("src.scale_image.ImageReader", side_effect=Exception("boom")):
        result = scaled_image_flowable(dummy_image, max_height=50)
        assert result is None


def test_invalid_dimensions(dummy_image: Path) -> None:
    """Function should return None if image has zero or negative dimensions."""
    fake_reader = patch("src.scale_image.ImageReader")
    with fake_reader as mock_reader:
        instance = mock_reader.return_value
        instance.getSize.return_value = (0, 0)
        result = scaled_image_flowable(dummy_image, max_height=50)
        assert result is None


def test_downscaling(dummy_image: Path) -> None:
    """Tall image should be scaled down if ih > max_height."""
    result = scaled_image_flowable(dummy_image, max_height=10)
    assert isinstance(result, Image)
    assert result.drawHeight == 10


def test_equal_height_no_upscale(dummy_image: Path) -> None:
    """If ih == max_height and upscale=False, scale should be 1.0."""
    # Create image with height = 30
    from PIL import Image as PILImage

    path = dummy_image.parent / "eq.png"
    PILImage.new("RGB", (15, 30), color="blue").save(path)
    result = scaled_image_flowable(path, max_height=30, upscale=False)
    assert isinstance(result, Image)
    assert int(result.drawHeight) == 30


def test_smaller_no_upscale(dummy_image: Path) -> None:
    """Smaller image should not be scaled up if upscale=False."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "small.png"
    PILImage.new("RGB", (5, 5), color="green").save(path)
    result = scaled_image_flowable(path, max_height=50, upscale=False)
    assert isinstance(result, Image)
    assert result.drawHeight == 5


def test_upscale_smaller(dummy_image: Path) -> None:
    """Smaller image should be scaled up if upscale=True."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "tiny.png"
    PILImage.new("RGB", (5, 5), color="red").save(path)
    result = scaled_image_flowable(path, max_height=50, upscale=True)
    assert isinstance(result, Image)
    assert result.drawHeight == 50


def test_scaled_image_flowable_type(dummy_image: Path) -> None:
    """Ensure returned object is a ReportLab Image."""
    flowable = scaled_image_flowable(dummy_image, max_height=50)
    assert isinstance(flowable, Image)


def test_scaled_image_flowable_as_none_for_negative_height(dummy_image: Path) -> None:
    """Negative max_height returns None."""
    result = scaled_image_flowable(dummy_image, max_height=-10)
    assert result is None


def test_scaled_image_flowable_invalid_file_type(tmp_path: Path) -> None:
    """Return None if file is not an image."""
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("not an image")
    result = scaled_image_flowable(bad_file, max_height=50)
    assert result is None


def test_scaled_image_flowable_invalid_reader_size(dummy_image: Path) -> None:
    """If ImageReader returns invalid dimensions, function returns None."""
    with patch("src.scale_image.ImageReader") as mock_reader:
        inst = mock_reader.return_value
        inst.getSize.return_value = (-1, -1)
        result = scaled_image_flowable(dummy_image, max_height=10)
        assert result is None
