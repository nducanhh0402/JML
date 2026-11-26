"""
TF16FD3 - Kiểm thử cấu hình deploy Vercel, liên kết nội bộ và responsive Desktop/Mobile cho giao diện.
"""
import json
import pathlib
import re


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FRONTEND_DIR = REPO_ROOT / "frontend"

MAIN_DEMO_PAGES = [
    "index.html",
    "buyer/index.html",
    "buyer/products.html",
    "buyer/product-detail.html",
    "buyer/cart.html",
    "user/checkout.html",
    "user/orders.html",
    "user/profile.html",
    "user/addresses.html",
    "user/index.html",
    "auth/index.html",
    "seller/index.html",
    "admin/index.html",
    "admin/categories_brands.html",
    "admin/products.html",
]


def test_vercel_json_configuration():
    cfg_path = REPO_ROOT / "vercel.json"
    assert cfg_path.exists(), "Thiếu file cấu hình vercel.json ở thư mục gốc"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert cfg.get("outputDirectory") == "frontend"
    assert cfg.get("version") == 2
    rewrites = cfg.get("rewrites", [])
    assert any(r.get("source") == "/frontend/:path*" and r.get("destination") == "/:path*" for r in rewrites)


def test_all_main_pages_exist_with_viewport_and_no_conflicts():
    for rel in MAIN_DEMO_PAGES:
        page = FRONTEND_DIR / rel
        assert page.exists(), f"Thiếu trang demo: {rel}"
        html = page.read_text(encoding="utf-8")
        assert re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I), f"Thiếu thẻ viewport trong {rel}"
        assert "<<<<<<<" not in html and ">>>>>>>" not in html, f"Còn dấu conflict Git trong {rel}"


def test_no_broken_local_links_or_assets_on_vercel():
    broken = []
    for page in sorted(FRONTEND_DIR.rglob("*.html")):
        if "components" in page.parts:
            continue
        html = page.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'(?:href|src)=["\']([^"\'#?]+)["\']', html):
            ref = m.group(1).strip()
            if not ref or ref.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "${")):
                continue
            if ref.startswith("/"):
                target = FRONTEND_DIR / ref.lstrip("/").removeprefix("frontend/")
            else:
                target = (page.parent / ref).resolve()
            if not target.exists():
                broken.append((str(page.relative_to(REPO_ROOT)), ref))
    assert not broken, f"Phát hiện liên kết/tài nguyên cục bộ bị hỏng trên Vercel: {broken}"


def test_landing_page_links_and_responsive_breakpoints():
    landing = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
    assert "@media (max-width: 768px)" in landing
    assert "@media (max-width: 480px)" in landing
    for expected in (
        "./buyer/index.html",
        "./buyer/products.html",
        "./buyer/product-detail.html?id=101",
        "./buyer/cart.html",
        "./user/checkout.html",
        "./user/orders.html",
        "./user/profile.html",
        "./user/addresses.html",
        "./auth/index.html",
        "./seller/index.html",
        "./admin/index.html",
        "./admin/categories_brands.html",
        "./admin/products.html",
    ):
        assert expected in landing, f"Thiếu liên kết {expected} trong frontend/index.html"


def test_readme_documents_vercel_demo_section():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Vercel Live Demo" in readme
    assert "https://jml-teal.vercel.app" in readme
    assert "vercel.json" in readme
    for route in ("/buyer/index.html", "/buyer/products.html", "/user/checkout.html", "/auth/index.html", "/admin/index.html"):
        assert route in readme, f"README chưa ghi đường dẫn demo {route}"
