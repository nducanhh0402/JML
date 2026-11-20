import unittest
from datetime import date
from unittest.mock import patch

from fastapi import HTTPException

from backend.src.modules.admin.router import (
    get_admin_metrics,
    get_admin_revenue_report,
    get_admin_top_products,
)


class ReportCursor:
    def __init__(self):
        self.rows = []

    def execute(self, sql, args=None):
        sql_lower = sql.lower()
        if "count(*) as total, coalesce(sum(numeric_total)" in sql_lower:
            self.rows = [{"total": 12, "gmv": 3000000}]
        elif "count(*) as total from products where status = 'pending'" in sql_lower:
            self.rows = [{"total": 2}]
        elif "count(*) as total from products" in sql_lower:
            self.rows = [{"total": 15}]
        elif "count(*) as total from customers" in sql_lower:
            self.rows = [{"total": 8}]
        elif "count(*) as total from shops" in sql_lower:
            self.rows = [{"total": 5}]
        elif "group by report_date" in sql_lower:
            self.rows = [{"report_date": "20/11/2026", "order_count": 3, "gmv": 750000, "revenue": 52500}]
        elif "group by oi.name" in sql_lower:
            self.rows = [{"product_name": "Tai nghe JML", "sold_quantity": 10, "order_count": 4, "revenue": 2500000}]

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return list(self.rows)


class ReportConnection:
    def __init__(self):
        self.cur = ReportCursor()

    def cursor(self):
        return self.cur

    def close(self):
        pass


class TestAdminReports(unittest.TestCase):
    def test_revenue_report_by_day(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=ReportConnection()):
            result = get_admin_revenue_report(period="day", date_from=date(2026, 11, 1), date_to=date(2026, 11, 30))
        self.assertEqual(result["period_type"], "day")
        self.assertEqual(result["data"][0]["gmv"], 750000)
        self.assertEqual(result["total_gmv"], 750000)

    def test_revenue_report_rejects_invalid_range(self):
        with self.assertRaises(HTTPException) as ctx:
            get_admin_revenue_report(period="month", date_from=date(2026, 11, 30), date_to=date(2026, 11, 1))
        self.assertEqual(ctx.exception.status_code, 400)

    def test_top_products(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=ReportConnection()):
            result = get_admin_top_products(limit=5)
        self.assertEqual(result["top_products"][0]["name"], "Tai nghe JML")
        self.assertEqual(result["top_products"][0]["sold_quantity"], 10)

    def test_admin_metrics(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=ReportConnection()):
            result = get_admin_metrics()
        self.assertEqual(result["total_gmv"], 3000000)
        self.assertEqual(result["total_revenue"], 210000)
        self.assertEqual(result["total_orders"], 12)


if __name__ == "__main__":
    unittest.main()
