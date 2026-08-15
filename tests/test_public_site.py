from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES = {
    "/docs/": SITE / "index.html",
    "/docs/about/": SITE / "about" / "index.html",
    "/docs/miners/": SITE / "miners" / "index.html",
    "/docs/validators/": SITE / "validators" / "index.html",
    "/docs/troubleshooting/": SITE / "troubleshooting" / "index.html",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.scripts: list[dict[str, str]] = []
        self.stylesheets: list[str] = []
        self.canonicals: list[str] = []
        self.h1_count = 0
        self.main_count = 0
        self.current_count = 0
        self.inline_style_count = 0
        self._inline_script_depth = 0
        self.inline_script_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if identifier := values.get("id"):
            self.ids.add(identifier)
        if "style" in values:
            self.inline_style_count += 1
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        elif tag == "script":
            self.scripts.append(values)
            if not values.get("src"):
                self._inline_script_depth += 1
        elif tag == "link":
            rel = values.get("rel", "").split()
            if "stylesheet" in rel:
                self.stylesheets.append(values.get("href", ""))
            if "canonical" in rel:
                self.canonicals.append(values.get("href", ""))
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "main":
            self.main_count += 1
        if values.get("aria-current") == "page":
            self.current_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._inline_script_depth:
            self._inline_script_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._inline_script_depth:
            self.inline_script_text += data


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


class PublicSiteTests(unittest.TestCase):
    def test_pages_have_one_clear_document_structure(self) -> None:
        for route, path in PAGES.items():
            with self.subTest(route=route):
                page = parse_page(path)
                self.assertEqual(page.h1_count, 1)
                self.assertEqual(page.main_count, 1)
                self.assertEqual(page.current_count, 1)
                self.assertIn("main-content", page.ids)
                self.assertEqual(page.inline_style_count, 0)
                self.assertEqual(page.inline_script_text.strip(), "")
                self.assertEqual(
                    page.stylesheets,
                    ["/docs/assets/docs.css"],
                )
                self.assertEqual(
                    [script.get("src") for script in page.scripts],
                    ["/docs/assets/docs.js"],
                )
                self.assertEqual(
                    page.canonicals,
                    [f"https://instantsubnet.com{route}"],
                )

    def test_internal_routes_and_fragments_resolve(self) -> None:
        parsed = {route: parse_page(path) for route, path in PAGES.items()}
        for source_route, page in parsed.items():
            for href in page.hrefs:
                target = urlsplit(href)
                if target.scheme or target.netloc:
                    continue
                with self.subTest(source=source_route, href=href):
                    self.assertTrue(target.path.startswith("/docs/"))
                    self.assertIn(target.path, PAGES)
                    if target.fragment:
                        self.assertIn(target.fragment, parsed[target.path].ids)

    def test_assets_exist_and_pages_contain_no_operational_disclosures(self) -> None:
        self.assertTrue((SITE / "assets" / "docs.css").is_file())
        self.assertTrue((SITE / "assets" / "docs.js").is_file())
        self.assertTrue((SITE / "assets" / "favicon.svg").is_file())
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "README.md", *PAGES.values()]
        )
        self.assertIsNone(re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", public_text))
        self.assertIsNone(
            re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", public_text)
        )
        for forbidden in (
            "password-free SSH",
            "netuid 5",
            "BEGIN PRIVATE KEY",
            "BEGIN OPENSSH PRIVATE KEY",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden.casefold(), public_text.casefold())

    def test_docs_artifact_has_no_platform_asset_dependency(self) -> None:
        public_assets = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [SITE / "assets" / "docs.css", *PAGES.values()]
        )
        self.assertNotIn('url("/assets/', public_assets)
        self.assertNotIn('href="/assets/', public_assets)


if __name__ == "__main__":
    unittest.main()
