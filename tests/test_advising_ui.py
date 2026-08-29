import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "web"


class AdvisingUiRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portal_js = (WEB_ROOT / "portal.js").read_text(encoding="utf-8")
        cls.auth_js   = (WEB_ROOT / "auth.js").read_text(encoding="utf-8")
        cls.feature_js = (WEB_ROOT / "feature.js").read_text(encoding="utf-8")
        cls.pathway_html = (WEB_ROOT / "pathway.html").read_text(encoding="utf-8")
        cls.advisor_html = (WEB_ROOT / "advisor.html").read_text(encoding="utf-8")
        cls.server_py = (PROJECT_ROOT / "backend" / "server.py").read_text(encoding="utf-8")

    def test_signout_clears_localstorage_and_redirects_to_login(self):
        # signOut() must clear localStorage and redirect — no session/cookie API
        self.assertIn("clearAuthStorage", self.portal_js)
        self.assertIn("localStorage.removeItem", self.portal_js)
        self.assertIn("window.location.replace('login.html')", self.portal_js)
        # Must NOT rely on server-side session polling or /logout route
        self.assertNotIn("/api/auth/session", self.portal_js)
        self.assertNotIn("href = '/logout'", self.portal_js)

    def test_login_stores_student_id_in_localstorage(self):
        self.assertIn("academic_advisor_user_id", self.auth_js)
        self.assertIn("academic_advisor_faculty_session", self.auth_js)
        # Must NOT ping session endpoint on login page load
        self.assertNotIn("redirectExistingSession", self.auth_js)
        self.assertNotIn("/api/auth/session", self.auth_js)

    def test_protected_pages_check_localstorage_not_session_endpoint(self):
        self.assertIn("hasActiveSession", self.portal_js)
        self.assertIn("window.location.replace('login.html')", self.portal_js)
        self.assertNotIn("/api/auth/session", self.portal_js)
        self.assertNotIn("href = '/logout'", self.portal_js)

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
