from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/vouchers", tags=["Vouchers"])

AVAILABLE_VOUCHERS = {
    "FREESHIP": {
        "code": "FREESHIP",
        "type": "shipping",
        "desc": "Miễn phí 100% tiền vận chuyển",
        "min_order": 0,
        "badge": "Freeship Toàn Quốc"
    },
    "JML50K": {
        "code": "JML50K",
        "type": "fixed",
        "amount": 50000,
        "desc": "Giảm ngay 50.000 ₫ cho đơn từ 100.000 ₫",
        "min_order": 100000,
        "badge": "Giảm 50K"
    },
    "GIAM10": {
        "code": "GIAM10",
        "type": "percent",
        "percent": 10,
        "max_amount": 100000,
        "desc": "Giảm 10% (tối đa 100.000 ₫)",
        "min_order": 0,
        "badge": "Giảm 10%"
    },
    "VIP100K": {
        "code": "VIP100K",
        "type": "fixed",
        "amount": 100000,
        "desc": "Giảm ngay 100.000 ₫ cho đơn từ 1.000.000 ₫",
        "min_order": 1000000,
        "badge": "Vip 100K"
    }
}

class VoucherApplyRequest(BaseModel):
    code: str
    order_subtotal: int

@router.get("")
def list_vouchers():
    """Lấy danh sách các voucher khuyến mãi hiện có trên sàn."""
    return {"vouchers": list(AVAILABLE_VOUCHERS.values())}

@router.post("/apply")
def apply_voucher(payload: VoucherApplyRequest):
    """Kiểm tra và tính toán số tiền giảm giá của voucher."""
    code = payload.code.strip().upper()
    v = AVAILABLE_VOUCHERS.get(code)
    if not v:
        raise HTTPException(status_code=404, detail="Mã giảm giá không hợp lệ hoặc đã hết lượt!")

    if payload.order_subtotal < v["min_order"]:
        raise HTTPException(
            status_code=400,
            detail=f"Mã {code} yêu cầu đơn hàng tối thiểu từ {v['min_order']:,} ₫!"
        )

    discount = 0
    if v["type"] == "fixed":
        discount = min(v["amount"], payload.order_subtotal)
    elif v["type"] == "percent":
        discount = min(round(payload.order_subtotal * (v["percent"] / 100)), v.get("max_amount", 999999999))
    elif v["type"] == "shipping":
        discount = 15000  # Miễn phí ship tiêu chuẩn

    return {
        "message": f"Áp dụng mã {code} thành công!",
        "voucher": v,
        "discount_amount": discount
    }
