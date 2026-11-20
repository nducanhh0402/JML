"""
Bộ kiểm thử 16 Test Case cho API Đánh Giá Sản Phẩm (Reviews API)
Phạm vi kiểm thử:
1. Dữ liệu đúng (POST /api/reviews, GET /api/reviews/{product_id}, điểm trung bình, lọc sao, phân trang)
2. ID không tồn tại & ID không hợp lệ (404 / 400 / 422)
3. Đánh giá trùng lặp (mỗi người tối đa 1 đánh giá cho mỗi sản phẩm -> 409)
4. Điểm sao ngoài khoảng 1–5 và dữ liệu nhận xét không hợp lệ
"""

import unittest
from unittest.mock import patch
from fastapi import HTTPException
from pydantic import ValidationError

from backend.src.modules.review import router as review_router_module
from backend.tests.test_reviews import _FakeConnection


class TestReviewsAPICases(unittest.TestCase):
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
            side_effect=lambda: _FakeConnection(self.state),
        )

    # ------------------------------------------------------------------
    # NHÓM 1: DỮ LIỆU ĐÚNG (VALID DATA)
    # ------------------------------------------------------------------
    def test_tc01_create_valid_review_5_stars(self):
        """TC-01: Gửi đánh giá 5 sao hợp lệ với user_id và nhận xét."""
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

    def test_tc02_create_valid_boundary_ratings_1_and_5(self):
        """TC-02: Giá trị biên hợp lệ 1 sao và 5 sao cho điểm trung bình 3.0."""
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

    def test_tc03_multiple_reviews_update_average_and_breakdown(self):
        """TC-03: Nhiều người đánh giá cập nhật đúng điểm trung bình & phân bố sao."""
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
        # (5 + 4 + 4) / 3 = 4.333... -> 4.3
        self.assertEqual(res["average_rating"], 4.3)
        self.assertEqual(res["total_reviews"], 3)
        self.assertEqual(res["rating_breakdown"]["5"], 1)
        self.assertEqual(res["rating_breakdown"]["4"], 2)
        self.assertEqual(self.state["products"][1]["rating"], 4.3)

    def test_tc04_get_reviews_list_and_empty_product(self):
        """TC-04: Xem danh sách đánh giá (có dữ liệu & sản phẩm chưa có đánh giá)."""
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

    def test_tc05_filter_reviews_by_star_and_pagination(self):
        """TC-05: Lọc danh sách đánh giá theo số sao (?rating=4) và phân trang."""
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
    def test_tc06_post_review_nonexistent_product_id_404(self):
        """TC-06: Gửi đánh giá cho product_id không tồn tại -> 404."""
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

    def test_tc07_get_reviews_nonexistent_product_id_404(self):
        """TC-07: Xem danh sách đánh giá cho product_id không tồn tại -> 404."""
        with self._patch_db():
            with self.assertRaises(HTTPException) as ctx:
                review_router_module.get_product_reviews(
                    product_id=99999, rating=None, page=1, page_size=20
                )
        self.assertEqual(ctx.exception.status_code, 404)

    def test_tc08_get_reviews_invalid_product_id_zero_or_negative_400(self):
        """TC-08: Xem danh sách đánh giá với product_id <= 0 -> 400."""
        with self._patch_db():
            for invalid_id in (0, -5):
                with self.assertRaises(HTTPException) as ctx:
                    review_router_module.get_product_reviews(
                        product_id=invalid_id, rating=None, page=1, page_size=20
                    )
                self.assertEqual(ctx.exception.status_code, 400)

    def test_tc09_post_review_invalid_product_id_validation_error(self):
        """TC-09: Gửi đánh giá với product_id <= 0 -> lỗi validate Pydantic (HTTP 422)."""
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
    def test_tc10_duplicate_review_same_user_id_same_product_409(self):
        """TC-10: Cùng user_id gửi đánh giá lần 2 cho cùng sản phẩm -> 409 Conflict."""
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

    def test_tc11_duplicate_review_same_guest_username_409(self):
        """TC-11: Cùng user_name (không phân biệt hoa/thường) đánh giá trùng -> 409."""
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

    def test_tc12_same_user_can_review_different_products(self):
        """TC-12: Cùng user_id được phép đánh giá nhiều sản phẩm khác nhau."""
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
    def test_tc13_rating_below_min_zero(self):
        """TC-13: Điểm sao = 0 (nhỏ hơn 1) -> ValidationError (HTTP 422)."""
        with self.assertRaises(ValidationError):
            review_router_module.ReviewCreate(
                product_id=1, user_id=10, rating=0, comment="0 sao"
            )

    def test_tc14_rating_negative(self):
        """TC-14: Điểm sao âm (-3) -> ValidationError (HTTP 422)."""
        with self.assertRaises(ValidationError):
            review_router_module.ReviewCreate(
                product_id=1, user_id=10, rating=-3, comment="Sao âm"
            )

    def test_tc15_rating_above_max_6_and_99(self):
        """TC-15: Điểm sao > 5 (6, 99) -> ValidationError (HTTP 422)."""
        for bad_star in (6, 99):
            with self.assertRaises(ValidationError):
                review_router_module.ReviewCreate(
                    product_id=1, user_id=10, rating=bad_star, comment="Ngoài khoảng"
                )

    def test_tc16_empty_or_whitespace_comment_rejected(self):
        """TC-16: Nhận xét rỗng bị từ chối (422) và nhận xét toàn khoảng trắng bị từ chối (400)."""
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
