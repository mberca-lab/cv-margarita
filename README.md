# Career portfolio

Public career portfolio: research, selected analytical work and career experience.
GitHub Pages serves the site at
https://mberca.github.io/cv-margarita/.

The public edition uses LinkedIn for contact. Personal application CVs are not
hosted in this repository or offered as downloads.
The opening section positions the portfolio around people science and analytics,
AI adoption research, survey measurement and customer insight, with direct routes
to career experience and a LinkedIn CV request. Analytical ownership is scoped
to selected research studies, not a team-wide or programme-wide analytical lead
role, people management or ML model-development experience.

## Update the content

Edit `assets/portfolio.json` for career content, `site-template.html` for the
website design, and `build.cjs` for generated markup. Commit the generated
`index.html` so visitors do not need a build service.

```powershell
npm ci
python -m pip install -r requirements.txt
python -m playwright install chromium
npm run build
npm run test:cv
npm run test:themes
```

Both `npm run build` and `npm run build:site` update only `index.html`.
They never generate CV files in the public repository.

## Private CV generation

The existing CV generator remains available for local use. Set an absolute output
directory **outside this repository** before generating or rendering documents:

```powershell
$env:PORTFOLIO_PRIVATE_CV_DIR = 'C:\Private\career-exports'
npm run build:private-cv
npm run render
```

Both commands reject missing, relative or in-repository output directories.
The render step checks that the concise PDF has two pages and the detailed PDF
has four. The single-column Word CV uses standard headings, selectable text and
no layout tables. These generated files do not replace separately approved
application CVs. Keep all exports private unless separately reviewed for sharing.

The selected-work collection spans Microsoft, LinkedIn Glint, MetLife and
Telefónica. Keep it curated around delivered research, analytical workstreams
and measurement programmes, not routine activity counts. The three opening
evidence links are sourced from `highlights` in `assets/portfolio.json`.
The private detailed CV expands six leading cases with their question, contribution,
output and, where supported, analytical approach and interpretation. The two
remaining cases form a compact supporting-work section. Public evidence links
appear beside the relevant cases. The website opens with three contrasting
cases (agentic research, LinkedIn retention and MetLife measurement); five more
remain in a native, keyboard-accessible "Further work" disclosure. Category
filters search all eight and reveal matching additional cases. Direct case
links restore the all-work view and open the containing disclosure when needed.
Microsoft, LinkedIn and MetLife each show two leading achievements in the
initial career view. Their remaining bullets, and other employers' role details,
stay behind individual disclosures without duplicating the visible achievements.

Keep delivered recommendations distinct from
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

The footer theme selector offers Light, Dark, Premium Editorial and Retro '95,
keeping appearance controls out of the primary career navigation.
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

The owner approved keeping the website public while removing private-only CV
downloads on 21 October 2026. Keep personal contact details, original application
CVs, career workbooks, review conversations, customer data and internal source
documents outside this repository. Project descriptions distinguish personal
contribution from research scope and wider outcomes.

The previously committed CV files were backed up locally and removed from the
published branch and its rewritten history. Existing clones must not merge the
old history back into this repository; use a fresh clone of the cleaned branch.
History rewriting does not guarantee removal from GitHub caches, old commit
links, forks or copies already downloaded. Contact GitHub Support if removal of
cached historic copies is required.

The public build and publication tests prevent CV downloads from being
reintroduced. PDF, Word and HTML files under `assets/` are also ignored by Git.
The browser's printable career summary uses only the same public portfolio
content and LinkedIn contact link, not the removed application documents.

Only LinkedIn is used for public contact. Research links point to public
publications. Full-report co-author credit is verified against the report's
cover-page author list and is distinct from sole authorship or study ownership.
The 2023 LLM productivity report also verifies named co-authorship. Keep the
AI-readiness eBook at contributing-analyst credit unless personal authorship is
independently established. Research IDs connect cases to their public evidence.
All three publications have individual links in the research section and in
the locally generated private CVs. The post-migration customer case is explicitly
labelled as NPS analysis.
