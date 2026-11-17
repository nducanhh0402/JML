"""
TEST SUITE CHO TASK TF17119:
Viết API thêm, sửa, xóa, xem sản phẩm, cập nhật giá, tồn kho, ảnh; chỉ Admin được gọi.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

ADMIN_HEADERS = {"X-User-Role": "admin"}
CUSTOMER_HEADERS = {"X-User-Role": "customer"}
SELLER_HEADERS = {"X-User-Role": "seller"}


class TestTF17119AdminProductAPI(unittest.TestCase):
    created_product_id = None

    def test_01_rb_access_control_only_admin(self):
        """Kiểm tra quyền hạn RBAC: CHỈ ADMIN ĐƯỢC GỌI API."""
        # 1. Gọi không có header xác thực -> 401 Unauthorized
        res_no_auth = client.get("/api/admin/products")
        self.assertIn(res_no_auth.status_code, [401, 403])

        # 2. Gọi với vai trò Customer -> 403 Forbidden
        res_cust = client.get("/api/admin/products", headers=CUSTOMER_HEADERS)
        self.assertEqual(res_cust.status_code, 403)
        self.assertIn("Quyền truy cập bị từ chối", res_cust.json().get("detail", ""))

        # 3. Gọi với vai trò Seller -> 403 Forbidden
        res_seller = client.get("/api/admin/products", headers=SELLER_HEADERS)
        self.assertEqual(res_seller.status_code, 403)

        # 4. Gọi với vai trò Admin qua Header -> 200 OK
        res_admin = client.get("/api/admin/products", headers=ADMIN_HEADERS)
        self.assertEqual(res_admin.status_code, 200)

        # 5. Gọi với vai trò Admin qua Bearer token -> 200 OK
        res_bearer = client.get("/api/admin/products", headers={"Authorization": "Bearer admin_super_token"})
        self.assertEqual(res_bearer.status_code, 200)

        # 6. Gọi với vai trò Admin qua Query param -> 200 OK
        res_query = client.get("/api/admin/products?role=admin")
        self.assertEqual(res_query.status_code, 200)

    def test_02_admin_create_product(self):
        """Admin thêm mới sản phẩm lên sàn."""
        # Thử thêm khi không có quyền Admin -> 403
        deny_res = client.post("/api/admin/products", headers=CUSTOMER_HEADERS, json={
            "title": "Sản phẩm test trái phép",
            "price": 1000000
        })
        self.assertEqual(deny_res.status_code, 403)

        # Admin thêm hợp lệ
        payload = {
            "title": "Tai nghe Gaming HyperX Cloud Alpha Wireless Pro (TF17119 Test)",
            "price": 4500000,
            "original_price": 5200000,
            "stock": 50,
            "total_stock": 100,
            "category": "audio",
            "category_id": 1,
            "brand": "HyperX",
            "images": [
                "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80"
            ],
            "angles": ["Mặt trước", "Góc nghiêng"],
            "exclusive": "Hàng Chính Hãng",
            "shop_name": "HyperX Official Store",
            "status": "approved"
        }
        res = client.post("/api/admin/products", headers=ADMIN_HEADERS, json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("id", data)
        self.assertIn("product", data)
        TestTF17119AdminProductAPI.created_product_id = data["id"]
        self.assertEqual(data["product"]["title"], payload["title"])
        self.assertEqual(data["product"]["price"], 4500000)

    def test_03_admin_get_products_list_and_filters(self):
        """Admin xem danh sách sản phẩm kèm lọc và tìm kiếm."""
        res = client.get("/api/admin/products?q=TF17119&limit=10", headers=ADMIN_HEADERS)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total", data)
        self.assertIn("products", data)
        self.assertTrue(data["total"] >= 1)
        titles = [p["title"] for p in data["products"]]
        self.assertTrue(any("TF17119" in t for t in titles))

    def test_04_admin_get_product_detail(self):
        """Admin xem thông tin chi tiết của một sản phẩm."""
        prod_id = TestTF17119AdminProductAPI.created_product_id
        self.assertIsNotNone(prod_id)

        res = client.get(f"/api/admin/products/{prod_id}", headers=ADMIN_HEADERS)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("product", data)
        p = data["product"]
        self.assertEqual(p["id"], prod_id)
        self.assertEqual(p["price"], 4500000)
        self.assertIn("detailed_images", p)

    def test_05_admin_update_product(self):
        """Admin chỉnh sửa thông tin sản phẩm."""
        prod_id = TestTF17119AdminProductAPI.created_product_id
        update_payload = {
            "title": "Tai nghe HyperX Cloud Alpha ĐÃ CẬP NHẬT (TF17119)",
            "exclusive": "Siêu Phẩm 2026",
            "status": "approved"
        }
        res = client.put(f"/api/admin/products/{prod_id}", headers=ADMIN_HEADERS, json=update_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["product"]["title"], update_payload["title"])
        self.assertEqual(data["product"]["exclusive"], update_payload["exclusive"])

    def test_06_admin_update_product_price(self):
        """Admin cập nhật giá bán và tự động tính lại tỉ lệ giảm giá."""
        prod_id = TestTF17119AdminProductAPI.created_product_id
        price_payload = {
            "price": 3990000,
            "original_price": 5000000
        }
        # Gọi qua PATCH
        res_patch = client.patch(f"/api/admin/products/{prod_id}/price", headers=ADMIN_HEADERS, json=price_payload)
        self.assertEqual(res_patch.status_code, 200)
        data = res_patch.json()
        self.assertEqual(data["new_price"], 3990000)
        self.assertEqual(data["original_price"], 5000000)
        self.assertIn("%", data["discount"])

        # Gọi qua PUT
        res_put = client.put(f"/api/admin/products/{prod_id}/price", headers=ADMIN_HEADERS, json={"price": 3800000})
        self.assertEqual(res_put.status_code, 200)

    def test_07_admin_update_product_stock(self):
        """Admin cập nhật số lượng hàng tồn kho."""
        prod_id = TestTF17119AdminProductAPI.created_product_id
        stock_payload = {
            "stock": 85,
            "total_stock": 150
        }
        res = client.patch(f"/api/admin/products/{prod_id}/stock", headers=ADMIN_HEADERS, json=stock_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["stock"], 85)
        self.assertEqual(data["total_stock"], 150)

    def test_08_admin_manage_product_images(self):
        """Admin cập nhật, thêm mới và xóa ảnh sản phẩm."""
        prod_id = TestTF17119AdminProductAPI.created_product_id

        # 1. Cập nhật toàn bộ danh sách ảnh
        res_put = client.put(f"/api/admin/products/{prod_id}/images", headers=ADMIN_HEADERS, json={
            "images": [
                "https://example.com/img1.jpg",
                "https://example.com/img2.jpg"
            ],
            "angles": ["Mặt trước", "Cận cảnh"]
        })
        self.assertEqual(res_put.status_code, 200)
        self.assertEqual(len(res_put.json()["images"]), 2)

        # 2. Thêm 1 ảnh đơn lẻ
        res_post = client.post(f"/api/admin/products/{prod_id}/images", headers=ADMIN_HEADERS, json={
            "image_url": "https://example.com/img3_extra.jpg",
            "angle_name": "Góc 45 độ"
        })
        self.assertEqual(res_post.status_code, 201)
        img_id = res_post.json().get("image_id")
        self.assertIsNotNone(img_id)

        # 3. Xóa ảnh đơn lẻ vừa thêm
        res_del = client.delete(f"/api/admin/products/{prod_id}/images/{img_id}", headers=ADMIN_HEADERS)
        self.assertEqual(res_del.status_code, 200)

    def test_09_admin_delete_product(self):
        """Admin xóa sản phẩm khỏi sàn và kiểm tra không còn tồn tại."""
        prod_id = TestTF17119AdminProductAPI.created_product_id

        # Customer thử xóa -> 403 Forbidden
        deny_del = client.delete(f"/api/admin/products/{prod_id}", headers=CUSTOMER_HEADERS)
        self.assertEqual(deny_del.status_code, 403)

        # Admin xóa thành công -> 200 OK
        res_del = client.delete(f"/api/admin/products/{prod_id}", headers=ADMIN_HEADERS)
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.json().get("deleted_id"), prod_id)

        # Kiểm tra lại chi tiết -> 404 Not Found
        res_check = client.get(f"/api/admin/products/{prod_id}", headers=ADMIN_HEADERS)
        self.assertEqual(res_check.status_code, 404)


if __name__ == "__main__":
    unittest.main()
