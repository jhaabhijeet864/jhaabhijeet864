# Roadmap: Terminal Profile Engine

## Phase 1: Comparative Architecture Analysis & Codebase Audit
- [x] Analyze reference implementation (`AVIVASHISHTA29/AVIVASHISHTA29`).
- [x] Audit current profile codebase (`jhaabhijeet864/jhaabhijeet864`).
- [x] Classify findings and define auto-fix vs manual boundaries.

## Phase 2: Toolchain & Data Pipeline Scaffolding
- [x] Establish modular directory structure (`scripts/`, `data/`).
- [x] Create lightweight dependencies specification (`scripts/requirements.txt`).
- [x] Implement robust public scraper (`scripts/fetch_contributions.py`) for `jhaabhijeet864`.
- [x] Verify live data fetching and test snapshot generation (`data/contributions.json`).

## Phase 3: Core Vector Engine Implementation
- [x] Implement animated heatmap generator (`scripts/render_heatmap_svg.py`).
- [x] Implement animated stats / Neofetch generator (`scripts/render_stats_svg.py`).
- [x] Implement self-typing SMIL vector ASCII portrait generator (`scripts/make_ascii_svg.py`).
- [x] Provide photo pre-processing script (`scripts/prep_photo.py`) for future photo refreshes.

## Phase 4: CI/CD & Automation Workflow
- [x] Implement `.github/workflows/update-profile-art.yml` with daily cron and auto-commit.
- [x] Verify permission gates (`contents: write`) and concurrency handling.

## Phase 5: Terminal README Integration & Audit-Fix
- [x] Eliminate third-party Vercel & Demolab widget dependencies.
- [x] Replace static raster `ascii-art.png` with animated `ascii.svg`.
- [x] Compose cohesive terminal README with aligned widths and developer identity.
- [x] Run full end-to-end verification and audit report.
