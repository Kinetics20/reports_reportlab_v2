import logging
from pathlib import Path
from typing import Any, NoReturn

import pytest

import src.register_fonts as rf
from src.fontspec import FontSpec
from src.register_fonts import register_fonts


@pytest.fixture
def valid_font(tmp_path: Path) -> Path:
    """Create a dummy .ttf file and return its path."""
    p = tmp_path / "Dummy.ttf"
    p.write_bytes(b"fake-ttf")
    return p


def test_registers_new_font(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    valid_font: Path,
) -> None:
    """When font is not registered yet, it should be registered and logged at INFO."""
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr("src.register_fonts.pdfmetrics.getFont", lambda name: (_ for _ in ()).throw(KeyError))

    class FakeTTFont:
        def __init__(self, name: str, filename: str) -> None:
            self.name = name
            self.filename = filename

    monkeypatch.setattr(rf, "TTFont", FakeTTFont)

    def fake_register_font(ttfont: FakeTTFont) -> None:
        calls.append((ttfont.name, ttfont.filename))

    monkeypatch.setattr("src.register_fonts.pdfmetrics.registerFont", fake_register_font)

    spec = FontSpec(name="Dummy", file_path=valid_font)

    caplog.set_level(logging.DEBUG)
    register_fonts([spec])

    assert calls == [("Dummy", str(valid_font))]
    assert any("Successfully registered font: Dummy" in rec.message for rec in caplog.records)


def test_skips_duplicate_names_in_input(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, valid_font: Path
) -> None:
    """Duplicate font names in the input list should be skipped and warned."""
    monkeypatch.setattr("src.register_fonts.pdfmetrics.getFont", lambda name: (_ for _ in ()).throw(KeyError))
    monkeypatch.setattr("src.register_fonts.pdfmetrics.registerFont", lambda font: None)
    monkeypatch.setattr("src.register_fonts.TTFont", lambda name, path: (name, path))

    caplog.set_level("WARNING")

    spec1 = FontSpec(name="Duplicate", file_path=valid_font)
    spec2 = FontSpec(name="Duplicate", file_path=valid_font)
    register_fonts([spec1, spec2], logger=None)

    assert "Duplicate font in input" in caplog.text


def test_already_registered_is_debug_logged_and_not_registered_again(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, valid_font: Path
) -> None:
    """If font is already registered, do not call registerFont again."""
    called = {"count": 0}

    def fake_get_font(name: str) -> str:
        return "already-there"

    def fake_register_font(font: Any) -> None:
        called["count"] += 1

    monkeypatch.setattr("src.register_fonts.pdfmetrics.getFont", fake_get_font)
    monkeypatch.setattr("src.register_fonts.pdfmetrics.registerFont", fake_register_font)
    monkeypatch.setattr("src.register_fonts.TTFont", lambda name, path: (name, path))

    caplog.set_level("DEBUG")

    spec = FontSpec(name="Already", file_path=valid_font)
    register_fonts([spec], logger=None)

    assert called["count"] == 0
    assert "already registered" in caplog.text


def test_register_font_failure_is_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, valid_font: Path
) -> None:
    """Exceptions from pdfmetrics.registerFont should be caught and logged as exception."""

    def fake_get_font(name: str) -> NoReturn:
        raise KeyError

    def fake_register_font(font: Any) -> None:
        raise RuntimeError("bad font")

    monkeypatch.setattr("src.register_fonts.pdfmetrics.getFont", fake_get_font)
    monkeypatch.setattr("src.register_fonts.pdfmetrics.registerFont", fake_register_font)
    monkeypatch.setattr("src.register_fonts.TTFont", lambda name, path: (name, path))

    caplog.set_level("ERROR")

    spec = FontSpec(name="Broken", file_path=valid_font)
    register_fonts([spec], logger=None)

    assert "Failed to register font Broken" in caplog.text


def test_missing_file_is_warned_and_skipped(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    """If file disappears before registration, it should be skipped."""
    font_path = tmp_path / "GhostFont.ttf"
    font_path.write_bytes(b"fake-ttf")

    def fake_get_font(name: str) -> NoReturn:
        raise KeyError

    def fake_register_font(font: Any) -> None:
        raise OSError("file missing")

    monkeypatch.setattr("src.register_fonts.pdfmetrics.getFont", fake_get_font)
    monkeypatch.setattr("src.register_fonts.pdfmetrics.registerFont", fake_register_font)
    monkeypatch.setattr("src.register_fonts.TTFont", lambda name, path: (name, path))

    caplog.set_level("ERROR")

    spec = FontSpec(name="GhostFont", file_path=font_path)
    font_path.unlink()

    register_fonts([spec], logger=None)

    assert "Failed to register font GhostFont" in caplog.text
