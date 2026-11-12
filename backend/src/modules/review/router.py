from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

class ReviewCreate(BaseModel):
    product_id: int
    user_name: str
    rating: int = 5
    comment: str

@router.post("")
def add_product_review(payload: ReviewCreate):
    """Đánh giá và chấm sao cho sản phẩm sau khi đã mua hàng."""
    now_str = datetime.now().strftime("%d/%m/%Y")
    return {
        "message": "Cảm ơn bạn đã gửi đánh giá cho sản phẩm!",
        "review": {
            "product_id": payload.product_id,
            "user_name": payload.user_name,
            "rating": payload.rating,
            "comment": payload.comment,
            "created_at": now_str
        }
    }

@router.get("/{product_id}")
def get_product_reviews(product_id: int):
    """Lấy danh sách các nhận xét, đánh giá của sản phẩm."""
    return {
        "product_id": product_id,
        "rating": 5.0,
        "total_reviews": 12,
        "reviews": [
            {
                "id": 1,
                "user_name": "Trần Minh Quân",
                "rating": 5,
                "comment": "Sản phẩm chính hãng, đóng gói rất kỹ, shipper giao nhanh!",
                "date": "08/11/2026"
            },
            {
                "id": 2,
                "user_name": "Lê Hoàng Long",
                "rating": 5,
                "comment": "Rất đáng tiền, 10/10 điểm!",
                "date": "07/11/2026"
            }
        ]
    }
