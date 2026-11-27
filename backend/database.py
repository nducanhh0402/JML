import pymysql
import json
import os
from datetime import datetime

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from backend.src.config.database import (
    ConnectionWrapper,
    CursorWrapper,
    MYSQL_CONFIG,
    MySQLRow,
    ensure_database_exists,
    get_db_connection,
)


def ensure_users_constraints(cursor):
    """TF16EA5: Đảm bảo bảng users có UNIQUE index cho email và index cho số điện thoại.

    Idempotent - chạy nhiều lần an toàn. Các bước giống migrations/006_users_email_unique_index.sql:
      1. email cho phép NULL; email rỗng được chuyển thành NULL.
      2. Email trùng từ dữ liệu cũ: giữ tài khoản có id nhỏ nhất, các tài khoản còn lại đặt NULL.
      3. Tạo UNIQUE INDEX uq_users_email và INDEX idx_users_phone.
    """
    try:
        cursor.execute("ALTER TABLE users MODIFY email VARCHAR(255) NULL DEFAULT NULL;")
        cursor.execute("UPDATE users SET email = NULL WHERE email IS NOT NULL AND TRIM(email) = '';")
        cleared = cursor.execute(
            """
            UPDATE users u
            JOIN (
                SELECT email, MIN(id) AS keep_id
                FROM users
                WHERE email IS NOT NULL
                GROUP BY email
                HAVING COUNT(*) > 1
            ) d ON u.email = d.email AND u.id <> d.keep_id
            SET u.email = NULL;
            """
        )
        if cleared:
            print(f"[users] Đã xoá email trùng lặp của {cleared} tài khoản cũ để tạo UNIQUE index.")

        cursor.execute("SHOW INDEX FROM users;")
        rows = cursor.fetchall()
        index_names = {row["Key_name"] for row in rows}
        has_unique_email = any(
            row["Column_name"] == "email" and int(row["Non_unique"]) == 0 for row in rows
        )
        if not has_unique_email:
            cursor.execute("CREATE UNIQUE INDEX uq_users_email ON users (email);")
        if "idx_users_phone" not in index_names:
            cursor.execute("CREATE INDEX idx_users_phone ON users (phone);")
    except Exception as exc:  # không làm hỏng quá trình khởi động ứng dụng
        print(f"[users] Cảnh báo: không áp dụng được ràng buộc email duy nhất: {exc}")


def init_db(seed=False):
    """Khởi tạo các bảng MySQL (products, customers, orders, order_items, shops)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Bảng SHOPS (Cửa hàng / Sellers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shops (
        shop_key VARCHAR(50) PRIMARY KEY,
        id_display VARCHAR(50) NOT NULL,
        initials VARCHAR(10) NOT NULL,
        name VARCHAR(255) NOT NULL,
        badge VARCHAR(50) NOT NULL,
        badge_class VARCHAR(100) NOT NULL,
        meta TEXT NOT NULL,
        gmv VARCHAR(50) NOT NULL,
        fee VARCHAR(50) NOT NULL,
        product_count VARCHAR(50) NOT NULL,
        rating VARCHAR(50) NOT NULL,
        status VARCHAR(50) DEFAULT 'active'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 1b. Bảng CATEGORIES & BRANDS (Danh mục & Thương hiệu - TF16CEB / TF170B1)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        description VARCHAR(255) DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brands (
        id INT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        origin VARCHAR(100) DEFAULT NULL,
        logo_url TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 2. Bảng PRODUCTS (Sản phẩm trên sàn)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category VARCHAR(100) NOT NULL,
        category_id INT DEFAULT NULL,
        brand VARCHAR(100) DEFAULT '',
        brand_id INT DEFAULT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        price BIGINT NOT NULL,
        original_price BIGINT NOT NULL,
        discount VARCHAR(20) NOT NULL,
        rating FLOAT DEFAULT 5.0,
        sold INT DEFAULT 0,
        stock INT DEFAULT NULL,
        total_stock INT DEFAULT 100,
        images_json TEXT NOT NULL,
        angles_json TEXT NOT NULL,
        exclusive VARCHAR(100) DEFAULT '',
        shop_name VARCHAR(255) DEFAULT 'AB Technology Ltd',
        is_flash_sale TINYINT(1) DEFAULT 0,
        status VARCHAR(50) DEFAULT 'approved'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Đảm bảo bổ sung cột brand, description, stock, category_id, brand_id nếu bảng products đã tạo từ bản cũ
    try:
        cursor.execute("SHOW COLUMNS FROM products;")
        existing_cols = {row["Field"].lower() for row in cursor.fetchall()}
        if "category_id" not in existing_cols:
            cursor.execute("ALTER TABLE products ADD COLUMN category_id INT DEFAULT NULL AFTER category;")
        if "brand" not in existing_cols:
            cursor.execute("ALTER TABLE products ADD COLUMN brand VARCHAR(100) DEFAULT '' AFTER category_id;")
        if "brand_id" not in existing_cols:
            cursor.execute("ALTER TABLE products ADD COLUMN brand_id INT DEFAULT NULL AFTER brand;")
        if "description" not in existing_cols:
            cursor.execute("ALTER TABLE products ADD COLUMN description TEXT AFTER title;")
        if "stock" not in existing_cols:
            cursor.execute("ALTER TABLE products ADD COLUMN stock INT DEFAULT NULL AFTER sold;")
    except Exception:
        pass

    # 2b. Bảng PRODUCT_IMAGES (Ảnh đa góc chụp của sản phẩm)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_images (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        image_url TEXT NOT NULL,
        angle_name VARCHAR(100) DEFAULT 'Mặt trước',
        is_primary TINYINT(1) DEFAULT 0,
        display_order INT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_pi_product_id (product_id),
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 3. Bảng USERS (Tài khoản Đăng nhập cho Khách hàng, Chủ Shop, Admin)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        phone VARCHAR(50) DEFAULT '',
        email VARCHAR(255) DEFAULT '',
        address TEXT,
        shop_key VARCHAR(50) DEFAULT '',
        shop_name VARCHAR(255) DEFAULT '',
        cust_key VARCHAR(50) DEFAULT '',
        created_at VARCHAR(50) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 4. Bảng CARTS (Giỏ hàng của người dùng)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    try:
        cursor.execute("CREATE INDEX idx_cart_user ON carts (user_id);")
    except Exception:
        pass

    # 5. Bảng CART_ITEMS (Chi tiết từng mặt hàng trong giỏ)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cart_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL DEFAULT 1,
        price BIGINT NOT NULL DEFAULT 0,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
        UNIQUE KEY uniq_cart_product (cart_id, product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    try:
        cursor.execute("CREATE INDEX idx_cart_item_product ON cart_items (product_id);")
    except Exception:
        pass

    # 6. Bảng CUSTOMERS (Khách hàng / Người mua)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        cust_key VARCHAR(50) PRIMARY KEY,
        id_display VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL,
        avatar TEXT NOT NULL,
        `rank` VARCHAR(50) DEFAULT 'Đồng',
        rank_badge VARCHAR(100) NOT NULL,
        joined VARCHAR(50) NOT NULL,
        orders_count INT DEFAULT 0,
        total_spent VARCHAR(50) DEFAULT '0 ₫',
        status VARCHAR(50) DEFAULT 'Hoạt động',
        status_badge VARCHAR(100) DEFAULT 'bg-emerald-50 text-emerald-600',
        address TEXT NOT NULL,
        is_banned TINYINT(1) DEFAULT 0
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 7. Bảng ORDERS (Đơn hàng Trung gian & Quỹ giữ hộ Escrow)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_key VARCHAR(50) PRIMARY KEY,
        user_id INT NULL,
        id_display VARCHAR(50) NOT NULL,
        escrow_badge VARCHAR(100) NOT NULL,
        escrow_class VARCHAR(100) NOT NULL,
        time_info TEXT NOT NULL,
        shop_name VARCHAR(255) NOT NULL,
        shop_address TEXT NOT NULL,
        buyer_name VARCHAR(255) NOT NULL,
        buyer_phone VARCHAR(50) DEFAULT '',
        buyer_address TEXT NOT NULL,
        total VARCHAR(50) NOT NULL,
        numeric_total BIGINT DEFAULT 0,
        fee VARCHAR(50) NOT NULL,
        net VARCHAR(50) NOT NULL,
        status VARCHAR(50) DEFAULT 'escrow',
        created_at VARCHAR(50) NOT NULL,
        INDEX idx_order_user_id (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Đảm bảo bổ sung cột user_id cho bảng orders cũ nếu thiếu (TF172C2)
    try:
        cursor.execute("SHOW COLUMNS FROM orders;")
        order_cols = {row["Field"].lower() for row in cursor.fetchall()}
        if "user_id" not in order_cols:
            cursor.execute("ALTER TABLE orders ADD COLUMN user_id INT NULL AFTER order_key;")
            cursor.execute("CREATE INDEX idx_order_user_id ON orders (user_id);")
    except Exception:
        pass

    # 7b. Bảng PAYMENTS (Thanh toán COD / VNPay / Escrow - TF172C2 & TF1753A)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_key VARCHAR(50) NOT NULL,
        user_id INT NULL,
        payment_method VARCHAR(50) NOT NULL DEFAULT 'COD',
        payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
        amount BIGINT NOT NULL DEFAULT 0,
        transaction_code VARCHAR(100) DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_payment_order_key (order_key),
        INDEX idx_payment_user_id (user_id),
        INDEX idx_payment_status (payment_status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 8. Bảng ORDER_ITEMS (Chi tiết từng mặt hàng trong đơn)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_key VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        variant VARCHAR(255) NOT NULL,
        price VARCHAR(50) NOT NULL,
        qty VARCHAR(50) NOT NULL,
        subtotal VARCHAR(50) NOT NULL,
        FOREIGN KEY (order_key) REFERENCES orders (order_key) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Lịch sử chuyển trạng thái đơn hàng
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_status_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_key VARCHAR(50) NOT NULL,
        old_status VARCHAR(50) NULL,
        new_status VARCHAR(50) NOT NULL,
        changed_by INT NULL,
        note VARCHAR(255) DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_history_order_key (order_key),
        INDEX idx_history_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 9. Bảng BANNERS (Banner hiển thị trang chủ) - TF17398
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS banners (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL DEFAULT '',
        image_url TEXT NOT NULL,
        link_url VARCHAR(500) DEFAULT '',
        description TEXT DEFAULT (''),
        sort_order INT DEFAULT 0,
        is_active TINYINT(1) DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 10. Bảng USER_ADDRESSES (Sổ địa chỉ nhận hàng của người dùng) - TF170FF
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_addresses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        recipient_name VARCHAR(150) NOT NULL,
        phone VARCHAR(50) NOT NULL,
        province_city VARCHAR(100) DEFAULT '',
        district VARCHAR(100) DEFAULT '',
        ward VARCHAR(100) DEFAULT '',
        street_address VARCHAR(255) NOT NULL,
        full_address TEXT NOT NULL,
        is_default TINYINT(1) DEFAULT 0,
        tag VARCHAR(50) DEFAULT 'Nhà riêng',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    try:
        cursor.execute("CREATE INDEX idx_user_addresses_user ON user_addresses (user_id);")
    except Exception:
        pass
    try:
        cursor.execute("CREATE INDEX idx_user_addresses_user_default ON user_addresses (user_id, is_default);")
    except Exception:
        pass

    # 11. Bảng VOUCHERS (Mã giảm giá khuyến mãi) - TF1728C / TF17167
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vouchers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(150) NOT NULL DEFAULT '',
        description TEXT,
        discount_type VARCHAR(20) NOT NULL DEFAULT 'fixed',
        discount_value BIGINT NOT NULL DEFAULT 0,
        max_discount_amount BIGINT DEFAULT NULL,
        min_order_value BIGINT NOT NULL DEFAULT 0,
        usage_limit INT NOT NULL DEFAULT 100,
        used_count INT NOT NULL DEFAULT 0,
        start_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        end_date DATETIME NOT NULL,
        is_active TINYINT(1) NOT NULL DEFAULT 1,
        created_by INT DEFAULT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    try:
        cursor.execute("CREATE INDEX idx_vouchers_code ON vouchers (code);")
    except Exception:
        pass
    try:
        cursor.execute("CREATE INDEX idx_vouchers_active_dates ON vouchers (is_active, start_date, end_date);")
    except Exception:
        pass

    # 12. Bảng VOUCHER_USAGES (Lịch sử sử dụng mã giảm giá) - TF1728C
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voucher_usages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        voucher_id INT NOT NULL,
        user_id INT NOT NULL,
        order_key VARCHAR(50) DEFAULT NULL,
        discount_amount BIGINT NOT NULL DEFAULT 0,
        order_subtotal BIGINT NOT NULL DEFAULT 0,
        final_total BIGINT NOT NULL DEFAULT 0,
        used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (voucher_id) REFERENCES vouchers (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    try:
        cursor.execute("CREATE INDEX idx_usages_voucher ON voucher_usages (voucher_id);")
    except Exception:
        pass
    try:
        cursor.execute("CREATE INDEX idx_usages_user ON voucher_usages (user_id);")
    except Exception:
        pass
    try:
        cursor.execute("CREATE INDEX idx_usages_order ON voucher_usages (order_key);")
    except Exception:
        pass
    try:
        cursor.execute("CREATE INDEX idx_usages_user_voucher ON voucher_usages (user_id, voucher_id);")
    except Exception:
        pass

    # 13. Bảng REVIEWS (Đánh giá & chấm sao 1-5 cho từng sản phẩm) - TF174F6
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        user_id INT NULL,
        user_name VARCHAR(255) NOT NULL,
        rating TINYINT NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uniq_review_user_product (user_id, product_id),
        INDEX idx_review_product (product_id),
        INDEX idx_review_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 14. Bảng SEARCH_HISTORY (Lưu từ khóa tìm kiếm gần đây của người dùng) - TF16EF3
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_key VARCHAR(120) NOT NULL,
        user_id INT NULL,
        keyword VARCHAR(100) NOT NULL,
        keyword_normalized VARCHAR(100) NOT NULL,
        search_count INT NOT NULL DEFAULT 1,
        last_searched_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_search_history_user_keyword (user_key, keyword_normalized),
        INDEX idx_search_history_user_recent (user_key, last_searched_at),
        INDEX idx_search_history_user_id (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    # TF175F0: Index tối ưu lọc trạng thái, khoảng ngày và lịch sử đơn
    for index_sql in (
        "CREATE INDEX idx_order_status_created ON orders (status, created_at)",
        "CREATE INDEX idx_order_created_status ON orders (created_at, status)",
        "CREATE INDEX idx_order_item_order_name ON order_items (order_key, name)",
        "CREATE INDEX idx_history_order_created ON order_status_history (order_key, created_at)",
        # TF175BC: Index tối ưu truy vấn trang chủ (banner hoạt động, SP nổi bật, SP mới nhất, danh mục)
        "CREATE INDEX idx_banners_active_sort ON banners (is_active, sort_order)",
        "CREATE INDEX idx_products_status_rating_sold ON products (status, rating, sold)",
        "CREATE INDEX idx_products_status_id ON products (status, id)",
        "CREATE INDEX idx_products_status_category ON products (status, category)",
    ):
        try:
            cursor.execute(index_sql)
        except Exception:
            pass

    # Index email (UNIQUE) + index phone cho bảng users (TF16EA5)
    ensure_users_constraints(cursor)

    # Tạo sẵn tài khoản Super Admin mặc định nếu chưa có (admin / 123456)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin';")
    if cursor.fetchone()[0] == 0:
        now_str = datetime.now().strftime("%d/%m/%Y")
        cursor.execute(
            """
            INSERT INTO users (username, password, role, full_name, phone, email, address, created_at)
            VALUES ('admin', '123456', 'admin', 'Hoàng Nam (Super Admin)', '0900000000', 'admin@jmlstore.vn', 'Trụ sở JML Store', ?);
        """,
            (now_str,),
        )

    # Tự động đồng bộ số lượng đã bán (sold) của từng sản phẩm từ các đơn hàng thực tế
    try:
        cursor.execute("""
            UPDATE products p
            JOIN (
                SELECT name, SUM(CAST(qty AS UNSIGNED)) as total_sold
                FROM order_items
                GROUP BY name
            ) s ON p.title = s.name OR p.title LIKE CONCAT('%', s.name, '%')
            SET p.sold = GREATEST(p.sold, s.total_sold);
        """)
    except Exception:
        pass

    conn.commit()
    ensure_catalog_seed_data(conn)
    if seed:
        seed_initial_data(conn)
    conn.close()


def ensure_catalog_seed_data(conn):
    """Đảm bảo có sẵn danh mục, thương hiệu, sản phẩm và mã giảm giá mẫu khi DB mới khởi tạo."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM categories;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT IGNORE INTO categories (id, code, name, description) VALUES (?, ?, ?, ?);",
                [
                    (1, "tech", "Công Nghệ & Điện Tử", "Điện thoại, Laptop, Màn hình, Tai nghe và phụ kiện gaming cao cấp"),
                    (2, "fashion", "Thời Trang Nam Nữ", "Áo vest, blazer, sơ mi lụa, quần tây chuẩn form may đo thủ công"),
                    (3, "watch", "Đồng Hồ & Trang Sức", "Đồng hồ cơ Thụy Sĩ, đồng hồ thông minh, trang sức đá quý cao cấp"),
                    (4, "shoes", "Giày Dép Thời Trang", "Giày Oxford da bò Ý, sneaker thể thao, running shoes thoáng khí"),
                    (5, "beauty", "Mỹ Phẩm & Chăm Sóc Sắc Đẹp", "Nước hoa Pháp, serum chống lão hóa, kem dưỡng ẩm tế bào gốc"),
                ],
            )
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM brands;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT IGNORE INTO brands (id, code, name, origin, logo_url) VALUES (?, ?, ?, ?, ?);",
                [
                    (1, "apple", "Apple", "Hoa Kỳ (USA)", "https://cdn.iconscout.com/icon/free/png-256/apple-131-432549.png"),
                    (2, "samsung", "Samsung", "Hàn Quốc", "https://cdn.iconscout.com/icon/free/png-256/samsung-226432.png"),
                    (3, "sony", "Sony", "Nhật Bản", "https://cdn.iconscout.com/icon/free/png-256/sony-logo-icon-download-in-svg-png-gif-file-formats--technology-brand-pack-logos-icons-2738734.png"),
                    (4, "aristino", "Aristino", "Việt Nam / Phong cách Ý", "https://cdn.iconscout.com/icon/free/png-256/fashion-brand-logo-icon.png"),
                    (5, "owen", "Owen", "Việt Nam", "https://cdn.iconscout.com/icon/free/png-256/clothes-hanger-icon.png"),
                    (6, "rolex", "Rolex", "Thụy Sĩ", "https://cdn.iconscout.com/icon/free/png-256/rolex-logo-icon.png"),
                    (7, "nike", "Nike", "Hoa Kỳ (USA)", "https://cdn.iconscout.com/icon/free/png-256/nike-2-282672.png"),
                    (8, "adidas", "Adidas", "Đức", "https://cdn.iconscout.com/icon/free/png-256/adidas-9-282664.png"),
                    (9, "nvidia", "NVIDIA", "Hoa Kỳ (USA)", ""),
                    (10, "logitech", "Logitech", "Thụy Sĩ", ""),
                ],
            )
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM products;")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                (1, "tech", 1, "Apple", 1, "iPhone 15 Pro Max 256GB Titan Tự Nhiên", "Chip A17 Pro, khung Titan siêu bền, camera zoom quang 5x chuẩn chính hãng 100%.", 28990000, 34990000, "-17%", 4.9, 1420, 85, 200, '["https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800"]', '["Mặt trước"]', "Hot Trend", "AB Technology Ltd", 1, "approved"),
                (2, "tech", 1, "Apple", 1, "MacBook Pro 16 M3 Max 36GB / 1TB SSD", "Hiệu năng đồ họa chuyên nghiệp, màn hình Liquid Retina XDR sắc nét.", 68990000, 79990000, "-14%", 5.0, 310, 32, 50, '["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800"]', '["Mặt trước"]', "Official", "AB Technology Ltd", 0, "approved"),
                (3, "tech", 1, "Samsung", 2, "Samsung Galaxy S24 Ultra 512GB Titanium Gray", "Bút S-Pen tích hợp, Galaxy AI thông minh, camera 200MP.", 27490000, 33990000, "-19%", 4.8, 980, 115, 250, '["https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800"]', '["Toàn thân"]', "AI Phone", "AB Technology Ltd", 1, "approved"),
                (4, "tech", 1, "Sony", 3, "Tai nghe Chống Ồn Sony WH-1000XM5 Hi-Res Audio", "Chống ồn chủ động đỉnh cao, kết nối đa điểm mượt mà.", 6990000, 8990000, "-22%", 4.9, 750, 140, 300, '["https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800"]', '["Toàn cảnh"]', "Best Audio", "SoundMax & Marshall Audio", 0, "approved"),
                (5, "fashion", 2, "Aristino", 4, "Bộ Suit Nam May Đo Thủ Công Aristino Italian Wool", "Chất liệu len Ý phối tỷ lệ 50_50 thoáng nhẹ, giữ phom dáng sang trọng.", 4850000, 5990000, "-19%", 4.9, 230, 60, 100, '["https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800"]', '["Mặt trước"]', "Handmade", "Trungshop", 0, "approved"),
                (6, "fashion", 2, "Aristino", 4, "Áo Blazer Da Nam Cao Cấp Chuẩn Phong Cách Ý", "Da thật 100%, đường may tinh xảo, phù hợp sự kiện trang trọng.", 2450000, 3200000, "-23%", 4.8, 410, 95, 150, '["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800"]', '["Mặt trước"]', "Gentleman", "Trungshop", 1, "approved"),
                (7, "fashion", 2, "Owen", 5, "Áo Sơ Mi Nam Sợi Tre Bamboo Kháng Khuẩn Owen", "Sợi tre tự nhiên thoáng mát, chống nhăn hiệu quả cả ngày dài.", 580000, 750000, "-23%", 4.7, 1850, 350, 500, '["https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800"]', '["Mặt trước"]', "Eco Fashion", "Trungshop", 0, "approved"),
                (8, "fashion", 2, "Owen", 5, "Quần Tây Nam Dáng Slimfit Co Giãn 4 Chiều Owen", "Form slimfit tôn dáng, vải co giãn nhẹ thoải mái vận động.", 690000, 890000, "-22%", 4.8, 1200, 280, 400, '["https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800"]', '["Mặt trước"]', "Office Style", "Trungshop", 0, "approved"),
                (9, "watch", 3, "Rolex", 6, "Đồng Hồ Rolex Submariner Date Mặt Số Đen Thép Oystersteel", "Máy cơ tự động Thụy Sĩ, chống nước 300m, vành gốm Cerachrom.", 268000000, 295000000, "-9%", 5.0, 45, 8, 10, '["https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800"]', '["Mặt số"]', "Luxury Diver", "Luxury Watch Vietnam", 0, "approved"),
                (10, "watch", 3, "Apple", 1, "Apple Watch Ultra 2 GPS + Cellular 49mm Titanium", "Màn hình siêu sáng 3000 nits, vỏ Titanium bền bỉ.", 19490000, 21990000, "-11%", 4.9, 560, 75, 120, '["https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800"]', '["Mặt đồng hồ"]', "Rugged", "Luxury Watch Vietnam", 1, "approved"),
                (11, "shoes", 4, "Nike", 7, "Giày Chạy Bộ Nam Nike Air Zoom Pegasus 40", "Đệm Air Zoom êm ái, thoáng khí tối ưu cho chạy bộ hằng ngày.", 2890000, 3690000, "-22%", 4.8, 1620, 180, 300, '["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"]', '["Góc nghiêng"]', "Pro Runner", "Trungshop", 1, "approved"),
                (12, "shoes", 4, "Nike", 7, "Giày Thể Thao Nam Nike Air Jordan 1 Retro High OG", "Thiết kế bóng rổ huyền thoại, phối màu cổ điển chuẩn sưu tầm.", 4990000, 6200000, "-20%", 4.9, 890, 45, 80, '["https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800"]', '["Góc nghiêng"]', "Sneakerhead", "Trungshop", 0, "approved"),
                (13, "shoes", 4, "Adidas", 8, "Giày Chạy Bộ Nam Adidas Ultraboost Light 23", "Đế Boost siêu nhẹ hoàn trả năng lượng vượt trội.", 3200000, 4500000, "-29%", 4.9, 1430, 160, 250, '["https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800"]', '["Góc nghiêng"]', "Boost Tech", "Trungshop", 1, "approved"),
                (14, "shoes", 4, "Adidas", 8, "Giày Sneaker Cổ Điển Adidas Stan Smith Da Thật", "Kiểu dáng tối giản dễ phối đồ, đệm lót êm chân.", 1890000, 2400000, "-21%", 4.7, 2100, 210, 350, '["https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800"]', '["Góc nghiêng"]', "Iconic", "Trungshop", 0, "approved"),
                (15, "tech", 1, "Samsung", 2, "Màn Hình Đồ Họa Samsung ViewFinity S9 5K 27 inch", "Độ phân giải 5K chuẩn màu chuyên nghiệp cho thiết kế & dựng phim.", 23900000, 29990000, "-20%", 4.8, 110, 25, 40, '["https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800"]', '["Mặt trước"]', "Pro Display", "GearVN Official Store", 0, "approved"),
                (16, "tech", 1, "Sony", 3, "Máy Chơi Game Sony PlayStation 5 Slim 1TB SSD", "Tốc độ tải game siêu nhanh, hỗ trợ Ray Tracing thế hệ mới.", 13490000, 15990000, "-16%", 5.0, 1750, 90, 150, '["https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800"]', '["Mặt trước"]', "Gaming Beast", "GearVN Official Store", 1, "approved"),
                (17, "tech", 1, "NVIDIA", 9, "Card màn hình RTX 5090 Gaming OC 32GB GDDR7", "Kiến trúc Blackwell mạnh mẽ, hỗ trợ Ray Tracing thế hệ 4 và DLSS 4 cho 4K 240Hz.", 64990000, 69990000, "-7%", 5.0, 215, 20, 30, '["https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800"]', '["Toàn cảnh"]', "Flagship GPU", "GearVN Official Store", 1, "approved"),
                (18, "tech", 1, "Logitech", 10, "Chuột Không Dây Logitech MX Master 3S Silent", "Kết nối đa chế độ USB-C / 2.4G và Bluetooth, cảm biến 8000 DPI siêu chính xác.", 2490000, 2990000, "-17%", 4.9, 940, 160, 220, '["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800"]', '["Góc nghiêng"]', "Pro Mouse", "GearVN Official Store", 0, "approved"),
                (19, "watch", 3, "Rolex", 6, "Đồng Hồ Rolex Datejust 41 Mặt Vi Tính Xanh Thép Vàng Trắng", "Biểu tượng thanh lịch vượt thời gian, chế tác thủ công Thụy Sĩ.", 325000000, 360000000, "-10%", 5.0, 28, 5, 8, '["https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800"]', '["Mặt số"]', "Timeless Classic", "Luxury Watch Vietnam", 0, "approved"),
                (20, "fashion", 2, "Owen", 5, "Áo Khoác Nam Phao Lông Vũ Siêu Nhẹ Cản Gió Owen", "Giữ ấm tối ưu, trọng lượng siêu nhẹ, gấp gọn tiện lợi.", 1250000, 1690000, "-26%", 4.7, 530, 140, 220, '["https://images.unsplash.com/photo-1544923246-77307dd654cb?w=800"]', '["Mặt trước"]', "Winter Warmth", "Trungshop", 0, "approved"),
                (21, "tech", 1, "Apple", 1, "iPad Pro 13 inch M4 Ultra Retina XDR OLED 256GB", "Màn hình OLED Tandem siêu mỏng, chip Apple M4 mạnh mẽ.", 34990000, 37990000, "-8%", 5.0, 420, 55, 80, '["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800"]', '["Mặt trước"]', "OLED Master", "AB Technology Ltd", 1, "approved"),
            ]
            cursor.executemany(
                """
                INSERT IGNORE INTO products (
                    id, category, category_id, brand, brand_id, title, description,
                    price, original_price, discount, rating, sold, stock, total_stock,
                    images_json, angles_json, exclusive, shop_name, is_flash_sale, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                sample_products,
            )
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM vouchers;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO vouchers (code, name, description, discount_type, discount_value, max_discount_amount, min_order_value, usage_limit, used_count, start_date, end_date, is_active)
                VALUES
                    ('FREESHIP', 'Freeship Toàn Quốc', 'Miễn phí 100% tiền vận chuyển', 'shipping', 15000, 30000, 0, 1000, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
                    ('JML50K', 'Giảm 50K đơn từ 100K', 'Giảm ngay 50.000 ₫ cho đơn từ 100.000 ₫', 'fixed', 50000, NULL, 100000, 500, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
                    ('GIAM10', 'Giảm 10% tối đa 100K', 'Giảm 10% (tối đa 100.000 ₫)', 'percent', 10, 100000, 0, 200, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
                    ('VIP100K', 'Vip 100K đơn từ 1M', 'Giảm ngay 100.000 ₫ cho đơn từ 1.000.000 ₫', 'fixed', 100000, NULL, 1000000, 100, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1);
            """)
            conn.commit()
    except Exception as exc:
        print(f"[seed] Cảnh báo khi nạp dữ liệu catalog mặc định: {exc}")


def seed_initial_data(conn):
    """Nạp dữ liệu mẫu ban đầu nếu được yêu cầu."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM shops;")
    if cursor.fetchone()[0] == 0:
        shops_data = [
            (
                "SH-102",
                "#SH-102",
                "AB",
                "AB Technology Ltd",
                "JML MALL",
                "bg-danger-500 text-white",
                "Mã Shop: #SH-102 • Quận 1, TP.HCM",
                "$312,400.00",
                "$21,868.00",
                "142 mặt hàng",
                "★ 4.9 / 5.0",
                "active",
            ),
            (
                "SH-418",
                "#SH-418",
                "ZF",
                "Zara Fashion Store",
                "YÊU THÍCH+",
                "bg-warning-500 text-white",
                "Mã Shop: #SH-418 • Quận Hoàn Kiếm, Hà Nội",
                "$198,200.00",
                "$13,874.00",
                "98 mặt hàng",
                "★ 4.8 / 5.0",
                "active",
            ),
            (
                "SH-015",
                "#SH-015",
                "CF",
                "Canon Flagship Store",
                "JML MALL",
                "bg-danger-500 text-white",
                "Mã Shop: #SH-015 • Quận 3, TP.HCM",
                "$164,500.00",
                "$11,515.00",
                "64 mặt hàng",
                "★ 4.9 / 5.0",
                "active",
            ),
            (
                "SH-889",
                "#SH-889",
                "SM",
                "SoundMax Audio Shop",
                "TIÊU CHUẨN",
                "bg-neutral-200 text-neutral-700",
                "Mã Shop: #SH-889 • Hải Châu, Đà Nẵng",
                "$42,800.00",
                "$2,996.00",
                "52 mặt hàng",
                "★ 4.5 / 5.0",
                "active",
            ),
        ]
        cursor.executemany(
            "INSERT INTO shops VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            shops_data,
        )
        conn.commit()

    # Nạp dữ liệu mẫu ban đầu cho vouchers và voucher_usages (TF1728C)
    try:
        cursor.execute("SELECT COUNT(*) FROM vouchers;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO vouchers (id, code, name, description, discount_type, discount_value, max_discount_amount, min_order_value, usage_limit, used_count, start_date, end_date, is_active)
                VALUES
                    (1, 'FREESHIP', 'Freeship Toàn Quốc', 'Miễn phí 100% tiền vận chuyển', 'shipping', 15000, 30000, 0, 1000, 15, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
                    (2, 'JML50K', 'Giảm 50K đơn từ 200K', 'Giảm ngay 50.000 ₫ cho đơn từ 200.000 ₫', 'fixed', 50000, NULL, 200000, 500, 8, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
                    (3, 'GIAM10', 'Giảm 10% tối đa 100K', 'Giảm 10% (tối đa 100.000 ₫)', 'percent', 10, 100000, 100000, 300, 12, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
                    (4, 'VIP100K', 'Vip 100K đơn từ 1M', 'Giảm ngay 100.000 ₫ cho đơn từ 1.000.000 ₫', 'fixed', 100000, NULL, 1000000, 100, 3, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
                    (5, 'CHAOXUAN2026', 'Mừng Xuân 2026 Giảm 20%', 'Khuyến mãi năm mới giảm 20% tối đa 200.000 ₫', 'percent', 20, 200000, 300000, 200, 0, NOW(), DATE_ADD(NOW(), INTERVAL 6 MONTH), 1),
                    (6, 'TRIAN50', 'Tri Ân Khách Hàng', 'Mã tri ân giảm 50.000 ₫ cho đơn từ 150.000 ₫', 'fixed', 50000, NULL, 150000, 250, 5, NOW(), DATE_ADD(NOW(), INTERVAL 3 MONTH), 1);
            """)
            conn.commit()

            # Seed voucher usages mẫu
            cursor.execute("""
                INSERT INTO voucher_usages (voucher_id, user_id, order_key, discount_amount, order_subtotal, final_total, used_at)
                VALUES
                    (1, 1, 'ORD-202611-001', 15000, 185000, 170000, NOW()),
                    (2, 1, 'ORD-202611-002', 50000, 350000, 300000, NOW());
            """)
            conn.commit()
    except Exception:
        pass

    # Thêm tự động tạo order_date/index khi startup để dashboard query luôn tối ưu.
    try:
        cursor.execute("SHOW COLUMNS FROM orders LIKE 'order_date';")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE orders ADD COLUMN order_date DATE GENERATED ALWAYS AS (STR_TO_DATE(created_at, '%d/%m/%Y')) STORED")
    except Exception:
        pass
    for index_sql in (
        "CREATE INDEX idx_order_status_date ON orders (status, order_date)",
    ):
        try:
            cursor.execute(index_sql)
        except Exception:
            pass
