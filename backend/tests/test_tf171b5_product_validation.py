import unittest
import base64
import sys

try:
    import jwt
except ImportError:
    from jose import jwt
    sys.modules["jwt"] = jwt

from fastapi import HTTPException
from backend.schemas import ProductCreate
from backend.src.modules.admin.router import _validate_admin_product


class TestAdminProductValidationTF171B5(unittest.TestCase):
    """Bộ kiểm thử xác thực dữ liệu sản phẩm TF171B5:
    - Giá lớn hơn 0
    - Tồn kho không âm (>= 0)
    - Tên không trùng
    - Giới hạn loại và dung lượng ảnh (tối đa 2MB, định dạng JPG, JPEG, PNG, WEBP, GIF)
    """

    def test_price_must_be_greater_than_zero(self):
        # Giá âm
        payload_negative = ProductCreate(
            title="Đồng hồ nam test giá âm",
            category="watch",
            price=-50000,
            stock=10,
            image="https://example.com/test.jpg"
        )
        with self.assertRaises(HTTPException) as ctx:
            _validate_admin_product(payload_negative)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Giá sản phẩm phải lớn hơn 0", ctx.exception.detail)

        # Giá bằng 0
        payload_zero = ProductCreate(
            title="Đồng hồ nam test giá 0",
            category="watch",
            price=0,
            stock=10,
            image="https://example.com/test.jpg"
        )
        with self.assertRaises(HTTPException) as ctx:
            _validate_admin_product(payload_zero)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Giá sản phẩm phải lớn hơn 0", ctx.exception.detail)

    def test_stock_cannot_be_negative(self):
        # Tồn kho âm
        payload = ProductCreate(
            title="Áo polo nam test tồn kho âm",
            category="fashion",
            price=250000,
            stock=-5,
            image="https://example.com/test.png"
        )
        with self.assertRaises(HTTPException) as ctx:
            _validate_admin_product(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Tồn kho không được âm", ctx.exception.detail)

    def test_title_cannot_be_empty(self):
        payload = ProductCreate(
            title="   ",
            category="tech",
            price=150000,
            stock=10,
            image="https://example.com/test.jpg"
        )
        with self.assertRaises(HTTPException) as ctx:
            _validate_admin_product(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Tên sản phẩm không được để trống", ctx.exception.detail)

    def test_image_invalid_type_url(self):
        # Đường dẫn URL sai định dạng (không phải ảnh jpg/png/webp/gif)
        payload = ProductCreate(
            title="Sản phẩm thử URL sai đuôi",
            category="tech",
            price=100000,
            stock=10,
            image="https://example.com/file.pdf"
        )
        with self.assertRaises(HTTPException) as ctx:
            _validate_admin_product(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("định dạng hợp lệ", ctx.exception.detail)

    def test_image_invalid_type_base64(self):
        # Dữ liệu Base64 không đúng loại ảnh (ví dụ text/plain hoặc application/pdf)
        fake_b64 = "data:application/pdf;base64," + base64.b64encode(b"hello world").decode("utf-8")
        payload = ProductCreate(
            title="Sản phẩm thử MIME sai",
            category="tech",
            price=100000,
            stock=10,
            image=fake_b64
        )
        with self.assertRaises(HTTPException) as ctx:
            _validate_admin_product(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Loại ảnh không hợp lệ", ctx.exception.detail)

    def test_image_oversized_base64(self):
        # Dung lượng vượt quá 2MB (tạo payload > 2MB)
        large_bytes = b"x" * (2 * 1024 * 1024 + 1024)
        large_b64 = "data:image/png;base64," + base64.b64encode(large_bytes).decode("utf-8")
        payload = ProductCreate(
            title="Sản phẩm thử ảnh quá 2MB",
            category="tech",
            price=100000,
            stock=10,
            image=large_b64
        )
        with self.assertRaises(HTTPException) as ctx:
            _validate_admin_product(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Dung lượng ảnh vượt quá", ctx.exception.detail)

    def test_duplicate_title_rejected(self):
        # Lấy một tên sản phẩm đã có trong DB
        from backend.src.config.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM products LIMIT 1;")
        row = cursor.fetchone()
        conn.close()

        if row:
            existing_title = row["title"]
            existing_id = row["id"]
            # Tạo mới cùng tên
            payload = ProductCreate(
                title=existing_title,
                category="tech",
                price=300000,
                stock=20,
                image="https://example.com/item.jpg"
            )
            with self.assertRaises(HTTPException) as ctx:
                _validate_admin_product(payload)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("đã tồn tại trên sàn", ctx.exception.detail)

            # Cập nhật chính sản phẩm đó (exclude_id = existing_id) -> được phép
            try:
                _validate_admin_product(payload, exclude_id=existing_id)
            except HTTPException as e:
                self.fail(f"Cập nhật chính sản phẩm cùng tên bị từ chối: {e.detail}")

    def test_valid_product_passes_validation(self):
        # Ảnh nhỏ hợp lệ
        small_bytes = b"image content"
        valid_b64 = "data:image/jpeg;base64," + base64.b64encode(small_bytes).decode("utf-8")
        import uuid
        unique_name = f"Sản phẩm chuẩn xịn {uuid.uuid4().hex[:8]}"
        payload = ProductCreate(
            title=unique_name,
            category="tech",
            price=500000,
            stock=50,
            image=valid_b64
        )
        # Không được ném ngoại lệ
        try:
            _validate_admin_product(payload)
        except HTTPException as e:
            self.fail(f"Sản phẩm hợp lệ bị báo lỗi: {e.detail}")


if __name__ == "__main__":
    unittest.main()
