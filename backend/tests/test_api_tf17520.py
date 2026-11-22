"""
Bộ kiểm thử tổng hợp API Trang Chủ, Chi Tiết Sản Phẩm và Đánh Giá (Task TF17520)
Chạy độc lập với mock DB qua unittest để kiểm chứng:
1. API Trang chủ (/api/homepage*): dữ liệu đúng, limit, tự nạp banner mẫu, trạng thái rỗng.
2. API Chi tiết sản phẩm (/api/products/{product_id}): dữ liệu đúng, hết hàng, ID không tồn tại / <= 0 (404).
3. API Đánh giá (/api/reviews*): dữ liệu đúng, điểm trung bình, ID không tồn tại (404/400/422),
   đánh giá trùng (409), điểm sao ngoài khoảng 1..5 và nhận xét rỗng (422/400).
"""

import json
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from pydantic import ValidationError

from backend.src.modules.homepage import router as homepage_router_module
from backend.src.modules.product import router as product_router_module
from backend.src.modules.review import router as review_router_module
from backend.tests.test_product_detail import (
    SAMPLE_ROWS as PRODUCT_SAMPLE_ROWS,
    _FakeConnection as _FakeProductConnection,
)
from backend.tests.test_reviews import _FakeConnection as _FakeReviewConnection


class _FakeHomepageCursor:
    def __init__(self, state):
        self.state = state
        self._one = None
        self._all = []

    def execute(self, sql, params=None):
        sql_lower = " ".join(sql.strip().lower().split())
        self._one = None
        self._all = []

        if sql_lower.startswith("create table if not exists banners"):
            return

        if sql_lower.startswith("select count(*) as cnt from banners"):
            self._one = {"cnt": len(self.state["banners"])}
            return

        if "from banners where is_active = 1" in sql_lower:
            active = [b for b in self.state["banners"] if b.get("is_active", 1) == 1]
            active.sort(key=lambda x: x["sort_order"])
            self._all = active
            return

        if "from products" in sql_lower and "order by rating desc, sold desc" in sql_lower:
            limit = int(params[0]) if params else 10
            approved = [p for p in self.state["products"] if p.get("status") == "approved"]
            approved.sort(key=lambda x: (x["rating"], x["sold"]), reverse=True)
            self._all = approved[:limit]
            return

        if "from products" in sql_lower and "order by id desc" in sql_lower:
            limit = int(params[0]) if params else 10
            approved = [p for p in self.state["products"] if p.get("status") == "approved"]
            approved.sort(key=lambda x: x["id"], reverse=True)
            self._all = approved[:limit]
            return

        if "group by category" in sql_lower and "from products" in sql_lower:
            counts = {}
            for p in self.state["products"]:
                if p.get("status") == "approved":
                    cat = p["category"]
                    counts[cat] = counts.get(cat, 0) + 1
            self._all = [
                {"category": cat, "product_count": cnt}
                for cat, cnt in sorted(counts.items(), key=lambda item: item[1], reverse=True)
            ]

    def executemany(self, sql, rows):
        for idx, row in enumerate(rows, start=len(self.state["banners"]) + 1):
            title, image_url, link_url, description, sort_order, is_active = row
            self.state["banners"].append({
                "id": idx,
                "title": title,
                "image_url": image_url,
                "link_url": link_url,
                "description": description,
                "sort_order": sort_order,
                "is_active": is_active,
            })

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._all


class _FakeHomepageConnection:
    def __init__(self, state):
        self.state = state
        self.closed = False

    def cursor(self):
        return _FakeHomepageCursor(self.state)

    def commit(self):
        pass

    def close(self):
        self.closed = True


def _sample_homepage_state():
    return {
        "banners": [
            {
                "id": 1,
                "title": "Banner Active 2",
                "image_url": "https://example.com/b2.jpg",
                "link_url": "/products?category=tech",
                "description": "Tech sale",
                "sort_order": 2,
                "is_active": 1,
            },
            {
                "id": 2,
                "title": "Banner Hidden",
                "image_url": "https://example.com/hidden.jpg",
                "link_url": "/products",
                "description": "Hidden",
                "sort_order": 0,
                "is_active": 0,
            },
            {
                "id": 3,
                "title": "Banner Active 1",
                "image_url": "https://example.com/b1.jpg",
                "link_url": "/products?category=audio",
                "description": "Audio sale",
                "sort_order": 1,
                "is_active": 1,
            },
        ],
        "products": [
            {
                "id": 1,
                "category": "audio",
                "title": "Tai nghe Sony WH-1000XM5",
                "price": 7490000,
                "original_price": 9490000,
                "discount": "-21%",
                "rating": 4.9,
                "sold": 84,
                "total_stock": 100,
                "images_json": json.dumps(["https://example.com/sony.jpg"]),
                "angles_json": json.dumps(["Chính diện"]),
                "exclusive": "Bán Chạy",
                "shop_name": "SoundMax Audio",
                "is_flash_sale": 1,
                "status": "approved",
            },
            {
                "id": 2,
                "category": "audio",
                "title": "Loa Marshall Stanmore III",
                "price": 8900000,
                "original_price": 8900000,
                "discount": "0%",
                "rating": 4.8,
                "sold": 95,
                "total_stock": 100,
                "images_json": json.dumps(["https://example.com/marshall.jpg"]),
                "angles_json": json.dumps(["Mặt trước"]),
                "exclusive": "Chính Hãng",
                "shop_name": "SoundMax Audio",
                "is_flash_sale": 0,
                "status": "approved",
            },
            {
                "id": 3,
                "category": "tech",
                "title": "iPad Pro M4 256GB",
                "price": 26990000,
                "original_price": 28990000,
                "discount": "-7%",
                "rating": 5.0,
                "sold": 50,
                "total_stock": 50,
                "images_json": json.dumps(["https://example.com/ipad.jpg"]),
                "angles_json": json.dumps(["Toàn cảnh"]),
                "exclusive": "Hot Deal",
                "shop_name": "AB Technology",
                "is_flash_sale": 0,
                "status": "approved",
            },
            {
                "id": 4,
                "category": "watch",
                "title": "Đồng hồ chưa duyệt",
                "price": 5000000,
                "original_price": 5500000,
                "discount": "-9%",
                "rating": 5.0,
                "sold": 999,
                "total_stock": 10,
                "images_json": json.dumps(["https://example.com/watch.jpg"]),
                "angles_json": json.dumps(["Chính diện"]),
                "exclusive": "Chính Hãng",
                "shop_name": "Watch Store",
                "is_flash_sale": 0,
                "status": "pending",
            },
        ],
    }


class TestHomepageAPITF17520(unittest.TestCase):
    def setUp(self):
        self.state = _sample_homepage_state()

    def _patch_db(self):
        return patch.object(
            homepage_router_module,
            "get_db_connection",
            side_effect=lambda: _FakeHomepageConnection(self.state),
        )

    def test_tc_hp01_get_homepage_aggregated_valid_data(self):
        """TC-HP-01: GET /api/homepage trả về banners, featured, latest, categories và summary đúng."""
        with self._patch_db():
            res = homepage_router_module.get_homepage(featured_limit=2, latest_limit=2)

        self.assertEqual(len(res["banners"]), 2)
        self.assertEqual(res["banners"][0]["title"], "Banner Active 1")
        self.assertEqual([p["id"] for p in res["featured_products"]], [3, 1])
        self.assertEqual([p["id"] for p in res["latest_products"]], [3, 2])
        self.assertEqual(res["summary"]["total_banners"], 2)
        self.assertEqual(res["summary"]["total_featured"], 2)
        self.assertEqual(res["summary"]["total_latest"], 2)
        self.assertEqual(res["summary"]["total_categories"], 2)

    def test_tc_hp02_get_banners_active_sorted_and_auto_seed(self):
        """TC-HP-02: GET /api/homepage/banners lọc is_active=1 và tự nạp 5 banner mẫu khi trống."""
        with self._patch_db():
            res = homepage_router_module.get_banners()
        self.assertEqual(res["total"], 2)
        self.assertEqual([b["sortOrder"] for b in res["banners"]], [1, 2])

        self.state["banners"] = []
        with self._patch_db():
            seeded = homepage_router_module.get_banners()
        self.assertEqual(seeded["total"], 5)
        self.assertEqual(len(self.state["banners"]), 5)

    def test_tc_hp03_get_featured_and_latest_respect_limit_and_approved(self):
        """TC-HP-03: Featured & latest chỉ lấy sản phẩm approved và áp dụng đúng limit."""
        with self._patch_db():
            feat = homepage_router_module.get_featured_products(limit=10)
            latest = homepage_router_module.get_latest_products(limit=2)

        self.assertEqual([p["id"] for p in feat["featured_products"]], [3, 1, 2])
        self.assertTrue(all(p["status"] == "approved" for p in feat["featured_products"]))
        self.assertEqual([p["id"] for p in latest["latest_products"]], [3, 2])

    def test_tc_hp04_get_categories_grouped_counts(self):
        """TC-HP-04: GET /api/homepage/categories gom nhóm đúng số lượng theo danh mục approved."""
        with self._patch_db():
            res = homepage_router_module.get_homepage_categories()
        self.assertEqual(res["total"], 2)
        self.assertEqual(res["categories"][0]["id"], "audio")
        self.assertEqual(res["categories"][0]["productCount"], 2)
        self.assertEqual(res["categories"][1]["id"], "tech")
        self.assertEqual(res["categories"][1]["productCount"], 1)

    def test_tc_hp05_homepage_empty_approved_products(self):
        """TC-HP-05: Trang chủ trả về danh sách rỗng an toàn khi không có sản phẩm đã duyệt."""
        self.state["products"] = [p for p in self.state["products"] if p["status"] != "approved"]
        with self._patch_db():
            res = homepage_router_module.get_homepage(featured_limit=10, latest_limit=10)
        self.assertEqual(res["featured_products"], [])
        self.assertEqual(res["latest_products"], [])
        self.assertEqual(res["categories"], [])
        self.assertEqual(res["summary"]["total_featured"], 0)


class TestProductDetailAPITF17520(unittest.TestCase):
    def _patch_db(self):
        return patch.object(
            product_router_module,
            "get_db_connection",
            side_effect=lambda: _FakeProductConnection(PRODUCT_SAMPLE_ROWS),
        )

    def test_tc_pd01_get_product_detail_valid_data(self):
        """TC-PD-01: GET /api/products/1 trả đầy đủ ảnh, mô tả, thương hiệu, giá, tồn kho, SP liên quan."""
        with self._patch_db():
            data = product_router_module.get_product_by_id(1)

        self.assertEqual(data["id"], 1)
        self.assertEqual(data["brand"], "Sony")
        self.assertEqual(data["price"], 7490000)
        self.assertEqual(data["originalPrice"], 9490000)
        self.assertEqual(data["stock"], 16)
        self.assertTrue(data["inStock"])
        self.assertEqual(data["stockStatus"], "in_stock")
        self.assertEqual(len(data["images"]), 2)
        self.assertEqual(len(data["relatedProducts"]), 1)

    def test_tc_pd02_get_product_detail_out_of_stock(self):
        """TC-PD-02: GET /api/products/3 hết hàng trả inStock=False và stockStatus='out_of_stock'."""
        with self._patch_db():
            data = product_router_module.get_product_by_id(3)
        self.assertEqual(data["stock"], 0)
        self.assertFalse(data["inStock"])
        self.assertEqual(data["stockStatus"], "out_of_stock")

    def test_tc_pd03_get_product_detail_nonexistent_id_404(self):
        """TC-PD-03: GET /api/products/99999 (ID không tồn tại) -> HTTP 404."""
        with self._patch_db():
            with self.assertRaises(HTTPException) as ctx:
                product_router_module.get_product_by_id(99999)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("không tồn tại", ctx.exception.detail)

    def test_tc_pd04_get_product_detail_invalid_zero_or_negative_id_404(self):
        """TC-PD-04: GET /api/products/0 và /api/products/-1 -> HTTP 404."""
        with self._patch_db():
            for bad_id in (0, -1):
                with self.assertRaises(HTTPException) as ctx:
                    product_router_module.get_product_by_id(bad_id)
                self.assertEqual(ctx.exception.status_code, 404)


class TestReviewsAPITF17520(unittest.TestCase):
    def setUp(self):
        self.state = {
            "products": {
                1: {"id": 1, "title": "Tai nghe Sony WH-1000XM5", "rating": 5.0},
                2: {"id": 2, "title": "iPad Pro M4 256GB", "rating": 5.0},
                3: {"id": 3, "title": "Đồng hồ Tissot Le Locle", "rating": 5.0},
            },
            "users": {
                10: {"full_name": "Nguyễn Đức Anh", "username": "buyer"},
                11: {"full_name": "Vũ Dũng", "username": "dung36"},
                12: {"full_name": "Trịnh Quốc Trung", "username": "trungshop"},
            },
            "reviews": [],
            "next_id": 1,
        }

    def _patch_db(self):
        return patch.object(
            review_router_module,
            "get_db_connection",
            side_effect=lambda: _FakeReviewConnection(self.state),
        )

    # ------------------------------------------------------------------
    # NHÓM 1: DỮ LIỆU ĐÚNG (VALID DATA)
    # ------------------------------------------------------------------
    def test_tc_rv01_create_valid_review_5_stars(self):
        """TC-RV-01: Gửi đánh giá 5 sao hợp lệ với user_id và nhận xét."""
        with self._patch_db():
            res = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1,
                    user_id=10,
                    rating=5,
                    comment="Chất âm tuyệt vời, đóng gói kỹ!",
                )
            )
        self.assertEqual(res["review"]["rating"], 5)
        self.assertEqual(res["review"]["user_name"], "Nguyễn Đức Anh")
        self.assertEqual(res["average_rating"], 5.0)
        self.assertEqual(res["total_reviews"], 1)

    def test_tc_rv02_create_valid_boundary_ratings_1_and_5(self):
        """TC-RV-02: Giá trị biên hợp lệ 1 sao và 5 sao cho điểm trung bình 3.0."""
        with self._patch_db():
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=5, comment="Rất hài lòng"
                )
            )
            res = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=11, rating=1, comment="Không hợp nhu cầu"
                )
            )
        self.assertEqual(res["average_rating"], 3.0)
        self.assertEqual(res["total_reviews"], 2)

    def test_tc_rv03_multiple_reviews_update_average_and_breakdown(self):
        """TC-RV-03: Nhiều người đánh giá cập nhật đúng điểm trung bình & phân bố sao."""
        with self._patch_db():
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=5, comment="Xuất sắc"
                )
            )
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=11, rating=4, comment="Tốt"
                )
            )
            res = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=12, rating=4, comment="Đáng tiền"
                )
            )
        self.assertEqual(res["average_rating"], 4.3)
        self.assertEqual(res["total_reviews"], 3)
        self.assertEqual(res["rating_breakdown"]["5"], 1)
        self.assertEqual(res["rating_breakdown"]["4"], 2)
        self.assertEqual(self.state["products"][1]["rating"], 4.3)

    def test_tc_rv04_get_reviews_list_and_empty_product(self):
        """TC-RV-04: Xem danh sách đánh giá (có dữ liệu & sản phẩm chưa có đánh giá)."""
        with self._patch_db():
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=5, comment="Đánh giá 1"
                )
            )
            res_has_data = review_router_module.get_product_reviews(
                product_id=1, rating=None, page=1, page_size=20
            )
            res_empty = review_router_module.get_product_reviews(
                product_id=3, rating=None, page=1, page_size=20
            )
        self.assertEqual(res_has_data["total_reviews"], 1)
        self.assertEqual(res_has_data["average_rating"], 5.0)
        self.assertEqual(len(res_has_data["reviews"]), 1)
        self.assertEqual(res_empty["total_reviews"], 0)
        self.assertEqual(res_empty["average_rating"], 0.0)
        self.assertEqual(res_empty["reviews"], [])

    def test_tc_rv05_filter_reviews_by_star_and_pagination(self):
        """TC-RV-05: Lọc danh sách đánh giá theo số sao (?rating=4) và phân trang."""
        with self._patch_db():
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=5, comment="Tuyệt"
                )
            )
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=11, rating=4, comment="Ổn 1"
                )
            )
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=12, rating=4, comment="Ổn 2"
                )
            )
            filtered = review_router_module.get_product_reviews(
                product_id=1, rating=4, page=1, page_size=1
            )
        self.assertEqual(filtered["total_reviews"], 3)
        self.assertEqual(filtered["pagination"]["total"], 2)
        self.assertEqual(filtered["pagination"]["total_pages"], 2)
        self.assertEqual(len(filtered["reviews"]), 1)
        self.assertEqual(filtered["reviews"][0]["rating"], 4)

    # ------------------------------------------------------------------
    # NHÓM 2: ID KHÔNG TỒN TẠI / ID KHÔNG HỢP LỆ
    # ------------------------------------------------------------------
    def test_tc_rv06_post_review_nonexistent_product_id_404(self):
        """TC-RV-06: Gửi đánh giá cho product_id không tồn tại -> 404."""
        with self._patch_db():
            with self.assertRaises(HTTPException) as ctx:
                review_router_module.add_product_review(
                    review_router_module.ReviewCreate(
                        product_id=99999,
                        user_id=10,
                        rating=5,
                        comment="Sản phẩm không tồn tại",
                    )
                )
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("không tồn tại", ctx.exception.detail)

    def test_tc_rv07_get_reviews_nonexistent_product_id_404(self):
        """TC-RV-07: Xem danh sách đánh giá cho product_id không tồn tại -> 404."""
        with self._patch_db():
            with self.assertRaises(HTTPException) as ctx:
                review_router_module.get_product_reviews(
                    product_id=99999, rating=None, page=1, page_size=20
                )
        self.assertEqual(ctx.exception.status_code, 404)

    def test_tc_rv08_get_reviews_invalid_product_id_zero_or_negative_400(self):
        """TC-RV-08: Xem danh sách đánh giá với product_id <= 0 -> 400."""
        with self._patch_db():
            for invalid_id in (0, -5):
                with self.assertRaises(HTTPException) as ctx:
                    review_router_module.get_product_reviews(
                        product_id=invalid_id, rating=None, page=1, page_size=20
                    )
                self.assertEqual(ctx.exception.status_code, 400)

    def test_tc_rv09_post_review_invalid_product_id_validation_error(self):
        """TC-RV-09: Gửi đánh giá với product_id <= 0 -> lỗi validate Pydantic (HTTP 422)."""
        for bad_id in (0, -1):
            with self.assertRaises(ValidationError):
                review_router_module.ReviewCreate(
                    product_id=bad_id,
                    user_id=10,
                    rating=5,
                    comment="Test ID <= 0",
                )

    # ------------------------------------------------------------------
    # NHÓM 3: ĐÁNH GIÁ TRÙNG (DUPLICATE REVIEW)
    # ------------------------------------------------------------------
    def test_tc_rv10_duplicate_review_same_user_id_same_product_409(self):
        """TC-RV-10: Cùng user_id gửi đánh giá lần 2 cho cùng sản phẩm -> 409 Conflict."""
        with self._patch_db():
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=5, comment="Đánh giá lần 1"
                )
            )
            with self.assertRaises(HTTPException) as ctx:
                review_router_module.add_product_review(
                    review_router_module.ReviewCreate(
                        product_id=1, user_id=10, rating=2, comment="Đánh giá lần 2"
                    )
                )
            list_res = review_router_module.get_product_reviews(
                product_id=1, rating=None, page=1, page_size=20
            )
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertEqual(list_res["total_reviews"], 1)
        self.assertEqual(list_res["average_rating"], 5.0)

    def test_tc_rv11_duplicate_review_same_guest_username_409(self):
        """TC-RV-11: Cùng user_name (không phân biệt hoa/thường) đánh giá trùng -> 409."""
        with self._patch_db():
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1,
                    user_name="Nguyễn Văn A",
                    rating=5,
                    comment="Tốt lắm",
                )
            )
            with self.assertRaises(HTTPException) as ctx:
                review_router_module.add_product_review(
                    review_router_module.ReviewCreate(
                        product_id=1,
                        user_name="  nguyễn văn a  ",
                        rating=1,
                        comment="Spam lần 2",
                    )
                )
        self.assertEqual(ctx.exception.status_code, 409)

    def test_tc_rv12_same_user_can_review_different_products(self):
        """TC-RV-12: Cùng user_id được phép đánh giá nhiều sản phẩm khác nhau."""
        with self._patch_db():
            r1 = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=5, comment="SP 1 rất tốt"
                )
            )
            r2 = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=2, user_id=10, rating=4, comment="SP 2 ổn"
                )
            )
        self.assertEqual(r1["review"]["product_id"], 1)
        self.assertEqual(r2["review"]["product_id"], 2)

    # ------------------------------------------------------------------
    # NHÓM 4: ĐIỂM SAO NGOÀI KHOẢNG (OUT-OF-RANGE) & NHẬN XÉT RỖNG
    # ------------------------------------------------------------------
    def test_tc_rv13_rating_below_min_zero(self):
        """TC-RV-13: Điểm sao = 0 (nhỏ hơn 1) -> ValidationError (HTTP 422)."""
        with self.assertRaises(ValidationError):
            review_router_module.ReviewCreate(
                product_id=1, user_id=10, rating=0, comment="0 sao"
            )

    def test_tc_rv14_rating_negative(self):
        """TC-RV-14: Điểm sao âm (-3) -> ValidationError (HTTP 422)."""
        with self.assertRaises(ValidationError):
            review_router_module.ReviewCreate(
                product_id=1, user_id=10, rating=-3, comment="Sao âm"
            )

    def test_tc_rv15_rating_above_max_6_and_99(self):
        """TC-RV-15: Điểm sao > 5 (6, 99) -> ValidationError (HTTP 422)."""
        for bad_star in (6, 99):
            with self.assertRaises(ValidationError):
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=bad_star, comment="Ngoài khoảng"
                )

    def test_tc_rv16_empty_or_whitespace_comment_rejected(self):
        """TC-RV-16: Nhận xét rỗng bị từ chối (422) và nhận xét toàn khoảng trắng bị từ chối (400)."""
        with self.assertRaises(ValidationError):
            review_router_module.ReviewCreate(
                product_id=1, user_id=10, rating=5, comment=""
            )
        with self._patch_db():
            with self.assertRaises(HTTPException) as ctx:
                review_router_module.add_product_review(
                    review_router_module.ReviewCreate(
                        product_id=1, user_id=10, rating=5, comment="     "
                    )
                )
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
