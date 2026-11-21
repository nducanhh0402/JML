import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas import VNPayCreateUrlRequest
from backend.src.utils.vnpay import (
    build_payment_url,
    verify_vnpay_hash,
    get_vnpay_response_message,
    parse_order_key_from_txn_ref,
    VNPAY_TMN_CODE,
    VNPAY_HASH_SECRET
)
from backend.src.modules.payment.router import (
    create_payment_url,
    vnpay_return_callback,
    vnpay_ipn_webhook,
    get_order_payment_status,
    get_payment_methods
)


class FakeCursor:
    """Mock MySQL DictCursor cho phép kiểm tra truy vấn thanh toán VNPay."""
    def __init__(self, db_state):
        self.db = db_state
        self.last_query = ""
        self.last_args = None
        self.executed_queries = []
        self._fetched = None
        self.lastrowid = 1

    def execute(self, sql, args=None):
        self.last_query = sql
        self.last_args = args
        self.executed_queries.append((sql.strip(), args))
        sql_lower = sql.lower()

        # 1. SHOW TABLES
        if "show tables like" in sql_lower:
            table_name = "payments" if "payments" in sql_lower else "order_status_history"
            self._fetched = {f"Tables_in_jml ({table_name})": table_name}

        # 2. SELECT order
        elif "select" in sql_lower and "from orders" in sql_lower:
            order_key = args[0] if args else None
            matched = None
            for ord_item in self.db.get("orders", []):
                if ord_item.get("order_key") == order_key:
                    matched = dict(ord_item)
                    break
            self._fetched = matched

        # 3. SELECT payment
        elif "select" in sql_lower and "from payments" in sql_lower:
            order_key = args[0] if args else None
            matched = None
            for p in self.db.get("payments", []):
                if p.get("order_key") == order_key:
                    matched = dict(p)
                    break
            self._fetched = matched

        # 4. UPDATE payments
        elif "update payments" in sql_lower:
            p_status = args[0]
            txn_code = args[1]
            amount = args[2]
            order_key = args[3] if len(args) > 3 else None
            for p in self.db.get("payments", []):
                if p.get("order_key") == order_key:
                    p["payment_status"] = p_status
                    p["transaction_code"] = txn_code
                    p["amount"] = amount

        # 5. INSERT payments
        elif "insert into payments" in sql_lower:
            if args:
                self.db.setdefault("payments", []).append({
                    "order_key": args[0],
                    "user_id": args[1],
                    "payment_method": args[2],
                    "payment_status": args[3],
                    "amount": args[4],
                    "transaction_code": args[5]
                })

        # 6. UPDATE orders
        elif "update orders" in sql_lower:
            pass

        # 7. INSERT order_status_history
        elif "insert into order_status_history" in sql_lower:
            self.db.setdefault("history", []).append(args)

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return [self._fetched] if self._fetched else []

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FakeConnection:
    """Mock MySQL Connection."""
    def __init__(self, db_state):
        self.db = db_state
        self.committed = False
        self.rolled_back = False

    def cursor(self, *args, **kwargs):
        return FakeCursor(self.db)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


class TestVNPaySandboxIntegration(unittest.TestCase):
    def setUp(self):
        self.db_state = {
            "orders": [
                {
                    "order_key": "MP-9999",
                    "id_display": "#MP-9999",
                    "user_id": 1,
                    "buyer_name": "Trần Gia Huy",
                    "buyer_phone": "0987654321",
                    "numeric_total": 450000,
                    "total": "450.000 ₫",
                    "status": "preparing",
                    "time_info": "Thời gian đặt: 21/11/2026"
                }
            ],
            "payments": [
                {
                    "id": 1,
                    "order_key": "MP-9999",
                    "user_id": 1,
                    "payment_method": "vnpay",
                    "payment_status": "pending",
                    "amount": 450000,
                    "transaction_code": "MP-9999_120000"
                }
            ],
            "history": []
        }

    # =========================================================================
    # 1. TEST TIỆN ÍCH BẢO MẬT & HASH VNPAY (vnpay.py)
    # =========================================================================
    def test_01_build_payment_url_format(self):
        """Kiểm tra cấu trúc và tính đầy đủ của link thanh toán VNPay Sandbox."""
        order_key = "MP-1234"
        amount = 250000
        url, params = build_payment_url(
            order_key=order_key,
            amount=amount,
            order_desc="Thanh toan don hang test",
            ip_address="127.0.0.1"
        )

        self.assertTrue(url.startswith("https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"))
        self.assertIn("vnp_Version=2.1.0", url)
        self.assertIn("vnp_Command=pay", url)
        self.assertIn(f"vnp_TmnCode={VNPAY_TMN_CODE}", url)
        self.assertIn(f"vnp_Amount={amount * 100}", url)
        self.assertIn("vnp_SecureHash=", url)
        self.assertEqual(params["vnp_Amount"], str(amount * 100))

    def test_02_verify_vnpay_hash_valid(self):
        """Kiểm tra hàm verify_vnpay_hash xác thực thành công chữ ký hợp lệ."""
        order_key = "MP-1234"
        amount = 100000
        url, params = build_payment_url(order_key=order_key, amount=amount)

        # Trích xuất SecureHash từ URL
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(parsed.query)
        callback_params = {k: v[0] for k, v in q.items()}

        is_valid = verify_vnpay_hash(callback_params)
        self.assertTrue(is_valid)

    def test_03_verify_vnpay_hash_tampered_fails(self):
        """Kiểm tra phát hiện và từ chối khi dữ liệu thanh toán bị chỉnh sửa (chữ ký giả mạo)."""
        order_key = "MP-1234"
        amount = 100000
        url, _ = build_payment_url(order_key=order_key, amount=amount)

        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(parsed.query)
        callback_params = {k: v[0] for k, v in q.items()}

        # Sửa đổi số tiền (tampering)
        callback_params["vnp_Amount"] = "999999999"
        self.assertFalse(verify_vnpay_hash(callback_params))

        # Chữ ký sai lệch
        callback_params["vnp_SecureHash"] = "invalid_hash_signature"
        self.assertFalse(verify_vnpay_hash(callback_params))

    def test_04_parse_order_key_from_txn_ref(self):
        """Kiểm tra trích xuất order_key từ vnp_TxnRef có kèm timestamp."""
        self.assertEqual(parse_order_key_from_txn_ref("MP-9999_173000"), "MP-9999")
        self.assertEqual(parse_order_key_from_txn_ref("MP-5555"), "MP-5555")
        self.assertEqual(parse_order_key_from_txn_ref(""), "")

    def test_05_response_code_messages(self):
        """Kiểm tra giải mã thông điệp kết quả VNPay sang tiếng Việt."""
        self.assertIn("thành công", get_vnpay_response_message("00"))
        self.assertIn("hủy", get_vnpay_response_message("24"))
        self.assertIn("hết hạn", get_vnpay_response_message("11"))

    # =========================================================================
    # 2. TEST DANH SÁCH PHƯƠNG THỨC THANH TOÁN (GET /api/payment/methods)
    # =========================================================================
    def test_06_get_payment_methods_includes_vnpay(self):
        """Kiểm tra danh sách phương thức thanh toán có chứa VNPAY Sandbox."""
        methods_res = get_payment_methods()
        method_ids = [m["id"] for m in methods_res["methods"]]
        self.assertIn("cod", method_ids)
        self.assertIn("vnpay", method_ids)
        self.assertIn("escrow", method_ids)

    # =========================================================================
    # 3. TEST TẠO LINK THANH TOÁN (POST /api/payment/vnpay/create-url)
    # =========================================================================
    @patch("backend.src.modules.payment.router.get_db_connection")
    def test_07_create_payment_url_success(self, mock_db_conn):
        """Kiểm tra tạo URL thanh toán thành công cho đơn hàng hợp lệ."""
        mock_db_conn.return_value = FakeConnection(self.db_state)

        req_mock = MagicMock()
        req_mock.headers = {}
        req_mock.client.host = "192.168.1.1"

        payload = VNPayCreateUrlRequest(order_key="MP-9999")
        response = create_payment_url(payload, req_mock)

        self.assertEqual(response.status, "success")
        self.assertEqual(response.code, "00")
        self.assertEqual(response.order_key, "MP-9999")
        self.assertEqual(response.amount, 450000)
        self.assertTrue(response.payment_url.startswith("https://sandbox.vnpayment.vn/"))

    @patch("backend.src.modules.payment.router.get_db_connection")
    def test_08_create_payment_url_order_not_found(self, mock_db_conn):
        """Kiểm tra trả về lỗi 404 khi tạo link cho đơn hàng không tồn tại."""
        mock_db_conn.return_value = FakeConnection(self.db_state)

        req_mock = MagicMock()
        req_mock.headers = {}
        req_mock.client.host = "127.0.0.1"

        payload = VNPayCreateUrlRequest(order_key="MP-NONEXIST")
        with self.assertRaises(HTTPException) as ctx:
            create_payment_url(payload, req_mock)

        self.assertEqual(ctx.exception.status_code, 404)

    # =========================================================================
    # 4. TEST XỬ LÝ RETURN CALLBACK (GET /api/payment/vnpay-return)
    # =========================================================================
    @patch("backend.src.modules.payment.router.get_db_connection")
    def test_09_vnpay_return_successful_payment(self, mock_db_conn):
        """Kiểm tra callback return khi khách thanh toán thành công (Code 00)."""
        mock_db_conn.return_value = FakeConnection(self.db_state)

        # Tạo URL thanh toán để lấy chữ ký hợp lệ
        url, _ = build_payment_url("MP-9999", 450000)
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

        # Thêm các trường phản hồi thành công từ VNPay
        params["vnp_ResponseCode"] = "00"
        params["vnp_TransactionNo"] = "14285700"
        params["vnp_BankCode"] = "NCB"
        params["vnp_PayDate"] = "20261121173000"

        # Tính lại chữ ký hợp lệ với các trường kết quả
        from backend.src.utils.vnpay import VNPAY_HASH_SECRET
        import hmac, hashlib
        filtered = {k: v for k, v in params.items() if k.startswith("vnp_") and k not in ("vnp_SecureHash", "vnp_SecureHashType")}
        sorted_params = sorted(filtered.items())
        hash_data = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
        params["vnp_SecureHash"] = hmac.new(VNPAY_HASH_SECRET.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

        req_mock = MagicMock()
        req_mock.query_params = params
        req_mock.headers = {"accept": "application/json"}

        result = vnpay_return_callback(req_mock)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["code"], "00")
        self.assertEqual(result["order_key"], "MP-9999")
        self.assertEqual(result["transaction_no"], "14285700")

        # Kiểm tra trạng thái DB đã được cập nhật completed
        self.assertEqual(self.db_state["payments"][0]["payment_status"], "completed")

    @patch("backend.src.modules.payment.router.get_db_connection")
    def test_10_vnpay_return_failed_payment(self, mock_db_conn):
        """Kiểm tra callback return khi giao dịch bị khách hủy (Code 24)."""
        mock_db_conn.return_value = FakeConnection(self.db_state)

        url, _ = build_payment_url("MP-9999", 450000)
        import urllib.parse, hmac, hashlib
        from backend.src.utils.vnpay import VNPAY_HASH_SECRET
        parsed = urllib.parse.urlparse(url)
        params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

        params["vnp_ResponseCode"] = "24"  # Khách hàng hủy
        params["vnp_TransactionNo"] = "14285701"
        filtered = {k: v for k, v in params.items() if k.startswith("vnp_") and k not in ("vnp_SecureHash", "vnp_SecureHashType")}
        sorted_params = sorted(filtered.items())
        hash_data = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
        params["vnp_SecureHash"] = hmac.new(VNPAY_HASH_SECRET.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

        req_mock = MagicMock()
        req_mock.query_params = params
        req_mock.headers = {"accept": "application/json"}

        result = vnpay_return_callback(req_mock)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["code"], "24")
        self.assertEqual(self.db_state["payments"][0]["payment_status"], "failed")

    # =========================================================================
    # 5. TEST WEBHOOK IPN (GET/POST /api/payment/vnpay-ipn)
    # =========================================================================
    @patch("backend.src.modules.payment.router.get_db_connection")
    def test_11_vnpay_ipn_invalid_checksum(self, mock_db_conn):
        """Kiểm tra IPN từ chối khi chữ ký sai (RspCode 97)."""
        mock_db_conn.return_value = FakeConnection(self.db_state)

        req_mock = MagicMock()
        req_mock.query_params = {
            "vnp_TxnRef": "MP-9999_120000",
            "vnp_Amount": "45000000",
            "vnp_SecureHash": "fake_hash"
        }
        req_mock.method = "GET"

        ipn_res = vnpay_ipn_webhook(req_mock)
        self.assertEqual(ipn_res["RspCode"], "97")
        self.assertEqual(ipn_res["Message"], "Invalid Checksum")

    @patch("backend.src.modules.payment.router.get_db_connection")
    def test_12_vnpay_ipn_success(self, mock_db_conn):
        """Kiểm tra IPN xác thực thành công và cập nhật đơn hàng (RspCode 00)."""
        mock_db_conn.return_value = FakeConnection(self.db_state)

        url, _ = build_payment_url("MP-9999", 450000)
        import urllib.parse, hmac, hashlib
        from backend.src.utils.vnpay import VNPAY_HASH_SECRET
        parsed = urllib.parse.urlparse(url)
        params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

        params["vnp_ResponseCode"] = "00"
        params["vnp_TransactionNo"] = "99887766"
        params["vnp_BankCode"] = "VNPAYQR"
        filtered = {k: v for k, v in params.items() if k.startswith("vnp_") and k not in ("vnp_SecureHash", "vnp_SecureHashType")}
        sorted_params = sorted(filtered.items())
        hash_data = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
        params["vnp_SecureHash"] = hmac.new(VNPAY_HASH_SECRET.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

        req_mock = MagicMock()
        req_mock.query_params = params
        req_mock.method = "GET"

        ipn_res = vnpay_ipn_webhook(req_mock)
        self.assertEqual(ipn_res["RspCode"], "00")
        self.assertEqual(ipn_res["Message"], "Confirm Success")
        self.assertEqual(self.db_state["payments"][0]["payment_status"], "completed")

    # =========================================================================
    # 6. TEST TRA CỨU TRẠNG THÁI THANH TOÁN (GET /api/payment/status/{order_key})
    # =========================================================================
    @patch("backend.src.modules.payment.router.get_db_connection")
    def test_13_get_order_payment_status(self, mock_db_conn):
        """Kiểm tra API tra cứu trạng thái thanh toán theo order_key."""
        mock_db_conn.return_value = FakeConnection(self.db_state)

        status_res = get_order_payment_status("MP-9999")
        self.assertEqual(status_res["order_key"], "MP-9999")
        self.assertEqual(status_res["numeric_total"], 450000)
        self.assertEqual(status_res["payment_info"]["method"], "vnpay")
        self.assertEqual(status_res["payment_info"]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
