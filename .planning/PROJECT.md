# Project: jhaabhijeet864 GitHub Profile Engine

## Vision
Transform the personal GitHub profile (`jhaabhijeet864/jhaabhijeet864`) from a hybrid setup dependent on flaky third-party widget servers and static raster images into an autonomous, ultra-fast, zero-token, self-contained terminal experience rendered entirely through animated vector SVGs and daily GitHub Actions automation.

## Core Architecture Decisions
1. **Self-Contained Vector SVGs over Hosted Third-Party APIs**:
   - Retire dependencies on external services (`github-readme-stats-eight-theta.vercel.app`, `streak-stats.demolab.com`).
   - Generate native SVGs directly inside the repository (`contrib-heatmap.svg`, `stats.svg`, `ascii.svg`).
   - Zero cold starts, zero rate limits, zero broken image badges, zero third-party downtime.
2. **Zero-Token Scraping via Public Calendar Endpoint**:
   - Scrape `https://github.com/users/jhaabhijeet864/contributions` directly using lightweight `requests` + `beautifulsoup4`.
   - No GitHub Personal Access Token (PAT) required, no GraphQL quota exhaustion, no secret management.
   - Saves normalized statistics to `data/contributions.json`.
3. **SMIL & CSS Vector Animations**:
   - GitHub sanitizes `<script>` and inline CSS, but natively renders SVG files referenced via `<img>` and executes their internal SMIL and CSS `@keyframes`.
   - ASCII portrait types itself in row-by-row using synchronized `<clipPath>` wipes with an edge-riding cursor, freezing once completed.
   - Contribution heatmap reveals diagonally on load.
   - Stats card features live counter animations and animated monthly contribution bars.
4. **Terminal Layout & Brand Continuity**:
   - Retain Abhijeet's identity as Co-Founder of Pathixo, Chief AIML Engineer, and builder of deep AI/ML projects (KrocPDF, GPU Hardware Engine, Self-Improving Agentic System).
   - Lay out sections using Unix shell commands (`./contributions.sh`, `whoami`, `cat bio.md`, `./projects.sh`, `./ecosystem.sh`).
   - Match exact canvas dimensions (840x880) so portrait and stats tiles achieve 1:1 pixel parity side-by-side in GitHub markdown tables.

## Milestones
- **Milestone 1 (Active)**: Terminal Profile Engine Architecture & Deployment (ASCII Portrait, Neofetch Stats Card, Live Heatmap, Actions Cron, Layout Integration).
