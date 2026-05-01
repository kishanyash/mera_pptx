"""Slide decorators: header band, footer bar, divider rule, and rating badge.

These decorators are applied by the rendering engine after the core slide content
is placed. They enforce the branded chrome on every slide type.
"""
from __future__ import annotations

from typing import Any

from reportgen.rendering.geometry import Box
from reportgen.rendering.theme import BrandTheme, FontToken


def _hex_to_rgb(runtime: Any, hex_color: str) -> Any:
    return runtime.RGBColor.from_string(hex_color.removeprefix("#"))


def _add_filled_rect(
    slide: Any,
    box: Box,
    fill_hex: str,
    runtime: Any,
) -> Any:
    """Add a solid-filled rectangle shape to the slide."""
    shape = slide.shapes.add_shape(
        runtime.MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        runtime.Inches(box.left),
        runtime.Inches(box.top),
        runtime.Inches(box.width),
        runtime.Inches(box.height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _hex_to_rgb(runtime, fill_hex)
    shape.line.fill.background()
    return shape


def _add_label(
    slide: Any,
    box: Box,
    text: str,
    font_token: FontToken,
    runtime: Any,
    align: Any | None = None,
) -> Any:
    """Add a small text label at a specific position."""
    shape = slide.shapes.add_textbox(
        runtime.Inches(box.left),
        runtime.Inches(box.top),
        runtime.Inches(box.width),
        runtime.Inches(box.height),
    )
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    if align is not None:
        paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = font_token.family
    run.font.size = runtime.Pt(font_token.size_pt)
    run.font.bold = font_token.bold
    run.font.color.rgb = _hex_to_rgb(runtime, font_token.color_hex)
    return shape


def _add_thin_line(
    slide: Any,
    left: float,
    top: float,
    width: float,
    color_hex: str,
    runtime: Any,
    height: float = 0.015,
) -> Any:
    """Add a thin horizontal divider line."""
    shape = slide.shapes.add_shape(
        runtime.MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        runtime.Inches(left),
        runtime.Inches(top),
        runtime.Inches(width),
        runtime.Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _hex_to_rgb(runtime, color_hex)
    shape.line.fill.background()
    return shape


# ---------------------------------------------------------------------------
# Public decorators
# ---------------------------------------------------------------------------

def apply_header_band(
    slide: Any,
    theme: BrandTheme,
    runtime: Any,
    *,
    company_name: str = "",
    page_label: str = "",
) -> None:
    """Dark header band across the full slide width with firm name and page info."""
    geo = theme.slide_geometry
    header_font = theme.header_font or theme.subtitle_font

    # Header band rectangle
    _add_filled_rect(
        slide,
        Box(left=0, top=0, width=geo.width_inches, height=geo.header_height_inches),
        theme.palette.header_band,
        runtime,
    )

    # Firm name on the left
    _add_label(
        slide,
        Box(left=0.5, top=0.04, width=3.5, height=geo.header_height_inches - 0.08),
        theme.firm_name,
        header_font,
        runtime,
        align=runtime.PP_ALIGN.LEFT,
    )

    # Company name / page label on the right
    right_text = company_name
    if page_label:
        right_text = f"{company_name}  |  {page_label}" if company_name else page_label

    if right_text:
        _add_label(
            slide,
            Box(
                left=geo.width_inches - 5.0,
                top=0.04,
                width=4.5,
                height=geo.header_height_inches - 0.08,
            ),
            right_text,
            header_font,
            runtime,
            align=runtime.PP_ALIGN.RIGHT,
        )


def apply_divider_line(
    slide: Any,
    theme: BrandTheme,
    runtime: Any,
) -> None:
    """Thin accent-colored divider line below the header region."""
    geo = theme.slide_geometry
    _add_thin_line(
        slide,
        left=geo.content_margin_left,
        top=geo.divider_line_top,
        width=geo.width_inches - geo.content_margin_left - geo.content_margin_right,
        color_hex=theme.palette.accent,
        runtime=runtime,
    )


def apply_footer_bar(
    slide: Any,
    theme: BrandTheme,
    runtime: Any,
    *,
    analyst: str = "",
    report_date: str = "",
    page_number: int | None = None,
) -> None:
    """Subtle footer band at the bottom with analyst, date, and page number."""
    geo = theme.slide_geometry
    footer_font = theme.footer_font or FontToken(
        family="Aptos", size_pt=7, bold=False, color_hex="#6B7A8D"
    )

    footer_top = geo.height_inches - geo.footer_height_inches

    # Footer background band
    _add_filled_rect(
        slide,
        Box(left=0, top=footer_top, width=geo.width_inches, height=geo.footer_height_inches),
        theme.palette.footer_band,
        runtime,
    )

    # Left: analyst + date
    left_parts = [p for p in [analyst, report_date] if p]
    if left_parts:
        _add_label(
            slide,
            Box(left=0.5, top=footer_top + 0.04, width=5.0, height=geo.footer_height_inches - 0.08),
            "  |  ".join(left_parts),
            footer_font,
            runtime,
            align=runtime.PP_ALIGN.LEFT,
        )

    # Center: firm name
    _add_label(
        slide,
        Box(
            left=geo.width_inches / 2 - 2.0,
            top=footer_top + 0.04,
            width=4.0,
            height=geo.footer_height_inches - 0.08,
        ),
        theme.firm_name,
        footer_font,
        runtime,
        align=runtime.PP_ALIGN.CENTER,
    )

    # Right: page number
    if page_number is not None:
        _add_label(
            slide,
            Box(
                left=geo.width_inches - 2.0,
                top=footer_top + 0.04,
                width=1.5,
                height=geo.footer_height_inches - 0.08,
            ),
            f"Page {page_number}",
            footer_font,
            runtime,
            align=runtime.PP_ALIGN.RIGHT,
        )


def apply_rating_badge(
    slide: Any,
    rating: str,
    theme: BrandTheme,
    runtime: Any,
    *,
    box: Box | None = None,
) -> None:
    """Rounded rating badge (BUY/HOLD/SELL) with color-coded background."""
    badge_font = theme.rating_badge_font or FontToken(
        family="Aptos Display", size_pt=16, bold=True, color_hex="#FFFFFF"
    )
    color = theme.get_rating_color(rating)

    # Default position: upper-right area of the content zone
    if box is None:
        geo = theme.slide_geometry
        box = Box(
            left=geo.width_inches - geo.content_margin_right - 2.0,
            top=geo.content_top - 0.15,
            width=2.0,
            height=0.55,
        )

    shape = slide.shapes.add_shape(
        runtime.MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        runtime.Inches(box.left),
        runtime.Inches(box.top),
        runtime.Inches(box.width),
        runtime.Inches(box.height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _hex_to_rgb(runtime, color)
    shape.line.fill.background()

    # Adjust corner radius
    if hasattr(shape, "adjustments") and len(shape.adjustments) > 0:
        shape.adjustments[0] = 0.25

    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = False
    paragraph = frame.paragraphs[0]
    paragraph.alignment = runtime.PP_ALIGN.CENTER
    run = paragraph.add_run()
    run.text = rating.upper()
    run.font.name = badge_font.family
    run.font.size = runtime.Pt(badge_font.size_pt)
    run.font.bold = badge_font.bold
    run.font.color.rgb = _hex_to_rgb(runtime, badge_font.color_hex)


def apply_cover_background(
    slide: Any,
    theme: BrandTheme,
    runtime: Any,
) -> None:
    """Apply the hero cover slide background — dark primary fill with accent bar."""
    cover = theme.cover
    if cover is None:
        return

    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = _hex_to_rgb(runtime, cover.background_color)

    # Accent bar near the bottom third
    geo = theme.slide_geometry
    bar_top = geo.height_inches * 0.62
    _add_filled_rect(
        slide,
        Box(left=0, top=bar_top, width=geo.width_inches, height=0.06),
        cover.accent_bar_color,
        runtime,
    )

    # Thin accent line near the top
    _add_thin_line(
        slide,
        left=0.5,
        top=0.5,
        width=geo.width_inches - 1.0,
        color_hex=cover.accent_bar_color,
        runtime=runtime,
        height=0.02,
    )
