"""Tests for Phase 9: Brand Shell & Theme System."""
from pathlib import Path

import pytest

from reportgen.rendering.theme import (
    BrandTheme,
    CoverTheme,
    FontToken,
    SlideGeometry,
    ThemePalette,
    load_theme_from_json,
)


def test_brand_theme_json_loads_from_file():
    """The externalized brand_theme.json loads cleanly into a BrandTheme."""
    path = Path("assets/themes/brand_theme.json")
    if not path.exists():
        pytest.skip("brand_theme.json not found")
    theme = load_theme_from_json(path)
    assert theme.name == "tikona_research"
    assert theme.firm_name == "Tikona Research"
    assert len(theme.chart_palette) >= 4
    assert "BUY" in theme.rating_colors
    assert "SELL" in theme.rating_colors


def test_brand_theme_has_cover_definition():
    """Theme should include a cover-specific sub-theme."""
    path = Path("assets/themes/brand_theme.json")
    if not path.exists():
        pytest.skip("brand_theme.json not found")
    theme = load_theme_from_json(path)
    assert theme.cover is not None
    assert theme.cover.title_font.size_pt >= 28
    assert theme.cover.background_color.startswith("#")


def test_rating_color_lookup():
    """get_rating_color returns the correct mapped color."""
    path = Path("assets/themes/brand_theme.json")
    if not path.exists():
        pytest.skip("brand_theme.json not found")
    theme = load_theme_from_json(path)
    buy_color = theme.get_rating_color("BUY")
    sell_color = theme.get_rating_color("SELL")
    fallback = theme.get_rating_color("UNKNOWN")
    assert buy_color != sell_color
    assert fallback == theme.palette.accent


def test_slide_geometry_defaults():
    """SlideGeometry has sensible widescreen defaults."""
    geo = SlideGeometry()
    assert geo.width_inches == pytest.approx(13.333, rel=0.01)
    assert geo.height_inches == 7.5
    assert geo.content_top > geo.header_height_inches


def test_layout_registry_has_header_footer_flags():
    """Layout definitions should include the new has_header / has_footer flags."""
    from reportgen.rendering.layout_registry import LAYOUT_REGISTRY

    cover = LAYOUT_REGISTRY["cover_slide"]
    assert cover.has_header is False
    assert cover.has_footer is False
    assert cover.has_rating_badge is True

    thesis = LAYOUT_REGISTRY["investment_thesis"]
    assert thesis.has_header is True
    assert thesis.has_footer is True
    assert thesis.has_rating_badge is True

    disclaimer = LAYOUT_REGISTRY["disclaimer"]
    assert disclaimer.has_header is True
    assert disclaimer.has_footer is True
    assert disclaimer.has_rating_badge is False


def test_branded_pipeline_produces_valid_pptx(tmp_path):
    """End-to-end: the branded pipeline should produce a PPTX with correct slide count."""
    from pptx import Presentation

    from reportgen.orchestration.pipeline import run_local_pipeline

    bundle_path = Path("data/samples/bundles/abc_bundle.json")
    if not bundle_path.exists():
        pytest.skip("Sample bundle not found")

    result = run_local_pipeline(bundle_path, tmp_path)
    assert result.pptx_path.exists()
    assert result.pptx_path.stat().st_size > 0

    prs = Presentation(result.pptx_path)
    assert len(prs.slides) == 7  # 7 slides from mock planner

    # Widescreen dimensions (in EMU: 1 inch = 914400 EMU)
    expected_width_emu = int(13.333 * 914400)
    assert abs(prs.slide_width - expected_width_emu) < 914400 * 0.1  # within 0.1 inch tolerance
