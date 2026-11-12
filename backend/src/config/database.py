import os
import pymysql

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "123456"),
    "database": os.getenv("MYSQL_DB", "jml_marketplace"),
    "charset": "utf8mb4",
    "autocommit": True,
}


class MySQLRow(dict):
    """Hỗ trợ truy cập cả theo tên cột row['title'] và chỉ số row[0] như SQLite Row."""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class CursorWrapper:
    """Wrapper cho PyMySQL Cursor: Tự động chuyển đổi ký tự ? của SQLite sang %s của MySQL."""
    def __init__(self, cursor):
        self.cur = cursor

    def execute(self, sql, args=None):
        sql_converted = sql.replace("?", "%s")
        return self.cur.execute(sql_converted, args)

    def executemany(self, sql, args=None):
        sql_converted = sql.replace("?", "%s")
        return self.cur.executemany(sql_converted, args)

    def fetchone(self):
        row = self.cur.fetchone()
        return MySQLRow(row) if row else None

    def fetchall(self):
        rows = self.cur.fetchall()
        return [MySQLRow(r) for r in rows]

    def __getattr__(self, name):
        return getattr(self.cur, name)


class ConnectionWrapper:
    """Wrapper cho PyMySQL Connection."""
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return CursorWrapper(self.conn.cursor(pymysql.cursors.DictCursor))

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def __getattr__(self, name):
        return getattr(self.conn, name)


def ensure_database_exists():
    """Tự động tạo database MySQL 'jml_marketplace' nếu chưa có."""
    try:
        conn = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            charset="utf8mb4",
            autocommit=True
        )
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()
    except Exception as e:
        print("Cảnh báo kiểm tra database:", e)


def get_db_connection():
    """Tạo kết nối tới cơ sở dữ liệu MySQL Server (127.0.0.1:3306)."""
    ensure_database_exists()
    conn = pymysql.connect(**MYSQL_CONFIG)
    return ConnectionWrapper(conn)
