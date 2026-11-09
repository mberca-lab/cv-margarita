"""Check public publication boundaries, case depth and private CV exports."""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import fitz
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
DATA = json.loads((ASSETS / "portfolio.json").read_text(encoding="utf-8"))
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}


def normalise(text):
    return " ".join(text.split())


class CvTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.assets = Path(cls.directory.name)
        environment = {**os.environ, "PORTFOLIO_PRIVATE_CV_DIR": str(cls.assets)}
        subprocess.run(["node", "build.cjs", "--private-cv"], cwd=ROOT,
                       env=environment, check=True, capture_output=True, text=True)
        subprocess.run([sys.executable, "render_cv.py"], cwd=ROOT,
                       env=environment, check=True, capture_output=True, text=True)

    def test_research_credits_and_career_order_survive_pdf_export(self):
        for suffix, pages in [("cv", 2), ("portfolio-cv", 4)]:
            with self.subTest(suffix=suffix), fitz.open(
                self.assets / f"margarita-bermejo-cano-{suffix}.pdf"
            ) as document:
                self.assertEqual(len(document), pages)
                text = normalise(document[1].get_text())
                positions = [text.index(job["employer"]) for job in DATA["experience"][2:]]
                self.assertEqual(positions, sorted(positions))
                for research in DATA["research"]:
                    credit = research["role"].split(" / ")[0]
                    self.assertIn(
                        f"{credit}: {research['title']} ({research['year']}).", text
                    )
                llm = next(r for r in DATA["research"] if r["id"] == "llm-productivity")
                self.assertIn(f"Co-author: {llm['title']}", text)
                links = [link.get("uri") for link in document[1].get_links()]
                for research in DATA["research"]:
                    self.assertIn(research["url"], links)

    def test_detailed_pdf_adds_questions_reasoning_and_supporting_work(self):
        with fitz.open(self.assets / "margarita-bermejo-cano-portfolio-cv.pdf") as document:
            appendix = normalise(" ".join(page.get_text() for page in list(document)[2:]))
            for project in DATA["projects"]:
                with self.subTest(project=project["id"]):
                    self.assertIn(project["title"], appendix)
                    self.assertIn(project["outcome"], appendix)
                    if not project.get("supporting"):
                        self.assertIn(project["question"], appendix)
                        for key in ["approach", "interpretation"]:
                            if key in project:
                                self.assertIn(project[key], appendix)
            self.assertIn("SUPPORTING MEASUREMENT & EARLIER ANALYSIS", appendix)
            links = [
                link.get("uri")
                for page in list(document)[2:]
                for link in page.get_links()
            ]
            for project in DATA["projects"]:
                for research_id in project.get("researchIds", []):
                    research = next(r for r in DATA["research"] if r["id"] == research_id)
                    self.assertIn(research["url"], links)

    def test_pdf_export_includes_tags_language_and_outline(self):
        for suffix in ["cv", "portfolio-cv"]:
            with self.subTest(suffix=suffix), fitz.open(
                self.assets / f"margarita-bermejo-cano-{suffix}.pdf"
            ) as document:
                catalog = document.pdf_catalog()
                self.assertEqual(document.xref_get_key(catalog, "StructTreeRoot")[0], "xref")
                self.assertEqual(document.xref_get_key(catalog, "Lang")[0], "string")
                self.assertTrue(document.get_toc())

    def test_word_has_logical_headings_language_and_individual_publications(self):
        for edition in ["ats", "designed"]:
            with self.subTest(edition=edition), ZipFile(
                self.assets / f"margarita-bermejo-cano-cv-{edition}.docx"
            ) as package:
                document = ET.fromstring(package.read("word/document.xml"))
                styles = ET.fromstring(package.read("word/styles.xml"))
                relationships = ET.fromstring(package.read("word/_rels/document.xml.rels"))
                hyperlinks = {
                    relationship.get("Id"): relationship.get("Target")
                    for relationship in relationships.findall("r:Relationship", REL_NS)
                    if relationship.get("Type").endswith("/hyperlink")
                }
                linked_targets = [
                    hyperlinks[link.get(
                        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                    )]
                    for link in document.findall(".//w:hyperlink", NS)
                ]
                language = styles.find(
                    "w:docDefaults/w:rPrDefault/w:rPr/w:lang", NS
                )
                self.assertIsNotNone(language)
                self.assertEqual(language.get(f"{{{NS['w']}}}val"), "en-IE")
                paragraphs = document.findall("w:body/w:p", NS)
                headings = [
                    p.find("w:pPr/w:pStyle", NS).get(f"{{{NS['w']}}}val")
                    for p in paragraphs if p.find("w:pPr/w:pStyle", NS) is not None
                ]
                self.assertIn("Heading1", headings)
                self.assertIn("Heading2", headings)
                self.assertNotIn("Heading3", headings)
                texts = [normalise("".join(p.itertext())) for p in paragraphs]
                for research in DATA["research"]:
                    credit = research["role"].split(" / ")[0]
                    self.assertIn(
                        f"{credit}: {research['title']} ({research['year']}).", texts
                    )
                    self.assertIn(research["url"], linked_targets)
                self.assertEqual(document.findall(".//w:tbl", NS), [])


class CasePresentationTests(unittest.TestCase):
    def test_location_stays_country_only_on_screen_and_print(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto((ROOT / "index.html").as_uri())
                for selector in [".hero-role", "footer > span", ".cv-contact"]:
                    with self.subTest(selector=selector):
                        text = page.locator(selector).text_content()
                        self.assertIn("Ireland", text)
                        self.assertNotIn("Dublin", text)
            finally:
                browser.close()

    def test_recruiters_can_reach_experience_and_request_cv_from_the_intro(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                with browser.new_context(java_script_enabled=False) as context:
                    page = context.new_page()
                    page.goto((ROOT / "index.html").as_uri())
                    hero = page.locator(".hero")
                    self.assertIn("People Science", hero.locator("h1").inner_text())
                    self.assertIn("People Analytics · People Science · Workplace AI",
                                  hero.locator(".eyebrow").first.text_content())
                    self.assertNotIn("Microsoft", hero.locator(".hero-copy").inner_text())
                    self.assertIn("behavioural science", hero.locator(".intro").inner_text())
                    self.assertNotIn(DATA["headline"], hero.locator(".hero-role").inner_text())
                    request = hero.get_by_role("link", name="Request CV on LinkedIn")
                    self.assertTrue(request.is_visible())
                    self.assertEqual(request.get_attribute("href"), DATA["linkedin"])
                    experience = hero.get_by_role("link", name="View experience")
                    experience.click()
                    self.assertTrue(page.url.endswith("#experience"))
                    self.assertIn(DATA["experience"][0]["title"],
                                  page.locator("#experience").inner_text())
                    self.assertIn("Microsoft", page.locator("#experience").inner_text())
            finally:
                browser.close()

    def test_people_analytics_leads_without_losing_research_evidence(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto((ROOT / "index.html").as_uri())
                proofs = page.locator(".hero-evidence .proof")
                self.assertEqual(proofs.locator("strong").all_text_contents(),
                                 [highlight["title"] for highlight in DATA["highlights"]])
                self.assertEqual(proofs.first.get_attribute("href"),
                                 "#case-linkedin-retention")
                for index, highlight in enumerate(DATA["highlights"]):
                    proof = proofs.nth(index)
                    self.assertEqual(proof.get_attribute("href"), highlight["href"])
                    proof.click()
                    self.assertTrue(page.locator(highlight["href"]).is_visible())
                self.assertEqual(page.locator(".project-lead").get_attribute("id"),
                                 "case-linkedin-retention")
                self.assertIn("People insights, measurement & AI adoption",
                              page.locator("#work-title").inner_text())
                self.assertIn("Research is a foundation",
                              page.locator("#research .section-intro").inner_text())
                self.assertEqual(page.locator("#research a").count(),
                                 len(DATA["research"]))
            finally:
                browser.close()

    def test_principal_roles_show_two_achievements_and_expand_without_duplicates(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                with browser.new_context(java_script_enabled=False) as context:
                    page = context.new_page()
                    page.goto((ROOT / "index.html").as_uri())
                    page.locator(".early-career > summary").click()
                    for job in DATA["experience"]:
                        with self.subTest(job=job["id"]):
                            role = page.locator(f"#{job['id']}")
                            bullets = job["bullets"] + job.get("additional", [])
                            visible = bullets[:2] if job["id"] in [
                                "microsoft", "linkedin", "metlife"
                            ] else []
                            self.assertEqual(role.locator("li:visible").all_text_contents(),
                                             visible)
                            self.assertEqual(role.locator("li").all_text_contents(), bullets)
                            role.locator(".job-detail > summary").focus()
                            page.keyboard.press("Enter")
                            self.assertEqual(role.locator("li:visible").all_text_contents(),
                                             bullets)
                            page.keyboard.press("Enter")
                            self.assertEqual(role.locator("li:visible").all_text_contents(),
                                             visible)
            finally:
                browser.close()

    def test_public_site_has_contact_and_research_not_private_downloads(self):
        for pattern in ("*.pdf", "*.docx", "*.html"):
            self.assertEqual(list(ASSETS.glob(pattern)), [])
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", html))
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto((ROOT / "index.html").as_uri())
                self.assertEqual(page.locator("a[download]").count(), 0)
                self.assertEqual(page.locator('a[href^="./assets/"]').count(), 0)
                self.assertEqual(page.locator('a[href^="mailto:"], a[href^="tel:"]').count(), 0)
                self.assertEqual(page.get_by_role("link", name="Contact", exact=True)
                                 .get_attribute("href"), "#contact")
                self.assertIn("contact me on LinkedIn", page.locator(".contact-note").inner_text())
                self.assertEqual(page.get_by_role("link", name="Connect on LinkedIn")
                                 .get_attribute("href"), DATA["linkedin"])
                self.assertEqual(page.locator("#print-button").count(), 0)
            finally:
                browser.close()

    def test_default_build_does_not_create_cv_files(self):
        subprocess.run(["node", "build.cjs"], cwd=ROOT, check=True,
                       capture_output=True, text=True)
        for pattern in ("*.pdf", "*.docx", "*.html"):
            self.assertEqual(list(ASSETS.glob(pattern)), [])

    def test_private_export_requires_a_directory_outside_the_repository(self):
        for directory in ("", str(ASSETS), "relative-output"):
            environment = {**os.environ, "PORTFOLIO_PRIVATE_CV_DIR": directory}
            for command in (["node", "build.cjs", "--private-cv"],
                            [sys.executable, "render_cv.py"]):
                with self.subTest(directory=directory, command=command):
                    result = subprocess.run(command, cwd=ROOT, env=environment,
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("outside this repository", result.stderr)

    def test_all_publications_have_visible_individual_links(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto((ROOT / "index.html").as_uri())
                research_section = page.locator("#research")
                for research in DATA["research"]:
                    with self.subTest(research=research["id"]):
                        link = research_section.locator(f'a[href="{research["url"]}"]')
                        self.assertEqual(link.count(), 1)
                        self.assertTrue(link.is_visible())
                        self.assertIn(research["title"], research_section.inner_text())
                page.locator("#more-work > summary").click()
                nps_case = page.locator("#case-post-migration-customer-experience")
                self.assertEqual(nps_case.locator("h3").inner_text(),
                                 "Post-migration NPS analysis")
                self.assertIn("Net Promoter Score (NPS)", nps_case.inner_text())
            finally:
                browser.close()

    def test_cases_show_contribution_and_output_before_optional_methods(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto((ROOT / "index.html").as_uri())
                page.locator("#more-work > summary").click()
                for project in DATA["projects"]:
                    with self.subTest(project=project["id"]):
                        card = page.locator(f"#case-{project['id']}")
                        overview = card.locator(".case-overview")
                        self.assertEqual(
                            overview.locator("dt").all_text_contents(),
                            ["Question", "My contribution", "Delivered output"]
                        )
                        self.assertEqual(overview.locator("dd").all_text_contents(),
                                         [project["question"], project["contribution"], project["outcome"]])
                        if project.get("approach") or project.get("interpretation"):
                            card.locator("summary").click()
                            details = card.locator("details dl")
                            self.assertNotIn(project["outcome"], details.inner_text())
                            for key in ["approach", "interpretation"]:
                                if key in project:
                                    self.assertIn(project[key], details.inner_text())
                        else:
                            self.assertEqual(card.locator("details").count(), 0)
                        for research_id in project.get("researchIds", []):
                            research = next(
                                r for r in DATA["research"] if r["id"] == research_id
                            )
                            self.assertEqual(
                                card.locator(".project-link a").get_attribute("href"),
                                research["url"]
                            )
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
