import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from reportgen.schemas.common import NonEmptyString


class FontToken(BaseModel):
    model_config = ConfigDict(extra="forbid")

    family: NonEmptyString
    size_pt: int = Field(gt=0)
    bold: bool = False
    color_hex: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class ThemePalette(BaseModel):
    model_config = ConfigDict(extra="ignore")

    primary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    accent: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    text: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    muted_text: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    white: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    positive: str = Field(default="#1A8754", pattern=r"^#[0-9A-Fa-f]{6}$")
    negative: str = Field(default="#C0392B", pattern=r"^#[0-9A-Fa-f]{6}$")
    neutral: str = Field(default="#6B7A8D", pattern=r"^#[0-9A-Fa-f]{6}$")
    header_band: str = Field(default="#0B2545", pattern=r"^#[0-9A-Fa-f]{6}$")
    footer_band: str = Field(default="#E8E4DC", pattern=r"^#[0-9A-Fa-f]{6}$")


class CoverTheme(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title_font: FontToken
    subtitle_font: FontToken
    accent_bar_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    background_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class SlideGeometry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width_inches: float = 13.333
    height_inches: float = 7.5
    header_height_inches: float = 0.45
    footer_height_inches: float = 0.35
    content_margin_left: float = 0.65
    content_margin_right: float = 0.65
    content_top: float = 1.15
    content_bottom: float = 6.85
    divider_line_top: float = 0.95


class BrandTheme(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: NonEmptyString
    palette: ThemePalette
    chart_palette: list[str] = Field(default_factory=list)
    rating_colors: dict[str, str] = Field(default_factory=dict)
    title_font: FontToken
    subtitle_font: FontToken
    body_font: FontToken
    metric_font: FontToken
    metric_label_font: FontToken | None = None
    metric_value_font: FontToken | None = None
    header_font: FontToken | None = None
    footer_font: FontToken | None = None
    rating_badge_font: FontToken | None = None
    cover: CoverTheme | None = None
    slide_geometry: SlideGeometry = Field(default_factory=SlideGeometry)
    firm_name: str = "Research"
    logo_path: str | None = None

    def get_rating_color(self, rating: str) -> str:
        """Return the hex color for a rating, falling back to accent."""
        return self.rating_colors.get(rating.upper(), self.palette.accent)


DEFAULT_THEME = BrandTheme(
    name="research_default",
    palette=ThemePalette(
        primary="#0B2545",
        secondary="#13497B",
        accent="#D4A843",
        text="#1A1F27",
        muted_text="#6B7A8D",
        background="#F8F6F2",
        white="#FFFFFF",
        positive="#1A8754",
        negative="#C0392B",
        neutral="#6B7A8D",
        header_band="#0B2545",
        footer_band="#E8E4DC",
    ),
    chart_palette=["#0B2545", "#13497B", "#D4A843", "#1A8754", "#C0392B", "#6B7A8D"],
    rating_colors={"BUY": "#1A8754", "HOLD": "#D4A843", "SELL": "#C0392B", "REDUCE": "#E67E22"},
    title_font=FontToken(family="Aptos Display", size_pt=24, bold=True, color_hex="#0B2545"),
    subtitle_font=FontToken(family="Aptos", size_pt=13, bold=False, color_hex="#6B7A8D"),
    body_font=FontToken(family="Aptos", size_pt=11, bold=False, color_hex="#1A1F27"),
    metric_font=FontToken(family="Aptos", size_pt=14, bold=True, color_hex="#0B2545"),
    metric_label_font=FontToken(family="Aptos", size_pt=9, bold=False, color_hex="#6B7A8D"),
    metric_value_font=FontToken(family="Aptos", size_pt=18, bold=True, color_hex="#0B2545"),
    header_font=FontToken(family="Aptos", size_pt=8, bold=False, color_hex="#FFFFFF"),
    footer_font=FontToken(family="Aptos", size_pt=7, bold=False, color_hex="#6B7A8D"),
    rating_badge_font=FontToken(family="Aptos Display", size_pt=16, bold=True, color_hex="#FFFFFF"),
    cover=CoverTheme(
        title_font=FontToken(family="Aptos Display", size_pt=32, bold=True, color_hex="#FFFFFF"),
        subtitle_font=FontToken(family="Aptos", size_pt=16, bold=False, color_hex="#D4A843"),
        accent_bar_color="#D4A843",
        background_color="#0B2545",
    ),
    slide_geometry=SlideGeometry(),
    firm_name="Tikona Research",
)


def load_theme_from_json(path: Path) -> BrandTheme:
    """Load a BrandTheme from an externalized JSON file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return BrandTheme.model_validate(payload)
