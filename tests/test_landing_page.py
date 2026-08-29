import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "web"


class LandingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicate_ids = []
        self.local_assets = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.append(element_id)
            self.ids.add(element_id)
        if tag == "script" and attributes.get("src"):
            self.local_assets.append(attributes["src"].split("?")[0])
        if tag == "link" and attributes.get("href"):
            self.local_assets.append(attributes["href"].split("?")[0])


class LandingPageRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
        cls.login_html = (WEB_ROOT / "login.html").read_text(encoding="utf-8")
        cls.auth_js = (WEB_ROOT / "auth.js").read_text(encoding="utf-8")
        cls.parser = LandingParser()
        cls.parser.feed(cls.html)
        cls.login_parser = LandingParser()
        cls.login_parser.feed(cls.login_html)

    def test_landing_sections_and_separate_login_page_exist(self):
        required = {"project-title", "features-panel", "how-it-works-panel"}
        self.assertFalse(self.parser.duplicate_ids)
        self.assertFalse(required - self.parser.ids)
        self.assertNotIn("auth-form", self.parser.ids)
        for target in ("features", "how-it-works"):
            self.assertIn(f'data-landing-target="{target}"', self.html)
            self.assertIn(f'data-landing-panel="{target}"', self.html)
        self.assertGreaterEqual(self.html.count('href="login.html"'), 3)

        login_required = {"auth-form", "field-stack", "visual-canvas", "mode-switch"}
        self.assertFalse(self.login_parser.duplicate_ids)
        self.assertFalse(login_required - self.login_parser.ids)
        self.assertIn('href="index.html"', self.login_html)

    def test_successful_login_routes_to_the_correct_dashboard(self):
        self.assertIn("window.location.replace('home.html')", self.auth_js)
        self.assertIn("window.location.replace('governance.html')", self.auth_js)
        self.assertIn("/api/auth/session", self.auth_js)
        self.assertNotIn("localStorage", self.auth_js)

    def test_feature_and_workflow_content_is_complete(self):
        self.assertEqual(self.html.count('class="feature-number"'), 8)
        workflow = re.search(r'<ol class="workflow-list">(.*?)</ol>', self.html, re.DOTALL)
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.group(1).count("<li>"), 6)

    def test_local_landing_assets_exist(self):
        for asset in self.parser.local_assets + self.login_parser.local_assets:
            if asset.startswith(("http://", "https://")):
                continue
            self.assertTrue((WEB_ROOT / asset).exists(), asset)


if __name__ == "__main__":
    unittest.main()
