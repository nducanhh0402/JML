import os
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TestReadmeDemoTF16BE3(unittest.TestCase):
    def test_readme_contains_module_10_duc_anh_tf16be3(self):
        with open(os.path.join(ROOT, "README.md"), "r", encoding="utf-8") as f:
            readme = f.read()

        self.assertIn("TF16BE3", readme)
        self.assertIn("Nguyễn Đức Anh", readme)
        self.assertIn("B25DTCN220", readme)
        self.assertIn("DEMO_SCRIPT_TF16BE3.md", readme)
        self.assertIn("TEST_CASES_AUTH_RBAC_TF16BE3.md", readme)
        self.assertIn("APP_ENV=production", readme)
        self.assertIn("1t-XQzuHnHSxzVhezwbtGveCdZiSESl0S", readme)

    def test_demo_script_tf16be3_exists_and_has_steps(self):
        path = os.path.join(ROOT, "backend", "tests", "DEMO_SCRIPT_TF16BE3.md")
        with open(path, "r", encoding="utf-8") as f:
            script = f.read()

        self.assertIn("1280×900", script)
        self.assertIn("390×844", script)
        self.assertIn("/api/auth/login", script)
        self.assertIn("/api/user/change-password", script)
        self.assertIn("pytest", script)

    def test_test_cases_doc_tf16be3_exists_and_has_diagram(self):
        path = os.path.join(ROOT, "backend", "tests", "TEST_CASES_AUTH_RBAC_TF16BE3.md")
        with open(path, "r", encoding="utf-8") as f:
            doc = f.read()

        self.assertIn("sequenceDiagram", doc)
        self.assertIn("test_auth_register_login.py", doc)
        self.assertIn("test_production_mode.py", doc)
        self.assertIn("155", doc)


if __name__ == "__main__":
    unittest.main()
