"""TF17257: Script thêm 50 sản phẩm mẫu thuộc nhiều danh mục và thương hiệu.

Phục vụ kiểm thử các tính năng:
- Tìm kiếm từ khóa theo tên, mô tả, thương hiệu.
- Lọc theo danh mục (tech, fashion, watch, shoes, beauty).
- Lọc theo thương hiệu (Apple, Samsung, Sony, Nike, Adidas, Rolex, Casio, v.v.).
- Lọc theo khoảng giá (min_price, max_price), sắp xếp (giá tăng/giảm, bán chạy, đánh giá).
- Phân trang, hiển thị responsive trên máy tính và điện thoại.

Cách chạy:
    python -m backend.db.seeds.seed_50_products
hoặc:
    python backend/db/seeds/seed_50_products.py
"""
import json
import os
import sys
from typing import Any, Dict, List, Tuple

# Đảm bảo import được backend khi chạy trực tiếp file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from backend.database import get_db_connection, init_db
except ImportError:
    from backend.src.config.database import get_db_connection
    init_db = None


# ==============================================================================
# DANH MỤC & THƯƠNG HIỆU HỖ TRỢ
# ==============================================================================
CATEGORIES_SEED = [
    {"code": "tech", "name": "Công Nghệ & Điện Tử", "description": "Điện thoại, Laptop, Màn hình, Tai nghe và phụ kiện gaming cao cấp"},
    {"code": "fashion", "name": "Thời Trang Nam Nữ", "description": "Áo vest, blazer, sơ mi lụa, quần tây chuẩn form may đo thủ công"},
    {"code": "watch", "name": "Đồng Hồ & Trang Sức", "description": "Đồng hồ cơ Thụy Sĩ, đồng hồ thông minh, trang sức đá quý cao cấp"},
    {"code": "shoes", "name": "Giày Dép Thời Trang", "description": "Giày Oxford da bò Ý, sneaker thể thao, running shoes thoáng khí"},
    {"code": "beauty", "name": "Mỹ Phẩm & Chăm Sóc Sắc Đẹp", "description": "Nước hoa Pháp, serum chống lão hóa, kem dưỡng ẩm tế bào gốc"},
]

BRANDS_SEED = [
    {"code": "apple", "name": "Apple", "origin": "Hoa Kỳ (USA)", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/apple-131-432549.png"},
    {"code": "samsung", "name": "Samsung", "origin": "Hàn Quốc", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/samsung-226432.png"},
    {"code": "sony", "name": "Sony", "origin": "Nhật Bản", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/sony-logo-icon-download-in-svg-png-gif-file-formats--technology-brand-pack-logos-icons-2738734.png"},
    {"code": "xiaomi", "name": "Xiaomi", "origin": "Trung Quốc", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/xiaomi-1-282572.png"},
    {"code": "aristino", "name": "Aristino", "origin": "Việt Nam / Phong cách Ý", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/fashion-brand-logo-icon.png"},
    {"code": "owen", "name": "Owen", "origin": "Việt Nam", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/clothes-hanger-icon.png"},
    {"code": "gucci", "name": "Gucci", "origin": "Ý (Italy)", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/gucci-logo-icon.png"},
    {"code": "rolex", "name": "Rolex", "origin": "Thụy Sĩ", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/rolex-logo-icon.png"},
    {"code": "casio", "name": "Casio", "origin": "Nhật Bản", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/casio-logo-icon.png"},
    {"code": "nike", "name": "Nike", "origin": "Hoa Kỳ (USA)", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/nike-2-282672.png"},
    {"code": "adidas", "name": "Adidas", "origin": "Đức", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/adidas-9-282664.png"},
    {"code": "puma", "name": "Puma", "origin": "Đức", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/puma-logo-icon.png"},
    {"code": "chanel", "name": "Chanel", "origin": "Pháp", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/chanel-logo-icon.png"},
    {"code": "loreal", "name": "L'Oréal", "origin": "Pháp", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/loreal-logo-icon.png"},
    {"code": "innisfree", "name": "Innisfree", "origin": "Hàn Quốc", "logo_url": "https://cdn.iconscout.com/icon/free/png-256/cosmetics-makeup-icon.png"},
]


# ==============================================================================
# DANH SÁCH 50 SẢN PHẨM MẪU ĐẦY ĐỦ THUỘC 5 DANH MỤC & NHIỀU THƯƠNG HIỆU
# ==============================================================================
SAMPLE_PRODUCTS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # 1. CÔNG NGHỆ & ĐIỆN TỬ (tech) - 12 SẢN PHẨM
    # --------------------------------------------------------------------------
    {
        "category_code": "tech",
        "brand_code": "apple",
        "title": "Apple iPhone 15 Pro Max 256GB Titan Tự Nhiên",
        "description": "Siêu phẩm cao cấp khung viền Titan chuẩn hàng không vũ trụ, chip Apple A17 Pro mạnh mẽ, camera tiềm vọng zoom quang học 5x, màn hình Super Retina XDR Always-On.",
        "price": 29490000,
        "original_price": 34990000,
        "discount": "-16%",
        "rating": 4.9,
        "sold": 1250,
        "stock": 45,
        "total_stock": 100,
        "exclusive": "Hot Trend",
        "shop_name": "Apple Flagship Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800",
        "angles": [
            {"label": "Mặt trước Dynamic Island", "url": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800"},
            {"label": "Mặt lưng Titan Tự Nhiên", "url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800"},
            {"label": "Cụm 3 Camera 48MP", "url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "apple",
        "title": "Apple MacBook Pro 14 inch M3 Pro 18GB 512GB Space Black",
        "description": "Laptop đồ họa đỉnh cao với chip M3 Pro 11 nhân CPU, 14 nhân GPU, màn hình Liquid Retina XDR độ sáng 1600 nits, thời lượng pin ấn tượng lên tới 18 giờ làm việc.",
        "price": 49990000,
        "original_price": 54990000,
        "discount": "-9%",
        "rating": 5.0,
        "sold": 340,
        "stock": 20,
        "total_stock": 50,
        "exclusive": "JML Mall",
        "shop_name": "Apple Flagship Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800",
        "angles": [
            {"label": "Mặt trước Liquid Retina XDR", "url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800"},
            {"label": "Bàn phím Magic Keyboard & Cổng kết nối", "url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "apple",
        "title": "Apple iPad Air 5 M1 64GB WiFi Starlight",
        "description": "Máy tính bảng thời thượng mang sức mạnh chip Apple M1 đột phá, màn hình Liquid Retina 10.9 inch sắc nét, camera trước góc siêu rộng hỗ trợ Center Stage thông minh.",
        "price": 13790000,
        "original_price": 16990000,
        "discount": "-19%",
        "rating": 4.8,
        "sold": 890,
        "stock": 60,
        "total_stock": 120,
        "exclusive": "Bán Chạy",
        "shop_name": "Apple Flagship Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800",
        "angles": [
            {"label": "Mặt trước màn hình", "url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "apple",
        "title": "Apple AirPods Pro 2 MagSafe USB-C Chống Ồn Chủ Động",
        "description": "Tai nghe True Wireless cao cấp trang bị chip Apple H2, chống ồn chủ động ANC gấp 2 lần thế hệ trước, chế độ xuyên âm thích ứng và âm thanh không gian cá nhân hóa.",
        "price": 5490000,
        "original_price": 6190000,
        "discount": "-11%",
        "rating": 4.9,
        "sold": 2400,
        "stock": 120,
        "total_stock": 250,
        "exclusive": "Hot Trend",
        "shop_name": "Apple Flagship Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800",
        "angles": [
            {"label": "Hộp sạc và tai nghe", "url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "samsung",
        "title": "Samsung Galaxy S24 Ultra 5G 12GB 256GB Titanium Black",
        "description": "Điện thoại AI đỉnh cao với Galaxy AI tích hợp sẵn, màn hình phẳng Dynamic AMOLED 2X 6.8 inch 120Hz siêu sáng, khung viền Titan và bút S-Pen quyền năng.",
        "price": 26990000,
        "original_price": 33990000,
        "discount": "-21%",
        "rating": 4.9,
        "sold": 1100,
        "stock": 80,
        "total_stock": 150,
        "exclusive": "AI Phone",
        "shop_name": "Samsung Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800",
        "angles": [
            {"label": "Toàn thân và bút S-Pen", "url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "samsung",
        "title": "Samsung Galaxy Z Fold5 5G 12GB 512GB Icy Blue",
        "description": "Thiết kế gập không khe hở bản lề Flex tiên tiến, mở ra màn hình chính 7.6 inch đa nhiệm mượt mà, camera chuẩn flagship và chuẩn kháng nước IPX8 bền bỉ.",
        "price": 32990000,
        "original_price": 44990000,
        "discount": "-27%",
        "rating": 4.7,
        "sold": 430,
        "stock": 25,
        "total_stock": 60,
        "exclusive": "Flagship",
        "shop_name": "Samsung Official Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800",
        "angles": [
            {"label": "Màn hình mở rộng gập", "url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "samsung",
        "title": "Màn Hình Gaming Samsung Odyssey OLED G9 49 inch Cong 240Hz",
        "description": "Màn hình chơi game siêu rộng tỉ lệ 32:9 cong 1800R, tấm nền QD-OLED độ phân giải Dual QHD sắc nét, tần số quét 240Hz và tốc độ phản hồi siêu tốc 0.03ms.",
        "price": 31990000,
        "original_price": 39990000,
        "discount": "-20%",
        "rating": 4.9,
        "sold": 95,
        "stock": 15,
        "total_stock": 30,
        "exclusive": "Gaming Pro",
        "shop_name": "Samsung Official Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800",
        "angles": [
            {"label": "Góc nhìn toàn cảnh màn cong 49 inch", "url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "sony",
        "title": "Tai Nghe Chống Ồn Không Dây Sony WH-1000XM5 Black",
        "description": "Chuẩn mực tai nghe chống ồn hàng đầu thế giới với bộ xử lý kép V1 và QN1, màng loa 30mm tinh chỉnh âm thanh Hi-Res Audio, thời lượng pin 30 giờ liên tục.",
        "price": 6990000,
        "original_price": 8990000,
        "discount": "-22%",
        "rating": 4.9,
        "sold": 780,
        "stock": 70,
        "total_stock": 150,
        "exclusive": "Best Audio",
        "shop_name": "Sony Center Vietnam",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800",
        "angles": [
            {"label": "Toàn cảnh chụp tai màu đen", "url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "sony",
        "title": "Máy Chơi Game Sony PlayStation 5 Slim 1TB Chính Hãng",
        "description": "Máy chơi game console PS5 thế hệ mới nhỏ gọn hơn 30%, ổ cứng SSD tốc độ cao 1TB, đồ họa ray-tracing 4K 120fps sống động và tay cầm rung phản hồi xúc giác DualSense.",
        "price": 13290000,
        "original_price": 14990000,
        "discount": "-11%",
        "rating": 5.0,
        "sold": 1450,
        "stock": 55,
        "total_stock": 100,
        "exclusive": "Gaming Beast",
        "shop_name": "GearVN Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800",
        "angles": [
            {"label": "Thân máy PS5 và tay cầm DualSense", "url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "sony",
        "title": "Máy Ảnh Mirrorless Sony Alpha A7 IV Body Chính Hãng",
        "description": "Máy ảnh full-frame chuyên nghiệp cảm biến Exmor R CMOS 33MP, quay phim chuẩn 4K 60p 10-bit 4:2:2, hệ thống lấy nét tự động thời gian thực theo mắt người và động vật.",
        "price": 53990000,
        "original_price": 59990000,
        "discount": "-10%",
        "rating": 4.9,
        "sold": 210,
        "stock": 18,
        "total_stock": 40,
        "exclusive": "Pro Camera",
        "shop_name": "Sony Center Vietnam",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800",
        "angles": [
            {"label": "Thân máy mặt trước", "url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "xiaomi",
        "title": "Điện Thoại Xiaomi 14 5G 12GB 256GB Ống Kính Leica Summilux",
        "description": "Thiết kế nhỏ gọn vừa tay cầm, ống kính quang học Leica Summilux đỉnh cao, chip Snapdragon 8 Gen 3 siêu mạnh và hệ điều hành Xiaomi HyperOS tối ưu mượt mà.",
        "price": 17990000,
        "original_price": 22990000,
        "discount": "-22%",
        "rating": 4.8,
        "sold": 620,
        "stock": 65,
        "total_stock": 120,
        "exclusive": "Leica Camera",
        "shop_name": "Trungshop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800",
        "angles": [
            {"label": "Mặt lưng cụm camera Leica", "url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800"},
        ],
    },
    {
        "category_code": "tech",
        "brand_code": "xiaomi",
        "title": "Robot Hút Bụi Lau Nhà Xiaomi Dreame L10s Ultra Tự Giặt Giẻ Sấy Khô",
        "description": "Trạm sạc tự động thông minh tự làm sạch giẻ lau và sấy khô bằng khí nóng, lực hút 5300Pa mạnh mẽ, định hướng laser 3D tránh chướng ngại vật chính xác bằng AI.",
        "price": 14490000,
        "original_price": 19990000,
        "discount": "-28%",
        "rating": 4.8,
        "sold": 530,
        "stock": 40,
        "total_stock": 80,
        "exclusive": "Smart Home",
        "shop_name": "Trungshop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        "angles": [
            {"label": "Robot và trạm hút tự động", "url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800"},
        ],
    },

    # --------------------------------------------------------------------------
    # 2. THỜI TRANG NAM NỮ (fashion) - 10 SẢN PHẨM
    # --------------------------------------------------------------------------
    {
        "category_code": "fashion",
        "brand_code": "aristino",
        "title": "Bộ Suit Nam Công Sở May Đo Thủ Công Aristino Italian Wool",
        "description": "Bộ vest nam cao cấp dệt từ 100% sợi len lông cừu tự nhiên nhập khẩu từ Ý, form may đo Regular Fit tôn dáng vẻ sang trọng, lịch lãm cho quý ông công sở.",
        "price": 4850000,
        "original_price": 5990000,
        "discount": "-19%",
        "rating": 4.9,
        "sold": 320,
        "stock": 35,
        "total_stock": 70,
        "exclusive": "Handmade",
        "shop_name": "Aristino Tailor",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800",
        "angles": [
            {"label": "Mặt trước bộ Suit cao cấp", "url": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800"},
            {"label": "Cận ve áo và khuy sừng may đo", "url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "aristino",
        "title": "Áo Blazer Nam Phong Cách Hàn Quốc Aristino Form Slimfit",
        "description": "Chất vải tuyết mưa nhập khẩu mềm mịn, giữ nếp phẳng phiu không nhăn nhàu, thiết kế ve áo thanh thoát hiện đại, dễ dàng phối cùng sơ mi hoặc áo thun cổ tròn.",
        "price": 1850000,
        "original_price": 2450000,
        "discount": "-24%",
        "rating": 4.8,
        "sold": 650,
        "stock": 80,
        "total_stock": 150,
        "exclusive": "Smart Casual",
        "shop_name": "Aristino Tailor",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800",
        "angles": [
            {"label": "Mặt trước áo Blazer", "url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "aristino",
        "title": "Áo Sơ Mi Nam Sợi Tre Bamboo Kháng Khuẩn Aristino Dài Tay",
        "description": "Sợi tre Bamboo tự nhiên có đặc tính kháng khuẩn tự nhiên, hút ẩm tốt và thông thoáng gấp đôi cotton thông thường, giữ bề mặt vải luôn mát lạnh ngày hè.",
        "price": 750000,
        "original_price": 950000,
        "discount": "-21%",
        "rating": 4.8,
        "sold": 1900,
        "stock": 200,
        "total_stock": 400,
        "exclusive": "Eco Fashion",
        "shop_name": "Aristino Tailor",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800",
        "angles": [
            {"label": "Mặt trước áo sơ mi", "url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "aristino",
        "title": "Quần Tây Nam Cao Cấp Co Giãn 4 Chiều Aristino Màu Xanh Navy",
        "description": "Form quần đứng dáng thanh lịch, cạp tăng đơ thông minh ôm vừa vặn vòng eo, chất vải Poly pha Rayon co giãn 4 chiều cho cảm giác vận động cực kỳ thoải mái.",
        "price": 850000,
        "original_price": 1100000,
        "discount": "-23%",
        "rating": 4.8,
        "sold": 1400,
        "stock": 150,
        "total_stock": 300,
        "exclusive": "Office Style",
        "shop_name": "Aristino Tailor",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800",
        "angles": [
            {"label": "Dáng quần đứng form", "url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "owen",
        "title": "Áo Polo Nam Dệt Tổ Ong Thoáng Khí Owen Khử Mùi Hiệu Quả",
        "description": "Chất liệu dệt cấu trúc tổ ong tổ yến thoáng khí vượt trội, xử lý công nghệ Ion Bạc kháng khuẩn khử mùi mồ hôi tối ưu, cổ áo dệt bo dầy dặn không bai dão.",
        "price": 480000,
        "original_price": 650000,
        "discount": "-26%",
        "rating": 4.7,
        "sold": 3100,
        "stock": 300,
        "total_stock": 500,
        "exclusive": "Bán Chạy",
        "shop_name": "Dung36shop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800",
        "angles": [
            {"label": "Mặt trước áo Polo", "url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "owen",
        "title": "Áo Khoác Phao Nam Siêu Nhẹ Siêu Ấm Lông Vũ Owen",
        "description": "Lớp lót 90% lông vũ tự nhiên cao cấp, trọng lượng siêu nhẹ chỉ 250 gram, vải ngoài chống thấm nước nhẹ và cản gió lạnh tối đa trong những ngày đông giá rét.",
        "price": 1150000,
        "original_price": 1550000,
        "discount": "-26%",
        "rating": 4.8,
        "sold": 780,
        "stock": 90,
        "total_stock": 180,
        "exclusive": "Mùa Đông",
        "shop_name": "Dung36shop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800",
        "angles": [
            {"label": "Thân áo phao ấm áp", "url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "owen",
        "title": "Quần Kaki Nam Dáng Regular Thoải Mái Owen Màu Be Sáng",
        "description": "Vải cotton kaki dày dặn bề mặt mịn, được wash enzyme mềm mại giữ màu sắc bền lâu theo thời gian, thiết kế túi xéo sâu tiện dụng để ví và điện thoại.",
        "price": 520000,
        "original_price": 690000,
        "discount": "-25%",
        "rating": 4.7,
        "sold": 1650,
        "stock": 180,
        "total_stock": 350,
        "exclusive": "Casual Style",
        "shop_name": "Dung36shop",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800",
        "angles": [
            {"label": "Quần kaki be sáng", "url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "owen",
        "title": "Áo Len Cổ Tròn Nam Sợi Cashmere Dệt Mịn Owen",
        "description": "Áo len dệt từ sợi cashmere pha len merino mềm mượt, giữ ấm hiệu quả mà không gây ngứa ngáy, màu sắc trung tính trang nhã phù hợp mọi độ tuổi.",
        "price": 680000,
        "original_price": 890000,
        "discount": "-24%",
        "rating": 4.8,
        "sold": 820,
        "stock": 110,
        "total_stock": 200,
        "exclusive": "Mới Ra Mắt",
        "shop_name": "Dung36shop",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800",
        "angles": [
            {"label": "Áo len cổ tròn", "url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "gucci",
        "title": "Thắt Lưng Da Bò Nam Mặt Khóa Kim Loại Gucci GG Marmont",
        "description": "Thắt lưng da bê thượng hạng dập vân mềm bóng mịn, mặt khóa Double G mạ vàng cổ điển biểu tượng thời trang cao cấp từ nhà mốt nước Ý.",
        "price": 9800000,
        "original_price": 11500000,
        "discount": "-15%",
        "rating": 5.0,
        "sold": 115,
        "stock": 25,
        "total_stock": 50,
        "exclusive": "Luxury",
        "shop_name": "Luxury Goods VN",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=800",
        "angles": [
            {"label": "Mặt khóa GG Marmont", "url": "https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=800"},
        ],
    },
    {
        "category_code": "fashion",
        "brand_code": "gucci",
        "title": "Khăn Lụa Tơ Tằm Họa Tiết Hoa Cổ Điển Gucci Flora Silk Scarf",
        "description": "Chiếc khăn lụa 100% tơ tằm tự nhiên được may viền tay thủ công, in họa tiết vườn hoa Flora kinh điển tạo nên nét đẹp quý phái và kiêu sa.",
        "price": 11200000,
        "original_price": 13000000,
        "discount": "-14%",
        "rating": 4.9,
        "sold": 80,
        "stock": 15,
        "total_stock": 30,
        "exclusive": "Luxury",
        "shop_name": "Luxury Goods VN",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=800",
        "angles": [
            {"label": "Họa tiết khăn lụa Flora", "url": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=800"},
        ],
    },

    # --------------------------------------------------------------------------
    # 3. ĐỒNG HỒ & TRANG SỨC (watch) - 10 SẢN PHẨM
    # --------------------------------------------------------------------------
    {
        "category_code": "watch",
        "brand_code": "rolex",
        "title": "Đồng Hồ Cơ Rolex Submariner Date Mặt Số Đen Thép Oystersteel",
        "description": "Biểu tượng đồng hồ lặn biển chuyên nghiệp với vành bezel Cerachrom xoay một chiều gốm đen chống xước, bộ máy Calibre 3235 độ chính xác Chronometer tối cao.",
        "price": 285000000,
        "original_price": 310000000,
        "discount": "-8%",
        "rating": 5.0,
        "sold": 42,
        "stock": 5,
        "total_stock": 10,
        "exclusive": "Luxury Diver",
        "shop_name": "Luxury Watch Vietnam",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800",
        "angles": [
            {"label": "Mặt số và vành xoay Cerachrom", "url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "rolex",
        "title": "Đồng Hồ Rolex Datejust 36 Vành Khía Vàng Trắng Cọc Số Kim Cương",
        "description": "Tuyệt tác kinh điển với mặt số xà cừ óng ánh đính 10 viên kim cương tinh tuyển, dây đeo Jubilee 5 mối nối mềm mại ôm trọn cổ tay quý phái.",
        "price": 340000000,
        "original_price": 375000000,
        "discount": "-9%",
        "rating": 5.0,
        "sold": 28,
        "stock": 4,
        "total_stock": 8,
        "exclusive": "Timeless",
        "shop_name": "Luxury Watch Vietnam",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1547996160-71dfabb1a7b1?w=800",
        "angles": [
            {"label": "Mặt số xà cừ đính kim cương", "url": "https://images.unsplash.com/photo-1547996160-71dfabb1a7b1?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "rolex",
        "title": "Đồng Hồ Nam Rolex Cosmograph Daytona Mặt Trắng Dây Oyster",
        "description": "Chiếc đồng hồ bấm giờ tốc độ thể thao danh giá bậc nhất thế giới, trang bị bộ máy Calibre 4131 tích hợp thang đo tốc độ Tachymeter chính xác tuyệt đối.",
        "price": 460000000,
        "original_price": 500000000,
        "discount": "-8%",
        "rating": 5.0,
        "sold": 18,
        "stock": 3,
        "total_stock": 5,
        "exclusive": "Masterpiece",
        "shop_name": "Luxury Watch Vietnam",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800",
        "angles": [
            {"label": "Mặt số Chronograph 3 ô phụ", "url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "apple",
        "title": "Đồng Hồ Thông Minh Apple Watch Ultra 2 GPS + Cellular 49mm Titanium",
        "description": "Dành cho vận động viên và nhà thám hiểm với vỏ titan cấp 4 nhẹ bền chống ăn mòn, nút tác vụ Action Button tùy biến, độ sáng màn hình lên tới 3000 nits.",
        "price": 19990000,
        "original_price": 21990000,
        "discount": "-9%",
        "rating": 4.9,
        "sold": 620,
        "stock": 60,
        "total_stock": 100,
        "exclusive": "Rugged Sport",
        "shop_name": "Apple Flagship Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=800",
        "angles": [
            {"label": "Vỏ Titan 49mm góc cạnh", "url": "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "apple",
        "title": "Đồng Hồ Thông Minh Apple Watch Series 9 GPS 45mm Nhôm Midnight",
        "description": "Chip Apple S9 SiP mạnh mẽ với tính năng chạm hai lần ngón tay Double Tap kỳ diệu, cảm biến đo nồng độ oxy trong máu SpO2 và điện tâm đồ ECG chuẩn y tế.",
        "price": 9690000,
        "original_price": 11290000,
        "discount": "-14%",
        "rating": 4.9,
        "sold": 1350,
        "stock": 90,
        "total_stock": 180,
        "exclusive": "Bán Chạy",
        "shop_name": "Apple Flagship Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800",
        "angles": [
            {"label": "Màn hình cong viền siêu mỏng", "url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "samsung",
        "title": "Đồng Hồ Samsung Galaxy Watch 6 Classic 47mm Viền Xoay Vật Lý",
        "description": "Trở lại với vòng xoay bezel vật lý đặc trưng, mặt kính Sapphire chống trầy xước, tính năng phân tích thành phần cơ thể BIA và theo dõi giấc ngủ chuyên sâu.",
        "price": 7490000,
        "original_price": 9490000,
        "discount": "-21%",
        "rating": 4.8,
        "sold": 580,
        "stock": 70,
        "total_stock": 120,
        "exclusive": "Classic Smart",
        "shop_name": "Samsung Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800",
        "angles": [
            {"label": "Mặt đồng hồ và viền xoay", "url": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "casio",
        "title": "Đồng Hồ Thể Thao Nam Casio G-Shock GA-2100-1A1 Bát Giác Carbon",
        "description": "Dòng Casioak mỏng nhẹ kỷ lục chỉ 11.8mm với cấu trúc bảo vệ lõi carbon siêu bền bỉ, chống sốc và chống nước ở độ sâu 200M chịu mọi va đập khắc nghiệt.",
        "price": 2890000,
        "original_price": 3650000,
        "discount": "-21%",
        "rating": 4.9,
        "sold": 2900,
        "stock": 150,
        "total_stock": 300,
        "exclusive": "Tough Solar",
        "shop_name": "Casio Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800",
        "angles": [
            {"label": "Mặt bát giác đen toàn bộ All-black", "url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "casio",
        "title": "Đồng Hồ Nam Casio Edifice Chronograph Kim Loại Chống Nước 100M",
        "description": "Lấy cảm hứng từ xe đua thể thao tốc độ cao với 3 mặt số phụ bấm giờ chính xác, vỏ và dây kim loại thép không gỉ sáng bóng đẳng cấp.",
        "price": 3450000,
        "original_price": 4200000,
        "discount": "-18%",
        "rating": 4.8,
        "sold": 1200,
        "stock": 110,
        "total_stock": 200,
        "exclusive": "Chronograph",
        "shop_name": "Casio Official Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?w=800",
        "angles": [
            {"label": "Mặt đồng hồ kim loại thể thao", "url": "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "casio",
        "title": "Đồng Hồ Điện Tử Casio Vintage Mạ Vàng Cổ Điển A168WG-9W",
        "description": "Mẫu đồng hồ retro huyền thoại làm mưa làm gió nhiều thập kỷ qua, đèn nền phát quang điện quang học tử ngoại tử tế, tính năng bấm giờ và báo thức tiện dụng.",
        "price": 1350000,
        "original_price": 1700000,
        "discount": "-21%",
        "rating": 4.9,
        "sold": 3400,
        "stock": 220,
        "total_stock": 400,
        "exclusive": "Vintage Icon",
        "shop_name": "Casio Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800",
        "angles": [
            {"label": "Thân vỏ mạ vàng cổ điển", "url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800"},
        ],
    },
    {
        "category_code": "watch",
        "brand_code": "casio",
        "title": "Đồng Hồ Nữ Casio Sheen Đính Đá Swarovski Sang Trọng",
        "description": "Vẻ đẹp nữ tính và quý phái với viền đính đá pha lê Swarovski nhập khẩu Áo lấp lánh, mặt kính sapphire chống xước tuyệt đối và khả năng chống nước sinh hoạt.",
        "price": 3890000,
        "original_price": 4600000,
        "discount": "-15%",
        "rating": 4.8,
        "sold": 460,
        "stock": 65,
        "total_stock": 120,
        "exclusive": "Elegant",
        "shop_name": "Casio Official Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1518131672697-613becd4fab5?w=800",
        "angles": [
            {"label": "Mặt đồng hồ đính đá Swarovski", "url": "https://images.unsplash.com/photo-1518131672697-613becd4fab5?w=800"},
        ],
    },

    # --------------------------------------------------------------------------
    # 4. GIÀY DÉP THỜI TRANG (shoes) - 10 SẢN PHẨM
    # --------------------------------------------------------------------------
    {
        "category_code": "shoes",
        "brand_code": "nike",
        "title": "Giày Chạy Bộ Nam Nike Air Zoom Pegasus 40 Êm Ái Đa Năng",
        "description": "Dòng giày chạy biểu tượng với đệm bọt Nike React kết hợp 2 túi khí Zoom Air ở mũi và gót chân, mang lại cảm giác phản hồi lực tràn đầy năng lượng.",
        "price": 2890000,
        "original_price": 3690000,
        "discount": "-22%",
        "rating": 4.9,
        "sold": 1850,
        "stock": 140,
        "total_stock": 250,
        "exclusive": "Pro Runner",
        "shop_name": "Nike Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800",
        "angles": [
            {"label": "Góc nghiêng giày chạy Nike Pegasus", "url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "nike",
        "title": "Giày Thể Thao Nam Nike Air Jordan 1 Low Panda Phối Màu Trắng Đen",
        "description": "Phối màu Panda kinh điển dễ phối đồ nhất mọi thời đại, chất liệu da cao cấp mềm mại với bộ đệm Air-Sole êm nhẹ nâng đỡ từng bước chân đường phố.",
        "price": 3490000,
        "original_price": 4290000,
        "discount": "-19%",
        "rating": 4.9,
        "sold": 2200,
        "stock": 60,
        "total_stock": 120,
        "exclusive": "Streetwear",
        "shop_name": "Nike Official Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800",
        "angles": [
            {"label": "Góc nhìn đôi giày Jordan 1 Low", "url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "nike",
        "title": "Giày Thi Đấu Marathon Nike ZoomX Vaporfly Next% 3 Siêu Nhẹ",
        "description": "Vũ khí tốc độ phá vỡ mọi kỷ lục marathon thế giới, bọt ZoomX hoàn trả năng lượng tối ưu kết hợp tấm sợi carbon toàn bàn chân Flyplate tạo lực đẩy bứt phá.",
        "price": 5690000,
        "original_price": 6890000,
        "discount": "-17%",
        "rating": 5.0,
        "sold": 410,
        "stock": 35,
        "total_stock": 70,
        "exclusive": "Elite Marathon",
        "shop_name": "Nike Official Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800",
        "angles": [
            {"label": "Đế giày carbon ZoomX", "url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "nike",
        "title": "Giày Đá Bóng Cổ Thấp Nike Mercurial Vapor 15 Academy TF",
        "description": "Bộ đệm Zoom Air chuyên biệt cho sân bóng đá cỏ nhân tạo mang lại cảm giác bật nhún linh hoạt, vân cấu trúc bám bóng chính xác ở tốc độ bứt phá cao.",
        "price": 1950000,
        "original_price": 2390000,
        "discount": "-18%",
        "rating": 4.8,
        "sold": 1560,
        "stock": 120,
        "total_stock": 200,
        "exclusive": "Sân Cỏ Nhân Tạo",
        "shop_name": "Nike Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=800",
        "angles": [
            {"label": "Đinh dăm TF bám sân", "url": "https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "adidas",
        "title": "Giày Chạy Bộ Nam Adidas Ultraboost Light 23 Đế Đệm Boost Siêu Êm",
        "description": "Thế hệ Boost nhẹ hơn 30% đem lại trải nghiệm hoàn trả năng lượng phi thường, thân giày dệt sợi Primeknit ôm khít thoáng khí giảm áp lực bàn chân.",
        "price": 3250000,
        "original_price": 4500000,
        "discount": "-28%",
        "rating": 4.9,
        "sold": 1680,
        "stock": 95,
        "total_stock": 180,
        "exclusive": "Boost Tech",
        "shop_name": "Adidas Originals Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800",
        "angles": [
            {"label": "Đế đệm Ultraboost Light", "url": "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "adidas",
        "title": "Giày Thể Thao Cổ Điển Adidas Samba OG Da Trắng Mũi Da Lộn",
        "description": "Đôi giày sneaker retro tạo cơn sốt toàn cầu với chất da tự nhiên cao cấp, mũi giày chữ T da lộn tương phản và đế cao su gum bám đường đặc trưng.",
        "price": 2650000,
        "original_price": 3100000,
        "discount": "-15%",
        "rating": 4.9,
        "sold": 3300,
        "stock": 80,
        "total_stock": 150,
        "exclusive": "Hot Trend",
        "shop_name": "Adidas Originals Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?w=800",
        "angles": [
            {"label": "Mặt trước mũi da lộn Samba", "url": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "adidas",
        "title": "Giày Sneaker Thời Trang Adidas Superstar Mũi Vỏ Sò Cổ Điển",
        "description": "Biểu tượng văn hóa đường phố từ những năm 1970 với chi tiết mũi giày vỏ sò cao su shell toe bảo vệ ngón chân, 3 sọc răng cưa nguyên bản nổi bật.",
        "price": 1990000,
        "original_price": 2500000,
        "discount": "-20%",
        "rating": 4.8,
        "sold": 2800,
        "stock": 130,
        "total_stock": 250,
        "exclusive": "Iconic",
        "shop_name": "Adidas Originals Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=800",
        "angles": [
            {"label": "Mũi vỏ sò Shell Toe", "url": "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "adidas",
        "title": "Giày Bóng Rổ Cổ Thấp Adidas Forum Low Retro Trắng Xanh",
        "description": "Thiết kế quai dán mắt cá chân cổ điển đậm chất bóng rổ thập niên 80, thân giày bằng da thật êm ái kết hợp đế ngoài cupsole cao su bền bỉ.",
        "price": 2150000,
        "original_price": 2800000,
        "discount": "-23%",
        "rating": 4.7,
        "sold": 980,
        "stock": 75,
        "total_stock": 140,
        "exclusive": "Retro Style",
        "shop_name": "Adidas Originals Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800",
        "angles": [
            {"label": "Quai dán mắt cá chân Forum Low", "url": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "puma",
        "title": "Giày Thể Thao Sneaker Puma Suede Classic Phối Da Lộn Cao Cấp",
        "description": "Mẫu giày da lộn kinh điển của Puma với đường dải Formstrip uốn lượn hai bên hông, đế cao su nguyên khối chống trơn trượt hoàn hảo trên mọi bề mặt.",
        "price": 1750000,
        "original_price": 2200000,
        "discount": "-20%",
        "rating": 4.8,
        "sold": 1120,
        "stock": 100,
        "total_stock": 200,
        "exclusive": "Classic Suede",
        "shop_name": "GearVN Official Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800",
        "angles": [
            {"label": "Chất liệu da lộn mềm mịn", "url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800"},
        ],
    },
    {
        "category_code": "shoes",
        "brand_code": "puma",
        "title": "Giày Chạy Bộ Đệm Nitro Puma Velocity Nitro 2 Thoáng Khí",
        "description": "Trang bị lớp đệm Nitro Foam bơm khí nitơ tiên tiến đem lại độ đàn hồi vượt trội trong trọng lượng siêu nhẹ, đế ngoài Pumagrip bám đường trên mọi thời tiết.",
        "price": 2390000,
        "original_price": 3190000,
        "discount": "-25%",
        "rating": 4.8,
        "sold": 730,
        "stock": 85,
        "total_stock": 160,
        "exclusive": "Nitro Foam",
        "shop_name": "GearVN Official Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800",
        "angles": [
            {"label": "Góc nghiêng đế Nitro Foam", "url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"},
        ],
    },

    # --------------------------------------------------------------------------
    # 5. MỸ PHẨM & CHĂM SÓC SẮC ĐẸP (beauty) - 8 SẢN PHẨM
    # --------------------------------------------------------------------------
    {
        "category_code": "beauty",
        "brand_code": "chanel",
        "title": "Nước Hoa Nam Chanel Bleu de Chanel Eau de Parfum 100ml",
        "description": "Hương thơm gỗ thơm nồng nàn bí ẩn pha lẫn hổ phách và gỗ tuyết tùng, biểu trưng cho sự tự do phóng khoáng và lịch lãm của người đàn ông bản lĩnh.",
        "price": 3950000,
        "original_price": 4500000,
        "discount": "-12%",
        "rating": 5.0,
        "sold": 950,
        "stock": 50,
        "total_stock": 100,
        "exclusive": "Best Perfume",
        "shop_name": "Luxury Perfume Store",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=800",
        "angles": [
            {"label": "Chai nước hoa xanh đen nguyên khối", "url": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=800"},
        ],
    },
    {
        "category_code": "beauty",
        "brand_code": "chanel",
        "title": "Son Thỏi Lì Cao Cấp Chanel Rouge Allure L'Extrait 854 Rouge Puissant",
        "description": "Dòng son môi thượng hạng kết hợp sắc đỏ quyền lực rực rỡ với dưỡng chất từ hoa mơ và sáp thực vật nuôi dưỡng bờ môi căng mọng suốt cả ngày dài.",
        "price": 1650000,
        "original_price": 1900000,
        "discount": "-13%",
        "rating": 4.9,
        "sold": 1420,
        "stock": 85,
        "total_stock": 150,
        "exclusive": "High-end Lip",
        "shop_name": "Luxury Perfume Store",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800",
        "angles": [
            {"label": "Vỏ son bấm vàng đen sang trọng", "url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800"},
        ],
    },
    {
        "category_code": "beauty",
        "brand_code": "gucci",
        "title": "Nước Hoa Nữ Gucci Bloom Eau de Parfum Hương Hoa Cỏ Ngọt Ngào 100ml",
        "description": "Khu vườn hoa ngát hương phong phú với hoa huệ trắng Ấn Độ tự nhiên, hoa nhài Sambac và hoa trang leo Rangoon Creeper quý hiếm ngọt ngào quyến rũ.",
        "price": 3450000,
        "original_price": 4100000,
        "discount": "-16%",
        "rating": 4.9,
        "sold": 870,
        "stock": 45,
        "total_stock": 90,
        "exclusive": "Floral Notes",
        "shop_name": "Luxury Goods VN",
        "is_flash_sale": 0,
        "image_url": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=800",
        "angles": [
            {"label": "Chai gốm sứ hồng cổ điển", "url": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=800"},
        ],
    },
    {
        "category_code": "beauty",
        "brand_code": "gucci",
        "title": "Son Dưỡng Có Màu Gucci Rouge à Lèvres Satin Lipstick 505 Janet Rust",
        "description": "Tông màu đỏ đất quyến rũ với kết cấu satin mềm mướt giàu độ ẩm, vỏ son mạ vàng chạm khắc họa tiết hoa văn phong cách Art Deco tinh xảo.",
        "price": 1150000,
        "original_price": 1350000,
        "discount": "-15%",
        "rating": 4.8,
        "sold": 1180,
        "stock": 70,
        "total_stock": 130,
        "exclusive": "Best Seller",
        "shop_name": "Luxury Goods VN",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800",
        "angles": [
            {"label": "Vỏ son hoa văn Art Deco", "url": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800"},
        ],
    },
    {
        "category_code": "beauty",
        "brand_code": "loreal",
        "title": "Serum Dưỡng Sáng Giảm Thâm Nám L'Oreal Paris Glycolic-Bright 1.0% Glycolic Acid 30ml",
        "description": "Công thức đột phá với 1.0% Glycolic Acid nồng độ tối ưu giúp tẩy tế bào chết nhẹ nhàng, làm mờ vết thâm nám sau 14 ngày và mang lại làn da trắng sáng đều màu.",
        "price": 349000,
        "original_price": 449000,
        "discount": "-22%",
        "rating": 4.8,
        "sold": 3500,
        "stock": 350,
        "total_stock": 600,
        "exclusive": "Dưỡng Sáng Da",
        "shop_name": "Dung36shop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800",
        "angles": [
            {"label": "Chai serum giọt tinh chất", "url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800"},
        ],
    },
]

SAMPLE_PRODUCTS.extend([
    {
        "category_code": "beauty",
        "brand_code": "loreal",
        "title": "Nước Tẩy Trang Tươi Mát Da L'Oreal Paris Micellar Water 400ml",
        "description": "Công nghệ phân tử Micellar hút sạch bụi bẩn, dầu thừa và cặn trang điểm sâu trong lỗ chân lông mà không gây khô rát căng kít cho làn da.",
        "price": 179000,
        "original_price": 239000,
        "discount": "-25%",
        "rating": 4.9,
        "sold": 3500,
        "stock": 500,
        "total_stock": 800,
        "exclusive": "Bán Chạy",
        "shop_name": "Dung36shop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800",
        "angles": [
            {"label": "Chai nước tẩy trang 400ml", "url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800"},
        ],
    },
    {
        "category_code": "beauty",
        "brand_code": "innisfree",
        "title": "Serum Trà Xanh Dưỡng Ẩm Phục Hồi Da Innisfree Green Tea Seed Hyaluronic Serum 80ml",
        "description": "Chiết xuất tinh chất mầm trà xanh hữu cơ đảo Jeju kết hợp phức hợp 5 loại Hyaluronic Acid cấp ẩm sâu đa tầng, củng cố hàng rào bảo vệ da ẩm mượt căng bóng.",
        "price": 460000,
        "original_price": 620000,
        "discount": "-26%",
        "rating": 4.8,
        "sold": 2700,
        "stock": 240,
        "total_stock": 450,
        "exclusive": "Green Tea Tech",
        "shop_name": "Dung36shop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1608248597359-009138072049?w=800",
        "angles": [
            {"label": "Chai serum trà xanh Jeju", "url": "https://images.unsplash.com/photo-1608248597359-009138072049?w=800"},
        ],
    },
    {
        "category_code": "beauty",
        "brand_code": "innisfree",
        "title": "Kem Chống Nắng Kiềm Dầu Nâng Tông Innisfree Tone Up No Sebum Sunscreen EX SPF50+ 50ml",
        "description": "Khả năng kiềm dầu vượt trội lên tới 24 giờ với bột khoáng tự nhiên, màng lọc chống nắng vật lý bảo vệ da khỏi tia UVA/UVB và nâng tông trắng hồng tự nhiên.",
        "price": 260000,
        "original_price": 350000,
        "discount": "-26%",
        "rating": 4.8,
        "sold": 3200,
        "stock": 310,
        "total_stock": 500,
        "exclusive": "Kiềm Dầu 24h",
        "shop_name": "Dung36shop",
        "is_flash_sale": 1,
        "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800",
        "angles": [
            {"label": "Tuýp kem chống nắng nâng tông", "url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800"},
        ],
    },
])


# ==============================================================================
# HÀM THỰC THI SEED VÀO DATABASE
# ==============================================================================
def ensure_categories_and_brands(cursor) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Đảm bảo các danh mục và thương hiệu cần thiết đều đã tồn tại trong DB."""
    # 1. Đảm bảo Categories
    for cat in CATEGORIES_SEED:
        cursor.execute(
            """
            INSERT INTO categories (code, name, description)
            VALUES (?, ?, ?)
            ON DUPLICATE KEY UPDATE name=VALUES(name), description=VALUES(description);
            """,
            (cat["code"], cat["name"], cat["description"]),
        )

    # 2. Đảm bảo Brands
    for br in BRANDS_SEED:
        cursor.execute(
            """
            INSERT INTO brands (code, name, origin, logo_url)
            VALUES (?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE name=VALUES(name), origin=VALUES(origin), logo_url=VALUES(logo_url);
            """,
            (br["code"], br["name"], br["origin"], br["logo_url"]),
        )

    # Lấy map code -> id
    cursor.execute("SELECT id, code FROM categories;")
    category_map = {row["code"]: row["id"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, code FROM brands;")
    brand_map = {row["code"]: row["id"] for row in cursor.fetchall()}

    return category_map, brand_map


def seed_50_products(verbose: bool = True) -> Dict[str, Any]:
    """Thêm hoặc cập nhật 50 sản phẩm mẫu vào MySQL database.

    Trả về dictionary thống kê kết quả.
    """
    if init_db:
        try:
            init_db(seed=False)
        except Exception:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        category_map, brand_map = ensure_categories_and_brands(cursor)

        # Kiểm tra các cột trong bảng products
        cursor.execute("SHOW COLUMNS FROM products;")
        cols = {row["Field"].lower() for row in cursor.fetchall()}
        has_description = "description" in cols

        # Kiểm tra bảng product_images
        cursor.execute("SHOW TABLES LIKE 'product_images';")
        has_product_images = cursor.fetchone() is not None

        created_count = 0
        updated_count = 0
        category_stats: Dict[str, int] = {}
        brand_stats: Dict[str, int] = {}

        for p in SAMPLE_PRODUCTS:
            cat_code = p["category_code"]
            br_code = p["brand_code"]
            cat_id = category_map.get(cat_code)
            br_id = brand_map.get(br_code)

            # Lấy tên hiển thị của brand
            brand_name = next((b["name"] for b in BRANDS_SEED if b["code"] == br_code), br_code.capitalize())

            # Chuẩn bị images_json và angles_json
            images_list = [p["image_url"]]
            if p.get("angles"):
                images_list.extend([a["url"] for a in p["angles"] if a["url"] not in images_list])
            images_json = json.dumps(images_list, ensure_ascii=False)
            angles_json = json.dumps(p.get("angles", []), ensure_ascii=False)

            category_stats[cat_code] = category_stats.get(cat_code, 0) + 1
            brand_stats[brand_name] = brand_stats.get(brand_name, 0) + 1

            # Kiểm tra sản phẩm đã tồn tại theo title chưa
            cursor.execute("SELECT id FROM products WHERE title = ?;", (p["title"],))
            existing = cursor.fetchone()

            if existing:
                prod_id = existing["id"]
                if has_description:
                    cursor.execute(
                        """
                        UPDATE products
                        SET category = ?, category_id = ?, brand = ?, brand_id = ?,
                            description = ?, price = ?, original_price = ?, discount = ?,
                            rating = ?, sold = ?, stock = ?, total_stock = ?,
                            images_json = ?, angles_json = ?, exclusive = ?,
                            shop_name = ?, is_flash_sale = ?, status = 'approved'
                        WHERE id = ?;
                        """,
                        (
                            cat_code, cat_id, brand_name, br_id,
                            p["description"], p["price"], p["original_price"], p["discount"],
                            p["rating"], p["sold"], p["stock"], p["total_stock"],
                            images_json, angles_json, p["exclusive"],
                            p["shop_name"], p["is_flash_sale"], prod_id,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE products
                        SET category = ?, category_id = ?, brand = ?, brand_id = ?,
                            price = ?, original_price = ?, discount = ?,
                            rating = ?, sold = ?, stock = ?, total_stock = ?,
                            images_json = ?, angles_json = ?, exclusive = ?,
                            shop_name = ?, is_flash_sale = ?, status = 'approved'
                        WHERE id = ?;
                        """,
                        (
                            cat_code, cat_id, brand_name, br_id,
                            p["price"], p["original_price"], p["discount"],
                            p["rating"], p["sold"], p["stock"], p["total_stock"],
                            images_json, angles_json, p["exclusive"],
                            p["shop_name"], p["is_flash_sale"], prod_id,
                        ),
                    )
                updated_count += 1
            else:
                if has_description:
                    cursor.execute(
                        """
                        INSERT INTO products (
                            category, category_id, brand, brand_id, title, description,
                            price, original_price, discount, rating, sold, stock, total_stock,
                            images_json, angles_json, exclusive, shop_name, is_flash_sale, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved');
                        """,
                        (
                            cat_code, cat_id, brand_name, br_id, p["title"], p["description"],
                            p["price"], p["original_price"], p["discount"], p["rating"], p["sold"],
                            p["stock"], p["total_stock"], images_json, angles_json, p["exclusive"],
                            p["shop_name"], p["is_flash_sale"],
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO products (
                            category, category_id, brand, brand_id, title,
                            price, original_price, discount, rating, sold, stock, total_stock,
                            images_json, angles_json, exclusive, shop_name, is_flash_sale, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved');
                        """,
                        (
                            cat_code, cat_id, brand_name, br_id, p["title"],
                            p["price"], p["original_price"], p["discount"], p["rating"], p["sold"],
                            p["stock"], p["total_stock"], images_json, angles_json, p["exclusive"],
                            p["shop_name"], p["is_flash_sale"],
                        ),
                    )
                cursor.execute("SELECT LAST_INSERT_ID() AS id;")
                row = cursor.fetchone()
                prod_id = row["id"] if row else None
                created_count += 1

            # Seed ảnh vào product_images nếu bảng tồn tại
            if has_product_images and prod_id:
                cursor.execute("DELETE FROM product_images WHERE product_id = ?;", (prod_id,))
                order = 1
                cursor.execute(
                    """
                    INSERT INTO product_images (product_id, image_url, angle_name, is_primary, display_order)
                    VALUES (?, ?, 'Ảnh chính diện', 1, 1);
                    """,
                    (prod_id, p["image_url"]),
                )
                if p.get("angles"):
                    for angle in p["angles"]:
                        if angle["url"] == p["image_url"]:
                            continue
                        order += 1
                        cursor.execute(
                            """
                            INSERT INTO product_images (product_id, image_url, angle_name, is_primary, display_order)
                            VALUES (?, ?, ?, 0, ?);
                            """,
                            (prod_id, angle["url"], angle["label"], order),
                        )

        summary = {
            "total_products": len(SAMPLE_PRODUCTS),
            "created": created_count,
            "updated": updated_count,
            "categories": category_stats,
            "brands": brand_stats,
        }

        if verbose:
            print("=" * 70)
            print("TF17257: KẾT QUẢ SEED 50 SẢN PHẨM MẪU")
            print("=" * 70)
            print(f"Tổng số sản phẩm mẫu : {summary['total_products']}")
            print(f"- Thêm mới          : {summary['created']}")
            print(f"- Cập nhật          : {summary['updated']}")
            print("\nPhân bố theo Danh mục:")
            for code, count in summary["categories"].items():
                print(f"  • {code:<12}: {count} sản phẩm")
            print("\nPhân bố theo Thương hiệu:")
            for bname, count in summary["brands"].items():
                print(f"  • {bname:<15}: {count} sản phẩm")
            print("=" * 70)

        return summary
    finally:
        conn.close()


def generate_sql_file(output_path: str = None) -> str:
    """Tạo file script SQL tương ứng với 50 sản phẩm mẫu."""
    if output_path is None:
        output_path = os.path.join(CURRENT_DIR, "seed_50_products.sql")

    lines = [
        "-- ==============================================================================",
        "-- TF17257: Dữ liệu mẫu 50 sản phẩm thuộc nhiều danh mục, thương hiệu",
        "-- Phục vụ kiểm thử tìm kiếm, lọc theo danh mục/thương hiệu/giá, phân trang và responsive.",
        "-- ==============================================================================",
        "USE `jml_marketplace`;\n",
        "-- 1. CATEGORIES",
        "INSERT INTO `categories` (`code`, `name`, `description`) VALUES",
    ]

    cat_rows = []
    for c in CATEGORIES_SEED:
        desc = c["description"].replace("'", "\\'")
        name = c["name"].replace("'", "\\'")
        cat_rows.append(f"('{c['code']}', '{name}', '{desc}')")
    lines.append(",\n".join(cat_rows))
    lines.append("ON DUPLICATE KEY UPDATE `name`=VALUES(`name`), `description`=VALUES(`description`);\n")

    lines.append("-- 2. BRANDS")
    lines.append("INSERT INTO `brands` (`code`, `name`, `origin`, `logo_url`) VALUES")
    brand_rows = []
    for b in BRANDS_SEED:
        name = b["name"].replace("'", "\\'")
        origin = b["origin"].replace("'", "\\'")
        logo = b["logo_url"].replace("'", "\\'")
        brand_rows.append(f"('{b['code']}', '{name}', '{origin}', '{logo}')")
    lines.append(",\n".join(brand_rows))
    lines.append("ON DUPLICATE KEY UPDATE `name`=VALUES(`name`), `origin`=VALUES(`origin`), `logo_url`=VALUES(`logo_url`);\n")

    lines.append("-- 3. 50 SAMPLE PRODUCTS")
    lines.append("INSERT INTO `products` (")
    lines.append("    `category`, `category_id`, `brand`, `brand_id`, `title`, `description`,")
    lines.append("    `price`, `original_price`, `discount`, `rating`, `sold`, `stock`, `total_stock`,")
    lines.append("    `images_json`, `angles_json`, `exclusive`, `shop_name`, `is_flash_sale`, `status`")
    lines.append(")")
    lines.append("SELECT * FROM (")

    select_rows = []
    for p in SAMPLE_PRODUCTS:
        bname = next((b["name"] for b in BRANDS_SEED if b["code"] == p["brand_code"]), p["brand_code"].capitalize())
        images = [p["image_url"]]
        if p.get("angles"):
            images.extend([a["url"] for a in p["angles"] if a["url"] not in images])
        images_json = json.dumps(images, ensure_ascii=False).replace("'", "''")
        angles_json = json.dumps(p.get("angles", []), ensure_ascii=False).replace("'", "''")
        title = p["title"].replace("'", "''")
        desc = p["description"].replace("'", "''")
        shop = p["shop_name"].replace("'", "''")
        excl = p["exclusive"].replace("'", "''")

        row = (
            f"    SELECT '{p['category_code']}' AS `category`, "
            f"(SELECT `id` FROM `categories` WHERE `code`='{p['category_code']}' LIMIT 1) AS `category_id`, "
            f"'{bname}' AS `brand`, "
            f"(SELECT `id` FROM `brands` WHERE `code`='{p['brand_code']}' LIMIT 1) AS `brand_id`, "
            f"'{title}' AS `title`, '{desc}' AS `description`, "
            f"{p['price']} AS `price`, {p['original_price']} AS `original_price`, '{p['discount']}' AS `discount`, "
            f"{p['rating']} AS `rating`, {p['sold']} AS `sold`, {p['stock']} AS `stock`, {p['total_stock']} AS `total_stock`, "
            f"'{images_json}' AS `images_json`, '{angles_json}' AS `angles_json`, "
            f"'{excl}' AS `exclusive`, '{shop}' AS `shop_name`, {p['is_flash_sale']} AS `is_flash_sale`, 'approved' AS `status`"
        )
        select_rows.append(row)

    lines.append("\n    UNION ALL\n".join(select_rows))
    lines.append(") AS tmp")
    lines.append("ON DUPLICATE KEY UPDATE")
    lines.append("    `category`=VALUES(`category`), `category_id`=VALUES(`category_id`),")
    lines.append("    `brand`=VALUES(`brand`), `brand_id`=VALUES(`brand_id`),")
    lines.append("    `description`=VALUES(`description`), `price`=VALUES(`price`),")
    lines.append("    `original_price`=VALUES(`original_price`), `discount`=VALUES(`discount`),")
    lines.append("    `rating`=VALUES(`rating`), `sold`=VALUES(`sold`),")
    lines.append("    `stock`=VALUES(`stock`), `total_stock`=VALUES(`total_stock`),")
    lines.append("    `images_json`=VALUES(`images_json`), `angles_json`=VALUES(`angles_json`),")
    lines.append("    `exclusive`=VALUES(`exclusive`), `shop_name`=VALUES(`shop_name`),")
    lines.append("    `is_flash_sale`=VALUES(`is_flash_sale`), `status`=VALUES(`status`);\n")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


if __name__ == "__main__":
    generate_sql_file()
    seed_50_products(verbose=True)
