# Requirements: Milestone 1 — Terminal Profile Engine

## Functional Requirements

### Data Pipeline & Scraping
- **REQ-DATA-01**: `scripts/fetch_contributions.py` must scrape the public calendar HTML fragment at `https://github.com/users/jhaabhijeet864/contributions` without requiring authentication or personal access tokens.
- **REQ-DATA-02**: The scraper must compute:
  - Total contributions across the last 365+ days.
  - Current streak (handling active ongoing days cleanly without false breaks).
  - Longest streak and historical range dates.
  - Active days and active day percentage.
  - Best single day record (date + count).
  - Monthly contribution aggregates.
- **REQ-DATA-03**: Output structured JSON to `data/contributions.json`.

### SVG Generation
- **REQ-SVG-01 (Contribution Heatmap)**:
  - Generate `contrib-heatmap.svg` matching GitHub dark mode (`#0d1117` / `#0a0e14`).
  - Render full 53-week x 7-day grid with month and weekday labels.
  - Include diagonal slide-down reveal animation that plays once and freezes.
  - Include Less -> More legend and live stats footer.
  - Target canvas width: ~860px for terminal window balance.
- **REQ-SVG-02 (Stats Card)**:
  - Generate `stats.svg` with dimensions exactly matching the ASCII portrait (840 x 880).
  - Include terminal window controls and title bar (`jhaabhijeet864@github: ~/stats --live`).
  - Render 6 stat tiles (Current Streak, Longest Streak, Total Contributions, Active Days %, Best Day, Avg / Active Day).
  - Include monthly bar chart visualization at the bottom with animated growth bars.
- **REQ-SVG-03 (ASCII Portrait)**:
  - Generate `ascii.svg` (840 x 880) with terminal frame and title bar (`jhaabhijeet864@github: ~$ ./portrait.sh`).
  - Implement self-typing SMIL row wipes using `<clipPath>` and edge-riding cursor rectangle `<rect>` to animate top-to-bottom in ~6 seconds and freeze.
  - Include persistent blinking cursor prompt footer: `jhaabhijeet864@github:~$ whoami Abhijeet Jha`.

### Automation & CI/CD
- **REQ-CI-01**: `.github/workflows/update-profile-art.yml` must run on scheduled cron (~06:17 UTC daily), manual dispatch (`workflow_dispatch`), and push to `main`.
- **REQ-CI-02**: Workflow must install lightweight requirements (`requests`, `beautifulsoup4`), run the data fetcher, render `contrib-heatmap.svg` and `stats.svg`, and auto-commit changes with `[skip ci]`.

### Profile README Layout
- **REQ-LAYOUT-01**: Structure `README.md` with a centered terminal interface.
- **REQ-LAYOUT-02**: Use `<h3><code>...</code></h3>` for shell command headers to avoid disruptive GitHub markdown horizontal lines.
- **REQ-LAYOUT-03**: Align the 860px contribution heatmap and 2-column table (`420px + 420px`) for seamless visual edges.
- **REQ-LAYOUT-04**: Preserve and highlight Abhijeet's AI Founder identity, key projects (KrocPDF, GPU Engine, Agentic Systems), organizations, and contact links.
