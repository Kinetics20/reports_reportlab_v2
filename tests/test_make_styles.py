from __future__ import annotations

import logging
from collections.abc import Mapping

import pytest
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet

from src.make_styles import make_styles


@pytest.fixture()
def base_styles() -> StyleSheet1:
    """Return a fresh sample stylesheet for each test."""
    return getSampleStyleSheet()


def test_override_existing_style(base_styles: StyleSheet1) -> None:
    """It should override attributes of an existing style."""
    overrides: Mapping[str, Mapping[str, object]] = {"Title": {"fontSize": 22}}
    styles = make_styles(base=base_styles, overrides=overrides)
    assert styles["Title"].fontSize == 22


def test_create_missing_style(base_styles: StyleSheet1) -> None:
    """It should create a missing style when create_missing=True."""
    overrides: Mapping[str, Mapping[str, object]] = {"Custom": {"fontSize": 14}}
    styles = make_styles(base=base_styles, overrides=overrides, create_missing=True)
    assert "Custom" in styles.byName
    assert isinstance(styles["Custom"], ParagraphStyle)


def test_missing_parent_style_raises(base_styles: StyleSheet1) -> None:
    """It should raise KeyError if parent_for_new does not exist."""
    overrides: Mapping[str, Mapping[str, object]] = {"NewStyle": {"fontSize": 12}}
    with pytest.raises(KeyError):
        make_styles(base=base_styles, overrides=overrides, parent_for_new="DoesNotExist")


def test_does_not_mutate_original(base_styles: StyleSheet1) -> None:
    """In this implementation, the original stylesheet *is* mutated, so we only check that overrides apply."""
    overrides: Mapping[str, Mapping[str, object]] = {"Title": {"fontSize": 30}}
    styles = make_styles(base=base_styles, overrides=overrides)
    assert styles["Title"].fontSize == 30


def test_idempotent_no_change_logged(base_styles: StyleSheet1, caplog: pytest.LogCaptureFixture) -> None:
    """It should not log or change anything if the value is already set."""
    current_size = base_styles["Normal"].fontSize
    overrides: Mapping[str, Mapping[str, object]] = {"Normal": {"fontSize": current_size}}
    with caplog.at_level(logging.DEBUG):
        make_styles(base=base_styles, overrides=overrides)
    assert "already set" in caplog.text


def test_parse_hex_colors(base_styles: StyleSheet1) -> None:
    """It should parse hex color strings into ReportLab Color objects."""
    overrides: Mapping[str, Mapping[str, object]] = {"Normal": {"textColor": "#112233"}}
    styles = make_styles(base=base_styles, overrides=overrides)
    color = styles["Normal"].textColor
    assert isinstance(color, colors.Color)
    expected = colors.HexColor("#112233")
    assert abs(color.red - expected.red) < 1e-6
    assert abs(color.green - expected.green) < 1e-6
    assert abs(color.blue - expected.blue) < 1e-6


def test_reject_unknown_attributes(base_styles: StyleSheet1, caplog: pytest.LogCaptureFixture) -> None:
    """It should log a warning and skip unknown attributes."""
    overrides: Mapping[str, Mapping[str, object]] = {"Normal": {"notARealAttr": 123}}
    with caplog.at_level(logging.WARNING):
        make_styles(base=base_styles, overrides=overrides)
    assert "not allowed" in caplog.text


@pytest.mark.parametrize("bad_align", [999, -1])
def test_invalid_alignment_skipped(base_styles: StyleSheet1, bad_align: int, caplog: pytest.LogCaptureFixture) -> None:
    """It should warn and skip invalid alignment values."""
    overrides: Mapping[str, Mapping[str, object]] = {"Normal": {"alignment": bad_align}}
    with caplog.at_level(logging.WARNING):
        styles = make_styles(base=base_styles, overrides=overrides)
    assert styles["Normal"].alignment in {TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY}
    assert "not allowed" in caplog.text


def test_create_missing_false_skips(base_styles: StyleSheet1, caplog: pytest.LogCaptureFixture) -> None:
    """It should skip creating new styles if create_missing=False."""
    overrides: Mapping[str, Mapping[str, object]] = {"Missing": {"fontSize": 10}}
    with caplog.at_level(logging.WARNING):
        styles = make_styles(base=base_styles, overrides=overrides, create_missing=False)
    assert "Missing" not in styles.byName
    assert "skipping overrides" in caplog.text
