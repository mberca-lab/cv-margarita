"""Check review-driven content, case depth and downloadable CV semantics."""

import json
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
    def test_research_credits_and_career_order_survive_pdf_export(self):
        for suffix, pages in [("cv", 2), ("portfolio-cv", 4)]:
            with self.subTest(suffix=suffix), fitz.open(
                ASSETS / f"margarita-bermejo-cano-{suffix}.pdf"
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
        with fitz.open(ASSETS / "margarita-bermejo-cano-portfolio-cv.pdf") as document:
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
                ASSETS / f"margarita-bermejo-cano-{suffix}.pdf"
            ) as document:
                catalog = document.pdf_catalog()
                self.assertEqual(document.xref_get_key(catalog, "StructTreeRoot")[0], "xref")
                self.assertEqual(document.xref_get_key(catalog, "Lang")[0], "string")
                self.assertTrue(document.get_toc())

    def test_word_has_logical_headings_language_and_individual_publications(self):
        for edition in ["ats", "designed"]:
            with self.subTest(edition=edition), ZipFile(
                ASSETS / f"margarita-bermejo-cano-cv-{edition}.docx"
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
