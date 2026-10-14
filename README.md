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

## Publication boundaries

This repository contains only public-safe career content. Keep original CVs,
private career workbooks, review conversations, customer data and internal
source documents outside this repository. Project descriptions distinguish
personal contribution from research scope and wider outcomes.

Only LinkedIn is used for public contact. Research links point to public
publications. Full-report co-author credit is verified against the report's
cover-page author list and is distinct from sole authorship or study ownership.
