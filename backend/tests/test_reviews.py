"""
Unit test cho API Đánh giá sản phẩm (Reviews)
Kiểm tra: gửi đánh giá 1-5 sao, nhận xét, xem danh sách, tính điểm trung bình,
chặn mỗi người >1 đánh giá cho cùng 1 sản phẩm (409), và 404 khi sản phẩm không tồn tại.
"""

from datetime import datetime
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from pydantic import ValidationError

from backend.src.modules.review import router as review_router_module


class _FakeReviewCursor:
    def __init__(self, state):
        self.state = state
        self._one = None
        self._all = []
        self.lastrowid = None

    def execute(self, sql, params=None):
        sql_l = " ".join(sql.strip().lower().split())
        self._one = None
        self._all = []
        params = params or ()

        if sql_l.startswith("create table if not exists reviews"):
            return

        if "select id, title from products where id = ?" in sql_l or "select id from products where id = ?" in sql_l:
            pid = params[0]
            self._one = self.state["products"].get(pid)
            return

        if "select full_name, username from users where id = ?" in sql_l:
            uid = params[0]
            self._one = self.state["users"].get(uid)
            return

        if "select id from reviews where product_id = ? and user_id = ?" in sql_l:
            pid, uid = params[0], params[1]
            for rev in self.state["reviews"]:
                if rev["product_id"] == pid and rev["user_id"] == uid:
                    self._one = {"id": rev["id"]}
                    return
            return

        if "select id from reviews where product_id = ? and user_id is null" in sql_l:
            pid, uname = params[0], str(params[1]).strip().lower()
            for rev in self.state["reviews"]:
                if rev["product_id"] == pid and rev["user_id"] is None and rev["user_name"].strip().lower() == uname:
                    self._one = {"id": rev["id"]}
                    return
            return

        if sql_l.startswith("insert into reviews"):
            pid, uid, uname, rating, comment = params
            new_id = self.state["next_id"]
            self.state["next_id"] += 1
            row = {
                "id": new_id,
                "product_id": pid,
                "user_id": uid,
                "user_name": uname,
                "rating": rating,
                "comment": comment,
                "created_at": datetime(2026, 11, 21, 9, 0, 0),
            }
            self.state["reviews"].append(row)
            self.lastrowid = new_id
            return

        if sql_l.startswith("select * from reviews where id = ?"):
            rid = params[0]
            for rev in self.state["reviews"]:
                if rev["id"] == rid:
                    self._one = rev
                    return
            return

        if "avg(rating)" in sql_l and "from reviews" in sql_l:
            pid = params[0]
            matching = [r for r in self.state["reviews"] if r["product_id"] == pid]
            total = len(matching)
            avg_val = round(sum(r["rating"] for r in matching) / total, 1) if total > 0 else 0.0
            self._one = {
                "total_reviews": total,
                "average_rating": avg_val,
                "star_5": sum(1 for r in matching if r["rating"] == 5),
                "star_4": sum(1 for r in matching if r["rating"] == 4),
                "star_3": sum(1 for r in matching if r["rating"] == 3),
                "star_2": sum(1 for r in matching if r["rating"] == 2),
                "star_1": sum(1 for r in matching if r["rating"] == 1),
            }
            return

        if sql_l.startswith("update products set rating = ? where id = ?"):
            rating_val, pid = params
            if pid in self.state["products"]:
                self.state["products"][pid]["rating"] = rating_val
            return

        if "select count(*) as filtered_total from reviews" in sql_l:
            pid = params[0]
            matching = [r for r in self.state["reviews"] if r["product_id"] == pid]
            if len(params) == 2:
                matching = [r for r in matching if r["rating"] == params[1]]
            self._one = {"filtered_total": len(matching)}
            return

        if sql_l.startswith("select * from reviews where product_id = ?"):
            pid = params[0]
            matching = [r for r in self.state["reviews"] if r["product_id"] == pid]
            if "and rating = ?" in sql_l:
                star = params[1]
                limit, offset = params[2], params[3]
                matching = [r for r in matching if r["rating"] == star]
            else:
                limit, offset = params[1], params[2]
            matching = sorted(matching, key=lambda r: r["id"], reverse=True)
            self._all = matching[offset : offset + limit]
            return

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._all


class _FakeConnection:
    def __init__(self, state):
        self.state = state
        self.closed = False

    def cursor(self):
        return _FakeReviewCursor(self.state)

    def commit(self):
        pass

    def close(self):
        self.closed = True


class TestReviewsAPI(unittest.TestCase):
    def setUp(self):
        self.state = {
            "products": {
                1: {"id": 1, "title": "Sony WH-1000XM5", "rating": 5.0},
                2: {"id": 2, "title": "iPad Pro M4", "rating": 5.0},
            },
            "users": {
                10: {"full_name": "Nguyễn Đức Anh", "username": "buyer"},
                11: {"full_name": "Vũ Dũng", "username": "dung36"},
            },
            "reviews": [],
            "next_id": 1,
        }

    def test_rating_validation_1_to_5(self):
        with self.assertRaises(ValidationError):
            review_router_module.ReviewCreate(product_id=1, user_id=10, rating=0, comment="Quá tệ")
        with self.assertRaises(ValidationError):
            review_router_module.ReviewCreate(product_id=1, user_id=10, rating=6, comment="Quá tốt")

    def test_add_reviews_calculate_average_and_enforce_one_per_user_per_product(self):
        with patch.object(
            review_router_module,
            "get_db_connection",
            side_effect=lambda: _FakeConnection(self.state),
        ):
            # Người dùng 10 đánh giá sản phẩm 1 -> 5 sao
            res1 = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1,
                    user_id=10,
                    rating=5,
                    comment="Âm thanh rất hay, giao hàng nhanh!",
                )
            )
            self.assertEqual(res1["review"]["rating"], 5)
            self.assertEqual(res1["review"]["user_name"], "Nguyễn Đức Anh")
            self.assertEqual(res1["average_rating"], 5.0)
            self.assertEqual(res1["total_reviews"], 1)

            # Người dùng 11 đánh giá sản phẩm 1 -> 4 sao => trung bình 4.5
            res2 = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1,
                    user_id=11,
                    rating=4,
                    comment="Đóng gói cẩn thận, đeo êm tai.",
                )
            )
            self.assertEqual(res2["average_rating"], 4.5)
            self.assertEqual(res2["total_reviews"], 2)
            self.assertEqual(self.state["products"][1]["rating"], 4.5)

            # Người dùng 10 gửi đánh giá lần 2 cho cùng sản phẩm 1 -> bị chặn 409
            with self.assertRaises(HTTPException) as dup_ctx:
                review_router_module.add_product_review(
                    review_router_module.ReviewCreate(
                        product_id=1,
                        user_id=10,
                        rating=1,
                        comment="Đánh giá lại lần 2",
                    )
                )
            self.assertEqual(dup_ctx.exception.status_code, 409)

            # Người dùng 10 vẫn được đánh giá sản phẩm khác (product_id = 2)
            res3 = review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=2,
                    user_id=10,
                    rating=5,
                    comment="Màn hình OLED quá đẹp!",
                )
            )
            self.assertEqual(res3["total_reviews"], 1)

            # Xem danh sách & điểm trung bình sản phẩm 1
            list_res = review_router_module.get_product_reviews(product_id=1, rating=None, page=1, page_size=20)
            self.assertEqual(list_res["average_rating"], 4.5)
            self.assertEqual(list_res["total_reviews"], 2)
            self.assertEqual(list_res["rating_breakdown"]["5"], 1)
            self.assertEqual(list_res["rating_breakdown"]["4"], 1)
            self.assertEqual(len(list_res["reviews"]), 2)
            self.assertEqual(list_res["reviews"][0]["user_id"], 11)

            # Lọc theo 5 sao
            filtered = review_router_module.get_product_reviews(product_id=1, rating=5, page=1, page_size=20)
            self.assertEqual(len(filtered["reviews"]), 1)
            self.assertEqual(filtered["reviews"][0]["rating"], 5)

    def test_guest_duplicate_name_blocked_and_missing_product_404(self):
        with patch.object(
            review_router_module,
            "get_db_connection",
            side_effect=lambda: _FakeConnection(self.state),
        ):
            review_router_module.add_product_review(
                review_router_module.ReviewCreate(
                    product_id=1,
                    user_name="Trần Minh Quân",
                    rating=5,
                    comment="Rất đáng tiền!",
                )
            )
            with self.assertRaises(HTTPException) as dup_guest:
                review_router_module.add_product_review(
                    review_router_module.ReviewCreate(
                        product_id=1,
                        user_name="trần minh quân",
                        rating=3,
                        comment="Gửi lại lần 2",
                    )
                )
            self.assertEqual(dup_guest.exception.status_code, 409)

            with self.assertRaises(HTTPException) as not_found:
                review_router_module.get_product_reviews(product_id=99999, rating=None, page=1, page_size=20)
            self.assertEqual(not_found.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
