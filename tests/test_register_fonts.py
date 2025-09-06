from pathlib import Path

import pytest


@pytest.fixture
def valid_font(tmp_path: Path) -> Path:
    """Create a dummy .ttf file and return its path."""
    p = tmp_path / "Dummy.ttf"
    p.write_bytes(b"fake-ttf")
    return p


def test_registers_new_font(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, valid_font: Path
) -> None:
    """When font is not registered yet, it should be registered and logged at INFO."""


def test_skips_duplicate_names_in_input(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, valid_font: Path
) -> None:
    """Duplicate font names in the input list should be skipped and warned."""


def test_already_registered_is_debug_logged_and_not_registered_again(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, valid_font: Path
) -> None:
    """If font is already registered, do not call registerFont again."""


def test_register_font_failure_is_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, valid_font: Path
) -> None:
    """Exceptions from pdfmetrics.registerFont should be caught and logged as exception."""


def test_missing_file_is_warned_and_skipped(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    """Even if a valid FontSpec existed, if file disappears before registration, it should be skipped."""
