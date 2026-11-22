/**
 * TRANG CHI TIẾT SẢN PHẨM - JML STORE
 * Thư viện ảnh (slider + thumbnails + zoom lightbox), giá, tồn kho, chọn số lượng, thêm vào giỏ.
 */

const urlParams = new URLSearchParams(window.location.search);
const API_BASE_URL =
  urlParams.get("api") ||
  localStorage.getItem("JML_API_BASE_URL") ||
  (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "");

const CART_STORAGE_KEY = "JML_CART_ITEMS";
const FALLBACK_IMG =
  "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80";

const FALLBACK_CATALOG = [
  {
    id: 101,
    category: "audio",
    brand: "Sony",
    title: "Tai Nghe Chống Ồn Cao Cấp Sony WH-1000XM5 Black Edition",
    description:
      "Tai nghe chống ồn không dây Sony WH-1000XM5 sở hữu bộ xử lý V1 & HD QN1 cùng 8 micro cho chất âm Hi-Res Audio LDAC vượt trội và thời lượng pin lên đến 30 giờ.",
    price: 7490000,
    originalPrice: 9490000,
    discount: "-21%",
    rating: 4.9,
    sold: 84,
    stock: 16,
    totalStock: 100,
    images: [
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=800&q=80",
    ],
    angles: ["Chính diện", "Góc nghiêng", "Cận cảnh đệm da", "Thực tế lifestyle"],
    exclusive: "Bán Chạy",
    shopName: "SoundMax Audio",
  },
  {
    id: 102,
    category: "watch",
    brand: "Tissot",
    title: "Đồng Hồ Nam Cơ Tự Động Tissot Le Locle Powermatic 80",
    description:
      "Bộ máy cơ tự động Thụy Sĩ Powermatic 80 trữ cót 80 giờ, kính Sapphire chống trầy và mặt số vân Guilloche sang trọng.",
    price: 13800000,
    originalPrice: 17250000,
    discount: "-20%",
    rating: 5.0,
    sold: 46,
    stock: 4,
    totalStock: 50,
    images: [
      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?auto=format&fit=crop&w=800&q=80",
    ],
    angles: ["Mặt số Guilloche", "Góc nghiêng viền", "Nắp lưng lộ cơ", "Đeo trên cổ tay"],
    exclusive: "Hot Deal",
    shopName: "Luxury Watch Vietnam",
  },
  {
    id: 103,
    category: "audio",
    brand: "Harman Kardon",
    title: "Loa Bluetooth Harman Kardon Aura Studio 4 Hi-End",
    description:
      "Thiết kế vòm trong suốt kèm hiệu ứng ánh sáng Ambient Light 360 độ, âm bass uy lực 130W chuẩn phòng thu.",
    price: 5890000,
    originalPrice: 7500000,
    discount: "-22%",
    rating: 4.8,
    sold: 92,
    stock: 8,
    totalStock: 100,
    images: [
      "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80",
    ],
    angles: ["Vòm Acrylic", "Đèn Ambient LED"],
    exclusive: "Flash",
    shopName: "SoundMax Audio",
  },
  {
    id: 104,
    category: "audio",
    brand: "Apple",
    title: "Tai Nghe AirPods Max Không Gian Chống Ồn Chủ Động",
    description:
      "Driver động thiết kế riêng bởi Apple, âm thanh không gian Spatial Audio và khung thép không gỉ cao cấp.",
    price: 12490000,
    originalPrice: 13990000,
    discount: "-11%",
    rating: 4.8,
    sold: 189,
    stock: 22,
    totalStock: 100,
    images: [
      "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
    ],
    angles: ["Chụp tai vòm lưới", "Khung thép không gỉ"],
    exclusive: "Chính Hãng",
    shopName: "AB Technology Ltd",
  },
];

const STAR_LABELS = {
  1: "1/5 - Rất tệ",
  2: "2/5 - Không hài lòng",
  3: "3/5 - Bình thường",
  4: "4/5 - Hài lòng",
  5: "5/5 - Tuyệt vời",
};

let detailState = {
  product: null,
  images: [],
  angles: [],
  currentImageIndex: 0,
  qty: 1,
  availableStock: 0,
  selectedColor: "Đen Titan",
  selectedVersion: "Bản Tiêu Chuẩn (Fullbox)",
  reviewStar: 5,
  reviewFilterStar: null,
  reviewPage: 1,
};

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatCurrency(amount) {
  const num = Number(amount) || 0;
  return num.toLocaleString("vi-VN") + " ₫";
}

function getCategoryLabel(cat) {
  const map = {
    audio: "Thiết Bị Âm Thanh",
    watch: "Đồng Hồ Cao Cấp",
    fashion: "Thời Trang & Đồ Da",
    tech: "Thiết Bị Số & Công Nghệ",
  };
  return map[cat] || "Sản Phẩm Chính Hãng";
}

function getStockMeta(available) {
  if (available <= 0) {
    return { cls: "stock-out", label: "Hết hàng", inStock: false };
  }
  if (available <= 10) {
    return { cls: "stock-low", label: `Sắp hết hàng (còn ${available})`, inStock: true };
  }
  return { cls: "stock-in", label: `Còn hàng (${available} sẵn có)`, inStock: true };
}

function normalizeProductDetail(raw) {
  const images =
    Array.isArray(raw.images) && raw.images.length > 0
      ? raw.images
      : raw.thumbnail
      ? [raw.thumbnail]
      : raw.image
      ? [raw.image]
      : [FALLBACK_IMG];

  const angles =
    Array.isArray(raw.imageDetails) && raw.imageDetails.length > 0
      ? raw.imageDetails.map((d, i) => d.angle || `Góc chụp ${i + 1}`)
      : Array.isArray(raw.angles) && raw.angles.length > 0
      ? raw.angles
      : images.map((_, i) => `Góc chụp ${i + 1}`);

  const totalStock = Number(raw.totalStock ?? raw.total_stock ?? 100);
  const sold = Number(raw.sold ?? raw.soldCount ?? 0);
  const availableStock =
    raw.stock !== undefined && raw.stock !== null
      ? Math.max(0, Number(raw.stock))
      : Math.max(0, totalStock - sold);

  const price = Number(raw.price) || 0;
  const originalPrice = Math.max(price, Number(raw.originalPrice ?? raw.original_price ?? price) || 0);
  const discountAmount = Math.max(0, originalPrice - price);
  const discount =
    raw.discount ||
    (originalPrice > price ? `-${Math.round((discountAmount / originalPrice) * 100)}%` : "");

  return {
    id: raw.id,
    category: raw.category || "tech",
    categoryName: raw.categoryName || getCategoryLabel(raw.category),
    brand: raw.brand || raw.brandInfo?.name || raw.shopName || "JML Official",
    title: raw.title || "Sản phẩm JML Store",
    description:
      raw.description ||
      `${raw.title || "Sản phẩm"} chính hãng phân phối bởi ${raw.shopName || "JML Store"}, hỗ trợ bảo hành và đổi trả 30 ngày.`,
    price,
    originalPrice,
    discount,
    discountAmount,
    rating: Number(raw.rating ?? 5.0).toFixed(1),
    sold,
    totalStock,
    availableStock,
    images,
    angles,
    exclusive: raw.exclusive || "Chính Hãng",
    shopName: raw.shopName || raw.shop_name || "JML Official Store",
    relatedProducts: Array.isArray(raw.relatedProducts) ? raw.relatedProducts : [],
  };
}

function updateHeaderCartBadge() {
  try {
    const cart = JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || "[]");
    const count = cart.reduce((sum, it) => sum + (Number(it.qty) || 1), 0);
    const badge = document.getElementById("cartBadgeCount");
    if (badge) badge.textContent = count;
  } catch (e) {}
}

function showToast(title, msg, isError = false) {
  const container = document.getElementById("toastContainer");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = "toast";
  if (isError) toast.style.borderLeftColor = "#ef4444";
  toast.innerHTML = `
    <div class="toast-icon" style="${isError ? "background:#fee2e2;color:#dc2626;" : ""}">${isError ? "!" : "✓"}</div>
    <div class="toast-content">
      <div class="toast-title">${escapeHtml(title)}</div>
      <div class="toast-msg">${escapeHtml(msg)}</div>
    </div>
  `;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("show"));
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 350);
  }, 3200);
}

function renderNotFoundOrError(title, desc, showRetry = false) {
  const root = document.getElementById("productDetailRoot");
  if (!root) return;
  root.innerHTML = `
    <div class="section-state-box ${showRetry ? "is-error" : ""}" style="min-height: 320px;">
      <div class="state-icon">${showRetry ? "⚠️" : "🔍"}</div>
      <div class="state-title" style="font-size: 18px;">${escapeHtml(title)}</div>
      <div class="state-desc">${escapeHtml(desc)}</div>
      <div style="display: flex; gap: 12px; margin-top: 10px; flex-wrap: wrap; justify-content: center;">
        ${showRetry ? `<button class="btn-retry" onclick="loadProductDetailPage()">↻ Thử lại</button>` : ""}
        <a href="products.html" class="btn-retry" style="text-decoration: none; background: #0f172a;">← Quay lại danh sách sản phẩm</a>
      </div>
    </div>
  `;
}

function renderProductDetail(product, isOfflineDemo = false) {
  detailState.product = product;
  detailState.images = product.images;
  detailState.angles = product.angles;
  detailState.currentImageIndex = 0;
  detailState.availableStock = product.availableStock;
  detailState.qty = product.availableStock > 0 ? 1 : 0;

  document.title = `${product.title} - JML Store`;
  const stockMeta = getStockMeta(product.availableStock);
  const hasMultipleImages = product.images.length > 1;
  const isOut = !stockMeta.inStock;

  const colors = ["Đen Titan", "Bạc Ánh Kim", "Xanh Navy"];
  detailState.selectedColor = colors[0];
  detailState.selectedVersion = "Bản Tiêu Chuẩn (Fullbox)";
  detailState.reviewStar = 5;
  detailState.reviewFilterStar = null;
  detailState.reviewPage = 1;

  const authUser = getAuthenticatedUser();
  const defaultReviewerName = authUser ? authUser.full_name || authUser.username || "" : "";

  const root = document.getElementById("productDetailRoot");
  root.innerHTML = `
    <div class="product-detail-wrapper">
      ${
        isOfflineDemo
          ? `<div style="background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;padding:10px 14px;border-radius:10px;font-size:12.5px;font-weight:600;margin-bottom:14px;">
              ℹ️ Đang hiển thị dữ liệu mẫu offline do chưa kết nối tới FastAPI Backend (${escapeHtml(API_BASE_URL || "cổng 8000")}).
            </div>`
          : ""
      }

      <!-- Breadcrumb -->
      <div class="detail-breadcrumb-bar">
        <a href="products.html" class="btn-back-home" style="text-decoration: none;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Quay Lại Danh Sách
        </a>
        <div class="breadcrumb-trail">
          <a href="index.html">Trang Chủ</a>
          <span>/</span>
          <a href="products.html?category=${encodeURIComponent(product.category)}">${escapeHtml(product.categoryName)}</a>
          <span>/</span>
          <span class="breadcrumb-current" title="${escapeHtml(product.title)}">${escapeHtml(product.title)}</span>
        </div>
      </div>

      <!-- Showcase Grid -->
      <div class="product-showcase-grid">
        <!-- Cột trái: Thư viện ảnh -->
        <div class="showcase-gallery">
          <div class="main-image-viewport">
            ${product.discount && product.discount !== "0%" ? `<span class="detail-discount-tag">${escapeHtml(product.discount)}</span>` : ""}
            ${product.exclusive ? `<span class="detail-exclusive-tag">${escapeHtml(product.exclusive)}</span>` : ""}
            ${
              hasMultipleImages
                ? `<button type="button" class="gallery-nav-btn gallery-nav-prev" onclick="stepDetailImage(-1)" aria-label="Ảnh trước">❮</button>
                   <button type="button" class="gallery-nav-btn gallery-nav-next" onclick="stepDetailImage(1)" aria-label="Ảnh tiếp">❯</button>`
                : ""
            }
            <span class="gallery-zoom-hint">🔍 Bấm ảnh để phóng to</span>
            <span class="detail-angle-indicator" id="detailAngleBadge">${escapeHtml(product.angles[0] || "Ảnh 1")}</span>
            <img id="detailMainImg" src="${escapeHtml(product.images[0])}" alt="${escapeHtml(product.title)}" onclick="openDetailLightbox()" />
          </div>

          <!-- Thumbnails Strip -->
          <div class="gallery-thumbs-row" id="galleryThumbsRow">
            ${product.images
              .map(
                (img, idx) => `
              <div class="gallery-thumb-item ${idx === 0 ? "active" : ""}" onclick="selectDetailImage(${idx})">
                <img src="${escapeHtml(img)}" alt="${escapeHtml(product.angles[idx] || `Ảnh ${idx + 1}`)}" />
                <span>${escapeHtml(product.angles[idx] || `Ảnh ${idx + 1}`)}</span>
              </div>
            `
              )
              .join("")}
          </div>

          <div class="trust-features-grid">
            <div class="trust-item">
              <div class="trust-icon">🛡️</div>
              <div>
                <strong>100% Chính Hãng</strong>
                <span>Hoàn tiền 200% nếu phát hiện hàng giả</span>
              </div>
            </div>
            <div class="trust-item">
              <div class="trust-icon">🔄</div>
              <div>
                <strong>Đổi Trả 30 Ngày</strong>
                <span>Miễn phí nếu phát sinh lỗi NSX</span>
              </div>
            </div>
            <div class="trust-item">
              <div class="trust-icon">🚀</div>
              <div>
                <strong>Giao Nhanh Toàn Quốc</strong>
                <span>Kiểm tra hàng trước khi thanh toán</span>
              </div>
            </div>
            <div class="trust-item">
              <div class="trust-icon">💎</div>
              <div>
                <strong>Bảo Hành Chính Hãng</strong>
                <span>Hỗ trợ bảo hành điện tử 24 tháng</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Cột phải: Thông tin giá, tồn kho, chọn số lượng & thêm vào giỏ -->
        <div class="showcase-info">
          <div class="detail-mall-badge">
            <span class="mall-pill">✓ JML OFFICIAL</span>
            <span class="brand-pill">Thương hiệu: ${escapeHtml(product.brand)}</span>
            <span class="sku-pill">MÃ SP: #JML-${escapeHtml(product.id)}</span>
          </div>

          <h1 class="detail-product-title">${escapeHtml(product.title)}</h1>

          <div class="detail-meta-row">
            <div class="meta-rating">
              <span class="stars">★★★★★</span>
              <strong id="detailRatingValue">${escapeHtml(product.rating)}</strong>
            </div>
            <span>•</span>
            <span class="meta-reviews" id="detailReviewCountHeader">Đang tải đánh giá...</span>
            <span>•</span>
            <span class="meta-sold">Đã bán ${product.sold}</span>
            <span>•</span>
            <span class="stock-badge ${stockMeta.cls}" id="detailStockBadge">${escapeHtml(stockMeta.label)}</span>
          </div>

          <!-- Khối Giá -->
          <div class="detail-price-box">
            <div class="price-header">
              <span class="price-label">Giá Bán Niêm Yết</span>
              <span class="deal-pill">✓ GIÁ TỐT NHẤT HÔM NAY</span>
            </div>
            <div class="price-numbers">
              <span class="detail-current-price">${formatCurrency(product.price)}</span>
              ${
                product.originalPrice > product.price
                  ? `<span class="detail-original-price">${formatCurrency(product.originalPrice)}</span>`
                  : ""
              }
              ${
                product.discountAmount > 0
                  ? `<span class="detail-save-badge">Tiết kiệm ${formatCurrency(product.discountAmount)} (${escapeHtml(product.discount)})</span>`
                  : ""
              }
            </div>
            <div class="price-voucher-notice">
              🏪 Phân phối bởi <strong>${escapeHtml(product.shopName)}</strong> • Miễn phí vận chuyển đơn từ 500.000 ₫
            </div>
          </div>

          <!-- Biến thể màu sắc -->
          <div class="variant-section">
            <div class="variant-title">
              <span>Chọn Màu Sắc:</span>
              <strong id="selectedColorLabel">${escapeHtml(colors[0])}</strong>
            </div>
            <div class="variant-options">
              ${colors
                .map(
                  (c, idx) => `
                <button type="button" class="variant-btn ${idx === 0 ? "active" : ""}" onclick="selectDetailVariant(this, 'selectedColorLabel', '${escapeHtml(c)}', 'color')">
                  <span class="color-dot" style="background: ${idx === 0 ? "#111827" : idx === 1 ? "#94a3b8" : "#1e3a8a"};"></span>
                  ${escapeHtml(c)}
                </button>
              `
                )
                .join("")}
            </div>
          </div>

          <!-- Chọn Số Lượng & Tồn Kho -->
          <div class="quantity-section" style="flex-wrap: wrap;">
            <span class="qty-label">Số Lượng:</span>
            <div class="qty-picker">
              <button type="button" id="qtyDecreaseBtn" onclick="changeDetailQty(-1)" ${isOut || detailState.qty <= 1 ? "disabled" : ""}>−</button>
              <input
                type="number"
                id="detailQtyInput"
                value="${detailState.qty}"
                min="${isOut ? 0 : 1}"
                max="${product.availableStock}"
                ${isOut ? "disabled" : ""}
                onchange="onDetailQtyInput(this.value)"
              />
              <button type="button" id="qtyIncreaseBtn" onclick="changeDetailQty(1)" ${isOut || detailState.qty >= product.availableStock ? "disabled" : ""}>+</button>
            </div>
            <span class="stock-remain" id="stockRemainText">
              ${
                isOut
                  ? `<strong style="color:#dc2626;">Sản phẩm hiện đã hết hàng</strong>`
                  : `Còn lại <strong style="color:#0f172a;">${product.availableStock}</strong> sản phẩm trong kho (Tổng: ${product.totalStock})`
              }
            </span>
          </div>

          <!-- Nút Thêm Vào Giỏ & Mua Ngay -->
          <div class="detail-actions-row">
            <button type="button" class="btn-detail-add-cart" id="btnAddToCart" onclick="handleAddToCart(false)" ${isOut ? "disabled" : ""}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
              </svg>
              ${isOut ? "Tạm Hết Hàng" : "Thêm Vào Giỏ Hàng"}
            </button>
            <button type="button" class="btn-detail-buy-now" id="btnBuyNow" onclick="handleAddToCart(true)" ${isOut ? "disabled" : ""}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
              Mua Ngay
            </button>
          </div>

          <div class="shipping-info-card">
            <div class="shipping-row">
              <span>📦</span>
              <span><strong>Kho hàng:</strong> ${escapeHtml(product.shopName)} • Giao hàng tiêu chuẩn 1-3 ngày</span>
            </div>
            <div class="shipping-row">
              <span>🔒</span>
              <span><strong>Bảo vệ người mua:</strong> Quỹ trung gian Escrow giữ tiền đến khi bạn nhận hàng hài lòng</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs Mô Tả & Thông Số -->
      <section class="detail-tabs-section">
        <div class="detail-tab-nav">
          <button type="button" class="detail-tab-btn active" onclick="switchDetailTab(this, 'tabDesc')">Mô Tả Sản Phẩm</button>
          <button type="button" class="detail-tab-btn" onclick="switchDetailTab(this, 'tabSpecs')">Thông Số Kỹ Thuật</button>
          <button type="button" class="detail-tab-btn" onclick="scrollToReviewsSection()">Đánh Giá Khách Hàng (<span id="reviewsTabCount">0</span>)</button>
        </div>

        <div class="detail-tab-pane active" id="tabDesc">
          <p style="white-space: pre-line;">${escapeHtml(product.description)}</p>
        </div>

        <div class="detail-tab-pane" id="tabSpecs">
          <table class="spec-table">
            <tr><td class="spec-key">Tên sản phẩm</td><td>${escapeHtml(product.title)}</td></tr>
            <tr><td class="spec-key">Thương hiệu</td><td>${escapeHtml(product.brand)}</td></tr>
            <tr><td class="spec-key">Ngành hàng</td><td>${escapeHtml(product.categoryName)}</td></tr>
            <tr><td class="spec-key">Nhà bán hàng</td><td>${escapeHtml(product.shopName)}</td></tr>
            <tr><td class="spec-key">Tình trạng tồn kho</td><td>${escapeHtml(stockMeta.label)}</td></tr>
            <tr><td class="spec-key">Bảo hành</td><td>24 tháng chính hãng • Đổi mới trong 30 ngày</td></tr>
          </table>
        </div>
      </section>

      <!-- Khu Vực Đánh Giá & Form Gửi Đánh Giá (TF17554) -->
      <section class="detail-tabs-section" id="reviewsSection">
        <div class="section-title-wrap" style="margin-bottom: 18px;">
          <div>
            <h2 class="section-title">Đánh Giá &amp; Nhận Xét Khách Hàng</h2>
            <p class="section-subtitle">Mỗi người dùng được gửi 1 đánh giá (1–5 sao) cho sản phẩm này</p>
          </div>
        </div>

        <!-- Tổng quan điểm trung bình & phân bố 1-5 sao -->
        <div id="reviewsSummaryContainer">
          <div class="skeleton-block" style="width: 100%; height: 130px; margin-bottom: 20px;"></div>
        </div>

        <!-- Form gửi đánh giá -->
        <form class="review-form-card" id="reviewSubmitForm" onsubmit="submitProductReview(event)">
          <div class="review-form-title">✍️ Gửi Đánh Giá Của Bạn</div>
          <div class="star-picker-row" id="reviewStarPicker">
            <span style="font-size: 13px; font-weight: 700; color: var(--secondary); margin-right: 4px;">Chọn số sao:</span>
            ${[1, 2, 3, 4, 5]
              .map(
                (s) =>
                  `<button type="button" class="star-picker-btn active" data-star="${s}" onclick="selectReviewStar(${s})" title="${s} sao">★</button>`
              )
              .join("")}
            <span id="selectedStarLabel" style="font-size: 13px; font-weight: 700; color: #b45309; margin-left: 6px;">${STAR_LABELS[5]}</span>
          </div>

          <div class="review-form-grid">
            <div>
              <input
                type="text"
                id="reviewUserNameInput"
                class="review-input"
                placeholder="Tên của bạn (bắt buộc nếu chưa đăng nhập)..."
                value="${escapeHtml(defaultReviewerName)}"
                ${authUser && defaultReviewerName ? "readonly" : ""}
                maxlength="120"
              />
            </div>
            <div>
              <textarea
                id="reviewCommentInput"
                class="review-textarea"
                placeholder="Chia sẻ cảm nhận thực tế về chất lượng, đóng gói và trải nghiệm sản phẩm..."
                maxlength="2000"
                required
              ></textarea>
            </div>
            <div class="review-form-alert" id="reviewFormAlert"></div>
            <div class="review-form-actions">
              <span style="font-size: 12px; color: var(--text-muted);">
                ${authUser ? `Đang đăng nhập với tài khoản: <strong>${escapeHtml(defaultReviewerName)}</strong>` : "Mẹo: Đăng nhập để đồng bộ đánh giá theo tài khoản"}
              </span>
              <button type="submit" class="review-submit-btn" id="reviewSubmitBtn">Gửi Đánh Giá</button>
            </div>
          </div>
        </form>

        <!-- Bộ lọc theo sao -->
        <div class="review-filter-row" id="reviewFilterRow">
          <button type="button" class="review-filter-btn active" onclick="filterReviewsByStar(null, this)">Tất Cả</button>
          <button type="button" class="review-filter-btn" onclick="filterReviewsByStar(5, this)">5 ★</button>
          <button type="button" class="review-filter-btn" onclick="filterReviewsByStar(4, this)">4 ★</button>
          <button type="button" class="review-filter-btn" onclick="filterReviewsByStar(3, this)">3 ★</button>
          <button type="button" class="review-filter-btn" onclick="filterReviewsByStar(2, this)">2 ★</button>
          <button type="button" class="review-filter-btn" onclick="filterReviewsByStar(1, this)">1 ★</button>
        </div>

        <!-- Danh sách đánh giá -->
        <div id="reviewsListContainer">
          <div class="skeleton-block" style="width: 100%; height: 90px; margin-bottom: 10px;"></div>
          <div class="skeleton-block" style="width: 100%; height: 90px;"></div>
        </div>
      </section>

      <!-- Gợi Ý Sản Phẩm Cùng Danh Mục (TF17554) -->
      <section class="related-products-section" id="relatedProductsSection" style="margin-top: 36px;">
        <div class="section-title-wrap">
          <div>
            <h2 class="section-title">Sản Phẩm Cùng Danh Mục</h2>
            <p class="section-subtitle">Gợi ý các sản phẩm khác thuộc ngành hàng ${escapeHtml(product.categoryName)}</p>
          </div>
          <a href="products.html?category=${encodeURIComponent(product.category)}" class="view-all-link">Xem thêm cùng danh mục →</a>
        </div>
        <div class="recommend-grid" id="relatedProductsGrid"></div>
      </section>
    </div>
  `;

  loadProductReviews(product.id);
  loadRelatedCategoryProducts(product);
}

function selectDetailImage(index) {
  const { images, angles } = detailState;
  if (!images || images.length === 0) return;
  const safeIdx = ((index % images.length) + images.length) % images.length;
  detailState.currentImageIndex = safeIdx;

  const mainImg = document.getElementById("detailMainImg");
  const angleBadge = document.getElementById("detailAngleBadge");
  if (mainImg) mainImg.src = images[safeIdx];
  if (angleBadge) angleBadge.textContent = angles[safeIdx] || `Ảnh ${safeIdx + 1}`;

  document.querySelectorAll("#galleryThumbsRow .gallery-thumb-item").forEach((el, idx) => {
    el.classList.toggle("active", idx === safeIdx);
  });

  const lightbox = document.getElementById("detailLightbox");
  if (lightbox && lightbox.classList.contains("active")) {
    syncLightboxContent();
  }
}

function stepDetailImage(delta) {
  selectDetailImage(detailState.currentImageIndex + delta);
}

function syncLightboxContent() {
  const { images, angles, currentImageIndex } = detailState;
  const lbImg = document.getElementById("lightboxImg");
  const lbAngle = document.getElementById("lightboxAngleText");
  const lbIdx = document.getElementById("lightboxIndexText");
  if (lbImg && images[currentImageIndex]) lbImg.src = images[currentImageIndex];
  if (lbAngle) lbAngle.textContent = angles[currentImageIndex] || `Ảnh ${currentImageIndex + 1}`;
  if (lbIdx) lbIdx.textContent = `${currentImageIndex + 1} / ${images.length}`;
}

function openDetailLightbox() {
  const lb = document.getElementById("detailLightbox");
  if (!lb) return;
  syncLightboxContent();
  lb.classList.add("active");
}

function closeDetailLightbox(event) {
  const lb = document.getElementById("detailLightbox");
  if (!lb) return;
  if (!event || event.target === lb || !event.target.closest(".detail-lightbox-box")) {
    lb.classList.remove("active");
  }
}

function selectDetailVariant(btn, labelId, value, type) {
  const label = document.getElementById(labelId);
  if (label) label.textContent = value;
  if (btn && btn.parentElement) {
    btn.parentElement.querySelectorAll(".variant-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
  }
  if (type === "color") detailState.selectedColor = value;
  else detailState.selectedVersion = value;
}

function syncQtyUi() {
  const input = document.getElementById("detailQtyInput");
  const decBtn = document.getElementById("qtyDecreaseBtn");
  const incBtn = document.getElementById("qtyIncreaseBtn");
  const maxStock = detailState.availableStock;

  if (input) input.value = detailState.qty;
  if (decBtn) decBtn.disabled = maxStock <= 0 || detailState.qty <= 1;
  if (incBtn) incBtn.disabled = maxStock <= 0 || detailState.qty >= maxStock;
}

function changeDetailQty(delta) {
  const maxStock = detailState.availableStock;
  if (maxStock <= 0) return;

  let nextQty = detailState.qty + delta;
  if (nextQty < 1) nextQty = 1;
  if (nextQty > maxStock) {
    nextQty = maxStock;
    showToast("Giới hạn tồn kho", `Chỉ còn tối đa ${maxStock} sản phẩm trong kho.`, true);
  }
  detailState.qty = nextQty;
  syncQtyUi();
}

function onDetailQtyInput(rawVal) {
  const maxStock = detailState.availableStock;
  if (maxStock <= 0) {
    detailState.qty = 0;
    syncQtyUi();
    return;
  }

  let parsed = parseInt(rawVal, 10);
  if (isNaN(parsed) || parsed < 1) {
    parsed = 1;
  } else if (parsed > maxStock) {
    parsed = maxStock;
    showToast("Vượt tồn kho", `Số lượng tối đa có thể đặt là ${maxStock}.`, true);
  }
  detailState.qty = parsed;
  syncQtyUi();
}

function switchDetailTab(btn, paneId) {
  document.querySelectorAll(".detail-tab-btn").forEach((b) => b.classList.remove("active"));
  document.querySelectorAll(".detail-tab-pane").forEach((p) => p.classList.remove("active"));
  if (btn) btn.classList.add("active");
  const pane = document.getElementById(paneId);
  if (pane) pane.classList.add("active");
}

async function handleAddToCart(redirectToCart = false) {
  const p = detailState.product;
  if (!p) return;

  if (detailState.availableStock <= 0) {
    showToast("Hết hàng", "Sản phẩm hiện đã hết hàng trong kho.", true);
    return;
  }

  const qtyToAdd = Math.max(1, Math.min(detailState.qty, detailState.availableStock));
  let cart = [];
  try {
    cart = JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || "[]");
  } catch (e) {
    cart = [];
  }

  const existing = cart.find((item) => Number(item.id) === Number(p.id));
  const currentInCart = existing ? Number(existing.qty) || 1 : 0;
  if (currentInCart + qtyToAdd > detailState.availableStock) {
    showToast(
      "Vượt số lượng tồn kho",
      `Giỏ hàng đã có ${currentInCart} sản phẩm. Tổng số lượng không thể vượt ${detailState.availableStock}.`,
      true
    );
    return;
  }

  if (existing) {
    existing.qty = currentInCart + qtyToAdd;
    existing.stock = detailState.availableStock;
  } else {
    cart.push({
      id: p.id,
      product_id: p.id,
      title: p.title,
      variant: detailState.selectedColor,
      price: p.price,
      originalPrice: p.originalPrice,
      image: p.images[0] || FALLBACK_IMG,
      shopName: p.shopName,
      qty: qtyToAdd,
      stock: detailState.availableStock,
    });
  }

  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
  updateHeaderCartBadge();

  // Đồng bộ với Backend /api/cart/items nếu người dùng đã đăng nhập
  const user =
    (typeof Auth !== "undefined" && typeof Auth.getUser === "function" ? Auth.getUser() : null) ||
    JSON.parse(localStorage.getItem("JML_CUSTOMER_USER") || "null") ||
    JSON.parse(localStorage.getItem("JML_AUTH_USER") || "null");

  if (user && user.id) {
    try {
      await fetch(`${API_BASE_URL}/api/cart/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          product_id: p.id,
          quantity: qtyToAdd,
        }),
      });
    } catch (e) {
      // Giữ đồng bộ localStorage nếu backend offline
    }
  }

  showToast("Đã thêm vào giỏ hàng!", `${qtyToAdd}x ${p.title}`);
  if (redirectToCart) {
    setTimeout(() => {
      window.location.href = "cart.html";
    }, 250);
  }
}

async function loadProductDetailPage() {
  const rawId = urlParams.get("id") || urlParams.get("productId") || "1";
  const productId = parseInt(rawId, 10);

  if (isNaN(productId) || productId <= 0) {
    renderNotFoundOrError("Mã sản phẩm không hợp lệ", "Vui lòng chọn lại một sản phẩm từ danh sách.");
    return;
  }

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 7000);
    const res = await fetch(`${API_BASE_URL}/api/products/${productId}`, {
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (res.status === 404) {
      renderNotFoundOrError(
        "Sản phẩm không tồn tại",
        `Không tìm thấy sản phẩm có mã #${productId} trên hệ thống.`
      );
      return;
    }

    if (!res.ok) {
      throw new Error(`Máy chủ trả về mã lỗi HTTP ${res.status}`);
    }

    const data = await res.json();
    renderProductDetail(normalizeProductDetail(data), false);
  } catch (err) {
    // Nếu chưa chạy Backend, fallback tìm trong catalog mẫu theo ID hoặc sản phẩm đầu tiên khi demo
    const fallbackItem =
      FALLBACK_CATALOG.find((p) => Number(p.id) === productId) ||
      (urlParams.get("demo") === "1" ? FALLBACK_CATALOG[0] : null);
    if (fallbackItem) {
      renderProductDetail(normalizeProductDetail(fallbackItem), true);
      return;
    }
    renderNotFoundOrError(
      "Không tải được chi tiết sản phẩm",
      err.name === "AbortError" ? "Kết nối API bị quá thời gian chờ." : err.message,
      true
    );
  }
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeDetailLightbox();
  } else if (e.key === "ArrowLeft" && detailState.images.length > 1) {
    stepDetailImage(-1);
  } else if (e.key === "ArrowRight" && detailState.images.length > 1) {
    stepDetailImage(1);
  }
});

document.addEventListener("DOMContentLoaded", () => {
  updateHeaderCartBadge();
  const form = document.getElementById("detailSearchForm");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const q = (document.getElementById("detailSearchInput")?.value || "").trim();
      window.location.href = q ? `products.html?q=${encodeURIComponent(q)}` : "products.html";
    });
  }
  loadProductDetailPage();
});

// ============================================================================
// TF17554: DANH SÁCH ĐÁNH GIÁ, FORM GỬI ĐÁNH GIÁ & SẢN PHẨM CÙNG DANH MỤC
// ============================================================================
function getAuthenticatedUser() {
  try {
    if (typeof Auth !== "undefined" && typeof Auth.getUser === "function") {
      const u = Auth.getUser();
      if (u) return u;
    }
    return (
      JSON.parse(localStorage.getItem("JML_CUSTOMER_USER") || "null") ||
      JSON.parse(localStorage.getItem("JML_AUTH_USER") || "null")
    );
  } catch (e) {
    return null;
  }
}

function scrollToReviewsSection() {
  const sec = document.getElementById("reviewsSection");
  if (sec) sec.scrollIntoView({ behavior: "smooth" });
}

function selectReviewStar(star) {
  const safeStar = Math.max(1, Math.min(5, Number(star) || 5));
  detailState.reviewStar = safeStar;
  document.querySelectorAll("#reviewStarPicker .star-picker-btn").forEach((btn) => {
    const btnStar = Number(btn.dataset.star);
    btn.classList.toggle("active", btnStar <= safeStar);
  });
  const label = document.getElementById("selectedStarLabel");
  if (label) label.textContent = STAR_LABELS[safeStar] || `${safeStar}/5 sao`;
}

function filterReviewsByStar(star, btn) {
  detailState.reviewFilterStar = star;
  detailState.reviewPage = 1;
  document.querySelectorAll("#reviewFilterRow .review-filter-btn").forEach((b) => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  if (detailState.product) {
    loadProductReviews(detailState.product.id, star, 1);
  }
}

function renderStarsString(ratingVal) {
  const count = Math.max(0, Math.min(5, Math.round(Number(ratingVal) || 0)));
  return "★".repeat(count) + "☆".repeat(5 - count);
}

function getOfflineReviewsKey(productId) {
  return `JML_OFFLINE_REVIEWS_${productId}`;
}

function readOfflineReviews(productId) {
  try {
    return JSON.parse(localStorage.getItem(getOfflineReviewsKey(productId)) || "[]");
  } catch (e) {
    return [];
  }
}

function computeOfflineReviewStats(reviews) {
  const total = reviews.length;
  const breakdown = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
  let sum = 0;
  reviews.forEach((r) => {
    const s = Math.max(1, Math.min(5, Number(r.rating) || 5));
    breakdown[s] += 1;
    sum += s;
  });
  return {
    total_reviews: total,
    average_rating: total > 0 ? Number((sum / total).toFixed(1)) : 0,
    rating_breakdown: breakdown,
  };
}

function renderReviewsSummary(avgRating, totalReviews, breakdown) {
  const container = document.getElementById("reviewsSummaryContainer");
  const headerRating = document.getElementById("detailRatingValue");
  const headerCount = document.getElementById("detailReviewCountHeader");
  const tabCount = document.getElementById("reviewsTabCount");

  const displayAvg = totalReviews > 0 ? Number(avgRating || 0).toFixed(1) : "0.0";
  if (headerRating) headerRating.textContent = totalReviews > 0 ? displayAvg : detailState.product?.rating || "5.0";
  if (headerCount) headerCount.textContent = `${totalReviews} Đánh giá`;
  if (tabCount) tabCount.textContent = totalReviews;

  if (!container) return;
  const safeTotal = Math.max(1, Number(totalReviews) || 0);
  const barsHtml = [5, 4, 3, 2, 1]
    .map((star) => {
      const cnt = Number((breakdown && (breakdown[String(star)] ?? breakdown[star])) || 0);
      const pct = totalReviews > 0 ? Math.round((cnt / safeTotal) * 100) : 0;
      return `
        <div class="rating-bar-row">
          <span class="rating-bar-label">${star} ★</span>
          <div class="rating-bar-track"><div class="rating-bar-fill" style="width: ${pct}%;"></div></div>
          <span class="rating-bar-count">${cnt}</span>
        </div>`;
    })
    .join("");

  container.innerHTML = `
    <div class="reviews-summary-box">
      <div class="reviews-score-col">
        <div class="reviews-avg-number">${displayAvg}<span style="font-size:18px;color:var(--text-muted);font-weight:500;">/5</span></div>
        <div class="reviews-avg-stars">${totalReviews > 0 ? renderStarsString(avgRating) : "☆☆☆☆☆"}</div>
        <div style="font-size: 12.5px; color: var(--text-muted);">${totalReviews} lượt đánh giá</div>
      </div>
      <div class="reviews-bars-col">${barsHtml}</div>
    </div>
  `;
}

function renderReviewsList(reviews, isOfflineMode = false) {
  const container = document.getElementById("reviewsListContainer");
  if (!container) return;

  const offlineBanner = isOfflineMode
    ? `<div style="font-size:12px;color:#9a3412;background:#fff7ed;border:1px solid #fed7aa;padding:8px 12px;border-radius:8px;margin-bottom:12px;">
         ℹ️ Backend chưa kết nối — đang hiển thị đánh giá lưu cục bộ (localStorage).
       </div>`
    : "";

  if (!Array.isArray(reviews) || reviews.length === 0) {
    const emptyMsg = detailState.reviewFilterStar
      ? `Chưa có đánh giá ${detailState.reviewFilterStar} sao nào cho sản phẩm này.`
      : "Sản phẩm chưa có đánh giá nào. Hãy là người đầu tiên nhận xét!";
    container.innerHTML = `
      ${offlineBanner}
      <div class="section-state-box is-empty" style="min-height: 150px; padding: 24px;">
        <div class="state-icon">💬</div>
        <div class="state-title">Chưa có đánh giá</div>
        <div class="state-desc">${escapeHtml(emptyMsg)}</div>
      </div>
    `;
    return;
  }

  container.innerHTML =
    offlineBanner +
    reviews
      .map(
        (rev) => `
      <div class="review-card">
        <div class="review-header">
          <span class="reviewer-name">
            ${escapeHtml(rev.user_name || "Khách hàng")}
            <span class="verified-badge">✓ Khách hàng JML Store</span>
          </span>
          <span class="review-date">${escapeHtml(rev.date || rev.created_at || "")}</span>
        </div>
        <div class="review-stars">${renderStarsString(rev.rating)} <span style="color:var(--text-muted);font-size:12px;">(${Number(rev.rating)}/5)</span></div>
        <p style="margin-top: 4px; color: var(--text-main);">${escapeHtml(rev.comment)}</p>
      </div>
    `
      )
      .join("");
}

async function loadProductReviews(productId, starFilter = detailState.reviewFilterStar, page = 1) {
  const listEl = document.getElementById("reviewsListContainer");
  if (listEl) {
    listEl.innerHTML = `
      <div class="skeleton-block" style="width: 100%; height: 84px; margin-bottom: 10px;"></div>
      <div class="skeleton-block" style="width: 100%; height: 84px;"></div>`;
  }

  const query = new URLSearchParams({ page: String(page), page_size: "10" });
  if (starFilter !== null && starFilter !== undefined) {
    query.set("rating", String(starFilter));
  }

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 7000);
    const res = await fetch(`${API_BASE_URL}/api/reviews/${productId}?${query.toString()}`, {
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    renderReviewsSummary(data.average_rating ?? data.rating ?? 0, data.total_reviews ?? 0, data.rating_breakdown || {});
    renderReviewsList(data.reviews || [], false);
  } catch (err) {
    const allLocal = readOfflineReviews(productId);
    const stats = computeOfflineReviewStats(allLocal);
    const filtered = starFilter ? allLocal.filter((r) => Number(r.rating) === Number(starFilter)) : allLocal;
    renderReviewsSummary(stats.average_rating, stats.total_reviews, stats.rating_breakdown);
    renderReviewsList(filtered, true);
  }
}

function setReviewFormAlert(message, type) {
  const alertEl = document.getElementById("reviewFormAlert");
  if (!alertEl) return;
  alertEl.className = "review-form-alert";
  if (!message) {
    alertEl.textContent = "";
    return;
  }
  alertEl.classList.add(type === "success" ? "is-success" : "is-error");
  alertEl.textContent = message;
}

async function submitProductReview(e) {
  e.preventDefault();
  const product = detailState.product;
  if (!product) return;

  const user = getAuthenticatedUser();
  const nameInput = document.getElementById("reviewUserNameInput");
  const commentInput = document.getElementById("reviewCommentInput");
  const submitBtn = document.getElementById("reviewSubmitBtn");

  const userName = (nameInput?.value || "").trim() || (user ? user.full_name || user.username : "");
  const comment = (commentInput?.value || "").trim();
  const rating = detailState.reviewStar;

  if (!userName && !(user && user.id)) {
    setReviewFormAlert("Vui lòng nhập tên của bạn trước khi gửi đánh giá.", "error");
    return;
  }
  if (!comment) {
    setReviewFormAlert("Vui lòng nhập nội dung nhận xét cho sản phẩm.", "error");
    return;
  }

  setReviewFormAlert("", "");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Đang gửi...";
  }

  const headers = { "Content-Type": "application/json", Accept: "application/json" };
  const token = localStorage.getItem("JML_ACCESS_TOKEN");
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const payload = {
    product_id: Number(product.id),
    rating: Number(rating),
    comment,
    user_name: userName,
  };
  if (user && user.id) payload.user_id = Number(user.id);

  try {
    const res = await fetch(`${API_BASE_URL}/api/reviews`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    const data = await res.json().catch(() => ({}));

    if (res.status === 409) {
      const msg = data.detail || "Bạn đã đánh giá sản phẩm này rồi! Mỗi người chỉ được gửi 1 đánh giá cho mỗi sản phẩm.";
      setReviewFormAlert(msg, "error");
      showToast("Đã đánh giá trước đó", msg, true);
      return;
    }

    if (!res.ok) {
      const msg = data.detail || `Không thể gửi đánh giá (HTTP ${res.status})`;
      setReviewFormAlert(msg, "error");
      showToast("Lỗi gửi đánh giá", msg, true);
      return;
    }

    if (commentInput) commentInput.value = "";
    selectReviewStar(5);
    setReviewFormAlert(data.message || "Cảm ơn bạn đã gửi đánh giá cho sản phẩm!", "success");
    showToast("Đã gửi đánh giá!", "Đánh giá của bạn đã được ghi nhận.");
    await loadProductReviews(product.id, detailState.reviewFilterStar, 1);
  } catch (err) {
    // Offline fallback: lưu localStorage & kiểm tra trùng
    const localList = readOfflineReviews(product.id);
    const isDuplicate = localList.some((r) =>
      user && user.id
        ? Number(r.user_id) === Number(user.id)
        : String(r.user_name || "").trim().toLowerCase() === userName.toLowerCase()
    );
    if (isDuplicate) {
      const msg = "Bạn đã đánh giá sản phẩm này rồi! Mỗi người chỉ được gửi 1 đánh giá cho mỗi sản phẩm.";
      setReviewFormAlert(msg, "error");
      showToast("Đã đánh giá trước đó", msg, true);
      return;
    }

    localList.unshift({
      id: Date.now(),
      product_id: product.id,
      user_id: user ? user.id : null,
      user_name: userName,
      rating,
      comment,
      date: new Date().toLocaleDateString("vi-VN"),
    });
    localStorage.setItem(getOfflineReviewsKey(product.id), JSON.stringify(localList));
    if (commentInput) commentInput.value = "";
    selectReviewStar(5);
    setReviewFormAlert("Đã lưu đánh giá ở chế độ offline (localStorage).", "success");
    showToast("Đã gửi đánh giá!", "Lưu thành công (offline).");
    await loadProductReviews(product.id, detailState.reviewFilterStar, 1);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = "Gửi Đánh Giá";
    }
  }
}

function renderRelatedProductsGrid(items) {
  const grid = document.getElementById("relatedProductsGrid");
  if (!grid) return;

  if (!Array.isArray(items) || items.length === 0) {
    grid.innerHTML = `
      <div class="section-state-box is-empty" style="min-height: 160px; padding: 24px;">
        <div class="state-icon">🛍️</div>
        <div class="state-title">Chưa có thêm sản phẩm cùng danh mục</div>
        <div class="state-desc">Bạn có thể xem toàn bộ sản phẩm khác trong cửa hàng.</div>
      </div>
    `;
    return;
  }

  grid.innerHTML = items
    .slice(0, 4)
    .map((rel) => {
      const relImg = Array.isArray(rel.images) && rel.images[0] ? rel.images[0] : rel.image || FALLBACK_IMG;
      return `
        <div class="product-card" onclick="window.location.href='product-detail.html?id=${rel.id}'">
          <div class="product-img-wrapper">
            ${rel.discount ? `<span class="discount-tag">${escapeHtml(rel.discount)}</span>` : ""}
            <img src="${escapeHtml(relImg)}" alt="${escapeHtml(rel.title)}" style="width:100%;height:100%;object-fit:cover;" loading="lazy" />
          </div>
          <div class="product-body">
            <h3 class="product-title" title="${escapeHtml(rel.title)}">${escapeHtml(rel.title)}</h3>
            <div class="product-meta">
              <span class="rating-stars">★ ${escapeHtml(Number(rel.rating ?? 5.0).toFixed(1))}</span>
              <span>• Đã bán ${Number(rel.sold ?? rel.soldCount ?? 0)}</span>
            </div>
            <div class="price-row">
              <span class="current-price">${formatCurrency(rel.price)}</span>
              ${rel.originalPrice > rel.price ? `<span class="original-price">${formatCurrency(rel.originalPrice)}</span>` : ""}
            </div>
          </div>
        </div>
      `;
    })
    .join("");
}

async function loadRelatedCategoryProducts(product) {
  const grid = document.getElementById("relatedProductsGrid");
  if (!grid) return;

  if (Array.isArray(product.relatedProducts) && product.relatedProducts.length > 0) {
    renderRelatedProductsGrid(product.relatedProducts);
    return;
  }

  grid.innerHTML = Array.from({ length: 4 })
    .map(
      () => `
      <div class="skeleton-card">
        <div class="skeleton-block" style="width: 100%; height: 180px;"></div>
        <div class="skeleton-block" style="width: 85%; height: 15px;"></div>
        <div class="skeleton-block" style="width: 55%; height: 14px;"></div>
      </div>`
    )
    .join("");

  try {
    const res = await fetch(`${API_BASE_URL}/api/products?category=${encodeURIComponent(product.category)}`, {
      headers: { Accept: "application/json" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const list =
      Array.isArray(data.items) && data.items.length > 0
        ? data.items
        : [...(data.recommend_products || []), ...(data.flash_products || [])];
    const sameCat = list.filter((item) => Number(item.id) !== Number(product.id));
    renderRelatedProductsGrid(sameCat);
  } catch (err) {
    const fallbackSameCat = FALLBACK_CATALOG.filter(
      (item) => item.category === product.category && Number(item.id) !== Number(product.id)
    );
    renderRelatedProductsGrid(fallbackSameCat);
  }
}
