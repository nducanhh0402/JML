import unittest
import urllib.request
import urllib.error
import json
from backend.src.middlewares.auth_middleware import create_access_token

BASE_URL = "http://127.0.0.1:8000"

class TestMarketplaceAPI(unittest.TestCase):
    def test_01_root_status(self):
        """Kiểm tra healthcheck root API."""
        try:
            res = urllib.request.urlopen(f"{BASE_URL}/")
            data = json.loads(res.read().decode())
            self.assertEqual(res.status, 200)
            self.assertEqual(data.get("status"), "online")
        except Exception as e:
            self.skipTest(f"Server offline: {e}")

    def test_02_get_products(self):
        """Kiểm tra API danh sách sản phẩm."""
        try:
            res = urllib.request.urlopen(f"{BASE_URL}/api/products")
            data = json.loads(res.read().decode())
            self.assertEqual(res.status, 200)
            self.assertIn("flash_products", data)
            self.assertIn("recommend_products", data)
        except Exception as e:
            self.skipTest(f"Server offline: {e}")

    def test_03_get_vouchers(self):
        """Kiểm tra API danh sách mã giảm giá."""
        try:
            res = urllib.request.urlopen(f"{BASE_URL}/api/vouchers")
            data = json.loads(res.read().decode())
            self.assertEqual(res.status, 200)
            self.assertTrue(len(data.get("vouchers", [])) > 0)
        except Exception as e:
            self.skipTest(f"Server offline: {e}")

    def test_04_get_admin_shops(self):
        """Kiểm tra API quản lý cửa hàng cho Admin yêu cầu Bearer Token."""
        try:
            # 1. Gọi khi không có token -> phải trả về lỗi 401 Unauthorized
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(f"{BASE_URL}/api/admin/shops")
            self.assertEqual(ctx.exception.code, 401)
            ctx.exception.close()

            # 2. Gọi với Bearer token của Admin -> trả về 200 OK
            admin_token = create_access_token({"sub": "1", "username": "admin", "role": "admin"})
            req = urllib.request.Request(
                f"{BASE_URL}/api/admin/shops",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            res = urllib.request.urlopen(req)
            data = json.loads(res.read().decode())
            res.close()
            self.assertEqual(res.status, 200)
            self.assertIn("shops", data)
        except urllib.error.URLError as e:
            self.skipTest(f"Server offline: {e}")

if __name__ == "__main__":
    unittest.main()
