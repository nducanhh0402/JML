import os
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TestReadmeDemoTF16BEF(unittest.TestCase):
    def test_readme_has_demo_and_vercel_links(self):
        with open(os.path.join(ROOT, "README.md"), "r", encoding="utf-8") as f:
            readme = f.read()

        self.assertIn("Bản Demo Trực Tuyến", readme)
        self.assertIn("jml-teal.vercel.app", readme)
        self.assertIn("Kịch bản Demo & Minh chứng", readme)
        self.assertIn("Minh chứng nộp TF16BEF", readme)

    def test_demo_script_contains_desktop_mobile_and_terminal_steps(self):
        path = os.path.join(ROOT, "backend", "tests", "DEMO_SCRIPT_TF16BEF.md")
        with open(path, "r", encoding="utf-8") as f:
            script = f.read()

        self.assertIn("1280×900", script)
        self.assertIn("390×844", script)
        self.assertIn("/api/homepage", script)
        self.assertIn("benchmark_homepage_tf175bc", script)

    def test_readme_contains_run_instructions(self):
        with open(os.path.join(ROOT, "README.md"), "r", encoding="utf-8") as f:
            readme = f.read()

        self.assertIn("uvicorn backend.main:app", readme)
        self.assertIn("python -m http.server 5500", readme)
        self.assertIn("Swagger UI", readme)


if __name__ == "__main__":
    unittest.main()
