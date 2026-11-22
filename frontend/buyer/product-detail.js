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
];

let detailState = {
  product: null,
  images: [],
  angles: [],
  currentImageIndex: 0,
  qty: 1,
  availableStock: 0,
  selectedColor: "Đen Titan",
  selectedVersion: "Bản Tiêu Chuẩn (Fullbox)",
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

  const relatedHtml = product.relatedProducts.length
    ? `
      <section class="related-products-section" style="margin-top: 36px;">
        <div class="section-title-wrap">
          <div>
            <h2 class="section-title">Sản Phẩm Liên Quan</h2>
            <p class="section-subtitle">Cùng ngành hàng ${escapeHtml(product.categoryName)}</p>
          </div>
          <a href="products.html?category=${encodeURIComponent(product.category)}" class="view-all-link">Xem thêm →</a>
        </div>
        <div class="recommend-grid">
          ${product.relatedProducts
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
                      <span class="rating-stars">★ ${escapeHtml(rel.rating ?? 5.0)}</span>
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
            .join("")}
        </div>
      </section>
    `
    : "";

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
              <strong>${escapeHtml(product.rating)}</strong>
            </div>
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

      ${relatedHtml}
    </div>
  `;
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
