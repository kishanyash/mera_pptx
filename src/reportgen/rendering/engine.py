from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportgen.config import settings
from reportgen.rendering.chart_renderer import render_chart_block
from reportgen.rendering.data_resolver import RenderDataResolver
from reportgen.rendering.layout_registry import LayoutDefinition, get_layout_definition
from reportgen.rendering.metrics_renderer import render_metrics_block
from reportgen.rendering.pptx_runtime import load_pptx_runtime
from reportgen.rendering.slide_decorators import (
    apply_cover_background,
    apply_divider_line,
    apply_footer_bar,
    apply_header_band,
    apply_rating_badge,
)
from reportgen.rendering.table_renderer import render_table_block
from reportgen.rendering.text_renderer import add_bullet_list, add_textbox
from reportgen.rendering.theme import DEFAULT_THEME, BrandTheme, load_theme_from_json
from reportgen.schemas.blocks import BulletBlock, MetricsBlock, TextBlock
from reportgen.schemas.charts import ChartBlock
from reportgen.schemas.report import ReportSpec
from reportgen.schemas.slides import SlideSpec
from reportgen.schemas.tables import TableBlock


def _resolve_theme() -> BrandTheme:
    """Load theme from configured path, or fall back to DEFAULT_THEME."""
    if settings.theme_path and settings.theme_path.exists():
        return load_theme_from_json(settings.theme_path)
    # Also check for the standard location relative to project root
    standard_path = Path("assets/themes/brand_theme.json")
    if standard_path.exists():
        return load_theme_from_json(standard_path)
    return DEFAULT_THEME


class PresentationRenderer:
    def __init__(self, theme: BrandTheme | None = None) -> None:
        self.theme = theme or _resolve_theme()

    def render_to_path(self, report_spec: ReportSpec, out_path: Path) -> Path:
        runtime = load_pptx_runtime()
        presentation = runtime.Presentation()

        # Widescreen 16:9 slide dimensions
        geo = self.theme.slide_geometry
        presentation.slide_width = runtime.Inches(geo.width_inches)
        presentation.slide_height = runtime.Inches(geo.height_inches)

        resolver = RenderDataResolver(report_spec)

        for index, slide_spec in enumerate(report_spec.slides):
            self._render_slide(
                presentation,
                slide_spec,
                runtime,
                resolver,
                report_spec=report_spec,
                slide_index=index,
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        presentation.save(out_path)
        return out_path

    def _render_slide(
        self,
        presentation: Any,
        slide_spec: SlideSpec,
        runtime: Any,
        resolver: RenderDataResolver,
        *,
        report_spec: ReportSpec,
        slide_index: int,
    ) -> None:
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        layout_definition = get_layout_definition(slide_spec.layout)
        is_cover = slide_spec.layout == "cover_slide"

        # --- Background ---
        if is_cover:
            apply_cover_background(slide, self.theme, runtime)
        else:
            self._apply_background(slide, runtime)

        # --- Header band (non-cover slides) ---
        if layout_definition.has_header and not is_cover:
            company_name = report_spec.company.name
            page_label = f"Slide {slide_index + 1} of {len(report_spec.slides)}"
            apply_header_band(
                slide,
                self.theme,
                runtime,
                company_name=company_name,
                page_label=page_label,
            )
            apply_divider_line(slide, self.theme, runtime)

        # --- Title ---
        title_box = self._placeholder(layout_definition, "title")
        if title_box:
            if is_cover and self.theme.cover:
                font = self.theme.cover.title_font
            else:
                font = self.theme.title_font
            add_textbox(
                slide,
                title_box,
                slide_spec.title,
                font,
                runtime,
                theme=self.theme,
            )

        # --- Subtitle ---
        if slide_spec.subtitle:
            subtitle_box = self._placeholder(layout_definition, "subtitle")
            if subtitle_box:
                if is_cover and self.theme.cover:
                    font = self.theme.cover.subtitle_font
                else:
                    font = self.theme.subtitle_font
                add_textbox(
                    slide,
                    subtitle_box,
                    slide_spec.subtitle,
                    font,
                    runtime,
                    theme=self.theme,
                )

        # --- Content blocks ---
        counters: dict[str, int] = {}
        for block in slide_spec.blocks:
            block_type = getattr(block, "type", "")
            counters[block_type] = counters.get(block_type, 0) + 1
            placeholder = self._placeholder(layout_definition, block_type)
            if not placeholder:
                continue

            if isinstance(block, TextBlock):
                add_textbox(slide, placeholder, block.content, self.theme.body_font, runtime, theme=self.theme)
            elif isinstance(block, BulletBlock):
                add_bullet_list(slide, placeholder, list(block.items), self.theme.body_font, runtime, theme=self.theme)
            elif isinstance(block, MetricsBlock):
                render_metrics_block(slide, placeholder, block, runtime, theme=self.theme)
            elif isinstance(block, ChartBlock):
                render_chart_block(slide, placeholder, block, resolver, runtime, theme=self.theme)
            elif isinstance(block, TableBlock):
                render_table_block(slide, placeholder, block, resolver, runtime, theme=self.theme)

        # --- Rating badge (on designated layouts) ---
        if layout_definition.has_rating_badge:
            rating = report_spec.metadata.rating
            apply_rating_badge(slide, rating, self.theme, runtime)

        # --- Footer bar (non-cover slides) ---
        if layout_definition.has_footer and not is_cover:
            apply_footer_bar(
                slide,
                self.theme,
                runtime,
                analyst=report_spec.metadata.analyst,
                report_date=str(report_spec.metadata.report_date),
                page_number=slide_index + 1,
            )

    def _apply_background(self, slide: Any, runtime: Any) -> None:
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = runtime.RGBColor.from_string(
            self.theme.palette.background.removeprefix("#")
        )

    def _placeholder(self, layout_definition: LayoutDefinition, name: str):
        for placeholder in layout_definition.placeholders:
            if placeholder.name == name:
                return placeholder.box
        return None

def load_report_spec(path: Path) -> ReportSpec:
    return ReportSpec.model_validate(json.loads(path.read_text(encoding="utf-8")))
