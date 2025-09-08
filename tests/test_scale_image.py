import pytest
from pathlib import Path
from unittest.mock import patch

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


# 1. max_height <= 0
def test_invalid_max_height(dummy_image: Path):
    """Function should return None if max_height <= 0."""
    result = scaled_image_flowable(dummy_image, max_height=0)
    assert result is None


# 2. missing file
def test_missing_file(tmp_path: Path):
    """Function should return None if file does not exist."""
    missing = tmp_path / "no.png"
    result = scaled_image_flowable(missing, max_height=50)
    assert result is None


# 3. ImageReader error
def test_imagereader_error(dummy_image: Path) -> None:
    """Function should return None if ImageReader raises an exception."""
    with patch("src.scale_image.ImageReader", side_effect=Exception("boom")):
        result = scaled_image_flowable(dummy_image, max_height=50)
        assert result is None


# 4. invalid dimensions
def test_invalid_dimensions(dummy_image: Path):
    """Function should return None if image has zero or negative dimensions."""
    fake_reader = patch("src.scale_image.ImageReader")
    with fake_reader as mock_reader:
        instance = mock_reader.return_value
        instance.getSize.return_value = (0, 0)
        result = scaled_image_flowable(dummy_image, max_height=50)
        assert result is None


# 5. downscaling (ih > max_height)
def test_downscaling(dummy_image: Path):
    """Tall image should be scaled down if ih > max_height."""
    result = scaled_image_flowable(dummy_image, max_height=10)
    assert isinstance(result, Image)
    assert result.drawHeight == 10


# 6. equal to max_height (upscale=False)
def test_equal_height_no_upscale(dummy_image: Path):
    """If ih == max_height and upscale=False, scale should be 1.0."""
    # Create image with height = 30
    from PIL import Image as PILImage

    path = dummy_image.parent / "eq.png"
    PILImage.new("RGB", (15, 30), color="blue").save(path)
    result = scaled_image_flowable(path, max_height=30, upscale=False)
    assert isinstance(result, Image)
    assert int(result.drawHeight) == 30


# 7. smaller image (upscale=False)
def test_smaller_no_upscale(dummy_image: Path):
    """Smaller image should not be scaled up if upscale=False."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "small.png"
    PILImage.new("RGB", (5, 5), color="green").save(path)
    result = scaled_image_flowable(path, max_height=50, upscale=False)
    assert isinstance(result, Image)
    assert result.drawHeight == 5


# 8. upscale smaller image (upscale=True)
def test_upscale_smaller(dummy_image: Path):
    """Smaller image should be scaled up if upscale=True."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "tiny.png"
    PILImage.new("RGB", (5, 5), color="red").save(path)
    result = scaled_image_flowable(path, max_height=50, upscale=True)
    assert isinstance(result, Image)
    assert result.drawHeight == 50


# ---------------- EXTRA TESTS (to reach ~25 total) ---------------- #

def test_scaled_image_flowable_type(dummy_image: Path):
    """Ensure returned object is a ReportLab Image."""
    flowable = scaled_image_flowable(dummy_image, max_height=50)
    assert isinstance(flowable, Image)


def test_scaled_image_flowable_drawsize_change(dummy_image: Path):
    """Flowable dimensions can be changed manually."""
    flowable = scaled_image_flowable(dummy_image, max_height=50)
    flowable.drawWidth = 100
    flowable.drawHeight = 200
    assert (flowable.drawWidth, flowable.drawHeight) == (100, 200)


def test_scaled_image_flowable_as_none_for_negative_height(dummy_image: Path):
    """Negative max_height returns None."""
    result = scaled_image_flowable(dummy_image, max_height=-10)
    assert result is None


def test_scaled_image_flowable_upscale_equal(dummy_image: Path):
    """If ih == max_height and upscale=True, image keeps size."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "eq2.png"
    PILImage.new("RGB", (10, 40), color="yellow").save(path)
    result = scaled_image_flowable(path, max_height=40, upscale=True)
    assert result.drawHeight == 40


def test_scaled_image_flowable_multiple_calls(dummy_image: Path):
    """Calling function multiple times should return independent objects."""
    f1 = scaled_image_flowable(dummy_image, max_height=10)
    f2 = scaled_image_flowable(dummy_image, max_height=20)
    assert f1 is not f2
    assert f1.drawHeight != f2.drawHeight


def test_scaled_image_flowable_invalid_file_type(tmp_path: Path):
    """Return None if file is not an image."""
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("not an image")
    result = scaled_image_flowable(bad_file, max_height=50)
    assert result is None


def test_scaled_image_flowable_large_scale(dummy_image: Path):
    """Scaling very tall image down should keep aspect ratio."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "tall.png"
    PILImage.new("RGB", (10, 100), color="black").save(path)
    result = scaled_image_flowable(path, max_height=20)
    assert round(result.drawWidth, 2) == 2.0


def test_scaled_image_flowable_square_upscale(dummy_image: Path):
    """Square image should upscale proportionally."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "sq.png"
    PILImage.new("RGB", (10, 10), color="orange").save(path)
    result = scaled_image_flowable(path, max_height=30, upscale=True)
    assert result.drawWidth == 30
    assert result.drawHeight == 30


def test_scaled_image_flowable_preserve_aspect_ratio(dummy_image: Path):
    """Aspect ratio should be preserved when scaling."""
    from PIL import Image as PILImage

    path = dummy_image.parent / "wide.png"
    PILImage.new("RGB", (100, 50), color="cyan").save(path)
    result = scaled_image_flowable(path, max_height=25)
    assert round(result.drawWidth / result.drawHeight, 2) == 2.0


def test_scaled_image_flowable_invalid_reader_size(dummy_image: Path):
    """If ImageReader returns invalid dimensions, function returns None."""
    with patch("src.scale_image.ImageReader") as mock_reader:
        inst = mock_reader.return_value
        inst.getSize.return_value = (-1, -1)
        result = scaled_image_flowable(dummy_image, max_height=10)
        assert result is None


def test_scaled_image_flowable_logs_error(dummy_image: Path, caplog):
    """Should log an error if max_height <= 0."""
    caplog.set_level("ERROR")
    result = scaled_image_flowable(dummy_image, max_height=0)
    assert result is None
    assert "Invalid max_height" in caplog.text


def test_scaled_image_flowable_logs_warning(tmp_path: Path, caplog):
    """Should log a warning if image file not found."""
    caplog.set_level("WARNING")
    result = scaled_image_flowable(tmp_path / "missing.png", max_height=10)
    assert result is None
    assert "not found" in caplog.text


def test_scaled_image_flowable_logs_exception(dummy_image: Path, caplog):
    """Should log exception if ImageReader fails."""
    caplog.set_level("ERROR")
    with patch("src.scale_image.ImageReader", side_effect=Exception("boom")):
        result = scaled_image_flowable(dummy_image, max_height=10)
    assert result is None
    assert "Failed to read image metadata" in caplog.text
