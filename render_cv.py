"""Render private CV HTML outside the public repository."""

import asyncio
import os
from pathlib import Path

import fitz
from playwright.async_api import async_playwright


async def main():
    directory = os.environ.get("PORTFOLIO_PRIVATE_CV_DIR")
    if not directory or not Path(directory).is_absolute():
        raise ValueError(
            "Set PORTFOLIO_PRIVATE_CV_DIR to an absolute directory outside this repository."
        )
    assets = Path(directory).resolve()
    root = Path(__file__).resolve().parent
    if assets == root or root in assets.parents:
        raise ValueError("Private CV output must be outside this repository.")
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
