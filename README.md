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
The detailed CV expands six leading cases with their question, contribution,
output and, where supported, analytical approach and interpretation. The two
remaining cases form a compact supporting-work section. Public evidence links
appear beside the relevant cases. Keep delivered recommendations distinct from
adopted changes or measured effects; do not add methods or decisions without
source support.

Methods and tools follow Microsoft and LinkedIn achievements in the concise CV.
MetLife remains in the main experience sequence; the five pre-2012 employers
form a reverse-chronological earlier-career block. `cvBullets` and `cvSummary`
allow concise editing without removing the full website history.

PDF export requests document tags and an outline; the Word CV declares its
language and uses section headings above role headings. These features and
selectable text do not by themselves establish accessibility conformance or
compatibility with every ATS.

```powershell
npm run test:cv
```

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
The 2023 LLM productivity report also verifies named co-authorship. Keep the
AI-readiness eBook at contributing-analyst credit unless personal authorship is
independently established. Research IDs connect cases to their public evidence.
All three publications have individual links in the research section and in
the PDF and Word CV downloads. The post-migration customer case is explicitly
labelled as NPS analysis.
