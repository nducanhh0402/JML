"""
Module API Đánh Giá Sản Phẩm (Reviews) - JML Store Marketplace
=============================================================
- POST /api/reviews: Gửi đánh giá (1–5 sao, nhận xét), giới hạn mỗi người 1 đánh giá / 1 sản phẩm.
- GET /api/reviews/{product_id}: Xem danh sách đánh giá (có phân trang & lọc số sao), điểm trung bình và thống kê theo sao.
"""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import pymysql
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


class ReviewCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="ID sản phẩm được đánh giá")
    rating: int = Field(..., ge=1, le=5, description="Số sao đánh giá từ 1 đến 5")
    comment: str = Field(..., min_length=1, max_length=2000, description="Nội dung nhận xét")
    user_id: Optional[int] = Field(default=None, gt=0, description="ID người dùng đánh giá")
    user_name: Optional[str] = Field(default=None, max_length=255, description="Tên người đánh giá")


def _ensure_reviews_table(cursor) -> None:
    """Đảm bảo bảng reviews tồn tại trước khi truy vấn."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        user_id INT NULL,
        user_name VARCHAR(255) NOT NULL,
        rating TINYINT NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uniq_review_user_product (user_id, product_id),
        INDEX idx_review_product (product_id),
        INDEX idx_review_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)


def _resolve_reviewer(request: Optional[Request], payload: ReviewCreate, cursor) -> Tuple[Optional[int], str]:
    """Xác định user_id và tên hiển thị của người đánh giá từ JWT hoặc payload."""
    token_user: Optional[Dict[str, Any]] = None

    if request is not None:
        token_user = getattr(request.state, "user", None)
        if not token_user:
            auth_header = request.headers.get("Authorization", "")
            parts = auth_header.strip().split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                try:
                    from backend.src.middlewares.auth_middleware import decode_access_token
                    token_user = decode_access_token(parts[1])
                except ImportError:
                    token_user = None

    user_id: Optional[int] = None
    user_name: str = (payload.user_name or "").strip()

    if token_user:
        raw_uid = token_user.get("user_id") or token_user.get("id") or token_user.get("sub")
        if raw_uid is not None and str(raw_uid).isdigit():
            user_id = int(raw_uid)
        if not user_name:
            user_name = str(token_user.get("full_name") or token_user.get("username") or "").strip()

    if user_id is None and payload.user_id is not None:
        user_id = payload.user_id

    if user_id is not None and not user_name:
        cursor.execute("SELECT full_name, username FROM users WHERE id = ?;", (user_id,))
        u_row = cursor.fetchone()
        if u_row:
            user_name = (u_row.get("full_name") or u_row.get("username") or "").strip()

    if not user_name:
        if user_id is None:
            raise HTTPException(
                status_code=400,
                detail="Vui lòng cung cấp user_id hoặc tên người đánh giá (user_name).",
            )
        user_name = f"Khách hàng #{user_id}"

    return user_id, user_name


def _serialize_review(row: Dict[str, Any]) -> Dict[str, Any]:
    """Chuẩn hóa một bản ghi review từ DB sang JSON response."""
    created_raw = row.get("created_at")
    if isinstance(created_raw, datetime):
        created_iso = created_raw.isoformat()
        date_str = created_raw.strftime("%d/%m/%Y")
    else:
        created_iso = str(created_raw or "")
        date_str = created_iso[:10] if created_iso else datetime.now().strftime("%d/%m/%Y")

    return {
        "id": row["id"],
        "product_id": row["product_id"],
        "user_id": row.get("user_id"),
        "user_name": row.get("user_name") or "Khách hàng",
        "rating": int(row["rating"]),
        "comment": row["comment"],
        "created_at": created_iso,
        "date": date_str,
    }


def _compute_product_rating_stats(cursor, product_id: int) -> Dict[str, Any]:
    """Tính tổng số đánh giá, điểm trung bình (1 chữ số thập phân) và phân bố 1-5 sao."""
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_reviews,
            COALESCE(ROUND(AVG(rating), 1), 0) AS average_rating,
            SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) AS star_5,
            SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) AS star_4,
            SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) AS star_3,
            SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) AS star_2,
            SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) AS star_1
        FROM reviews
        WHERE product_id = ?;
        """,
        (product_id,),
    )
    stats = cursor.fetchone() or {}
    total = int(stats.get("total_reviews") or 0)
    avg_rating = float(stats.get("average_rating") or 0.0)
    breakdown = {
        "5": int(stats.get("star_5") or 0),
        "4": int(stats.get("star_4") or 0),
        "3": int(stats.get("star_3") or 0),
        "2": int(stats.get("star_2") or 0),
        "1": int(stats.get("star_1") or 0),
    }
    return {
        "total_reviews": total,
        "average_rating": avg_rating,
        "rating_breakdown": breakdown,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def add_product_review(payload: ReviewCreate, request: Request = None):
    """
    Gửi đánh giá (1–5 sao, nhận xét) cho sản phẩm.
    Ràng buộc: mỗi người dùng chỉ được gửi tối đa 1 đánh giá cho mỗi sản phẩm.
    """
    cleaned_comment = " ".join(payload.comment.strip().split())
    if not cleaned_comment:
        raise HTTPException(
            status_code=400,
            detail="Nội dung nhận xét không được để trống.",
        )

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _ensure_reviews_table(cursor)

        cursor.execute("SELECT id, title FROM products WHERE id = ?;", (payload.product_id,))
        product_row = cursor.fetchone()
        if not product_row:
            raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")

        user_id, user_name = _resolve_reviewer(request, payload, cursor)

        # Kiểm tra người dùng đã đánh giá sản phẩm này chưa
        if user_id is not None:
            cursor.execute(
                "SELECT id FROM reviews WHERE product_id = ? AND user_id = ? LIMIT 1;",
                (payload.product_id, user_id),
            )
        else:
            cursor.execute(
                "SELECT id FROM reviews WHERE product_id = ? AND user_id IS NULL AND LOWER(TRIM(user_name)) = LOWER(TRIM(?)) LIMIT 1;",
                (payload.product_id, user_name),
            )

        if cursor.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Bạn đã đánh giá sản phẩm này rồi! Mỗi người chỉ được gửi 1 đánh giá cho mỗi sản phẩm.",
            )

        try:
            cursor.execute(
                "INSERT INTO reviews (product_id, user_id, user_name, rating, comment) VALUES (?, ?, ?, ?, ?);",
                (payload.product_id, user_id, user_name, payload.rating, cleaned_comment),
            )
        except pymysql.err.IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="Bạn đã đánh giá sản phẩm này rồi! Mỗi người chỉ được gửi 1 đánh giá cho mỗi sản phẩm.",
            )

        review_id = getattr(cursor, "lastrowid", None)
        if review_id:
            cursor.execute("SELECT * FROM reviews WHERE id = ?;", (review_id,))
            created_row = cursor.fetchone()
        else:
            cursor.execute(
                "SELECT * FROM reviews WHERE product_id = ? ORDER BY id DESC LIMIT 1;",
                (payload.product_id,),
            )
            created_row = cursor.fetchone()

        stats = _compute_product_rating_stats(cursor, payload.product_id)

        # Đồng bộ điểm trung bình mới vào bảng products
        cursor.execute(
            "UPDATE products SET rating = ? WHERE id = ?;",
            (stats["average_rating"], payload.product_id),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "message": "Cảm ơn bạn đã gửi đánh giá cho sản phẩm!",
        "review": _serialize_review(created_row),
        "average_rating": stats["average_rating"],
        "total_reviews": stats["total_reviews"],
        "rating_breakdown": stats["rating_breakdown"],
    }


@router.get("/{product_id}")
def get_product_reviews(
    product_id: int,
    rating: Optional[int] = Query(default=None, ge=1, le=5, description="Lọc đánh giá theo số sao (1-5)"),
    page: int = Query(default=1, ge=1, description="Trang hiện tại"),
    page_size: int = Query(default=20, ge=1, le=100, description="Số đánh giá mỗi trang"),
):
    """Lấy danh sách nhận xét, điểm trung bình và phân bố số sao của sản phẩm."""
    if product_id <= 0:
        raise HTTPException(status_code=400, detail="Mã sản phẩm không hợp lệ.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _ensure_reviews_table(cursor)

        cursor.execute("SELECT id FROM products WHERE id = ?;", (product_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")

        stats = _compute_product_rating_stats(cursor, product_id)

        where_sql = "WHERE product_id = ?"
        params: List[Any] = [product_id]
        if rating is not None:
            where_sql += " AND rating = ?"
            params.append(rating)

        cursor.execute(f"SELECT COUNT(*) AS filtered_total FROM reviews {where_sql};", tuple(params))
        filtered_total = int((cursor.fetchone() or {}).get("filtered_total") or 0)

        offset = (page - 1) * page_size
        cursor.execute(
            f"SELECT * FROM reviews {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?;",
            tuple(params + [page_size, offset]),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    total_pages = math.ceil(filtered_total / page_size) if filtered_total > 0 else 0

    return {
        "product_id": product_id,
        "average_rating": stats["average_rating"],
        "rating": stats["average_rating"],
        "total_reviews": stats["total_reviews"],
        "rating_breakdown": stats["rating_breakdown"],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": filtered_total,
            "total_pages": total_pages,
        },
        "reviews": [_serialize_review(r) for r in rows],
    }
