const fs = require("node:fs");
const path = require("node:path");
const {
  Document, Packer, Paragraph, TextRun, Footer, PageNumber,
  HeadingLevel, LevelFormat, AlignmentType, ExternalHyperlink
} = require("docx");

const root = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(root, "assets", "portfolio.json"), "utf8"));
const template = fs.readFileSync(path.join(root, "site-template.html"), "utf8").replace(/\r\n/g, "\n");
const escape = value => String(value).replace(/[&<>"']/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[char]));
const list = items => `<ul>${items.map(item => `<li>${escape(item)}</li>`).join("")}</ul>`;
const cvPageTwoJobs = data.experience.slice(2, 5);
const cvEarlierJobs = data.experience.slice(5);
const themeStyle = template.match(/:root \{[\s\S]*?\n    \* \{/)[0].replace(/\n    \* \{$/, "");
const themeScript = template.match(/<script>[\s\S]*?<\/script>/)[0];
const featuredProjectIds = ["agentic-research", "linkedin-retention", "metlife-service-survey"];

const cvStyles = `
    .cv-document { font-family: Arial, sans-serif; font-size: 10.5pt; line-height: 1.38; color: var(--cp-text); }
    .cv-document .cv-page { max-width: 210mm; margin: 24px auto; padding: 14mm; background: var(--cp-surface); }
    .cv-document h1 { font: 400 27pt/1.08 Georgia, serif; letter-spacing: -.035em; margin: 0 0 8px; }
    .cv-document .cv-headline { color: var(--cp-accent); font-size: 12pt; font-weight: 700; margin: 0 0 4px; }
    .cv-document .cv-contact { font-size: 9.5pt; margin: 4px 0 12px; overflow-wrap: anywhere; }
    .cv-document h2 { font: 700 11pt Arial, sans-serif; letter-spacing: .025em; text-transform: uppercase; color: var(--cp-accent); margin: 14px 0 6px; }
    .cv-document h3 { font: 700 10.5pt/1.3 Arial, sans-serif; margin: 10px 0 2px; }
    .cv-document p { margin: 4px 0; }
    .cv-document ul { margin: 4px 0 8px; padding-left: 16px; }
    .cv-document li { margin: 4px 0; }
    .cv-document .cv-date { font-size: 9.5pt; font-weight: 400; color: var(--cp-text-muted); }
    .cv-document .cv-scope { font-size: 10pt; color: var(--cp-text-muted); margin: 2px 0 4px; }
    .cv-document .cv-skills { font-size: 10pt; }
    .cv-document .cv-footer { font-size: 8.5pt; color: var(--cp-text-muted); margin-top: 14px; border-top: 1px solid var(--cp-border); padding-top: 6px; }
    .cv-document .cv-project { break-inside: avoid; margin: 0 0 12px; }
    .cv-document .cv-project h3 { margin-top: 12px; }
    .cv-document .cv-project p { margin: 4px 0; }
    .cv-document .cv-supporting { font-size: 10pt; }
    .cv-document a { color: inherit; text-underline-offset: 3px; }
    @page { size: A4; margin: 14mm; }
    @media print {
      html[data-theme], :root { color-scheme: light; --cp-bg: #ffffff; --cp-surface: #ffffff; --cp-text: #242424; --cp-text-muted: #5c5c5c; --cp-accent: #b11f4b; --cp-border: #dedede; }
      body { margin: 0; background: var(--cp-bg); }
      .cv-document .cv-page { margin: 0; padding: 0; max-width: none; }
      .cv-document .cv-page + .cv-page { break-before: page; }
      .cv-document h2, .cv-document h3 { break-after: avoid; }
      .cv-document li { break-inside: avoid; }
    }`;

function cvJob(job) {
  return `<article><h3>${escape(job.title)} | ${escape(job.employer)}
    <span class="cv-date">/ ${escape(job.dates)}</span></h3>
    ${job.id === "telefonica" ? `<p class="cv-scope">${escape(job.scope)}</p>` : ""}
    ${list(job.cvBullets || job.bullets)}</article>`;
}

function researchLinks(project) {
  return (project.researchIds || []).map(id => data.research.find(research => research.id === id));
}

function cvProject(project) {
  return `<article class="cv-project"><h3>${escape(project.title)} <span class="cv-date">/ ${escape(project.dates)}</span></h3>
    <p class="cv-scope">${escape(project.employer)} · ${escape(project.status)}</p>
    <p><b>Question:</b> ${escape(project.question)}</p>
    <p><b>My contribution:</b> ${escape(project.contribution)}</p>
    ${project.approach ? `<p><b>Approach:</b> ${escape(project.approach)}</p>` : ""}
    <p><b>Output:</b> ${escape(project.outcome)}</p>
    ${project.interpretation ? `<p><b>Interpretation:</b> ${escape(project.interpretation)}</p>` : ""}
    ${researchLinks(project).map(research => `<p><a href="${escape(research.url)}">${escape(research.linkLabel || "Read the public report")}</a></p>`).join("")}
    </article>`;
}

function cvMarkup(extended = false) {
  const total = extended ? 4 : 2;
  const footer = page => `<p class="cv-footer">${escape(data.name)} / ${escape(data.edition)} / ${page} of ${total}</p>`;
  const education = data.education.map(([degree, institution, detail]) =>
    `<p><b>${escape(degree)}</b> / ${escape(institution)}${detail ? ` / ${escape(detail)}` : ""}</p>`).join("");
  let markup = `<div class="cv-document">
    <section class="cv-page">
      <h1>${escape(data.name)}</h1>
      <p class="cv-headline">${escape(data.headline)}</p>
      <p>${escape(data.specialisms)}</p>
      <p class="cv-contact">${escape(data.location)} · ${escape(data.languages)} ·
        <a href="${escape(data.linkedin)}">linkedin.com/in/margaritabermejocano</a><br>
        <a href="${escape(data.website)}">mberca.github.io/cv-margarita</a></p>
      <h2>Profile</h2><p>${escape(data.summary)}</p>
      <h2>Experience</h2>${cvJob(data.experience[0])}${cvJob(data.experience[1])}
      <h2>Methods & tools</h2><div class="cv-skills">${data.cvSkills.map(([name, text]) => `<p><b>${escape(name)}:</b> ${escape(text)}</p>`).join("")}</div>
      ${footer(1)}
    </section>
    <section class="cv-page">
      <h2>Experience / continued</h2>${cvPageTwoJobs.map(cvJob).join("")}
      <h2>Earlier career</h2><div class="cv-skills">${cvEarlierJobs.map(job =>
        `<p><b>${escape(job.employer)} / ${escape(job.title)}</b> / ${escape(job.dates)}. ${escape(job.cvSummary)}</p>`).join("")}</div>
      <h2>Public research & analytical contributions</h2>
      ${data.research.map(research => `<p><b>${escape(research.role.split(" / ")[0])}:</b>
        <a href="${escape(research.url)}">${escape(research.title)}</a> (${escape(research.year)}).</p>`).join("")}
      <h2>Education & certification</h2><div class="cv-skills">${education}
        <p><b>${escape(data.certifications[0])}</b></p></div>
      <h2>Knowledge sharing & inclusion</h2><p class="cv-skills">${escape(data.community)}</p>
      ${footer(2)}
    </section>`;
  if (extended) {
    const selected = data.projects.filter(project => !project.supporting);
    const supporting = data.projects.filter(project => project.supporting);
    for (const [page, projects] of [selected.slice(0, 4), selected.slice(4)].entries()) {
      markup += `<section class="cv-page"><h2>Selected research, analytics &amp; measurement / ${page + 1}</h2>`;
      markup += projects.map(cvProject).join("");
      if (page === 1 && supporting.length) {
        markup += `<h2>Supporting measurement &amp; earlier analysis</h2><div class="cv-supporting">`;
        for (const project of supporting) {
          markup += `<article class="cv-project"><h3>${escape(project.title)} <span class="cv-date">/ ${escape(project.employer)} / ${escape(project.dates)}</span></h3>
            <p>${escape(project.contribution)}</p><p><b>Output:</b> ${escape(project.outcome)}</p></article>`;
        }
        markup += "</div>";
      }
      markup += `${footer(page + 3)}</section>`;
    }
  }
  return markup + "</div>";
}

function projectMarkup(project) {
  return `<article class="project${project.id === featuredProjectIds[0] ? " project-lead" : ""}" id="case-${escape(project.id)}" data-category="${escape(project.category)}">
    <span class="project-number" aria-hidden="true">${escape(project.number)}</span>
    <div class="meta"><span>${escape(project.number)} / ${escape(project.categoryLabel.toUpperCase())}</span><span>${escape(project.dates)}</span></div>
    <p class="project-employer">${escape(project.employer)}</p>
    <h3>${escape(project.title)}</h3><p>${escape(project.summary)}</p>
    <dl class="case case-overview">
      <div><dt>Question</dt><dd>${escape(project.question)}</dd></div>
      <div><dt>My contribution</dt><dd>${escape(project.contribution)}</dd></div>
      <div><dt>Delivered output</dt><dd>${escape(project.outcome)}</dd></div>
    </dl>
    ${researchLinks(project).map(research => `<p class="project-link"><a href="${escape(research.url)}" target="_blank" rel="noopener noreferrer">${escape(research.linkLabel || "Read the full research report")} <span aria-hidden="true">↗</span></a></p>`).join("")}
    <div class="tags">${project.tags.map(tag => `<span class="tag">${escape(tag)}</span>`).join("")}</div>
    <p class="status">${escape(project.status)}</p>
    ${project.approach || project.interpretation ? `<details><summary>Methods &amp; interpretation</summary><dl class="case">
      ${project.approach ? `<div><dt>Analytical approach</dt><dd>${escape(project.approach)}</dd></div>` : ""}
      ${project.interpretation ? `<div><dt>Interpretation</dt><dd>${escape(project.interpretation)}</dd></div>` : ""}
    </dl></details>` : ""}</article>`;
}

function jobMarkup(job) {
  const bullets = [...job.bullets, ...(job.additional || [])];
  const highlights = ["microsoft", "linkedin", "metlife"].includes(job.id) ? bullets.slice(0, 2) : [];
  const remaining = bullets.slice(highlights.length);
  return `<article class="job" id="${escape(job.id)}"><p class="date">${escape(job.dates)}</p><div>
    <h3>${escape(job.title)}</h3><p class="org">${escape(job.employer)} / ${escape(job.team)}</p>
    <p class="scope">${escape(job.scope)}</p>
    ${highlights.length ? list(highlights) : ""}
    ${remaining.length ? `<details class="job-detail"><summary>${highlights.length ? "More role details" : "Role details"}</summary>${list(remaining)}</details>` : ""}</div></article>`;
}

function heading(id, number, eyebrow, title) {
  return `<div class="section-head"><span class="eyebrow">${number} / ${eyebrow}</span><h2 id="${id}">${title}</h2></div>`;
}

function siteMarkup() {
  const publication = data.research[0];
  const featured = featuredProjectIds.map(id => data.projects.find(project => project.id === id));
  const further = data.projects.filter(project => !featuredProjectIds.includes(project.id));
  return `<a class="skip" href="#main">Skip to content</a>
  <div class="shell">
    <header class="topbar"><div class="topbar-inner">
      <a class="brand" href="#main" aria-label="Margarita Bermejo Cano, back to top"><span class="monogram" aria-hidden="true">mb.</span><span class="brand-name">Margarita<br>Bermejo Cano</span></a>
      <nav aria-label="Main navigation"><a href="#work">Work</a><a href="#research">Research</a><a href="#experience">Experience</a><a href="#contact">Contact</a></nav>
    </div><p class="theme-status" id="theme-status" role="status" hidden></p></header>
    <main class="main" id="main">
      <header class="hero">
        <div class="hero-copy">
          <p class="eyebrow">${escape(data.specialisms)}</p>
          <p class="hero-name">${escape(data.name)}</p><p class="hero-role">${escape(data.location)} · ${escape(data.languages)}</p>
          <h1>People Science<br><em>&amp; Analytics.</em></h1>
          <p class="intro">${escape(data.heroIntro)}</p>
          <div class="actions"><a class="button primary" href="#work">Explore my work <span aria-hidden="true">↗</span></a><a class="button" href="#experience">View experience <span aria-hidden="true">↗</span></a><a class="button" href="${escape(data.linkedin)}" target="_blank" rel="noopener noreferrer">Request CV on LinkedIn <span aria-hidden="true">↗</span></a></div>
          <p class="hero-caption">R-first analysis · Clear recommendations · English &amp; Spanish</p>
        </div>
        <aside class="hero-evidence" aria-label="Selected career evidence">
          <p class="eyebrow">Selected evidence</p>
          ${data.highlights.map((highlight, index) => `<a class="proof" href="${escape(index === 0 ? publication.url : highlight.href)}">
            <span class="proof-index" aria-hidden="true">0${index + 1}</span><div>
            <strong>${escape(highlight.title)}</strong><p>${escape(highlight.text)}</p><span>${escape(index === 0 ? "Microsoft / read the 2025 report" : highlight.context)} <span aria-hidden="true">↗</span></span></div>
          </a>`).join("")}
        </aside>
      </header>
      <section id="work" aria-labelledby="work-title">
        ${heading("work-title", "01", "Selected work", "Research, analytics &amp; measurement.")}
        <p class="section-intro">Analytical leadership at Microsoft, customer-facing retention insight at LinkedIn Glint and end-to-end measurement at MetLife. Each case shows the question, my contribution and the delivered output, with methods available to explore. Confidential findings and customer details are omitted.</p>
        <div class="filters" id="project-filters" role="group" aria-label="Filter selected work" hidden>
          ${[["all", "All work"], ["research", "AI research"], ["customer", "Customer analytics"], ["workforce", "Workforce & measurement"]].map(([value, label]) => `<button class="filter" type="button" data-filter="${value}" aria-pressed="${value === "all"}">${escape(label)}</button>`).join("")}
        </div>
        <p class="project-count" id="project-count" aria-live="polite" aria-atomic="true">Showing ${featured.length} of ${data.projects.length} examples</p>
        <div class="projects">${featured.map(projectMarkup).join("")}</div>
        <details class="more-work" id="more-work"><summary>Further work / ${further.length} examples</summary>
          <div class="projects">${further.map(projectMarkup).join("")}</div>
        </details>
        <div class="contributions"><h3>Beyond the case studies</h3>
          ${data.contributions.map(group => `<details><summary>${escape(group.title)}</summary>${list(group.items)}</details>`).join("")}
        </div>
      </section>
      <section id="research" aria-labelledby="research-title">
        ${heading("research-title", "02", "Public research", "Three publications. Shared contributions.")}
        <article class="publication"><div>
          <p class="eyebrow">${escape(publication.role)} / ${escape(publication.publisher)} / ${escape(publication.year)}</p>
          <h3>${escape(publication.title)}</h3><p>${escape(publication.detail)}</p>
          <a class="button" href="${escape(publication.url)}" target="_blank" rel="noopener noreferrer">Read the full report <span aria-hidden="true">↗</span></a>
        </div><div class="publication-proof"><strong>1,800</strong><p>Full-time employees across nine markets in the published study.</p><p>${escape(publication.scope)}</p><p>${escape(publication.credit)}</p></div></article>
        <div class="research-notes">${data.research.slice(1).map(research => `<article><h3>${escape(research.title)}</h3><p><b>${escape(research.role)} / ${escape(research.year)}.</b> ${escape(research.detail)}</p>
          <a class="button" href="${escape(research.url)}" target="_blank" rel="noopener noreferrer">${escape(research.linkLabel)} <span aria-hidden="true">↗</span></a></article>`).join("")}</div>
      </section>
      <section id="experience" aria-labelledby="experience-title">
        ${heading("experience-title", "03", "Career", "A career built around people and evidence.")}
        <p class="section-intro">From workforce reporting and HR systems to customer analytics and AI research, the context has changed. The work still begins with understanding the problem and making the evidence useful.</p>
        <nav class="timeline" aria-label="Career timeline">${[5, 4, 3, 2, 1, 0].map(index => `<a href="#${data.experience[index].id}">${["2022", "2019", "2015", "2014", "2012", "2011"][index]} / ${escape(data.experience[index].employer.split(" / ")[0])}</a>`).join("")}</nav>
        ${data.experience.slice(0, 6).map(jobMarkup).join("")}
        <details class="early-career"><summary>Earlier foundations / 2006–2011</summary>${data.experience.slice(6).map(jobMarkup).join("")}</details>
      </section>
      <section id="methods" aria-labelledby="methods-title">
        ${heading("methods-title", "04", "Toolkit", "The craft behind the insight.")}
        <div class="methods">${data.skills.map(group => `<article><h3>${escape(group.title)}</h3>${list(group.items)}</article>`).join("")}</div>
      </section>
      <section id="about" aria-labelledby="about-title">
        ${heading("about-title", "05", "How I work", "Start with the question. Stay with the evidence.")}
        <div class="principles">
          <article><div class="principle-mark" aria-hidden="true">?</div><h3>Make the question answerable.</h3><p>Clarify the decision, test the measurement and choose an analytical approach that fits the problem.</p></article>
          <article><div class="principle-mark" aria-hidden="true">↗</div><h3>Make the answer useful.</h3><p>Explain the findings, their limitations and the practical options—not just the statistical result.</p></article>
          <article><div class="principle-mark" aria-hidden="true">↻</div><h3>Make the work reusable.</h3><p>Build documented methods, reusable code and clear handovers so recurring work can be rerun rather than rebuilt.</p></article>
        </div>
      </section>
      <section id="background" aria-labelledby="background-title">
        ${heading("background-title", "06", "Background", "More than one way of thinking.")}
        <div class="education">${data.education.map(([degree, institution, detail]) => `<article><h3>${escape(degree)}</h3><p>${escape(institution)}${detail ? ` / ${escape(detail)}` : ""}</p></article>`).join("")}</div>
        <p class="certification">${escape(data.certifications[0])}</p>
      </section>
      <section id="contact" aria-labelledby="contact-title" class="closing">
        <div><h2 id="contact-title">Let's compare notes.</h2><p>For people science and analytics opportunities, research conversations or a current CV, connect with me on LinkedIn. My focus is AI adoption, survey measurement and customer insight.</p>
          <div class="actions"><a class="button" href="${escape(data.linkedin)}" target="_blank" rel="noopener noreferrer">Connect on LinkedIn <span aria-hidden="true">↗</span></a></div>
        </div><div class="resource-list">
          <a class="button" href="https://github.com/mberca" target="_blank" rel="noopener noreferrer"><span>Explore my GitHub projects</span><span aria-hidden="true">↗</span></a>
          <a class="button" href="#research"><span>Browse public research</span><span aria-hidden="true">↗</span></a>
          <p class="contact-note">For a current CV, contact me on LinkedIn. Personal application documents are not hosted on this site.</p>
        </div>
      </section>
      <footer><span>${escape(data.name)} / Dublin / ${escape(data.edition)}</span>
        <label class="theme-picker" id="theme-picker" hidden><span>Theme</span>
          <select class="theme" id="theme-select">
            <option value="light">Light</option><option value="dark">Dark</option>
            <option value="premium">Premium Editorial</option><option value="retro95">Retro '95</option>
          </select>
        </label>
      </footer>
    </main>
  </div>
  <div class="print-resume">${cvMarkup()}</div>
  <script>
    const themeSelect = document.querySelector("#theme-select");
    const themeStatus = document.querySelector("#theme-status");
    themeSelect.value = document.documentElement.getAttribute("data-theme");
    document.querySelector("#theme-picker").hidden = false;
    themeSelect.addEventListener("change", () => {
      const theme = themeSelect.value;
      document.documentElement.setAttribute("data-theme", theme);
      themeStatus.hidden = true;
      try {
        window.localStorage.setItem("portfolio-theme", theme);
      } catch (error) {
        if (!["SecurityError", "QuotaExceededError"].includes(error.name)) throw error;
        console.warn("The selected theme could not be saved in browser storage.");
        themeStatus.textContent = "Theme applied for this visit. Your browser could not save the preference.";
        themeStatus.hidden = false;
      }
      const url = new URL(window.location.href);
      if (url.searchParams.has("scoutTheme")) {
        url.searchParams.set("scoutTheme", theme);
        window.history.replaceState(null, "", url);
      }
    });
    const filterGroup = document.querySelector("#project-filters");
    const filters = [...filterGroup.querySelectorAll("button")];
    const projects = [...document.querySelectorAll(".project")];
    const moreWork = document.querySelector("#more-work");
    function updateProjectCount() {
      const count = projects.filter(project => !project.hidden &&
        (!moreWork.contains(project) || moreWork.open)).length;
      document.querySelector("#project-count").textContent = \`Showing \${count} of \${projects.length} examples\`;
    }
    function selectFilter(value) {
      filters.forEach(filter => filter.setAttribute("aria-pressed", String(filter.dataset.filter === value)));
      projects.forEach(project => {
        project.hidden = value !== "all" && project.dataset.category !== value;
      });
      moreWork.hidden = ![...moreWork.querySelectorAll(".project")].some(project => !project.hidden);
      moreWork.open = value !== "all";
      updateProjectCount();
    }
    filterGroup.hidden = false;
    filters.forEach(button => button.addEventListener("click", () => selectFilter(button.dataset.filter)));
    moreWork.addEventListener("toggle", updateProjectCount);
    function revealCase(hash) {
      const project = projects.find(item => "#" + item.id === hash);
      if (!project) return;
      selectFilter("all");
      if (moreWork.contains(project)) moreWork.open = true;
      updateProjectCount();
    }
    document.querySelectorAll('a[href^="#case-"]').forEach(link =>
      link.addEventListener("click", () => revealCase(link.hash)));
    window.addEventListener("hashchange", () => revealCase(window.location.hash));
    revealCase(window.location.hash);
  </script>`;
}

function cvHtml(extended) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${escape(data.name)} / ${extended ? "Detailed CV" : "CV"}</title>${themeScript}
    <style>${themeStyle}body { margin: 0; background: var(--cp-bg); }${cvStyles}</style></head><body>${cvMarkup(extended)}</body></html>`.replace(/[ \t]+$/gm, "");
}

function docxCv(designed) {
  const accent = designed ? "B11F4B" : "242424";
  const text = (value, options = {}) => new TextRun({ text: value, ...options });
  const paragraph = (value, options = {}) => new Paragraph({ children: [text(value)], ...options });
  const heading = value => paragraph(value, { heading: HeadingLevel.HEADING_1 });
  const hyperlink = (label, link) => new ExternalHyperlink({
    link, children: [new TextRun({ text: label, color: accent, underline: {} })]
  });
  const children = [
    paragraph(data.name, { heading: HeadingLevel.TITLE }),
    paragraph(data.headline, { style: "CVHeadline" }),
    paragraph(data.specialisms, { style: "CVContact" }),
    new Paragraph({ style: "CVContact", children: [
      text(`${data.location} | ${data.languages} | `),
      hyperlink("LinkedIn", data.linkedin), text(" | "), hyperlink("Portfolio", data.website)
    ] }),
    heading("Profile"), paragraph(data.summary), heading("Experience")
  ];
  function addJob(job) {
    children.push(paragraph(`${job.title} | ${job.employer}`, { heading: HeadingLevel.HEADING_2 }));
    children.push(paragraph(`${job.dates} | ${job.location}`, { style: "CVContact" }));
    if (job.id === "telefonica") children.push(paragraph(job.scope, { style: "CVSmall" }));
    children.push(...(job.cvBullets || job.bullets).map(value => paragraph(value, { numbering: { reference: "bullets", level: 0 } })));
  }
  addJob(data.experience[0]); addJob(data.experience[1]);
  children.push(heading("Methods & tools"));
  children.push(...data.cvSkills.map(([name, detail]) => new Paragraph({
    style: "CVSmall", children: [text(`${name}: `, { bold: true }), text(detail)]
  })));
  children.push(paragraph("Experience / continued", { heading: HeadingLevel.HEADING_1, pageBreakBefore: true }));
  cvPageTwoJobs.forEach(addJob);
  children.push(heading("Earlier career"));
  children.push(...cvEarlierJobs.map(job => new Paragraph({
    style: "CVSmall", children: [
      text(`${job.employer} | ${job.title}`, { bold: true }),
      text(` | ${job.dates}. ${job.cvSummary}`)
    ]
  })));
  children.push(heading("Public research & analytical contributions"));
  children.push(...data.research.map(research => new Paragraph({ children: [
    text(`${research.role.split(" / ")[0]}: `, { bold: true }),
    hyperlink(research.title, research.url),
    text(` (${research.year}).`)
  ] })));
  children.push(heading("Education & certification"));
  children.push(...data.education.map(([degree, institution, detail]) =>
    new Paragraph({ style: "CVSmall", children: [
      text(degree, { bold: true }), text(` | ${institution}${detail ? ` | ${detail}` : ""}`)
    ] })));
  children.push(paragraph(data.certifications[0], { style: "CVSmall" }));
  children.push(heading("Knowledge sharing & inclusion"), paragraph(data.community, { style: "CVSmall" }));
  return new Document({
    creator: data.name,
    title: `${data.name} — People Science & Analytics`,
    description: "Career CV with public-safe achievements and source-verified research credit.",
    styles: {
      default: {
        document: {
          run: { font: "Arial", size: 21, color: "242424", language: { value: "en-IE" } },
          paragraph: { spacing: { after: 70, line: 265 } }
        }
      },
      paragraphStyles: [
        { id: "Title", name: "Title", basedOn: "Normal", next: "Normal",
          run: { font: designed ? "Georgia" : "Arial", size: 48, color: accent },
          paragraph: { spacing: { after: 110 }, keepNext: true } },
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { bold: true, size: 23, color: accent },
          paragraph: { spacing: { before: 150, after: 60 }, keepNext: true, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { bold: true, size: 21 },
          paragraph: { spacing: { before: 120, after: 20 }, keepNext: true, outlineLevel: 1 } },
        { id: "CVHeadline", name: "CV Headline", basedOn: "Normal",
          run: { bold: true, size: 24, color: accent }, paragraph: { spacing: { after: 60 }, keepNext: true } },
        { id: "CVContact", name: "CV Contact", basedOn: "Normal",
          run: { size: 19, color: "5C5C5C" }, paragraph: { spacing: { after: 50 }, keepNext: true } },
        { id: "CVSmall", name: "CV Small", basedOn: "Normal",
          run: { size: 20 }, paragraph: { spacing: { after: 55, line: 240 } } }
      ]
    },
    numbering: {
      config: [{
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 240, hanging: 180 } } }
        }]
      }]
    },
    sections: [{
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 800, bottom: 800, left: 800, right: 800 } }
      },
      footers: { default: new Footer({ children: [
        new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [text(`${data.name} | ${data.edition} | `, { size: 16, color: "5C5C5C" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "5C5C5C" })]
        })
      ] }) },
      children
    }]
  });
}

function privateCvDirectory() {
  const directory = process.env.PORTFOLIO_PRIVATE_CV_DIR;
  if (!directory || !path.isAbsolute(directory)) {
    throw new Error("Set PORTFOLIO_PRIVATE_CV_DIR to an absolute directory outside this repository.");
  }
  const normalise = value => process.platform === "win32" ? value.toLowerCase() : value;
  const repository = normalise(fs.realpathSync(root));
  const resolved = normalise(path.resolve(directory));
  if (resolved === repository || resolved.startsWith(repository + path.sep)) {
    throw new Error("Private CV output must be outside this repository.");
  }
  fs.mkdirSync(directory, { recursive: true });
  const destination = fs.realpathSync(directory);
  const realDestination = normalise(destination);
  if (realDestination === repository || realDestination.startsWith(repository + path.sep)) {
    throw new Error("Private CV output must not resolve inside this repository.");
  }
  return destination;
}

async function main() {
  if (!data.projects.length || data.experience.length !== 10 ||
      data.projects.some(project => !project.id || !project.employer || !project.category ||
        (project.researchIds || []).some(id => !data.research.some(research => research.id === id))) ||
      cvEarlierJobs.some(job => !job.cvSummary) ||
      new Set(data.projects.map(project => project.id)).size !== data.projects.length) {
    throw new Error("Unexpected portfolio structure or missing project identity");
  }
  if (!process.argv.includes("--private-cv")) {
    const site = template.replace("{{CV_STYLES}}", cvStyles).replace("{{BODY}}", siteMarkup()).replace(/[ \t]+$/gm, "");
    if (site.includes("{{")) throw new Error("Unresolved template token");
    fs.writeFileSync(path.join(root, "index.html"), site);
    console.log(`Built public website: ${featuredProjectIds.length} featured cases. No CV files generated.`);
    return;
  }
  const directory = privateCvDirectory();
  fs.writeFileSync(path.join(directory, "margarita-bermejo-cano-cv.html"), cvHtml(false));
  fs.writeFileSync(path.join(directory, "margarita-bermejo-cano-portfolio-cv.html"), cvHtml(true));
  for (const [designed, suffix] of [[false, "ats"], [true, "designed"]]) {
    const buffer = await Packer.toBuffer(docxCv(designed));
    fs.writeFileSync(path.join(directory, `margarita-bermejo-cano-cv-${suffix}.docx`), buffer);
  }
  console.log(`Built private CVs outside the repository: ${directory}`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
