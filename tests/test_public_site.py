from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES = {
    "/": SITE / "index.html",
    "/about/": SITE / "about" / "index.html",
    "/miners/": SITE / "miners" / "index.html",
    "/validators/": SITE / "validators" / "index.html",
    "/troubleshooting/": SITE / "troubleshooting" / "index.html",
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
                    ["/assets/docs.css"],
                )
                self.assertEqual(
                    [script.get("src") for script in page.scripts],
                    ["/assets/docs.js"],
                )
                self.assertEqual(
                    page.canonicals,
                    [f"https://docs.instantsubnet.com{route}"],
                )
                self.assertEqual(
                    page.hrefs.count("https://instantsubnet.com/"),
                    1,
                )

    def test_internal_routes_and_fragments_resolve(self) -> None:
        parsed = {route: parse_page(path) for route, path in PAGES.items()}
        for source_route, page in parsed.items():
            for href in page.hrefs:
                target = urlsplit(href)
                if target.scheme or target.netloc:
                    continue
                with self.subTest(source=source_route, href=href):
                    self.assertTrue(target.path.startswith("/"))
                    self.assertIn(target.path, PAGES)
                    if target.fragment:
                        self.assertIn(target.fragment, parsed[target.path].ids)

    def test_assets_exist_and_pages_contain_no_operational_disclosures(self) -> None:
        self.assertTrue((SITE / "assets" / "docs.css").is_file())
        self.assertTrue((SITE / "assets" / "docs.js").is_file())
        self.assertTrue((SITE / "assets" / "instant-mark-light.svg").is_file())
        self.assertTrue((SITE / "assets" / "instant-mark-dark.svg").is_file())
        self.assertTrue((SITE / "assets" / "favicon.svg").is_file())
        for path in PAGES.values():
            page = path.read_text(encoding="utf-8")
            self.assertIn('class="docs-brand-mark-light"', page)
            self.assertIn('class="docs-brand-mark-dark"', page)
            self.assertNotIn('aria-hidden="true">IN</span>', page)
            self.assertIn('<a href="https://instantsubnet.com/">Home</a>', page)
            self.assertNotIn(">Website</a>", page)
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "README.md", *PAGES.values()]
        )
        self.assertEqual(
            set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", public_text)),
            {"127.0.0.1"},
        )
        self.assertIsNone(
            re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", public_text)
        )
        for forbidden in (
            "password-free SSH",
            "localnet",
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

    def test_miner_docs_match_the_public_phase_three_workflow(self) -> None:
        miner = PAGES["/miners/"].read_text(encoding="utf-8")
        troubleshooting = PAGES["/troubleshooting/"].read_text(encoding="utf-8")
        overview = PAGES["/"].read_text(encoding="utf-8")
        about = PAGES["/about/"].read_text(encoding="utf-8")

        for expected in (
            "curl -fsSL https://instantsubnet.com/miner/install | sudo bash",
            "Enter the registered Miner UID",
            "Enter the registered SS58 hotkey",
            'sudo "$MINER_CLI" status',
            'sudo "$MINER_CLI" stats',
            'sudo "$MINER_CLI" update check',
            'sudo "$MINER_CLI" update apply',
            "127.0.0.1:8787",
            "Miner Kit never auto-updates",
            "131,072-token combined context",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, miner)

        for expected in (
            "instant-worker.service",
            "instant-vllm.service",
            "The installer cannot find my hotkey",
            "Does Instant limit generation to 64 tokens?",
            "Local statistics do not store prompts",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, troubleshooting)

        public_miner_text = "\n".join((miner, overview, about))
        for stale in (
            "public installer is unavailable",
            "public miner installer is not published",
            "Public access unavailable",
            "Miner participation is not open to the public",
            "public miner profile",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale.casefold(), public_miner_text.casefold())

    def test_validator_docs_match_the_public_phase_four_workflow(self) -> None:
        validator = PAGES["/validators/"].read_text(encoding="utf-8")
        troubleshooting = PAGES["/troubleshooting/"].read_text(encoding="utf-8")
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "README.md", *PAGES.values()]
        )

        for expected in (
            "python3 scripts/start_validator.py",
            "INSTANT_NETWORK=&lt;network&gt;",
            "INSTANT_NETUID=&lt;netuid&gt;",
            "INSTANT_PLATFORM_REPORT_URL=https://api.instantsubnet.com/validator/v1/reports/latest",
            "INSTANT_PLATFORM_SIGNER=5E1oV49jn5s2pZMkn1NSNCE3pU6afjKMcAhDPvy2iZacQVp5",
            "INSTANT_WALLET_NAME=&lt;wallet name&gt;",
            "INSTANT_WALLET_HOTKEY=&lt;hotkey name&gt;",
            "INSTANT_WALLET_PATH=~/.bittensor/wallets",
            "python3 scripts/update_validator.py --once",
            "pm2 startup",
            "pm2 status instant-validator-updater",
            "crontab -l | grep instant-validator-run-once",
            "scripts/run_validator.sh",
            "instant-validator-updater",
            "60 × speed_bps",
            "normalized_weight = floor(score_bps × 65,535 / highest_score_bps)",
            "Ninety percent performance, ten percent discovery",
            "Update or restore the schedules",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, validator)

        for expected in (
            "empty Miner list",
            "instant-validator-updater",
            "configured network, netuid, Platform signer",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, troubleshooting)

        for stale in (
            "Finney is the public default",
            "Process each finalized Miner report once",
            "report_already_processed",
            "period_end_block",
            "100% burn",
            "burn mode",
            "shadow mode",
            "NOT SUBMITTED",
            "performance vector",
            "weight submission",
            "modes are mutually exclusive",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale.casefold(), public_text.casefold())


if __name__ == "__main__":
    unittest.main()
