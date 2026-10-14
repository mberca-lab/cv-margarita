"""Render the generated CV HTML into selectable-text PDF downloads."""

import asyncio
from pathlib import Path

import fitz
from playwright.async_api import async_playwright


async def main():
    assets = Path(__file__).resolve().parent / "assets"
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            page = await browser.new_page()
            await page.emulate_media(media="print")
            for suffix, expected_pages in [("cv", 2), ("portfolio-cv", 4)]:
                name = f"margarita-bermejo-cano-{suffix}"
                await page.goto((assets / f"{name}.html").as_uri())
                await page.pdf(
                    path=str(assets / f"{name}.pdf"),
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                    tagged=True,
                    outline=True,
                )
                with fitz.open(assets / f"{name}.pdf") as document:
                    if len(document) != expected_pages:
                        raise ValueError(
                            f"{name}: expected {expected_pages} pages, got {len(document)}"
                        )
                    if any(not pdf_page.get_text().strip() for pdf_page in document):
                        raise ValueError(f"{name}: an empty PDF page was generated")
                print(f"Rendered {name}.pdf ({expected_pages} pages)")
        finally:
            await browser.close()


asyncio.run(main())
