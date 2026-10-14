# Career portfolio

Static, accessible career portfolio published from `main` by GitHub Pages.

## Update the content

Edit `assets/portfolio.json` for career content, `site-template.html` for the
website design, and `build.cjs` for the CV layouts. Generated HTML, Word and PDF
downloads are committed so visitors do not need a build service.

```powershell
npm ci
python -m pip install -r requirements.txt
python -m playwright install chromium
npm run build
npm run render
```

The render step checks that the concise PDF has two pages and the detailed PDF
has four. Inspect both layouts after changing content. The single-column Word
CV uses standard headings, selectable text and no layout tables.

The selected-work collection spans Microsoft, LinkedIn Glint, MetLife and
Telefónica. Keep it curated around delivered research, analytical workstreams
and measurement programmes, not routine activity counts. The three opening
evidence links are sourced from `highlights` in `assets/portfolio.json`.
The detailed CV divides the selected cases evenly across its two appendix
pages. Methods and tools follow Microsoft and LinkedIn achievements in the
concise CV rather than displacing the experience from the opening page.

## Theme options

The header theme selector offers Light, Dark, Premium Editorial and Retro '95.
Selections are saved in browser storage when available. A `scoutTheme` query
parameter (`light`, `dark`, `premium` or `retro95`) overrides the saved preference
for shareable previews; changing the selector updates that preview parameter.
Without a saved selection or valid preview, the site follows the browser's
light/dark preference. If storage is blocked, switching still works for the
current visit and an explanatory message is shown.

Themes only affect the screen presentation. The printable CV and PDF/Word
downloads retain their professional formatting.

```powershell
npm run test:themes
```

## Publication boundaries

This repository contains only public-safe career content. Keep original CVs,
private career workbooks, review conversations, customer data and internal
source documents outside this repository. Project descriptions distinguish
personal contribution from research scope and wider outcomes.

Only LinkedIn is used for public contact. Research links point to public
publications. Full-report co-author credit is verified against the report's
cover-page author list and is distinct from sole authorship or study ownership.
