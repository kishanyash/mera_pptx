from pydantic import BaseModel, ConfigDict, Field

from reportgen.rendering.geometry import Box, PlaceholderGeometry
from reportgen.schemas.common import NonEmptyString
from reportgen.schemas.slides import SlideLayout


class BlockRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    block_type: NonEmptyString
    min_count: int = Field(ge=0)
    max_count: int | None = Field(default=None, ge=1)


class LayoutDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    layout: SlideLayout
    display_name: NonEmptyString
    allowed_block_types: set[NonEmptyString]
    required_blocks: list[BlockRequirement] = Field(default_factory=list)
    placeholders: list[PlaceholderGeometry] = Field(default_factory=list)
    has_header: bool = True
    has_footer: bool = True
    has_rating_badge: bool = False
    notes: str | None = None


def _ph(name: str, left: float, top: float, width: float, height: float) -> PlaceholderGeometry:
    return PlaceholderGeometry(name=name, box=Box(left=left, top=top, width=width, height=height))


# All layouts use widescreen 13.333" x 7.5" geometry.
# Content area: left=0.65, right=0.65, top=1.15 (below header+divider), bottom=6.85 (above footer).
# Usable content width: ~12.0"  |  Usable content height: ~5.7"

LAYOUT_REGISTRY: dict[SlideLayout, LayoutDefinition] = {
    "cover_slide": LayoutDefinition(
        layout="cover_slide",
        display_name="Cover Slide",
        allowed_block_types={"text", "metrics"},
        required_blocks=[BlockRequirement(block_type="metrics", min_count=1, max_count=1)],
        has_header=False,
        has_footer=False,
        has_rating_badge=True,
        placeholders=[
            _ph("title", 0.8, 1.5, 10.0, 1.2),
            _ph("subtitle", 0.8, 2.9, 9.0, 0.6),
            _ph("metrics", 0.8, 5.0, 10.0, 1.4),
        ],
        notes="Hero cover: dark background, large title, rating badge, and headline metrics.",
    ),
    "investment_thesis": LayoutDefinition(
        layout="investment_thesis",
        display_name="Investment Thesis",
        allowed_block_types={"text", "bullets"},
        required_blocks=[
            BlockRequirement(block_type="text", min_count=1, max_count=1),
            BlockRequirement(block_type="bullets", min_count=1, max_count=1),
        ],
        has_rating_badge=True,
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("text", 0.7, 1.2, 5.5, 5.2),
            _ph("bullets", 6.6, 1.2, 5.7, 5.2),
        ],
    ),
    "company_snapshot": LayoutDefinition(
        layout="company_snapshot",
        display_name="Company Snapshot",
        allowed_block_types={"text", "metrics"},
        required_blocks=[
            BlockRequirement(block_type="text", min_count=1, max_count=1),
            BlockRequirement(block_type="metrics", min_count=1, max_count=1),
        ],
        has_rating_badge=True,
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("text", 0.7, 1.2, 6.0, 4.0),
            _ph("metrics", 7.2, 1.2, 5.4, 3.5),
        ],
    ),
    "text_plus_bullets": LayoutDefinition(
        layout="text_plus_bullets",
        display_name="Text Plus Bullets",
        allowed_block_types={"text", "bullets"},
        required_blocks=[
            BlockRequirement(block_type="text", min_count=1, max_count=1),
            BlockRequirement(block_type="bullets", min_count=1, max_count=1),
        ],
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("text", 0.7, 1.2, 5.5, 5.2),
            _ph("bullets", 6.6, 1.2, 5.7, 5.2),
        ],
    ),
    "text_plus_chart": LayoutDefinition(
        layout="text_plus_chart",
        display_name="Text Plus Chart",
        allowed_block_types={"text", "chart"},
        required_blocks=[
            BlockRequirement(block_type="text", min_count=1, max_count=1),
            BlockRequirement(block_type="chart", min_count=1, max_count=1),
        ],
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("text", 0.7, 1.2, 4.5, 5.2),
            _ph("chart", 5.6, 1.1, 6.7, 5.4),
        ],
    ),
    "full_width_chart": LayoutDefinition(
        layout="full_width_chart",
        display_name="Full Width Chart",
        allowed_block_types={"chart"},
        required_blocks=[BlockRequirement(block_type="chart", min_count=1, max_count=1)],
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("chart", 0.7, 1.2, 11.8, 5.3),
        ],
    ),
    "full_table": LayoutDefinition(
        layout="full_table",
        display_name="Full Table",
        allowed_block_types={"table"},
        required_blocks=[BlockRequirement(block_type="table", min_count=1, max_count=1)],
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("table", 0.65, 1.2, 12.0, 5.3),
        ],
    ),
    "valuation_summary": LayoutDefinition(
        layout="valuation_summary",
        display_name="Valuation Summary",
        allowed_block_types={"text", "metrics", "table"},
        required_blocks=[
            BlockRequirement(block_type="text", min_count=1, max_count=1),
            BlockRequirement(block_type="metrics", min_count=1, max_count=1),
        ],
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("text", 0.7, 1.2, 5.0, 2.0),
            _ph("metrics", 6.2, 1.2, 6.2, 2.0),
            _ph("table", 0.65, 3.5, 12.0, 3.0),
        ],
    ),
    "risks_and_catalysts": LayoutDefinition(
        layout="risks_and_catalysts",
        display_name="Risks And Catalysts",
        allowed_block_types={"bullets", "text"},
        required_blocks=[BlockRequirement(block_type="bullets", min_count=1, max_count=1)],
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("bullets", 0.7, 1.2, 11.5, 5.3),
        ],
    ),
    "disclaimer": LayoutDefinition(
        layout="disclaimer",
        display_name="Disclaimer",
        allowed_block_types={"text"},
        required_blocks=[BlockRequirement(block_type="text", min_count=1, max_count=1)],
        placeholders=[
            _ph("title", 0.65, 0.55, 9.0, 0.55),
            _ph("text", 0.7, 1.2, 11.5, 5.3),
        ],
    ),
}


def get_layout_definition(layout: SlideLayout) -> LayoutDefinition:
    return LAYOUT_REGISTRY[layout]
