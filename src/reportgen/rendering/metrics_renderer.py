from __future__ import annotations

from typing import Any

from reportgen.rendering.geometry import Box
from reportgen.rendering.theme import BrandTheme, FontToken
from reportgen.schemas.blocks import MetricsBlock


def _apply_font(run: Any, token: FontToken, runtime: Any) -> None:
    run.font.name = token.family
    run.font.size = runtime.Pt(token.size_pt)
    run.font.bold = token.bold
    run.font.color.rgb = runtime.RGBColor.from_string(token.color_hex.removeprefix("#"))


def render_metrics_block(
    slide: Any,
    box: Box,
    block: MetricsBlock,
    runtime: Any,
    *,
    theme: BrandTheme,
) -> None:
    """Render metric cards as label + value pairs arranged horizontally.

    When the theme provides separate metric_label_font and metric_value_font,
    the label is rendered in a muted smaller font and the value in a bold larger
    font — giving a professional card appearance. Falls back to single font if
    the extended tokens are not set.
    """
    item_count = len(block.items)
    column_width = box.width / max(item_count, 1)

    label_font = theme.metric_label_font or theme.metric_font
    value_font = theme.metric_value_font or theme.metric_font

    for index, item in enumerate(block.items):
        card_left = box.left + (index * column_width)
        card_width = column_width - 0.15

        # Label row (top portion)
        label_box = Box(
            left=card_left,
            top=box.top,
            width=card_width,
            height=box.height * 0.35,
        )
        label_shape = slide.shapes.add_textbox(
            runtime.Inches(label_box.left),
            runtime.Inches(label_box.top),
            runtime.Inches(label_box.width),
            runtime.Inches(label_box.height),
        )
        label_frame = label_shape.text_frame
        label_frame.clear()
        label_frame.word_wrap = True
        label_para = label_frame.paragraphs[0]
        label_para.alignment = runtime.PP_ALIGN.CENTER
        label_run = label_para.add_run()
        label_run.text = item.label.upper()
        _apply_font(label_run, label_font, runtime)

        # Value row (bottom portion)
        value_box = Box(
            left=card_left,
            top=box.top + box.height * 0.35,
            width=card_width,
            height=box.height * 0.65,
        )
        value_shape = slide.shapes.add_textbox(
            runtime.Inches(value_box.left),
            runtime.Inches(value_box.top),
            runtime.Inches(value_box.width),
            runtime.Inches(value_box.height),
        )
        value_frame = value_shape.text_frame
        value_frame.clear()
        value_frame.word_wrap = True
        value_para = value_frame.paragraphs[0]
        value_para.alignment = runtime.PP_ALIGN.CENTER
        value_run = value_para.add_run()
        value_run.text = str(item.value)
        _apply_font(value_run, value_font, runtime)
