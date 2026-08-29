import unittest

from fastapi.testclient import TestClient

from backend.app import app


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_student_login_returns_student_and_no_session_cookie(self):
        login = self.client.post(
            "/api/auth/login",
            json={"regno": "241FA04077", "password": "password123"},
        )
        self.assertEqual(login.status_code, 200)
        data = login.json()
        self.assertTrue(data["success"])
        self.assertIn("student", data)
        self.assertNotIn("password",      data["student"])
        self.assertNotIn("password_hash", data["student"])
        # No session cookie should be set
        self.assertNotIn("acadgraph_session", login.headers.get("set-cookie", ""))

    def test_logout_is_a_no_op_and_returns_success(self):
        logout = self.client.post("/api/auth/logout")
        self.assertEqual(logout.status_code, 200)
        self.assertTrue(logout.json()["success"])

    def test_wrong_credentials_return_401(self):
        response = self.client.post(
            "/api/auth/login",
            json={"regno": "241FA04077", "password": "incorrect"},
        )
        self.assertEqual(response.status_code, 401)

    def test_faculty_login_returns_success(self):
        login = self.client.post(
            "/api/admin/login",
            json={"username": "faculty", "password": "faculty123"},
        )
        self.assertEqual(login.status_code, 200)
        self.assertTrue(login.json().get("success"))


if __name__ == "__main__":
    unittest.main()
