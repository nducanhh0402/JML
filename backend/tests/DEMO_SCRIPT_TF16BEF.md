# Kịch bản Video Demo - TF16BEF

## Thông tin
- Thời lượng đề xuất: 2 phút 20 giây.
- Nền tảng quay: OBS Studio, Loom hoặc Xbox Game Bar.
- Kích thước desktop: 1280×900.
- Kích thước mobile: 390×844.

## Chuẩn bị trước quay
1. Chạy backend tại `http://127.0.0.1:8000`.
2. Chạy frontend tại `http://127.0.0.1:5500` hoặc dùng Vercel Live Demo.
3. Chuẩn bị tài khoản Buyer: `buyer / 123456`.
4. Mở sẵn Swagger `/docs` và terminal chạy test/benchmark.

## Kịch bản

| Thời gian | Hành động màn hình | Nội dung cần nói |
|---|---|---|
| 0:00–0:20 | Mở trang chủ Desktop | Giới thiệu JML Marketplace, Hero Slider, danh mục, Flash Sale và sản phẩm nổi bật/mới nhất. |
| 0:20–0:45 | Chuyển sang Mobile | Chỉ rõ layout 2 cột, banner, dropdown tìm kiếm và menu không bị tràn ngang. |
| 0:45–1:15 | Mở chi tiết sản phẩm | Đổi góc chụp ảnh, mở Lightbox, kiểm tra giá/tồn kho, chọn số lượng và thêm vào giỏ. |
| 1:15–1:45 | Cuộn đánh giá | Lọc theo sao, gửi nhận xét mới, thử gửi trùng để minh chứng cảnh báo 409. |
| 1:45–2:10 | Mở Swagger | Gọi nhanh `GET /api/homepage`, `GET /api/products/{id}` và `GET/POST /api/reviews`. |
| 2:10–2:20 | Terminal | Chạy 1 test/benchmark và kết thúc bằng link repository/PR. |

## Lệnh minh chứng trong terminal

```bash
python -m unittest backend.tests.test_homepage_optimization_tf175bc backend.tests.test_product_detail -v
python -m backend.tests.benchmark_homepage_tf175bc
```

## Sau khi quay

1. Tải video lên YouTube không danh sách, Loom hoặc Google Drive.
2. Thêm link video vào phần Pull Request TF16BEF.
3. Ghi rõ thời lượng, desktop/mobile, API và kết quả kiểm thử trong phần mô tả PR.
