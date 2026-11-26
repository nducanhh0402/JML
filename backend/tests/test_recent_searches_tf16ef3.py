"""TF16EF3: Kiểm thử API lưu và trả về từ khóa tìm kiếm gần đây của người dùng."""

import json
import socket
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
import uuid

from fastapi import FastAPI
import uvicorn

from backend.src.modules.product.router import router as product_router

app = FastAPI(title="JML Recent Searches Test App")
app.include_router(product_router)


@app.get("/health")
def _health():
    return {"status": "ok"}


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class TestRecentSearchesTF16EF3(unittest.TestCase):
    server = None
    thread = None
    base_url = ""

    @classmethod
    def setUpClass(cls):
        port = _find_free_port()
        cls.base_url = f"http://127.0.0.1:{port}"
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        cls.server = uvicorn.Server(config)
        cls.server.install_signal_handlers = lambda: None
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()

        for _ in range(50):
            try:
                with urllib.request.urlopen(f"{cls.base_url}/health", timeout=1) as resp:
                    if resp.status == 200:
                        return
            except Exception:
                time.sleep(0.1)
        raise RuntimeError("Không thể khởi động test server cho TF16EF3.")

    @classmethod
    def tearDownClass(cls):
        if cls.server is not None:
            cls.server.should_exit = True
        if cls.thread is not None:
            cls.thread.join(timeout=3)

    def setUp(self):
        self.sid_a = f"test_{uuid.uuid4().hex[:12]}"
        self.sid_b = f"test_{uuid.uuid4().hex[:12]}"

    def tearDown(self):
        self._request("DELETE", "/api/products/recent-searches", params={"session_id": self.sid_a})
        self._request("DELETE", "/api/products/recent-searches", params={"session_id": self.sid_b})
        self._request("DELETE", "/api/products/recent-searches", params={"user_id": 999101})

    def _request(self, method: str, path: str, params=None, body=None, headers=None):
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8")
            err.close()
            try:
                return err.code, json.loads(raw)
            except Exception:
                return err.code, {"raw": raw}

    def test_01_route_order_before_product_id(self):
        paths = [r.path for r in product_router.routes if hasattr(r, "methods")]
        self.assertLess(paths.index("/api/products/recent-searches"), paths.index("/api/products/{product_id}"))

    def test_02_save_dedup_bump_and_count(self):
        st1, d1 = self._request(
            "POST",
            "/api/products/recent-searches",
            body={"keyword": "Tai nghe Sony", "session_id": self.sid_a},
        )
        self.assertEqual(st1, 200)
        self.assertTrue(d1["saved"])
        self.assertEqual(d1["keywords"], ["Tai nghe Sony"])

        time.sleep(0.01)
        st2, _ = self._request(
            "POST",
            "/api/products/recent-searches",
            body={"keyword": "MacBook Pro", "session_id": self.sid_a},
        )
        self.assertEqual(st2, 200)

        time.sleep(0.01)
        # Tìm lại từ khóa cũ khác viết hoa & dư dấu trắng -> phải gộp (không trùng) và nhảy lên đầu
        st3, d3 = self._request(
            "POST",
            "/api/products/recent-searches",
            body={"keyword": "  tai   NGHE   sony ", "session_id": self.sid_a},
        )
        self.assertEqual(st3, 200)
        self.assertEqual(d3["total"], 2)
        self.assertEqual(d3["keywords"], ["tai NGHE sony", "MacBook Pro"])
        self.assertEqual(d3["items"][0]["search_count"], 2)

    def test_03_reject_empty_or_whitespace_keyword(self):
        for bad_kw in ("", "    ", "\t\n"):
            st, data = self._request(
                "POST",
                "/api/products/recent-searches",
                body={"keyword": bad_kw, "session_id": self.sid_a},
            )
            self.assertEqual(st, 400)
            self.assertIn("trống", data["detail"])

    def test_04_auto_save_from_search_endpoint_and_prefix_suggest(self):
        st_s1, res1 = self._request(
            "GET",
            "/api/products/search",
            params={"q": "Apple Watch", "session_id": self.sid_a},
        )
        self.assertEqual(st_s1, 200)
        self.assertFalse(res1["is_empty_keyword"])

        time.sleep(0.01)
        st_s2, _ = self._request(
            "GET",
            "/api/products/search",
            params={"q": "AirPods Max", "session_id": self.sid_a},
        )
        self.assertEqual(st_s2, 200)

        time.sleep(0.01)
        # Từ khóa rỗng không được lưu vào lịch sử
        self._request("GET", "/api/products/search", params={"q": "   ", "session_id": self.sid_a})

        st_get, d_get = self._request(
            "GET",
            "/api/products/recent-searches",
            params={"session_id": self.sid_a, "limit": 10},
        )
        self.assertEqual(st_get, 200)
        self.assertEqual(d_get["keywords"], ["AirPods Max", "Apple Watch"])

        # Lọc gợi ý theo prefix đang gõ
        st_pref, d_pref = self._request(
            "GET",
            "/api/products/recent-searches",
            params={"session_id": self.sid_a, "prefix": "air"},
        )
        self.assertEqual(st_pref, 200)
        self.assertEqual(d_pref["keywords"], ["AirPods Max"])

    def test_05_user_isolation_and_delete_single_or_clear_all(self):
        self._request("POST", "/api/products/recent-searches", body={"keyword": "Đồng hồ Tissot", "session_id": self.sid_a})
        self._request("POST", "/api/products/recent-searches", body={"keyword": "Giày Nike", "session_id": self.sid_a})
        self._request("POST", "/api/products/recent-searches", body={"keyword": "Nước hoa Dior", "session_id": self.sid_b})
        self._request("POST", "/api/products/recent-searches", body={"keyword": "iPad Pro", "user_id": 999101})

        _, da = self._request("GET", "/api/products/recent-searches", params={"session_id": self.sid_a})
        _, db = self._request("GET", "/api/products/recent-searches", params={"session_id": self.sid_b})
        _, du = self._request("GET", "/api/products/recent-searches", params={"user_id": 999101})
        self.assertEqual(set(da["keywords"]), {"Đồng hồ Tissot", "Giày Nike"})
        self.assertEqual(db["keywords"], ["Nước hoa Dior"])
        self.assertEqual(du["keywords"], ["iPad Pro"])

        # Không được phép xóa từ khóa thuộc session/user khác
        other_id = db["items"][0]["id"]
        st_forbidden, _ = self._request(
            "DELETE",
            f"/api/products/recent-searches/{other_id}",
            params={"session_id": self.sid_a},
        )
        self.assertEqual(st_forbidden, 404)

        # Xóa 1 từ khóa của chính mình
        own_id = da["items"][0]["id"]
        st_del, d_del = self._request(
            "DELETE",
            f"/api/products/recent-searches/{own_id}",
            params={"session_id": self.sid_a},
        )
        self.assertEqual(st_del, 200)
        self.assertTrue(d_del["deleted"])

        _, da_after = self._request("GET", "/api/products/recent-searches", params={"session_id": self.sid_a})
        self.assertEqual(da_after["total"], 1)

        # Xóa toàn bộ lịch sử của sid_a (không ảnh hưởng sid_b)
        st_clr, d_clr = self._request("DELETE", "/api/products/recent-searches", params={"session_id": self.sid_a})
        self.assertEqual(st_clr, 200)
        self.assertEqual(d_clr["deleted"], 1)

        _, db_still = self._request("GET", "/api/products/recent-searches", params={"session_id": self.sid_b})
        self.assertEqual(db_still["keywords"], ["Nước hoa Dior"])

    def test_06_max_20_history_cap_per_user(self):
        for i in range(1, 25):
            st, _ = self._request(
                "POST",
                "/api/products/recent-searches",
                body={"keyword": f"Từ khóa mẫu {i:02d}", "session_id": self.sid_a},
            )
            self.assertEqual(st, 200)
            time.sleep(0.002)

        _, res = self._request("GET", "/api/products/recent-searches", params={"session_id": self.sid_a, "limit": 20})
        self.assertEqual(res["total"], 20)
        self.assertEqual(res["keywords"][0], "Từ khóa mẫu 24")
        self.assertNotIn("Từ khóa mẫu 01", res["keywords"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
