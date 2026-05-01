# PPTX Research Report Generator

This repository contains the foundation for a PPTX-first research report generator for equity research and wealth-management workflows.

## Completed Phases

### Phase 1–8: Foundation & Pipeline Skeleton
- Canonical source-of-truth schema (Pydantic models)
- Input ingestion, validation, and normalization
- Mock AI slide planner + report spec builder
- Layout registry with 10 slide layouts
- Deterministic PPTX renderer (text, bullets, metrics, charts, tables)
- PDF export (LibreOffice / PowerPoint backends)
- Orchestration pipeline with run manifests and QA checks
- Regression harness across sample bundles

### Phase 9: Brand Shell & Theme System
- Externalized `assets/themes/brand_theme.json` — colors, fonts, chart palette, rating-color map
- Theme loader replaces hardcoded defaults; engine loads from JSON or falls back gracefully
- Widescreen 16:9 slide geometry (13.333" × 7.5")
- Header band with firm name and slide context on every content slide
- Accent divider line below header
- Footer bar with analyst, date, and page number
- Dark hero cover slide with accent bars and large typography
- Color-coded rating badge (BUY/HOLD/SELL/REDUCE) on cover, thesis, and snapshot slides
- Metric cards redesigned: label/value split with distinct font tokens
- Chart palette extended to 8 harmonious colors

## Current Capabilities

- typed Pydantic models for the report domain
- sample input bundles under `data/samples/` (ABC, XYZ)
- CLI command to validate and normalize the bundle with business-rule checks
- full end-to-end pipeline: `validate → plan → build spec → render PPTX → export PDF`
- branded slide output that reads as a professional sell-side research note

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
reportgen run-pipeline --bundle data/samples/bundles/abc_bundle.json --out-root output
```

## CLI Commands

```bash
reportgen validate-input   --bundle <path>
reportgen plan-slides      --bundle <path> --out <path>
reportgen build-report-spec --bundle <path> --out <path>
reportgen render-report    --spec <path> --out <path>
reportgen export-pdf       --pptx <path> --out <path>
reportgen run-pipeline     --bundle <path> --out-root <dir>
```

## Repo Structure

- `src/reportgen/schemas/` — canonical domain models
- `src/reportgen/ingestion/` — input loading, validation, normalization
- `src/reportgen/ai/` — AI planner (mock + Anthropic client)
- `src/reportgen/planning/` — layout policy, report spec builder, slide plan validation
- `src/reportgen/rendering/` — PPTX engine, layout registry, theme, decorators
- `src/reportgen/export/` — PDF conversion
- `src/reportgen/orchestration/` — end-to-end pipeline
- `src/reportgen/storage/` — filesystem store, manifests
- `src/reportgen/qa/` — validators, render checks, regression
- `assets/themes/` — externalized brand theme JSON
- `data/samples/` — reference input bundles
- `project-blueprint.md` — full implementation direction
- `muscle-plan.md` — phases 9–14 roadmap

## Next Planned Steps

- Phase 10: Finance Content Depth (expanded layouts + schema)
- Phase 11: Real AI Planner (Anthropic replaces mock as default)
- Phase 12: Numeric Integrity & Formatting Authority
- Phase 13: Chart Quality Pass
- Phase 14: Compliance, PDF, and Pilot Hardening
