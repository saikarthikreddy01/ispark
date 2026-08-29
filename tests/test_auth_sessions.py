import unittest

from fastapi.testclient import TestClient

from backend.app import app


class AuthenticationSessionTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_student_login_session_and_logout(self):
        login = self.client.post(
            "/api/auth/login",
            json={"regno": "241FA04077", "password": "password123"},
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn("acadgraph_session", login.headers.get("set-cookie", ""))

        session = self.client.get("/api/auth/session")
        self.assertEqual(session.status_code, 200)
        self.assertEqual(session.json()["role"], "student")
        self.assertEqual(session.json()["student"]["id"], "241FA04077")
        self.assertNotIn("password", session.json()["student"])
        self.assertNotIn("password_hash", session.json()["student"])

        logout = self.client.post("/api/auth/logout")
        self.assertEqual(logout.status_code, 200)
        self.assertIn("cookies", logout.headers.get("clear-site-data", ""))
        self.assertEqual(self.client.get("/api/auth/session").status_code, 401)

    def test_faculty_session_controls_review_access(self):
        self.assertEqual(self.client.get("/api/admin/stats").status_code, 401)
        login = self.client.post(
            "/api/admin/login",
            json={"username": "faculty", "password": "faculty123"},
        )
        self.assertEqual(login.status_code, 200)

        session = self.client.get("/api/auth/session")
        self.assertEqual(session.status_code, 200)
        self.assertEqual(session.json()["role"], "faculty")
        self.assertEqual(self.client.get("/api/admin/stats").status_code, 200)

    def test_wrong_credentials_do_not_create_session(self):
        response = self.client.post(
            "/api/auth/login",
            json={"regno": "241FA04077", "password": "incorrect"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.client.get("/api/auth/session").status_code, 401)


if __name__ == "__main__":
    unittest.main()
