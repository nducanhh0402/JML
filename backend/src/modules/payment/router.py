from fastapi import APIRouter

router = APIRouter(prefix="/api/payment", tags=["Payment"])

@router.get("/methods")
def get_payment_methods():
    """Lấy danh sách các phương thức thanh toán được hỗ trợ trên sàn."""
    return {
        "methods": [
            {
                "id": "cod",
                "name": "Nhận hàng trả tiền (COD)",
                "icon": "📦",
                "desc": "Thanh toán bằng tiền mặt khi shipper giao hàng tận nơi"
            },
            {
                "id": "escrow",
                "name": "Thanh toán bảo đảm qua Sàn JML (Escrow)",
                "icon": "🔒",
                "desc": "Sàn giữ hộ tiền 100% đến khi người mua kiểm tra và bấm 'Đã nhận được hàng'"
            }
        ]
    }
