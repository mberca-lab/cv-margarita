"""Check theme selection, resilience and screen/print presentation."""

import json
import os
import tempfile
import unittest
from pathlib import Path

import fitz
from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parent
URL = (ROOT / "index.html").as_uri()
THEMES = ["light", "dark", "premium", "retro95"]
FEATURED_IDS = ["linkedin-retention", "agentic-research", "metlife-service-survey"]
DATA = json.loads((ROOT / "assets" / "portfolio.json").read_text(encoding="utf-8"))


class ThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context(color_scheme="light", reduced_motion="reduce")
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def current_theme(self):
        return self.page.locator("html").get_attribute("data-theme")

    def test_selection_persists_and_preserves_content(self):
        self.page.goto(URL)
        selector = self.page.get_by_role("combobox", name="Theme", exact=True)
        self.assertEqual(selector.locator("option").evaluate_all("(els) => els.map(e => e.value)"), THEMES)
        original = self.page.locator("main").inner_text()
        palettes = []
        for theme in THEMES:
            selector.select_option(theme)
            self.assertEqual(self.current_theme(), theme)
            self.assertEqual(self.page.evaluate("localStorage.getItem('portfolio-theme')"), theme)
            self.page.reload()
            self.assertEqual(self.current_theme(), theme)
            self.assertEqual(selector.input_value(), theme)
            self.assertEqual(self.page.locator("main").inner_text(), original)
            palettes.append(self.page.locator("html").evaluate(
                "(el) => getComputedStyle(el).getPropertyValue('--cp-bg').trim()"))
        self.assertEqual(len(set(palettes)), 4)

    def test_preview_overrides_saved_choice_and_invalid_preview_uses_system(self):
        self.page.emulate_media(color_scheme="dark")
        self.page.goto(URL + "?scoutTheme=unknown")
        self.assertEqual(self.current_theme(), "dark")
        self.page.get_by_role("combobox", name="Theme", exact=True).select_option("retro95")
        self.page.goto(URL + "?scoutTheme=premium#research")
        self.assertEqual(self.current_theme(), "premium")
        self.page.get_by_role("combobox", name="Theme", exact=True).select_option("light")
        self.assertTrue(self.page.url.endswith("?scoutTheme=light#research"))
        self.page.reload()
        self.assertEqual(self.current_theme(), "light")

    def test_blocked_storage_and_no_javascript_leave_content_usable(self):
        self.page.add_init_script("""
          Object.defineProperty(window, "localStorage", {
            get() { throw new DOMException("Blocked for this test", "SecurityError"); }
          });
        """)
        self.page.goto(URL)
        self.page.get_by_role("combobox", name="Theme", exact=True).select_option("premium")
        self.assertEqual(self.current_theme(), "premium")
        self.assertIn("could not save", self.page.get_by_role("status").inner_text())
        self.assertEqual(self.page.locator(".project:visible").count(), len(FEATURED_IDS))
        with self.browser.new_context(java_script_enabled=False) as context:
            page = context.new_page()
            page.goto(URL)
            self.assertTrue(page.locator("#theme-picker").is_hidden())
            self.assertEqual(page.locator(".project:visible").count(), len(FEATURED_IDS))
            page.locator("#more-work > summary").click()
            self.assertEqual(page.locator(".project:visible").count(), len(DATA["projects"]))
            self.assertEqual(page.locator(".research-notes a").count(), 2)

    def test_curated_cases_expand_filter_and_deep_link_without_losing_evidence(self):
        self.page.goto(URL)
        visible = self.page.locator(".project:visible")
        self.assertEqual(visible.evaluate_all("(els) => els.map(el => el.id)"),
                         ["case-" + identifier for identifier in FEATURED_IDS])
        expect(self.page.locator("#project-count")).to_have_text("Showing 3 of 8 examples")
        self.page.locator("#more-work > summary").focus()
        self.page.keyboard.press("Enter")
        self.assertEqual(visible.count(), len(DATA["projects"]))
        expect(self.page.locator("#project-count")).to_have_text("Showing 8 of 8 examples")
        for category, label in [("research", "Workplace AI"), ("workforce", "Workforce & measurement"),
                                ("customer", "Customer analytics")]:
            self.page.get_by_role("button", name=label, exact=True).click()
            self.assertEqual(visible.count(), sum(p["category"] == category for p in DATA["projects"]))
        self.page.get_by_role("button", name="All work", exact=True).click()
        self.assertEqual(visible.count(), len(FEATURED_IDS))
        self.page.goto(URL + "#case-post-migration-customer-experience")
        self.assertTrue(self.page.locator("#case-post-migration-customer-experience").is_visible())
        self.assertEqual(visible.count(), len(DATA["projects"]))
        self.page.locator("#more-work > summary").click()
        self.assertEqual(visible.count(), len(FEATURED_IDS))
        expect(self.page.locator("#project-count")).to_have_text("Showing 3 of 8 examples")
        for project in DATA["projects"]:
            case = self.page.locator("#case-" + project["id"])
            for field in ["question", "contribution", "outcome"]:
                self.assertIn(project[field], case.text_content())
        self.assertEqual(self.page.locator(".job-detail").count(), len(DATA["experience"]))

    def test_responsive_themes_keep_filters_links_and_print_working(self):
        self.page.goto(URL)
        artifacts = os.environ.get("PORTFOLIO_TEST_ARTIFACTS")
        for theme in THEMES:
            self.page.get_by_role("combobox", name="Theme", exact=True).select_option(theme)
            for width in [320, 390, 768, 1440]:
                self.page.set_viewport_size({"width": width, "height": 1000})
                self.assertTrue(self.page.evaluate(
                    "document.documentElement.scrollWidth <= innerWidth"), (theme, width))
                selector = self.page.locator("#theme-select")
                self.assertGreaterEqual(selector.bounding_box()["height"], 44)
                if width == 390 and theme in ["light", "dark"]:
                    self.assertLess(self.page.locator(".topbar").bounding_box()["height"], 80)
                    self.assertLess(self.page.locator(".proof").first.evaluate(
                        "(el) => el.getBoundingClientRect().top + window.scrollY"), 844)
                if artifacts and theme in ["premium", "retro95"] and width in [390, 1440]:
                    directory = Path(artifacts)
                    directory.mkdir(parents=True, exist_ok=True)
                    self.page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
                    self.page.screenshot(path=str(directory / f"{theme}-{width}.png"))
            self.page.get_by_role("button", name="Customer analytics", exact=True).click()
            self.assertEqual(self.page.locator(".project:visible").count(),
                             sum(p["category"] == "customer" for p in DATA["projects"]))
            self.page.locator('.proof[href="#case-metlife-service-survey"]').click()
            self.assertTrue(self.page.locator("#case-metlife-service-survey").is_visible())
            for research in DATA["research"][1:]:
                self.assertEqual(self.page.locator(".research-notes a").filter(
                    has_text=research["linkLabel"]).get_attribute("href"), research["url"])
            with tempfile.TemporaryDirectory() as directory:
                self.page.emulate_media(media="print")
                output = Path(directory) / "cv.pdf"
                self.page.pdf(path=str(output), format="A4", prefer_css_page_size=True)
                with fitz.open(output) as document:
                    self.assertEqual(len(document), 2, theme)
                    self.assertIn("2025 Agentic Teaming & Trust Research Report",
                                  document[0].get_text())
                self.assertTrue(self.page.locator(".shell").is_hidden())
                self.assertEqual(self.page.locator("body").evaluate(
                    "(el) => getComputedStyle(el).backgroundColor"), "rgb(255, 255, 255)")
                self.page.emulate_media(media="screen")


if __name__ == "__main__":
    unittest.main()
