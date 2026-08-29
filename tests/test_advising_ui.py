import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "web"


class AdvisingUiRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portal_js = (WEB_ROOT / "portal.js").read_text(encoding="utf-8")
        cls.feature_js = (WEB_ROOT / "feature.js").read_text(encoding="utf-8")
        cls.pathway_html = (WEB_ROOT / "pathway.html").read_text(encoding="utf-8")
        cls.advisor_html = (WEB_ROOT / "advisor.html").read_text(encoding="utf-8")
        cls.protected_html = [
            (WEB_ROOT / filename).read_text(encoding="utf-8")
            for filename in ("home.html", "advisor.html", "pathway.html", "graph.html", "governance.html", "profile.html")
        ]
        cls.server_py = (PROJECT_ROOT / "backend" / "server.py").read_text(encoding="utf-8")

    def test_protected_pages_and_signout_use_separate_login_page(self):
        self.assertIn("new URL('login.html'", self.portal_js)
        self.assertIn("location.href = 'login.html'", self.portal_js)
        self.assertNotIn("new URL('index.html'", self.portal_js)
        self.assertIn("localStorage.clear()", self.portal_js)
        self.assertIn("sessionStorage.clear()", self.portal_js)
        self.assertNotIn("fetch(API + '/api/auth/logout'", self.portal_js)
        self.assertTrue(all('portal.js?v=14' in html for html in self.protected_html))

    def test_pathway_has_controls_progress_and_constraint_status(self):
        for marker in ("data-pathway-form", "data-plan-status", "max_credits", "target_graduation"):
            self.assertIn(marker, self.pathway_html)
        for marker in ("degree_progress_percent", "constraints_checked", "pathway-timeline", "unscheduled_courses"):
            self.assertIn(marker, self.feature_js if marker != "constraints_checked" else self.server_py)

    def test_advisor_exposes_verification_evidence_and_agent_trace(self):
        for marker in ("data-advisor-context", "data-agent-status", "data-quick-actions"):
            self.assertIn(marker, self.advisor_html)
        for marker in ("renderAgentTrace", "renderAdvisorEvidence", "citation_details", "needs_faculty_approval"):
            self.assertIn(marker, self.feature_js)


if __name__ == "__main__":
    unittest.main()
