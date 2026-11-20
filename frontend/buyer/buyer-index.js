// --------------------------------------------------------------------------
// DỮ LIỆU SẢN PHẨM MẪU (DATA STORE KÈM BỘ SƯU TẬP ẢNH ĐA GÓC CHỤP CHO MỖI SẢN PHẨM)
// --------------------------------------------------------------------------
const API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_FLASH_PRODUCTS = [
  {
    id: 101,
    category: "audio",
    title: "Tai Nghe Chống Ồn Cao Cấp Sony WH-1000XM5 Black Edition",
    price: 7490000,
    originalPrice: 9490000,
    discount: "-21%",
    rating: 4.9,
    sold: 84,
    totalStock: 100,
    images: [
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Chính diện",
      "Góc nghiêng",
      "Cận cảnh đệm da",
      "Trên tay lifestyle",
    ],
    exclusive: "Bán Chạy",
  },
  {
    id: 102,
    category: "watch",
    title: "Đồng Hồ Nam Cơ Tự Động Tissot Le Locle Powermatic 80",
    price: 13800000,
    originalPrice: 17250000,
    discount: "-20%",
    rating: 5.0,
    sold: 46,
    totalStock: 50,
    images: [
      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Mặt số Guilloche",
      "Góc nghiêng viền",
      "Nắp lưng lộ cơ",
      "Đeo trên cổ tay",
    ],
    exclusive: "Hot Deal",
  },
  {
    id: 103,
    category: "audio",
    title: "Loa Bluetooth Harman Kardon Aura Studio 4 Hi-End",
    price: 5890000,
    originalPrice: 7500000,
    discount: "-22%",
    rating: 4.8,
    sold: 92,
    totalStock: 100,
    images: [
      "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Vòm Acrylic",
      "Đèn Ambient LED",
      "Màng Subwoofer",
      "Phòng khách tối giản",
    ],
    exclusive: "Flash",
  },
  {
    id: 104,
    category: "fashion",
    title: "Kính Mát Phân Cực Ray-Ban Aviator Classic Gold Frame",
    price: 3650000,
    originalPrice: 4800000,
    discount: "-24%",
    rating: 4.7,
    sold: 71,
    totalStock: 80,
    images: [
      "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1577803645773-f96470509666?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1508296695146-257a814070b4?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Khung mạ vàng",
      "Mặt nghiêng gọng",
      "Tròng kính râm",
      "Phối đồ phong cách",
    ],
    exclusive: "Trend",
  },
  {
    id: 105,
    category: "tech",
    title: "Bàn Phím Cơ Không Dây NuPhy Air75 V2 Low-Profile",
    price: 2990000,
    originalPrice: 3800000,
    discount: "-21%",
    rating: 4.9,
    sold: 58,
    totalStock: 60,
    images: [
      "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Mặt phím PBT",
      "Độ mỏng hông",
      "Switch cơ học",
      "Bàn làm việc Desk",
    ],
    exclusive: "Sắp Cháy Hàng",
  },
];

const DEFAULT_RECOMMEND_PRODUCTS = [
  {
    id: 201,
    category: "tech",
    title: "iPad Pro M4 11-inch OLED Siêu Mỏng 256GB Space Black",
    price: 26990000,
    originalPrice: 28990000,
    discount: "-7%",
    rating: 5.0,
    soldCount: 342,
    images: [
      "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1561154464-82e9adf32764?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1585792180666-f75a7c518801?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Màn hình Ultra OLED",
      "Cạnh vát mỏng 5.1mm",
      "Mặt lưng Space Black",
      "Trải nghiệm Apple Pencil",
    ],
  },
  {
    id: 202,
    category: "watch",
    title: "Apple Watch Ultra 2 GPS + Cellular Dây Alpine Loop",
    price: 20490000,
    originalPrice: 21990000,
    discount: "-7%",
    rating: 4.9,
    soldCount: 512,
    images: [
      "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1510017803434-a899398421b3?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1508615039623-a25605d2b022?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Màn hình 3000 nits",
      "Nút Action Titanium",
      "Khóa dệt Alpine",
      "Đeo dã ngoại ngoài trời",
    ],
  },
  {
    id: 203,
    category: "audio",
    title: "Tai Nghe Airpods Max Apple Bản Không Gian Chống Ồn",
    price: 12490000,
    originalPrice: 13990000,
    discount: "-11%",
    rating: 4.8,
    soldCount: 189,
    images: [
      "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Chụp tai vòm lưới",
      "Khung thép không gỉ",
      "Núm xoay Digital Crown",
      "Phối trang phục thời thượng",
    ],
  },
  {
    id: 204,
    category: "fashion",
    title: "Ví Da Nam Cầm Tay Epsom Đen Thủ Công Phong Cách Pháp",
    price: 1850000,
    originalPrice: 2400000,
    discount: "-23%",
    rating: 4.9,
    soldCount: 420,
    images: [
      "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1606503829066-512aaee498e9?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Vân da dập Epsom",
      "Đường may chỉ sáp",
      "Ngăn thẻ & tiền",
      "Cầm tay phong cách quý ông",
    ],
  },
  {
    id: 205,
    category: "tech",
    title: "Máy Ảnh Mirrorless Fujifilm X-T5 Cổ Điển Kèm Ống Kính Kit",
    price: 43900000,
    originalPrice: 46500000,
    discount: "-6%",
    rating: 5.0,
    soldCount: 95,
    images: [
      "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1512790182412-b19e6d62bc39?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1495745966610-2a67f2297e5e?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Mặt trước phong cách Retro",
      "Vòng xoay kim loại cơ",
      "Màn hình lật đa hướng",
      "Chụp thực địa đường phố",
    ],
  },
  {
    id: 206,
    category: "fashion",
    title: "Áo Blazer Dạ Nam Thiết Kế Slimfit Chuẩn Phong Cách Ý",
    price: 2450000,
    originalPrice: 3200000,
    discount: "-23%",
    rating: 4.7,
    soldCount: 130,
    images: [
      "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1598808503746-f34c53b9323e?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1490114538077-0a7f8cb49891?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Dáng áo Slimfit",
      "Cận cảnh ve áo & cúc sừng",
      "Chất dạ cừu dệt mịn",
      "Phối tổng thể thanh lịch",
    ],
  },
  {
    id: 207,
    category: "watch",
    title: "Đồng Hồ Nữ Dây Kim Loại Citizen Eco-Drive Năng Lượng Ánh Sáng",
    price: 5200000,
    originalPrice: 6500000,
    discount: "-20%",
    rating: 4.8,
    soldCount: 215,
    images: [
      "https://images.unsplash.com/photo-1508615039623-a25605d2b022?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Khảm xà cừ mặt số",
      "Góc nghiêng viền đá",
      "Dây thép đan mắt nhỏ",
      "Đeo tay dạ tiệc sang trọng",
    ],
  },
  {
    id: 208,
    category: "audio",
    title: "Loa Di Động Marshall Emberton II Âm Thanh Đa Hướng",
    price: 3950000,
    originalPrice: 4600000,
    discount: "-14%",
    rating: 4.9,
    soldCount: 670,
    images: [
      "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Lưới tản nhiệt đồng thau",
      "Núm điều hướng kim loại",
      "Mặt sau chống nước IP67",
      "Cầm tay picnic dã ngoại",
    ],
  },
  {
    id: 209,
    category: "fashion",
    title: "Túi Xách Nữ Da Thật Quai Xách Sang Trọng Tone Beige",
    price: 3200000,
    originalPrice: 4100000,
    discount: "-22%",
    rating: 4.8,
    soldCount: 310,
    images: [
      "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Chính diện tone Beige",
      "Khóa kim loại mạ vàng",
      "Cận cảnh vân da bò",
      "Mix outfit dạo phố",
    ],
  },
  {
    id: 210,
    category: "tech",
    title: "Chuột Công Thái Học Không Dây Logitech MX Master 3S",
    price: 2190000,
    originalPrice: 2600000,
    discount: "-16%",
    rating: 5.0,
    soldCount: 890,
    images: [
      "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80",
    ],
    angles: [
      "Form dáng Ergonomic",
      "Con lăn MagSpeed thép",
      "Cụm nút ngón cái",
      "Setup bàn làm việc tối giản",
    ],
  },
];

// --------------------------------------------------------------------------
// ĐỒNG BỘ DỮ LIỆU SẢN PHẨM TỪ FASTAPI + SQL DATABASE
// --------------------------------------------------------------------------
// --------------------------------------------------------------------------
// ĐỒNG BỘ DỮ LIỆU TRANG CHỦ TỪ FASTAPI + TRẠNG THÁI LOADING / ERROR / EMPTY (TF1745E)
// --------------------------------------------------------------------------
let FLASH_PRODUCTS = [];
let RECOMMEND_PRODUCTS = [];
let LATEST_PRODUCTS = [];
let HOMEPAGE_CATEGORIES = [];
let HOMEPAGE_BANNERS = [];
let activeRecommendCategory = "all";

const DEFAULT_HOMEPAGE_BANNERS = [
  {
    title: "Âm Thanh Đỉnh Cao - Giảm 25%",
    description: "Bộ sưu tập tai nghe & loa Hi-End chính hãng",
    imageUrl: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80",
  },
  {
    title: "Đồng Hồ Cơ Thụy Sĩ Sang Trọng",
    description: "Khẳng định phong thái & đẳng cấp vượt thời gian",
    imageUrl: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80",
  },
  {
    title: "Thời Trang & Đồ Da Quý Ông",
    description: "Bộ sưu tập mới",
    imageUrl: "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=600&q=80",
  },
  {
    title: "Thiết Bị Số & PC",
    description: "Hiệu năng mạnh mẽ",
    imageUrl: "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80",
  },
];

const DEFAULT_HOMEPAGE_CATEGORIES = [
  { id: "audio", name: "Thiết Bị Âm Thanh", icon: "🎧" },
  { id: "watch", name: "Đồng Hồ Cao Cấp", icon: "⌚" },
  { id: "fashion", name: "Thời Trang & Đồ Da", icon: "👔" },
  { id: "tech", name: "Thiết Bị Số & PC", icon: "📱" },
];

function escapeHomepageHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function fetchHomepageJson(url, timeoutMs = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    if (!res.ok) {
      const err = new Error(`Máy chủ trả về mã lỗi HTTP ${res.status}`);
      err.status = res.status;
      throw err;
    }
    return await res.json();
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Kết nối API quá thời gian chờ (Timeout)");
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

function renderSectionLoadingState(section) {
  if (section === "banners") {
    const slidesEl = document.getElementById("bannerSlidesContainer");
    const sideEl = document.getElementById("sideBannersContainer");
    const arrowsEl = document.getElementById("sliderArrows");
    const dotsEl = document.getElementById("sliderDots");
    if (arrowsEl) arrowsEl.style.display = "none";
    if (dotsEl) dotsEl.innerHTML = "";
    if (slidesEl) {
      slidesEl.innerHTML = `
              <div class="section-state-box is-dark is-loading" style="border-radius: 0; border: none;">
                <div class="spinner-ring"></div>
                <div class="state-title">Đang tải banner trang chủ...</div>
                <div class="state-desc">Vui lòng đợi trong giây lát.</div>
              </div>`;
    }
    if (sideEl) {
      sideEl.innerHTML = `
              <div class="side-banner skeleton-block" style="background-image: none; min-height: 185px;"></div>
              <div class="side-banner skeleton-block" style="background-image: none; min-height: 185px;"></div>`;
    }
    return;
  }

  if (section === "categories") {
    const grid = document.getElementById("categoriesGrid");
    if (!grid) return;
    grid.innerHTML = Array.from({ length: 4 })
      .map(
        () => `
              <div class="skeleton-card" style="align-items: center;">
                <div class="skeleton-block" style="width: 48px; height: 48px; border-radius: 50%;"></div>
                <div class="skeleton-block" style="width: 75%; height: 14px;"></div>
              </div>`,
      )
      .join("");
    return;
  }

  const containerMap = {
    flash: "flashProductsContainer",
    recommend: "recommendProductsContainer",
    latest: "latestProductsContainer",
  };
  const el = document.getElementById(containerMap[section]);
  if (!el) return;
  el.innerHTML = Array.from({ length: 4 })
    .map(
      () => `
            <div class="skeleton-card">
              <div class="skeleton-block" style="width: 100%; height: 190px;"></div>
              <div class="skeleton-block" style="width: 88%; height: 16px;"></div>
              <div class="skeleton-block" style="width: 55%; height: 14px;"></div>
              <div class="skeleton-block" style="width: 100%; height: 34px; margin-top: 6px;"></div>
            </div>`,
    )
    .join("");
}

function renderSectionErrorState(section, errorMsg) {
  const safeMsg = escapeHomepageHtml(
    errorMsg || "Không thể kết nối máy chủ API.",
  );
  if (section === "banners") {
    const slidesEl = document.getElementById("bannerSlidesContainer");
    const sideEl = document.getElementById("sideBannersContainer");
    const arrowsEl = document.getElementById("sliderArrows");
    const dotsEl = document.getElementById("sliderDots");
    if (arrowsEl) arrowsEl.style.display = "none";
    if (dotsEl) dotsEl.innerHTML = "";
    if (slidesEl) {
      slidesEl.innerHTML = `
              <div class="section-state-box is-dark is-error" style="border-radius: 0; border: none;">
                <div class="state-icon">⚠️</div>
                <div class="state-title">Không tải được banner trang chủ</div>
                <div class="state-desc">${safeMsg}</div>
                <button class="btn-retry" onclick="retryHomepageSection('banners')">↻ Thử lại</button>
              </div>`;
    }
    if (sideEl) {
      sideEl.innerHTML = `
              <div class="section-state-box is-error" style="min-height: 185px; padding: 18px;">
                <div class="state-title" style="font-size: 14px;">Banner phụ chưa sẵn sàng</div>
                <div class="state-desc" style="font-size: 12px;">${safeMsg}</div>
              </div>`;
    }
    return;
  }

  const cfg = {
    categories: {
      id: "categoriesGrid",
      title: "Không tải được danh mục nổi bật",
    },
    flash: {
      id: "flashProductsContainer",
      title: "Không tải được sản phẩm Flash Sale",
    },
    recommend: {
      id: "recommendProductsContainer",
      title: "Không tải được sản phẩm gợi ý / nổi bật",
    },
    latest: {
      id: "latestProductsContainer",
      title: "Không tải được sản phẩm mới nhất",
    },
  }[section];
  const el = cfg && document.getElementById(cfg.id);
  if (!el) return;
  el.innerHTML = `
          <div class="section-state-box is-error">
            <div class="state-icon">⚠️</div>
            <div class="state-title">${cfg.title}</div>
            <div class="state-desc">${safeMsg}</div>
            <button class="btn-retry" onclick="retryHomepageSection('${section}')">↻ Thử lại</button>
          </div>`;
}

function renderSectionEmptyState(section, customTitle, customDesc) {
  if (section === "banners") {
    const slidesEl = document.getElementById("bannerSlidesContainer");
    const sideEl = document.getElementById("sideBannersContainer");
    const arrowsEl = document.getElementById("sliderArrows");
    const dotsEl = document.getElementById("sliderDots");
    if (arrowsEl) arrowsEl.style.display = "none";
    if (dotsEl) dotsEl.innerHTML = "";
    if (slidesEl) {
      slidesEl.innerHTML = `
              <div class="section-state-box is-dark is-empty" style="border-radius: 0; border: none;">
                <div class="state-icon">🖼️</div>
                <div class="state-title">${escapeHomepageHtml(customTitle || "Chưa có banner nào đang hoạt động")}</div>
                <div class="state-desc">${escapeHomepageHtml(customDesc || "Các chương trình khuyến mãi sẽ sớm được cập nhật.")}</div>
              </div>`;
    }
    if (sideEl) {
      sideEl.innerHTML = `
              <div class="section-state-box is-empty" style="min-height: 185px; padding: 18px;">
                <div class="state-icon" style="width: 38px; height: 38px; font-size: 18px;">📢</div>
                <div class="state-title" style="font-size: 14px;">Chưa có banner phụ</div>
              </div>`;
    }
    return;
  }

  const defaults = {
    categories: {
      id: "categoriesGrid",
      icon: "🗂️",
      title: "Chưa có danh mục hiển thị",
      desc: "Hiện chưa có danh mục sản phẩm nào được kích hoạt.",
    },
    flash: {
      id: "flashProductsContainer",
      icon: "⚡",
      title: "Chưa có sản phẩm Flash Sale nào đang chạy",
      desc: "Vui lòng quay lại sau để săn các deal giảm giá sốc.",
    },
    recommend: {
      id: "recommendProductsContainer",
      icon: "📦",
      title: "Hiện chưa có sản phẩm nào trên kệ",
      desc: "Không có sản phẩm phù hợp để hiển thị ở khu vực này.",
    },
    latest: {
      id: "latestProductsContainer",
      icon: "✨",
      title: "Chưa có sản phẩm mới nhất",
      desc: "Hiện chưa có sản phẩm mới nào vừa được đăng bán.",
    },
  }[section];
  const el = defaults && document.getElementById(defaults.id);
  if (!el) return;
  el.innerHTML = `
          <div class="section-state-box is-empty">
            <div class="state-icon">${defaults.icon}</div>
            <div class="state-title">${escapeHomepageHtml(customTitle || defaults.title)}</div>
            <div class="state-desc">${escapeHomepageHtml(customDesc || defaults.desc)}</div>
          </div>`;
}

function renderHomepageBanners(banners) {
  HOMEPAGE_BANNERS = Array.isArray(banners) ? banners : [];
  const slidesEl = document.getElementById("bannerSlidesContainer");
  const sideEl = document.getElementById("sideBannersContainer");
  const arrowsEl = document.getElementById("sliderArrows");
  const dotsEl = document.getElementById("sliderDots");

  if (HOMEPAGE_BANNERS.length === 0) {
    renderSectionEmptyState("banners");
    return;
  }

  const heroBanners = HOMEPAGE_BANNERS.slice(
    0,
    Math.max(1, HOMEPAGE_BANNERS.length - 2),
  );
  const subBanners =
    HOMEPAGE_BANNERS.length > 2 ? HOMEPAGE_BANNERS.slice(-2) : [];

  if (slidesEl) {
    slidesEl.innerHTML = heroBanners
      .map((b, idx) => {
        const title = escapeHomepageHtml(b.title || "Ưu đãi JML Store");
        const desc = escapeHomepageHtml(
          b.description || "Khám phá các sản phẩm chính hãng trên JML Store.",
        );
        const imgUrl = escapeHomepageHtml(
          b.imageUrl ||
            b.image_url ||
            "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=1200&q=80",
        );
        const Tag = idx === 0 ? "h1" : "h2";
        return `
                <div class="slide ${idx === 0 ? "active" : ""}" style="background-image: url('${imgUrl}');">
                  <div class="slide-content">
                    <span class="slide-tag">✨ JML Banner #${idx + 1}</span>
                    <${Tag} class="slide-title">${title}</${Tag}>
                    <p class="slide-desc">${desc}</p>
                    <button class="btn-hero" onclick="scrollToFlashSale()">
                      Khám Phá Ngay
                      <svg fill="none" height="16" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" width="16">
                        <path d="M5 12h14M12 5l7 7-7 7"></path>
                      </svg>
                    </button>
                  </div>
                </div>`;
      })
      .join("");
  }

  const hasMulti = heroBanners.length > 1;
  if (arrowsEl) arrowsEl.style.display = hasMulti ? "flex" : "none";
  if (dotsEl) {
    dotsEl.innerHTML = hasMulti
      ? heroBanners
          .map(
            (_, idx) =>
              `<div class="slider-dot ${idx === 0 ? "active" : ""}" data-index="${idx}"></div>`,
          )
          .join("")
      : "";
    dotsEl.querySelectorAll(".slider-dot").forEach((dot) => {
      dot.addEventListener("click", (e) => {
        const idx = parseInt(e.target.dataset.index, 10);
        showSlide(idx);
        resetSliderTimer();
      });
    });
  }

  if (sideEl) {
    if (subBanners.length === 0) {
      sideEl.innerHTML = `
              <div class="section-state-box is-empty" style="min-height: 185px; padding: 18px;">
                <div class="state-icon" style="width: 38px; height: 38px; font-size: 18px;">📢</div>
                <div class="state-title" style="font-size: 14px;">Chưa có banner phụ</div>
              </div>`;
    } else {
      sideEl.innerHTML = subBanners
        .map((b, idx) => {
          const title = escapeHomepageHtml(b.title || "Ưu đãi nổi bật");
          const desc = escapeHomepageHtml(b.description || "Khám phá ngay");
          return `
                  <div class="side-banner side-banner-${idx === 0 ? "1" : "2"}">
                    <span style="font-size: 11px; font-weight: 700; color: #fed7aa; text-transform: uppercase;">${desc}</span>
                    <h3 class="side-banner-title">${title}</h3>
                    <a class="side-banner-link" href="#flashSaleSection" onclick="scrollToFlashSale(); return false;">Khám phá chi tiết →</a>
                  </div>`;
        })
        .join("");
    }
  }

  currentSlide = 0;
  if (hasMulti) startSliderAutoPlay();
  else clearInterval(sliderInterval);
}

function renderHomepageCategories(categories) {
  HOMEPAGE_CATEGORIES = Array.isArray(categories) ? categories : [];
  const grid = document.getElementById("categoriesGrid");
  const tabsEl = document.getElementById("recommendTabs");

  if (tabsEl) {
    const catTabs = HOMEPAGE_CATEGORIES.map((c) => {
      const id = escapeHomepageHtml(c.id);
      const name = escapeHomepageHtml(c.name || c.id);
      return `<button class="tab-btn ${activeRecommendCategory === c.id ? "active" : ""}" onclick="filterCategory('${id}', this)">${name}</button>`;
    }).join("");
    tabsEl.innerHTML = `<button class="tab-btn ${activeRecommendCategory === "all" ? "active" : ""}" onclick="filterCategory('all', this)">Tất Cả</button>${catTabs}`;
  }

  if (!grid) return;
  if (HOMEPAGE_CATEGORIES.length === 0) {
    renderSectionEmptyState("categories");
    return;
  }

  grid.innerHTML = HOMEPAGE_CATEGORIES.map((c) => {
    const id = escapeHomepageHtml(c.id);
    const name = escapeHomepageHtml(c.name || c.id);
    const icon = escapeHomepageHtml(c.icon || "🛍️");
    return `
            <div class="category-card" onclick="filterCategory('${id}'); scrollToRecommend();">
              <div class="category-icon">${icon}</div>
              <div class="category-name">${name}</div>
            </div>`;
  }).join("");
}

function renderLatestProducts(items) {
  LATEST_PRODUCTS = Array.isArray(items) ? items : [];
  const container = document.getElementById("latestProductsContainer");
  if (!container) return;

  if (LATEST_PRODUCTS.length === 0) {
    renderSectionEmptyState("latest");
    return;
  }

  container.innerHTML = LATEST_PRODUCTS.map((product) => {
    const mainImg = product.images ? product.images[0] : product.image;
    return `
          <div class="product-card" onclick="openProductDetail(${product.id})">
            ${createCarouselMarkup(product)}
            <div class="product-body">
              <h3 class="product-title" title="${escapeHomepageHtml(product.title)}">${escapeHomepageHtml(product.title)}</h3>
              <div class="product-meta">
                <span class="rating-stars">★ ${product.rating}</span>
                <span>• Đã bán ${product.soldCount ?? product.sold ?? 0}</span>
              </div>
              <div class="price-row">
                <span class="current-price">${formatCurrency(product.price)}</span>
                <span class="original-price">${formatCurrency(product.originalPrice)}</span>
              </div>
              <div style="margin-top: auto;">
                <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${String(product.title || "").replace(/'/g, "\'")}', ${product.price}, '${mainImg}', '${String(product.shopName || "").replace(/'/g, "\'")}')">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                  Thêm Vào Giỏ
                </button>
              </div>
            </div>
          </div>`;
  }).join("");
  attachHoverCarouselListeners(container);
}

async function loadProductsFromFastAPI() {
  const params = new URLSearchParams(window.location.search);
  const forcedState = params.get("state");
  if (forcedState === "loading") {
    ["banners", "categories", "flash", "recommend", "latest"].forEach(
      renderSectionLoadingState,
    );
    return;
  }
  if (forcedState === "empty") {
    ["banners", "categories", "flash", "recommend", "latest"].forEach((s) =>
      renderSectionEmptyState(s),
    );
    return;
  }
  if (forcedState === "error") {
    ["banners", "categories", "flash", "recommend", "latest"].forEach((s) =>
      renderSectionErrorState(s, "Chế độ kiểm thử trạng thái lỗi API."),
    );
    return;
  }

  ["banners", "categories", "flash", "recommend", "latest"].forEach(
    renderSectionLoadingState,
  );

  try {
    const homeData = await fetchHomepageJson(`${API_BASE_URL}/api/homepage`);
    HOMEPAGE_BANNERS = homeData.banners || [];
    HOMEPAGE_CATEGORIES = homeData.categories || [];
    RECOMMEND_PRODUCTS = homeData.featured_products || [];
    LATEST_PRODUCTS = homeData.latest_products || [];

    renderHomepageBanners(HOMEPAGE_BANNERS);
    renderHomepageCategories(HOMEPAGE_CATEGORIES);
    renderRecommendProducts(activeRecommendCategory);
    renderLatestProducts(LATEST_PRODUCTS);

    try {
      const prodData = await fetchHomepageJson(`${API_BASE_URL}/api/products`);
      FLASH_PRODUCTS = prodData.flash_products || [];
      renderFlashSaleProducts();
    } catch (flashErr) {
      renderSectionErrorState("flash", flashErr.message);
    }
  } catch (err) {
    // Chạy ở chế độ Local nếu chưa bật server FastAPI
    console.warn("Chế độ Local/Offline do chưa kết nối API:", err.message);
    FLASH_PRODUCTS =
      JSON.parse(localStorage.getItem("JML_FLASH_PRODUCTS") || "null") ||
      DEFAULT_FLASH_PRODUCTS;
    RECOMMEND_PRODUCTS =
      JSON.parse(localStorage.getItem("JML_RECOMMEND_PRODUCTS") || "null") ||
      DEFAULT_RECOMMEND_PRODUCTS;
    LATEST_PRODUCTS = [...RECOMMEND_PRODUCTS, ...FLASH_PRODUCTS].sort(
      (a, b) => (b.id || 0) - (a.id || 0),
    );
    renderHomepageBanners(DEFAULT_HOMEPAGE_BANNERS);
    renderHomepageCategories(DEFAULT_HOMEPAGE_CATEGORIES);
    renderFlashSaleProducts();
    renderRecommendProducts(activeRecommendCategory);
    renderLatestProducts(LATEST_PRODUCTS);
  }
}

async function loadProductsFallbackFromAPI() {
  try {
    const data = await fetchHomepageJson(`${API_BASE_URL}/api/products`);
    FLASH_PRODUCTS = Array.isArray(data.flash_products)
      ? data.flash_products
      : [];
    RECOMMEND_PRODUCTS = Array.isArray(data.recommend_products)
      ? data.recommend_products
      : [];
    LATEST_PRODUCTS = [...RECOMMEND_PRODUCTS, ...FLASH_PRODUCTS].sort(
      (a, b) => (b.id || 0) - (a.id || 0),
    );
    renderFlashSaleProducts();
    renderRecommendProducts(activeRecommendCategory);
    renderLatestProducts(LATEST_PRODUCTS);
  } catch (err) {
    renderSectionErrorState("flash", err.message);
    renderSectionErrorState("recommend", err.message);
    renderSectionErrorState("latest", err.message);
  }
}

async function retryHomepageSection(section) {
  renderSectionLoadingState(section);
  try {
    if (section === "banners") {
      const data = await fetchHomepageJson(
        `${API_BASE_URL}/api/homepage/banners`,
      );
      renderHomepageBanners(data.banners || []);
    } else if (section === "categories") {
      try {
        const data = await fetchHomepageJson(
          `${API_BASE_URL}/api/homepage/categories`,
        );
        renderHomepageCategories(data.categories || []);
      } catch (e) {
        if (e.status === 404) {
          const catData = await fetchHomepageJson(
            `${API_BASE_URL}/api/categories`,
          );
          renderHomepageCategories(catData.categories || []);
        } else {
          throw e;
        }
      }
    } else if (section === "flash") {
      const data = await fetchHomepageJson(`${API_BASE_URL}/api/products`);
      FLASH_PRODUCTS = data.flash_products || [];
      renderFlashSaleProducts();
    } else if (section === "recommend") {
      try {
        const data = await fetchHomepageJson(
          `${API_BASE_URL}/api/homepage/featured-products`,
        );
        RECOMMEND_PRODUCTS = data.featured_products || [];
        renderRecommendProducts(activeRecommendCategory);
      } catch (e) {
        if (e.status === 404) {
          const data = await fetchHomepageJson(`${API_BASE_URL}/api/products`);
          RECOMMEND_PRODUCTS = data.recommend_products || [];
          renderRecommendProducts(activeRecommendCategory);
        } else {
          throw e;
        }
      }
    } else if (section === "latest") {
      try {
        const data = await fetchHomepageJson(
          `${API_BASE_URL}/api/homepage/latest-products`,
        );
        LATEST_PRODUCTS = data.latest_products || [];
        renderLatestProducts(LATEST_PRODUCTS);
      } catch (e) {
        if (e.status === 404) {
          const data = await fetchHomepageJson(`${API_BASE_URL}/api/products`);
          LATEST_PRODUCTS = [
            ...(data.recommend_products || []),
            ...(data.flash_products || []),
          ].sort((a, b) => (b.id || 0) - (a.id || 0));
          renderLatestProducts(LATEST_PRODUCTS);
        } else {
          throw e;
        }
      }
    }
  } catch (err) {
    renderSectionErrorState(section, err.message);
  }
}

window.addEventListener("storage", () => {
  loadProductsFromFastAPI();
});
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) loadProductsFromFastAPI();
});

// Dữ liệu mô tả chi tiết & thông số kỹ thuật bổ sung cho trang chi tiết
const PRODUCT_EXTRA_INFO = {
  101: {
    brand: "Sony",
    origin: "Nhật Bản / Lắp ráp Malaysia",
    warranty: "12 tháng chính hãng Sony Việt Nam",
    desc: "Tai nghe chống ồn không dây Sony WH-1000XM5 sở hữu công nghệ dẫn đầu ngành với hai bộ xử lý chuyên dụng V1 và HD QN1, kiểm soát 8 micro để triệt tiêu tiếng ồn một cách triệt để nhất. Thiết kế driver 30mm sử dụng màng vòm sợi carbon siêu cứng cho chất âm tinh tế, truyền tải chuẩn xác từng nốt nhạc Hi-Res Audio Wireless LDAC.",
    specs: [
      { key: "Thương hiệu", val: "Sony" },
      { key: "Dòng sản phẩm", val: "WH-1000XM5 Flagship Series" },
      {
        key: "Bộ xử lý chống ồn",
        val: "Dual Processor V1 & HD Noise Cancelling QN1",
      },
      {
        key: "Thời lượng pin",
        val: "30 giờ (bật ANC), 40 giờ (tắt ANC)",
      },
      { key: "Cổng sạc", val: "USB Type-C hỗ trợ chuẩn Power Delivery" },
      { key: "Trọng lượng", val: "250g (thiết kế siêu nhẹ đệm da mềm)" },
      {
        key: "Tính năng thông minh",
        val: "Speak-to-Chat, Quick Attention, Auto NC Optimizer",
      },
    ],
    colors: ["Đen Black Edition", "Bạc Silver White", "Xanh Midnight Blue"],
  },
  102: {
    brand: "Tissot 1853",
    origin: "Thụy Sĩ (Swiss Made)",
    warranty: "24 tháng quốc tế chính hãng",
    desc: "Tissot Le Locle Powermatic 80 là dòng đồng hồ cơ tự động kinh điển tôn vinh thị trấn Le Locle - cái nôi đồng hồ Thụy Sĩ. Mặt số được chạm trổ hoa văn Guilloche Clous de Paris tinh xảo, cọc số La Mã mang đậm phong thái quý tộc cổ điển. Trái tim là cỗ máy cơ Powermatic 80 trữ cót lên đến 80 giờ hoạt động bền bỉ.",
    specs: [
      { key: "Thương hiệu", val: "Tissot 1853" },
      { key: "Xuất xứ", val: "Thụy Sĩ (Swiss Made)" },
      {
        key: "Bộ máy cơ",
        val: "Automatic Powermatic 80.111 (23 chân kính)",
      },
      { key: "Thời gian trữ cót", val: "80 giờ bền bỉ" },
      { key: "Đường kính mặt", val: "39.3 mm • Độ dày 9.8 mm" },
      {
        key: "Kính bảo vệ",
        val: "Sapphire nguyên khối chống trầy xước tuyệt đối",
      },
      {
        key: "Chất liệu vỏ & dây",
        val: "Thép không gỉ 316L mạ công nghệ PVD cao cấp",
      },
    ],
    colors: [
      "Bạc Mặt Trắng Cổ Điển",
      "Vàng Demi Hoàng Gia",
      "Mặt Đen Lịch Lãm",
    ],
  },
  201: {
    brand: "Apple Inc.",
    origin: "Hoa Kỳ / Lắp ráp chính hãng",
    warranty: "12 tháng Apple Care toàn quốc",
    desc: "iPad Pro M4 11-inch hoàn toàn mới là bước nhảy vọt công nghệ với độ mỏng khó tin chỉ 5.1mm, tích hợp vi xử lý Apple M4 thế hệ tiếp theo mang lại hiệu năng đồ họa và trí tuệ nhân tạo vượt trội. Màn hình Ultra Retina XDR sử dụng công nghệ Tandem OLED đột phá với độ sáng tối đa 1600 nits.",
    specs: [
      { key: "Thương hiệu", val: "Apple" },
      {
        key: "Vi xử lý",
        val: "Apple M4 Chip (10-core CPU, 10-core GPU, 16-core NPU)",
      },
      {
        key: "Màn hình",
        val: "11 inch Ultra Retina XDR Tandem OLED 120Hz ProMotion",
      },
      {
        key: "Độ sáng tối đa",
        val: "1600 nits (HDR content), 1000 nits tiêu chuẩn",
      },
      { key: "Bộ nhớ", val: "256GB / 512GB / 1TB / 2TB Ultra Fast SSD" },
      {
        key: "Độ mỏng",
        val: "5.1 mm (Chiếc iPad mỏng nhất lịch sử Apple)",
      },
      {
        key: "Hỗ trợ phụ kiện",
        val: "Apple Pencil Pro, Magic Keyboard M4",
      },
    ],
    colors: ["Đen Không Gian (Space Black)", "Bạc Ánh Kim (Silver)"],
  },
};

// Trạng thái Giỏ hàng (Cart state)
let cartItems = [];
const CART_STORAGE_KEY = "JML_CART_ITEMS";

function readStoredCart() {
  try {
    const storedCart = JSON.parse(
      localStorage.getItem(CART_STORAGE_KEY) || "[]",
    );
    return Array.isArray(storedCart) ? storedCart : [];
  } catch (error) {
    return [];
  }
}

function restoreCartFromStorage() {
  cartItems = readStoredCart();
  updateCartDisplay();
}

function parseCartItemImg(raw) {
  const fallback =
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=200&q=60";
  if (!raw) return fallback;
  try {
    const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
    return Array.isArray(parsed) && parsed.length > 0 ? parsed[0] : fallback;
  } catch (e) {
    return typeof raw === "string" ? raw : fallback;
  }
}

function triggerCartBadgeBounce() {
  const badges = [
    document.getElementById("cartCountBadge"),
    document.getElementById("cartBadgeCount"),
  ];
  badges.forEach((badge) => {
    if (badge) {
      badge.classList.remove("bounce");
      void badge.offsetWidth; // Trigger reflow
      badge.classList.add("bounce");
    }
  });
}

async function syncCartAfterLogin() {
  // TF17097: Đồng bộ giỏ hàng và biểu tượng giỏ ở header sau khi đăng nhập
  const user =
    (typeof Auth !== "undefined" ? Auth.getUser() : null) ||
    JSON.parse(localStorage.getItem("JML_CUSTOMER_USER") || "null") ||
    JSON.parse(localStorage.getItem("JML_AUTH_USER") || "null");

  // 1. Nếu chưa đăng nhập: Khôi phục giỏ hàng cục bộ (guest cart)
  if (!user || !user.id) {
    restoreCartFromStorage();
    return;
  }

  const localItems = readStoredCart();

  try {
    // 2. Nếu khách có món trong giỏ trước khi đăng nhập, đẩy đồng bộ lên API backend
    if (localItems.length > 0) {
      for (const it of localItems) {
        const prodId = it.id || it.product_id;
        const qty = it.qty || it.quantity || 1;
        if (prodId) {
          try {
            await fetch(`${API_BASE_URL}/api/cart/items`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                user_id: user.id,
                product_id: prodId,
                quantity: qty,
              }),
            });
          } catch (e) {
            // Bỏ qua lỗi nếu 1 sản phẩm không thể thêm (hết hàng, ...)
          }
        }
      }
    }

    // 3. Tải giỏ hàng cập nhật nhất từ Backend API
    const res = await fetch(`${API_BASE_URL}/api/cart/${user.id}`);
    if (res.ok) {
      const data = await res.json();
      const serverItems = data.items || [];
      cartItems = serverItems.map((it) => ({
        id: it.product_id,
        product_id: it.product_id,
        cartItemId: it.cart_item_id,
        title: it.title,
        price: it.price || it.unit_price || it.cart_price,
        originalPrice: it.price || it.unit_price,
        image: it.images_json ? parseCartItemImg(it.images_json) : (it.image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=200&q=60"),
        qty: it.quantity,
        shopName: it.shop_name || "JML Store",
      }));
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
    } else {
      restoreCartFromStorage();
    }
  } catch (err) {
    console.warn("Không thể kết nối API giỏ hàng, giữ giỏ cục bộ:", err);
    restoreCartFromStorage();
  }

  // 4. Cập nhật số lượng món trên biểu tượng giỏ ở header và dropdown
  updateCartDisplay();
  triggerCartBadgeBounce();

  // Đồng bộ lại view cart SPA nếu đang hiển thị
  if (typeof cvRender === "function") {
    cvRender();
  }
}

// Helper format tiền tệ VNĐ
function formatCurrency(amount) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(amount);
}

function getCategoryName(cat) {
  switch (cat) {
    case "audio":
      return "Thiết Bị Âm Thanh";
    case "watch":
      return "Đồng Hồ Cao Cấp";
    case "fashion":
      return "Thời Trang & Đồ Da";
    case "tech":
      return "Thiết Bị Số & Công Nghệ";
    default:
      return "Sản Phẩm Cao Cấp";
  }
}

function getProductById(id) {
  const numId = parseInt(id, 10);
  return (
    FLASH_PRODUCTS.find((p) => p.id === numId) ||
    RECOMMEND_PRODUCTS.find((p) => p.id === numId) ||
    FLASH_PRODUCTS[0]
  );
}

// Helper tạo cấu trúc Multi-Image Carousel bên trong khung ảnh sản phẩm
function createCarouselMarkup(product) {
  const images = product.images || [product.image];
  const angles = product.angles || [
    "Chính diện",
    "Góc nghiêng",
    "Cận cảnh",
    "Thực tế",
  ];

  const imagesHtml = images
    .map(
      (img, idx) => `
        <img src="${img}" alt="${product.title} - ${angles[idx] || "Góc " + (idx + 1)}" class="product-slide-img ${idx === 0 ? "active" : ""}" data-index="${idx}" loading="lazy">
      `,
    )
    .join("");

  const dotsHtml = images
    .map(
      (_, idx) => `
        <span class="product-mini-dot ${idx === 0 ? "active" : ""}" data-dot-index="${idx}"></span>
      `,
    )
    .join("");

  const angleBadgeHtml = `
        <span class="product-angle-badge" data-badge>${angles[0] || "Ảnh 1"}</span>
      `;

  return `
        <div class="product-img-wrapper" data-carousel-id="${product.id}" data-angles='${JSON.stringify(angles).replace(/'/g, "&apos;")}'>
          <span class="discount-tag">${product.discount}</span>
          ${product.exclusive ? `<span class="exclusive-tag">${product.exclusive}</span>` : ""}
          <div class="product-carousel-track">
            ${imagesHtml}
          </div>
          <div class="product-mini-indicators">
            ${dotsHtml}
          </div>
          ${angleBadgeHtml}
        </div>
      `;
}

// --------------------------------------------------------------------------
// 1. RENDER SẢN PHẨM FLASH SALE & GỢI Ý
// --------------------------------------------------------------------------
function renderFlashSaleProducts() {
  const container = document.getElementById("flashProductsContainer");
  if (!container) return;
  if (!FLASH_PRODUCTS || FLASH_PRODUCTS.length === 0) {
    container.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 36px 16px; background: #fff; border-radius: 16px; border: 1px dashed #cbd5e1; margin: 8px 0;">
              <p style="font-weight: 600; font-size: 14px; color: #64748b;">Chưa có sản phẩm Flash Sale nào đang chạy</p>
            </div>
          `;
    return;
  }
  container.innerHTML = FLASH_PRODUCTS.map((product) => {
    const percentSold = Math.round((product.sold / product.totalStock) * 100);
    const mainImg = product.images ? product.images[0] : product.image;
    return `
          <div class="product-card" onclick="openProductDetail(${product.id})">
            ${createCarouselMarkup(product)}
            <div class="product-body">
              <h3 class="product-title" title="${product.title}">${product.title}</h3>
              <div class="product-meta">
                <span class="rating-stars">★ ${product.rating}</span>
                <span>• Đã bán ${product.sold}</span>
              </div>
              <div class="price-row">
                <span class="current-price">${formatCurrency(product.price)}</span>
                <span class="original-price">${formatCurrency(product.originalPrice)}</span>
              </div>
              <div class="progress-box">
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill" style="width: ${percentSold}%;"></div>
                </div>
                <div class="progress-text">
                  <span>Đã bán ${product.sold}/${product.totalStock}</span>
                  <span>${percentSold}%</span>
                </div>
              </div>
              <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${product.title.replace(/'/g, "\\'")}', ${product.price}, '${mainImg}', '${(product.shopName || "").replace(/'/g, "\\'")}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                Thêm Vào Giỏ
              </button>
            </div>
          </div>
        `;
  }).join("");
  attachHoverCarouselListeners(container);
}

function renderRecommendProducts(category = "all") {
  const container = document.getElementById("recommendProductsContainer");
  if (!container) return;
  const filtered =
    category === "all"
      ? RECOMMEND_PRODUCTS
      : RECOMMEND_PRODUCTS.filter((p) => p.category === category);

  if (!filtered || filtered.length === 0) {
    container.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 48px 16px; background: #fff; border-radius: 16px; border: 1px dashed #cbd5e1; margin: 16px 0;">
              <div style="font-size: 36px; margin-bottom: 8px;">📦</div>
              <p style="font-weight: 700; font-size: 15px; color: #334155; margin-bottom: 4px;">Hiện chưa có sản phẩm nào trên kệ</p>
              <p style="font-size: 13px; color: #64748b;">Admin có thể thêm sản phẩm mới từ trang Quản trị Sàn để xuất hiện tại đây.</p>
            </div>
          `;
    return;
  }

  container.innerHTML = filtered
    .map((product) => {
      const mainImg = product.images ? product.images[0] : product.image;
      return `
          <div class="product-card" onclick="openProductDetail(${product.id})">
            ${createCarouselMarkup(product)}
            <div class="product-body">
              <h3 class="product-title" title="${product.title}">${product.title}</h3>
              <div class="product-meta">
                <span class="rating-stars">★ ${product.rating}</span>
                <span>• Đã bán ${product.soldCount}</span>
              </div>
              <div class="price-row">
                <span class="current-price">${formatCurrency(product.price)}</span>
                <span class="original-price">${formatCurrency(product.originalPrice)}</span>
              </div>
              <div style="margin-top: auto;">
                <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${product.title.replace(/'/g, "\\'")}', ${product.price}, '${mainImg}', '${(product.shopName || "").replace(/'/g, "\\'")}')">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                  Thêm Vào Giỏ
                </button>
              </div>
            </div>
          </div>
        `;
    })
    .join("");
  attachHoverCarouselListeners(container);
}

// --------------------------------------------------------------------------
// CƠ CHẾ HOVER CAROUSEL TỰ ĐỘNG CHUYỂN GÓC CHỤP SẢN PHẨM TRÊN CARD (1.1s/lần)
// --------------------------------------------------------------------------
function attachHoverCarouselListeners(parentContainer) {
  const wrappers = parentContainer.querySelectorAll(".product-img-wrapper");

  wrappers.forEach((wrapper) => {
    const slides = wrapper.querySelectorAll(".product-slide-img");
    const dots = wrapper.querySelectorAll(".product-mini-dot");
    const badge = wrapper.querySelector("[data-badge]");

    let angles = [];
    try {
      angles = JSON.parse(wrapper.dataset.angles || "[]");
    } catch (e) {
      angles = [];
    }

    if (slides.length <= 1) return;

    let activeIdx = 0;
    let timer = null;

    function setSlide(idx) {
      activeIdx = idx % slides.length;
      slides.forEach((s, i) => {
        s.classList.toggle("active", i === activeIdx);
      });
      dots.forEach((d, i) => {
        d.classList.toggle("active", i === activeIdx);
      });
      if (badge && angles[activeIdx]) {
        badge.textContent = angles[activeIdx];
      }
    }

    // Cho phép hover vào từng dot để chuyển góc ngay tức khắc
    dots.forEach((dot, dotIdx) => {
      dot.addEventListener("mouseenter", (e) => {
        e.stopPropagation();
        clearInterval(timer);
        setSlide(dotIdx);
      });
    });

    // Tự động chuyển lần lượt mỗi 1.1 giây khi người dùng hover chuột
    wrapper.addEventListener("mouseenter", () => {
      clearInterval(timer);
      timer = setInterval(() => {
        setSlide(activeIdx + 1);
      }, 1100);
    });

    // Khi rê chuột ra ngoài (mouseleave), tự động trở về ảnh đại diện ban đầu
    wrapper.addEventListener("mouseleave", () => {
      clearInterval(timer);
      setSlide(0);
    });
  });
}

// --------------------------------------------------------------------------
// 2. MÀN HÌNH CHI TIẾT SẢN PHẨM (SINGLE PAGE APPLICATION DETAIL VIEW)
// --------------------------------------------------------------------------
let currentDetailProduct = null;
let currentDetailQty = 1;
let currentSelectedColor = "";
let currentSelectedVersion = "";

function openProductDetail(productId) {
  const product = getProductById(productId);
  if (!product) return;
  currentDetailProduct = product;
  currentDetailQty = 1;

  // Lấy thông tin mở rộng hoặc tạo thông số mặc định phù hợp
  const extra = PRODUCT_EXTRA_INFO[product.id] || {
    brand: "Thương Hiệu Cao Cấp",
    origin: "Nhập khẩu chính hãng",
    warranty: "24 tháng chính hãng JML Store",
    desc: `${product.title} là sản phẩm hàng đầu trong bộ sưu tập cao cấp, được chế tác tỉ mỉ từ những vật liệu tinh hoa nhất. Sản phẩm đáp ứng tiêu chuẩn khắt khe về độ hoàn thiện, tính thẩm mỹ và độ bền bỉ dài lâu.`,
    specs: [
      { key: "Tên sản phẩm", val: product.title },
      { key: "Danh mục", val: getCategoryName(product.category) },
      {
        key: "Tiêu chuẩn kiểm duyệt",
        val: "100% Chính hãng phân phối độc quyền",
      },
      { key: "Tình trạng", val: "Mới 100% nguyên hộp kèm thẻ bảo hành" },
      { key: "Bảo hành", val: "24 tháng đổi mới trong 30 ngày nếu lỗi" },
    ],
    colors: ["Màu Tiêu Chuẩn (Mặc định)", "Phiên Bản Giới Hạn"],
  };

  const images = product.images || [product.image];
  const angles = product.angles || [
    "Chính diện",
    "Góc nghiêng",
    "Cận cảnh",
    "Thực tế",
  ];
  const totalStockVal = Number(product.totalStock ?? 100);
  const soldVal = Number(product.sold ?? product.soldCount ?? 0);
  const availableStock =
    product.stock !== undefined && product.stock !== null
      ? Math.max(0, Number(product.stock))
      : Math.max(0, totalStockVal - soldVal);
  product.availableStock = availableStock;
  currentDetailQty = availableStock > 0 ? 1 : 0;
  const isOutOfStock = availableStock <= 0;
  const stockBadgeClass = isOutOfStock ? "stock-out" : availableStock <= 10 ? "stock-low" : "stock-in";
  const stockBadgeText = isOutOfStock
    ? "Hết hàng"
    : availableStock <= 10
    ? `Sắp hết hàng (còn ${availableStock})`
    : `Còn hàng (${availableStock} sẵn có)`;
  currentSelectedColor = extra.colors[0];
  currentSelectedVersion = "Bản Tiêu Chuẩn";

  const detailContainer = document.getElementById("view-product-detail");
  const homeContainer = document.getElementById("view-home");

  // Gợi ý 4 sản phẩm cùng phân khúc
  const relatedList = RECOMMEND_PRODUCTS.filter(
    (p) => p.id !== product.id,
  ).slice(0, 4);
  const relatedCardsHtml = relatedList
    .map((rel) => {
      const relImg = rel.images ? rel.images[0] : rel.image;
      return `
            <div class="product-card" onclick="openProductDetail(${rel.id})">
              ${createCarouselMarkup(rel)}
              <div class="product-body">
                <h3 class="product-title" title="${rel.title}">${rel.title}</h3>
                <div class="product-meta">
                  <span class="rating-stars">★ ${rel.rating}</span>
                  <span>• Đã bán ${rel.soldCount}</span>
                </div>
                <div class="price-row">
                  <span class="current-price">${formatCurrency(rel.price)}</span>
                  <span class="original-price">${formatCurrency(rel.originalPrice)}</span>
                </div>
                <div style="margin-top: auto;">
                  <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${rel.title.replace(/'/g, "\\'")}', ${rel.price}, '${relImg}', '${(rel.shopName || "").replace(/'/g, "\\'")}')">
                    Thêm Vào Giỏ
                  </button>
                </div>
              </div>
            </div>
          `;
    })
    .join("");

  detailContainer.innerHTML = `
          <div class="product-detail-wrapper">
            <!-- Breadcrumb Navigation -->
            <div class="detail-breadcrumb-bar">
              <button class="btn-back-home" onclick="showHomeView()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                Quay Lại Danh Sách
              </button>
              <div class="breadcrumb-trail">
                <a href="#" onclick="showHomeView(); return false;">Trang Chủ</a>
                <span>/</span>
                <span class="breadcrumb-cat" onclick="filterCategory('${product.category || "all"}'); showHomeView(); scrollToRecommend();" style="cursor: pointer;">${getCategoryName(product.category)}</span>
                <span>/</span>
                <span class="breadcrumb-current" title="${product.title}">${product.title}</span>
              </div>
            </div>

            <!-- Product Showcase Grid -->
            <div class="product-showcase-grid">
              <!-- Left Column: Gallery & Angle Selector -->
              <div class="showcase-gallery">
                <div class="main-image-viewport">
                  <span class="detail-discount-tag">${product.discount}</span>
                  ${product.exclusive ? `<span class="detail-exclusive-tag">${product.exclusive}</span>` : ""}
                  <span class="detail-angle-indicator" id="detailAngleBadge">${angles[0]}</span>
                  <img id="detailMainImg" src="${images[0]}" alt="${product.title}">
                </div>

                <!-- Thumbnail angles row -->
                <div class="gallery-thumbs-row">
                  ${images
                    .map(
                      (img, idx) => `
                    <div class="gallery-thumb-item ${idx === 0 ? "active" : ""}" onclick="switchDetailImage(${idx}, '${img}', '${angles[idx] || "Góc " + (idx + 1)}')">
                      <img src="${img}" alt="${angles[idx]}">
                      <span>${angles[idx] || "Ảnh " + (idx + 1)}</span>
                    </div>
                  `,
                    )
                    .join("")}
                </div>

                <!-- Trust Guarantees Box -->
                <div class="trust-features-grid">
                  <div class="trust-item">
                    <div class="trust-icon">🛡️</div>
                    <div>
                      <strong>100% Chính Hãng</strong>
                      <span>Đền bù 200% nếu phát hiện giả</span>
                    </div>
                  </div>
                  <div class="trust-item">
                    <div class="trust-icon">🔄</div>
                    <div>
                      <strong>Đổi Trả 30 Ngày</strong>
                      <span>Miễn phí 100% nếu có lỗi từ NSX</span>
                    </div>
                  </div>
                  <div class="trust-item">
                    <div class="trust-icon">🚀</div>
                    <div>
                      <strong>Giao Hỏa Tốc 2H</strong>
                      <span>Nội thành Hà Nội & TP.HCM</span>
                    </div>
                  </div>
                  <div class="trust-item">
                    <div class="trust-icon">💎</div>
                    <div>
                      <strong>Bảo Hành 24 Tháng</strong>
                      <span>Bảo hành điện tử chính hãng</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right Column: Purchasing & Details -->
              <div class="showcase-info">
                <div class="detail-mall-badge">
                  <span class="mall-pill">✓ JML OFFICIAL MALL</span>
                  <span class="sku-pill">MÃ SP: #LX-${product.id}</span>
                </div>

                <h1 class="detail-product-title">${product.title}</h1>

                <div class="detail-meta-row">
                  <div class="meta-rating">
                    <span class="stars">★★★★★</span>
                    <strong>${product.rating}</strong>
                  </div>
                  <span>•</span>
                  <span class="meta-reviews">184 Đánh giá thực tế</span>
                  <span>•</span>
                  <span class="meta-sold">Đã bán ${product.sold || product.soldCount || 120}</span>
                </div>

                <!-- Price Box -->
                <div class="detail-price-box">
                  <div class="price-header">
                    <span class="price-label">Giá Ưu Đãi Độc Quyền</span>
                    <span class="deal-pill">⚡ FLASH SALE TIẾT KIỆM</span>
                  </div>
                  <div class="price-numbers">
                    <span class="detail-current-price">${formatCurrency(product.price)}</span>
                    <span class="detail-original-price">${formatCurrency(product.originalPrice)}</span>
                    <span class="detail-save-badge">Tiết kiệm ${formatCurrency(product.originalPrice - product.price)} (${product.discount})</span>
                  </div>
                  <div class="price-voucher-notice">
                    🎁 Tặng Voucher 100K cho thành viên VIP • Miễn phí vận chuyển toàn quốc
                  </div>
                </div>

                <!-- Variant: Màu Sắc -->
                <div class="variant-section">
                  <div class="variant-title">
                    <span>Chọn Màu Sắc:</span>
                    <strong id="selectedColorLabel">${extra.colors[0]}</strong>
                  </div>
                  <div class="variant-options">
                    ${extra.colors
                      .map(
                        (c, i) => `
                      <button class="variant-btn ${i === 0 ? "active" : ""}" onclick="selectVariant(this, 'selectedColorLabel', '${c}')">
                        <span class="color-dot" style="background: ${i === 0 ? "#111827" : i === 1 ? "#94a3b8" : "#cbd5e1"};"></span>
                        ${c}
                      </button>
                    `,
                      )
                      .join("")}
                  </div>
                </div>

                <!-- Variant: Phiên Bản -->
                <div class="variant-section">
                  <div class="variant-title">
                    <span>Phiên Bản / Dung Lượng:</span>
                    <strong id="selectedVersionLabel">Bản Tiêu Chuẩn (Fullbox)</strong>
                  </div>
                  <div class="variant-options">
                    <button class="variant-btn active" onclick="selectVariant(this, 'selectedVersionLabel', 'Bản Tiêu Chuẩn (Fullbox)')">
                      Bản Tiêu Chuẩn (Fullbox)
                    </button>
                    <button class="variant-btn" onclick="selectVariant(this, 'selectedVersionLabel', 'Bản Nâng Cấp Kèm Quà Tặng')">
                      Bản Nâng Cấp Kèm Quà Tặng
                    </button>
                  </div>
                </div>

                <!-- Quantity Picker -->
                <div class="quantity-section" style="flex-wrap: wrap;">
                  <span class="qty-label">Số Lượng:</span>
                  <div class="qty-picker">
                    <button type="button" id="detailQtyDecBtn" onclick="changeDetailQty(-1)" ${isOutOfStock || currentDetailQty <= 1 ? "disabled" : ""}>−</button>
                    <input type="number" id="detailQtyInput" value="${currentDetailQty}" min="${isOutOfStock ? 0 : 1}" max="${availableStock}" ${isOutOfStock ? "disabled" : ""} onchange="onSpaDetailQtyInput(this.value)">
                    <button type="button" id="detailQtyIncBtn" onclick="changeDetailQty(1)" ${isOutOfStock || currentDetailQty >= availableStock ? "disabled" : ""}>+</button>
                  </div>
                  <span class="stock-badge ${stockBadgeClass}">${stockBadgeText}</span>
                  <span class="stock-remain">${isOutOfStock ? "Sản phẩm hiện tạm hết hàng" : `Còn lại <strong>${availableStock}</strong> sản phẩm trong kho`}</span>
                </div>

                <!-- CTA Action Buttons -->
                <div class="detail-actions-row">
                  <button class="btn-detail-add-cart" onclick="addCurrentDetailToCart()" ${isOutOfStock ? "disabled" : ""}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                    ${isOutOfStock ? "Tạm Hết Hàng" : "Thêm Vào Giỏ Hàng"}
                  </button>
                  <button class="btn-detail-buy-now" onclick="buyCurrentDetailNow()" ${isOutOfStock ? "disabled" : ""}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                    Mua Ngay Với Giá Ưu Đãi
                  </button>
                </div>

                <!-- Shipping Summary Box -->
                <div class="shipping-info-card">
                  <div class="shipping-row">
                    <span>📍 Địa chỉ nhận hàng:</span>
                    <strong>Tòa nhà Discovery Complex, Cầu Giấy, Hà Nội</strong>
                    <a href="#" onclick="showToast('Vị trí', 'Cập nhật địa chỉ nhận hàng'); return false;" style="color: var(--primary); font-weight: 600; margin-left: auto;">Thay đổi</a>
                  </div>
                  <div class="shipping-row">
                    <span>🚚 Vận chuyển:</span>
                    <strong style="color: var(--success);">Miễn phí vận chuyển hỏa tốc</strong>
                    <span style="color: var(--text-muted);">(Dự kiến nhận hàng trong ngày mai)</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tabbed Detailed Info Section -->
            <div class="detail-tabs-section">
              <div class="detail-tab-nav">
                <button class="detail-tab-btn active" onclick="switchDetailTab('tab-desc', this)">Mô Tả Sản Phẩm</button>
                <button class="detail-tab-btn" onclick="switchDetailTab('tab-specs', this)">Thông Số Kỹ Thuật</button>
                <button class="detail-tab-btn" onclick="switchDetailTab('tab-reviews', this)">Đánh Giá Khách Hàng (184)</button>
                <button class="detail-tab-btn" onclick="switchDetailTab('tab-policy', this)">Chính Sách & Bảo Hành</button>
              </div>

              <!-- Tab 1: Mô tả -->
              <div id="tab-desc" class="detail-tab-pane active">
                <p style="margin-bottom: 16px; font-size: 15px;">${extra.desc}</p>
                <h4 style="font-size: 16px; font-weight: 700; color: var(--secondary); margin: 20px 0 10px;">Đặc Điểm Nổi Bật</h4>
                <ul style="padding-left: 20px; display: flex; flex-direction: column; gap: 8px;">
                  <li>Thiết kế công thái học hiện đại, tôn vinh đẳng cấp người sử dụng.</li>
                  <li>Sử dụng linh kiện cao cấp từ nhà sản xuất uy tín toàn cầu.</li>
                  <li>Kiểm định chất lượng nghiêm ngặt trước khi xuất xưởng và giao đến tay người tiêu dùng.</li>
                  <li>Tích hợp đầy đủ phụ kiện chính hãng nguyên hộp.</li>
                </ul>
              </div>

              <!-- Tab 2: Thông số kỹ thuật -->
              <div id="tab-specs" class="detail-tab-pane">
                <table class="spec-table">
                  <tbody>
                    ${extra.specs
                      .map(
                        (sp) => `
                      <tr>
                        <td class="spec-key">${sp.key}</td>
                        <td class="spec-val">${sp.val}</td>
                      </tr>
                    `,
                      )
                      .join("")}
                  </tbody>
                </table>
              </div>

              <!-- Tab 3: Đánh giá -->
              <div id="tab-reviews" class="detail-tab-pane">
                <div style="display: flex; align-items: center; gap: 20px; background: var(--surface-dim); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
                  <div style="font-size: 38px; font-weight: 800; color: var(--secondary); line-height: 1;">4.9<span style="font-size: 18px; color: var(--text-muted); font-weight: 500;">/5</span></div>
                  <div>
                    <div style="color: #f59e0b; font-size: 16px; margin-bottom: 4px;">★★★★★</div>
                    <div style="font-size: 12px; color: var(--text-muted);">Dựa trên 184 lượt đánh giá từ người mua đã xác thực</div>
                  </div>
                </div>

                <div class="review-card">
                  <div class="review-header">
                    <span class="reviewer-name">Nguyễn Văn Hoàng <span class="verified-badge">✓ Đã mua hàng tại JML Store</span></span>
                    <span class="review-date">3 ngày trước</span>
                  </div>
                  <div class="review-stars">★★★★★</div>
                  <p>Hàng chính hãng đóng gói rất kỹ lưỡng. Giao hàng chỉ mất 2 tiếng ở Hà Nội, đúng chuẩn mô tả và màu sắc trên ảnh. Rất hài lòng!</p>
                </div>

                <div class="review-card">
                  <div class="review-header">
                    <span class="reviewer-name">Trần Thùy Linh <span class="verified-badge">✓ Đã mua hàng tại JML Store</span></span>
                    <span class="review-date">1 tuần trước</span>
                  </div>
                  <div class="review-stars">★★★★★</div>
                  <p>Sản phẩm cao cấp, chất lượng hoàn thiện tuyệt vời. Nhân viên hỗ trợ tư vấn rất nhiệt tình và kích hoạt bảo hành điện tử nhanh chóng.</p>
                </div>
              </div>

              <!-- Tab 4: Chính sách -->
              <div id="tab-policy" class="detail-tab-pane">
                <div style="display: flex; flex-direction: column; gap: 14px;">
                  <div>
                    <strong style="color: var(--secondary);">1. Chính sách bảo hành chính hãng:</strong>
                    <p style="margin-top: 4px;">Bảo hành 12 - 24 tháng theo quy chuẩn của nhà sản xuất. Kích hoạt bảo hành điện tử thông minh qua số điện thoại mua hàng.</p>
                  </div>
                  <div>
                    <strong style="color: var(--secondary);">2. Chính sách đổi mới 30 ngày:</strong>
                    <p style="margin-top: 4px;">Đổi mới 1:1 miễn phí trong 30 ngày đầu tiên nếu sản phẩm phát sinh lỗi từ nhà sản xuất (yêu cầu giữ nguyên hộp và phụ kiện).</p>
                  </div>
                  <div>
                    <strong style="color: var(--secondary);">3. Cam kết nguồn gốc:</strong>
                    <p style="margin-top: 4px;">100% sản phẩm phân phối bởi JML Store là hàng chính ngạch có hóa đơn VAT và tem chống hàng giả của Bộ Công An.</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Related Products Section -->
            <div class="related-products-section">
              <div class="section-title-wrap">
                <div>
                  <h2 class="section-title">Sản Phẩm Cùng Bộ Sưu Tập</h2>
                  <p class="section-subtitle">Gợi ý sản phẩm tương tự có thể bạn cũng quan tâm</p>
                </div>
              </div>
              <div class="recommend-grid">${relatedCardsHtml}</div>
            </div>
          </div>
        `;

  // Chuyển SPA view
  const cartContainer = document.getElementById("view-cart");
  if (cartContainer) cartContainer.classList.remove("active");
  homeContainer.classList.remove("active");
  detailContainer.classList.add("active");
  window.location.hash = "product/" + product.id;
  window.scrollTo({ top: 0, behavior: "smooth" });

  // Gắn listener hover cho các card liên quan
  attachHoverCarouselListeners(detailContainer);
}

function showHomeView() {
  const detailContainer = document.getElementById("view-product-detail");
  const homeContainer = document.getElementById("view-home");
  const cartContainer = document.getElementById("view-cart");
  if (detailContainer) detailContainer.classList.remove("active");
  if (cartContainer) cartContainer.classList.remove("active");
  if (homeContainer) homeContainer.classList.add("active");
  window.location.hash = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function switchDetailImage(index, imgSrc, angleName) {
  const mainImg = document.getElementById("detailMainImg");
  const angleBadge = document.getElementById("detailAngleBadge");
  if (mainImg) mainImg.src = imgSrc;
  if (angleBadge) angleBadge.textContent = angleName;

  document.querySelectorAll(".gallery-thumb-item").forEach((thumb, idx) => {
    thumb.classList.toggle("active", idx === index);
  });
}

function selectVariant(button, labelId, value) {
  const label = document.getElementById(labelId);
  if (label) label.textContent = value;
  const parent = button.parentElement;
  if (parent) {
    parent
      .querySelectorAll(".variant-btn")
      .forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");
  }
  if (labelId === "selectedColorLabel") currentSelectedColor = value;
  if (labelId === "selectedVersionLabel") currentSelectedVersion = value;
}

function syncSpaDetailQtyUi(maxStock) {
  const input = document.getElementById("detailQtyInput");
  const decBtn = document.getElementById("detailQtyDecBtn");
  const incBtn = document.getElementById("detailQtyIncBtn");
  if (input) input.value = currentDetailQty;
  if (decBtn) decBtn.disabled = maxStock <= 0 || currentDetailQty <= 1;
  if (incBtn) incBtn.disabled = maxStock <= 0 || currentDetailQty >= maxStock;
}

function changeDetailQty(delta) {
  const maxStock = Math.max(0, Number(currentDetailProduct?.availableStock ?? 45));
  if (maxStock <= 0) return;
  let val = (Number(currentDetailQty) || 1) + delta;
  if (val < 1) val = 1;
  if (val > maxStock) {
    val = maxStock;
    showToast("Giới hạn tồn kho", `Chỉ còn tối đa ${maxStock} sản phẩm trong kho.`);
  }
  currentDetailQty = val;
  syncSpaDetailQtyUi(maxStock);
}

function onSpaDetailQtyInput(rawVal) {
  const maxStock = Math.max(0, Number(currentDetailProduct?.availableStock ?? 45));
  if (maxStock <= 0) {
    currentDetailQty = 0;
    syncSpaDetailQtyUi(0);
    return;
  }
  let val = parseInt(rawVal, 10);
  if (isNaN(val) || val < 1) val = 1;
  if (val > maxStock) {
    val = maxStock;
    showToast("Vượt tồn kho", `Số lượng tối đa có thể đặt là ${maxStock}.`);
  }
  currentDetailQty = val;
  syncSpaDetailQtyUi(maxStock);
}

function addCurrentDetailToCart() {
  if (!currentDetailProduct) return;
  const maxStock = Math.max(0, Number(currentDetailProduct.availableStock ?? 45));
  if (maxStock <= 0) {
    showToast("Hết hàng", "Sản phẩm hiện tạm hết hàng trong kho.");
    return;
  }

  const mainImg = currentDetailProduct.images
    ? currentDetailProduct.images[0]
    : currentDetailProduct.image;
  const titleWithVariant = `${currentDetailProduct.title} (${currentSelectedColor || "Tiêu chuẩn"})`;
  const shopName = currentDetailProduct.shopName || "Trungshop";
  const qtyToAdd = Math.max(1, Math.min(currentDetailQty || 1, maxStock));

  const existing = cartItems.find(
    (it) => Number(it.id) === Number(currentDetailProduct.id) && it.title === titleWithVariant
  );
  const currentInCart = existing ? Number(existing.qty) || 1 : 0;
  if (currentInCart + qtyToAdd > maxStock) {
    showToast("Vượt tồn kho", `Tổng số lượng trong giỏ không thể vượt quá ${maxStock}.`);
    return;
  }

  if (existing) {
    existing.qty = currentInCart + qtyToAdd;
    existing.stock = maxStock;
  } else {
    cartItems.push({
      id: currentDetailProduct.id,
      product_id: currentDetailProduct.id,
      title: titleWithVariant,
      price: currentDetailProduct.price,
      originalPrice: currentDetailProduct.originalPrice,
      image: mainImg,
      qty: qtyToAdd,
      stock: maxStock,
      shopName: shopName,
    });
  }
  updateCartDisplay();

  if (cartCountBadge) {
    cartCountBadge.classList.remove("bounce");
    void cartCountBadge.offsetWidth;
    cartCountBadge.classList.add("bounce");
  }

  showToast(
    "Đã thêm vào giỏ hàng!",
    `${qtyToAdd}x ${titleWithVariant}`,
  );
}

function buyCurrentDetailNow() {
  addCurrentDetailToCart();
  cartDropdown.classList.add("active");
  handleCheckout();
}

function switchDetailTab(tabId, btn) {
  document
    .querySelectorAll(".detail-tab-btn")
    .forEach((b) => b.classList.remove("active"));
  document
    .querySelectorAll(".detail-tab-pane")
    .forEach((p) => p.classList.remove("active"));
  btn.classList.add("active");
  const target = document.getElementById(tabId);
  if (target) target.classList.add("active");
}

// Xử lý URL hash để đồng bộ SPA (nút Back/Forward của trình duyệt)
function checkUrlHash() {
  const hash = window.location.hash;
  if (hash.startsWith("#product/")) {
    const id = hash.replace("#product/", "");
    if (id) openProductDetail(id);
  } else if (hash === "#cart") {
    showCartView();
  } else {
    showHomeView();
  }
}

window.addEventListener("hashchange", checkUrlHash);

function filterCategory(cat, element) {
  activeRecommendCategory = cat;
  document.querySelectorAll(".recommend-tabs .tab-btn").forEach((btn) => {
    const btnCat = btn.getAttribute("onclick");
    if (element) {
      btn.classList.toggle("active", btn === element);
    } else if (btnCat && btnCat.includes(`'${cat}'`)) {
      btn.classList.add("active");
    } else if (cat === "all" && btnCat && btnCat.includes("'all'")) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });
  renderRecommendProducts(cat);
}

function scrollToRecommend() {
  const sec = document.querySelector(".recommend-section");
  if (sec) sec.scrollIntoView({ behavior: "smooth" });
}

function scrollToFlashSale() {
  const sec = document.getElementById("flashSaleSection");
  if (sec) sec.scrollIntoView({ behavior: "smooth" });
}

// --------------------------------------------------------------------------
// 3. HERO SLIDER BANNER INTERACTION (AUTOPLAY + NAVIGATION)
// --------------------------------------------------------------------------
let currentSlide = 0;
let sliderInterval;

function getSliderSlides() {
  return document.querySelectorAll("#bannerSlidesContainer .slide");
}

function getSliderDots() {
  return document.querySelectorAll("#sliderDots .slider-dot");
}

function showSlide(index) {
  const slides = getSliderSlides();
  const dots = getSliderDots();
  if (!slides.length) return;
  const safeIndex = ((index % slides.length) + slides.length) % slides.length;
  slides.forEach((s, i) => {
    s.classList.toggle("active", i === safeIndex);
  });
  dots.forEach((d, i) => {
    d.classList.toggle("active", i === safeIndex);
  });
  currentSlide = safeIndex;
}

function nextSlide() {
  const slides = getSliderSlides();
  if (!slides.length) return;
  const next = (currentSlide + 1) % slides.length;
  showSlide(next);
}

function prevSlide() {
  const slides = getSliderSlides();
  if (!slides.length) return;
  const prev = (currentSlide - 1 + slides.length) % slides.length;
  showSlide(prev);
}

function startSliderAutoPlay() {
  clearInterval(sliderInterval);
  if (getSliderSlides().length <= 1) return;
  sliderInterval = setInterval(nextSlide, 5000);
}

function resetSliderTimer() {
  clearInterval(sliderInterval);
  startSliderAutoPlay();
}

const nextBtn = document.getElementById("nextSlideBtn");
if (nextBtn) {
  nextBtn.addEventListener("click", () => {
    nextSlide();
    resetSliderTimer();
  });
}

const prevBtn = document.getElementById("prevSlideBtn");
if (prevBtn) {
  prevBtn.addEventListener("click", () => {
    prevSlide();
    resetSliderTimer();
  });
}

// --------------------------------------------------------------------------
// 4. FLASH SALE REALTIME COUNTDOWN TIMER
// --------------------------------------------------------------------------
let countdownRemainingSeconds = 4 * 3600 + 18 * 60 + 45;

function updateCountdown() {
  if (countdownRemainingSeconds <= 0) {
    countdownRemainingSeconds = 4 * 3600; // Reset loop
  } else {
    countdownRemainingSeconds--;
  }

  const h = Math.floor(countdownRemainingSeconds / 3600);
  const m = Math.floor((countdownRemainingSeconds % 3600) / 60);
  const s = countdownRemainingSeconds % 60;

  const hBox = document.getElementById("hoursBox");
  const mBox = document.getElementById("minutesBox");
  const sBox = document.getElementById("secondsBox");

  if (hBox) hBox.textContent = String(h).padStart(2, "0");
  if (mBox) mBox.textContent = String(m).padStart(2, "0");
  if (sBox) sBox.textContent = String(s).padStart(2, "0");
}

setInterval(updateCountdown, 1000);
updateCountdown();

// --------------------------------------------------------------------------
// 5. GIỎ HÀNG (SHOPPING CART) & HIỆU ỨNG BOUNCE BADGE
// --------------------------------------------------------------------------
const cartCountBadge = document.getElementById("cartCountBadge");
const cartCountHeader = document.getElementById("cartCountHeader");
const cartToggleBtn = document.getElementById("cartToggleBtn");
const cartDropdown = document.getElementById("cartDropdown");
const cartItemsList = document.getElementById("cartItemsList");
const cartTotalSum = document.getElementById("cartTotalSum");

const notifToggleBtn = document.getElementById("notifToggleBtn");
const notifDropdown = document.getElementById("notifDropdown");
const userProfileBtn = document.getElementById("userProfileBtn");
const userDropdown = document.getElementById("userDropdown");

function closeAllDropdowns() {
  if (cartDropdown) cartDropdown.classList.remove("active");
  if (notifDropdown) notifDropdown.style.display = "none";
  if (userDropdown) userDropdown.style.display = "none";
}

if (cartToggleBtn) {
  cartToggleBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isActive = cartDropdown.classList.contains("active");
    closeAllDropdowns();
    if (!isActive) cartDropdown.classList.add("active");
  });
}

if (notifToggleBtn) {
  notifToggleBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isShown = notifDropdown.style.display === "flex";
    closeAllDropdowns();
    if (!isShown) notifDropdown.style.display = "flex";
  });
}

if (userProfileBtn) {
  userProfileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isShown = userDropdown.style.display === "flex";
    closeAllDropdowns();
    if (!isShown) userDropdown.style.display = "flex";
  });
}

// Ngăn chặn sự kiện click bên trong dropdown làm đóng chính nó
[cartDropdown, notifDropdown, userDropdown].forEach((dd) => {
  if (dd) {
    dd.addEventListener("click", (e) => e.stopPropagation());
  }
});

// Click ra bên ngoài để đóng toàn bộ popups/dropdowns
document.addEventListener("click", () => {
  closeAllDropdowns();
});

function addToCart(title, price, image, shopName = "") {
  const productShop = shopName || "Trungshop";
  const existing = cartItems.find((item) => item.title === title);
  if (existing) {
    existing.qty = (existing.qty || 1) + 1;
  } else {
    cartItems.push({
      title,
      price,
      image,
      qty: 1,
      shopName: productShop,
    });
  }
  updateCartDisplay();

  // Kích hoạt hiệu ứng nảy icon giỏ hàng
  if (cartCountBadge) {
    cartCountBadge.classList.remove("bounce");
    void cartCountBadge.offsetWidth; // Trigger reflow
    cartCountBadge.classList.add("bounce");
  }

  // Bật Toast notification
  showToast("Đã thêm vào giỏ hàng!", title);
}

function removeFromCart(index) {
  const removed = cartItems.splice(index, 1)[0];
  updateCartDisplay();
  showToast("Đã xóa khỏi giỏ", removed ? removed.title : "");
}

function changeCartQuantity(index, change) {
  const item = cartItems[index];
  if (!item) return;
  const nextQty = (item.qty || 1) + change;
  if (nextQty <= 0) removeFromCart(index);
  else {
    item.qty = nextQty;
    updateCartDisplay();
  }
}

function updateCartDisplay() {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
  const totalQty = cartItems.reduce((acc, item) => acc + (item.qty || 1), 0);
  if (cartCountBadge) cartCountBadge.textContent = totalQty;
  const secondaryBadge = document.getElementById("cartBadgeCount");
  if (secondaryBadge) secondaryBadge.textContent = totalQty;
  if (cartCountHeader) cartCountHeader.textContent = `${totalQty} sản phẩm`;

  if (!cartItemsList || !cartTotalSum) return;

  if (cartItems.length === 0) {
    cartItemsList.innerHTML =
      '<p style="font-size: 13px; color: var(--text-muted); text-align: center; padding: 24px 0;">Chưa có sản phẩm nào trong giỏ hàng</p>';
    cartTotalSum.textContent = "0 ₫";
    return;
  }

  const total = cartItems.reduce(
    (sum, item) => sum + item.price * (item.qty || 1),
    0,
  );
  cartTotalSum.textContent = formatCurrency(total);

  cartItemsList.innerHTML = cartItems
    .map(
      (item, idx) => `
        <div class="cart-item">
          <img src="${item.image}" alt="${item.title}">
          <div class="cart-item-info">
            <div style="font-weight: 600; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; max-width: 170px;" title="${item.title}">${item.title}</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <div style="display: flex; align-items: center; gap: 7px;">
                <button type="button" onclick="changeCartQuantity(${idx}, -1)" aria-label="Giảm số lượng" style="width: 24px; height: 24px; border: 1px solid #d1d5db; border-radius: 5px; background: #fff; cursor: pointer; font-size: 16px; line-height: 1;">−</button>
                <span class="cart-item-price">${formatCurrency(item.price)} <span style="font-size: 11px; color: var(--text-muted); font-weight: 500;">x${item.qty || 1}</span></span>
                <button type="button" onclick="changeCartQuantity(${idx}, 1)" aria-label="Tăng số lượng" style="width: 24px; height: 24px; border: 1px solid #d1d5db; border-radius: 5px; background: #fff; cursor: pointer; font-size: 16px; line-height: 1;">+</button>
              </div>
              <button onclick="removeFromCart(${idx})" title="Xóa khỏi giỏ" style="color: #ef4444; font-size: 14px; padding: 2px 6px; cursor: pointer; border-radius: 4px;">✕</button>
            </div>
          </div>
        </div>
      `,
    )
    .join("");
}

function handleCheckout() {
  if (cartItems.length === 0) {
    showToast(
      "Thông báo",
      "Giỏ hàng đang trống! Vui lòng chọn sản phẩm trước khi thanh toán.",
    );
    return;
  }
  openCheckoutModal();
}

function syncCustomerAuthHeader() {
  const rawCust =
    localStorage.getItem("JML_CUSTOMER_USER") ||
    localStorage.getItem("JML_AUTH_USER");
  const avatarEl = document.getElementById("headerUserAvatar");
  const nameEl = document.getElementById("headerUserName");
  const dropNameEl = document.getElementById("dropdownUserFullName");

  if (rawCust) {
    try {
      const user = JSON.parse(rawCust);
      if (user && user.full_name) {
        const words = user.full_name.trim().split(/\s+/);
        const initials =
          words.length >= 2
            ? (words[0][0] + words[words.length - 1][0]).toUpperCase()
            : user.full_name.slice(0, 2).toUpperCase();
        if (avatarEl) avatarEl.textContent = initials;
        if (nameEl) nameEl.textContent = user.full_name;
        if (dropNameEl) {
          const roleLabel =
            user.role === "admin"
              ? "Admin"
              : user.role === "seller"
                ? "Chủ Shop"
                : user.rank || "Thành viên";
          dropNameEl.textContent = `${user.full_name} (${roleLabel})`;
        }
        return;
      }
    } catch (e) {}
  }
  if (avatarEl) avatarEl.textContent = "KH";
  if (nameEl) nameEl.textContent = "Đăng nhập";
  if (dropNameEl) dropNameEl.textContent = "Khách vãng lai (Chưa đăng nhập)";
}

function handleUserLogout() {
  localStorage.removeItem("JML_CUSTOMER_USER");
  localStorage.removeItem("JML_AUTH_USER");
  localStorage.removeItem(CART_STORAGE_KEY);
  cartItems = [];
  updateCartDisplay();
  syncCustomerAuthHeader();
  if (typeof cvRender === "function") cvRender();
  showToast("Đăng xuất", "Bạn đã đăng xuất tài khoản thành công!");
}

function openCustomerAuthModal(mode = "login") {
  const modal = document.getElementById("customerAuthModal");
  if (!modal) return;
  modal.style.display = "flex";
  switchCustAuthMode(mode);
}

function closeCustomerAuthModal() {
  const modal = document.getElementById("customerAuthModal");
  if (modal) modal.style.display = "none";
}

function switchCustAuthMode(mode) {
  const tabLogin = document.getElementById("custTabLogin");
  const tabReg = document.getElementById("custTabRegister");
  const formLogin = document.getElementById("custLoginForm");
  const formReg = document.getElementById("custRegisterForm");
  const alertEl = document.getElementById("custAuthAlert");
  if (alertEl) alertEl.style.display = "none";

  if (mode === "login") {
    tabLogin.style.background = "#fff";
    tabLogin.style.color = "#0d6efd";
    tabLogin.style.borderBottom = "2px solid #0d6efd";
    tabReg.style.background = "transparent";
    tabReg.style.color = "#64748b";
    tabReg.style.borderBottom = "2px solid transparent";
    formLogin.style.display = "flex";
    formReg.style.display = "none";
  } else {
    tabReg.style.background = "#fff";
    tabReg.style.color = "#0d6efd";
    tabReg.style.borderBottom = "2px solid #0d6efd";
    tabLogin.style.background = "transparent";
    tabLogin.style.color = "#64748b";
    tabLogin.style.borderBottom = "2px solid transparent";
    formLogin.style.display = "none";
    formReg.style.display = "flex";
  }
}

async function handleCustomerLoginSubmit(e) {
  e.preventDefault();
  const username = document.getElementById("custLoginUser").value.trim();
  const password = document.getElementById("custLoginPass").value;
  const alertEl = document.getElementById("custAuthAlert");

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, role: "customer" }),
    });
    const data = await res.json();
    if (!res.ok) {
      alertEl.style.display = "block";
      alertEl.style.background = "#fef2f2";
      alertEl.style.color = "#ef4444";
      alertEl.style.border = "1px solid #fecaca";
      alertEl.textContent = data.detail || "Đăng nhập thất bại!";
      return;
    }
    localStorage.setItem("JML_CUSTOMER_USER", JSON.stringify(data.user));
    syncCustomerAuthHeader();
    syncCartAfterLogin();
    closeCustomerAuthModal();
    showToast(
      "Đăng nhập thành công",
      `Chào mừng ${data.user.full_name} quay trở lại!`,
    );
  } catch (err) {
    alertEl.style.display = "block";
    alertEl.style.background = "#fef2f2";
    alertEl.style.color = "#ef4444";
    alertEl.textContent = "Không thể kết nối máy chủ!";
  }
}

async function handleCustomerRegisterSubmit(e) {
  e.preventDefault();
  const name = document.getElementById("custRegName").value.trim();
  const phone = document.getElementById("custRegPhone").value.trim();
  const password = document.getElementById("custRegPass").value;
  const address = document.getElementById("custRegAddress").value.trim();
  const alertEl = document.getElementById("custAuthAlert");

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: phone,
        password: password,
        role: "customer",
        full_name: name,
        phone: phone,
        email: `${phone}@jmlstore.vn`,
        address: address,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      alertEl.style.display = "block";
      alertEl.style.background = "#fef2f2";
      alertEl.style.color = "#ef4444";
      alertEl.style.border = "1px solid #fecaca";
      alertEl.textContent = data.detail || "Đăng ký thất bại!";
      return;
    }
    localStorage.setItem("JML_CUSTOMER_USER", JSON.stringify(data.user));
    syncCustomerAuthHeader();
    syncCartAfterLogin();
    closeCustomerAuthModal();
    showToast(
      "Đăng ký thành công",
      `Chúc mừng ${data.user.full_name} đã tạo tài khoản thành công!`,
    );
  } catch (err) {
    alertEl.style.display = "block";
    alertEl.style.background = "#fef2f2";
    alertEl.style.color = "#ef4444";
    alertEl.textContent = "Không thể kết nối máy chủ!";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  syncCustomerAuthHeader();
  syncCartAfterLogin();
});

// Lắng nghe sự kiện đăng nhập / đăng xuất để đồng bộ biểu tượng giỏ hàng tức thì
window.addEventListener("auth_state_changed", () => {
  syncCustomerAuthHeader();
  syncCartAfterLogin();
});

window.addEventListener("storage", (event) => {
  if (event.key === CART_STORAGE_KEY) restoreCartFromStorage();
  if (event.key === "JML_CUSTOMER_USER" || event.key === "JML_AUTH_USER") {
    syncCustomerAuthHeader();
    syncCartAfterLogin();
  }
});

// Quản lý Voucher & Phương Thức Vận Chuyển
let appliedVoucher = null;

const AVAILABLE_VOUCHERS = {
  FREESHIP: {
    code: "FREESHIP",
    type: "shipping",
    desc: "Miễn phí 100% tiền vận chuyển",
    minOrder: 0,
  },
  JML50K: {
    code: "JML50K",
    type: "fixed",
    amount: 50000,
    desc: "Giảm ngay 50.000 ₫",
    minOrder: 100000,
  },
  GIAM10: {
    code: "GIAM10",
    type: "percent",
    percent: 10,
    maxAmount: 100000,
    desc: "Giảm 10% (tối đa 100.000 ₫)",
    minOrder: 0,
  },
  VIP100K: {
    code: "VIP100K",
    type: "fixed",
    amount: 100000,
    desc: "Giảm 100.000 ₫ cho đơn từ 1.000.000 ₫",
    minOrder: 1000000,
  },
};

function openCheckoutModal() {
  const modal = document.getElementById("userCheckoutModal");
  if (!modal) return;

  // Reset voucher
  appliedVoucher = null;
  const vInput = document.getElementById("checkoutVoucherInput");
  if (vInput) vInput.value = "";
  const vStatus = document.getElementById("voucherStatusText");
  if (vStatus) {
    vStatus.style.display = "none";
    vStatus.textContent = "";
  }

  // Tự động điền thông tin Khách hàng đang đăng nhập nếu có
  const rawCust =
    localStorage.getItem("JML_CUSTOMER_USER") ||
    localStorage.getItem("JML_AUTH_USER");
  if (rawCust) {
    try {
      const u = JSON.parse(rawCust);
      if (u.full_name)
        document.getElementById("checkoutBuyerName").value = u.full_name;
      if (u.phone)
        document.getElementById("checkoutBuyerPhone").value = u.phone;
      if (u.address)
        document.getElementById("checkoutBuyerAddress").value = u.address;
    } catch (e) {}
  }

  updateCheckoutTotals();
  modal.style.display = "flex";
}

function closeCheckoutModal() {
  const modal = document.getElementById("userCheckoutModal");
  if (modal) modal.style.display = "none";
}

function updateCheckoutTotals() {
  const subtotal = cartItems.reduce(
    (sum, item) => sum + item.price * (item.qty || 1),
    0,
  );
  const count = cartItems.reduce((sum, item) => sum + (item.qty || 1), 0);

  const shipSelect = document.getElementById("checkoutShippingMethod");
  const selectedOpt = shipSelect
    ? shipSelect.options[shipSelect.selectedIndex]
    : null;
  let baseShipFee = selectedOpt
    ? parseInt(selectedOpt.getAttribute("data-fee") || "15000")
    : 15000;
  let shipName = selectedOpt
    ? selectedOpt.getAttribute("data-name") || "Tiêu Chuẩn (GHN Express)"
    : "Tiêu Chuẩn (GHN Express)";

  let discountAmount = 0;
  let isFreeShipping = false;

  if (appliedVoucher) {
    if (appliedVoucher.type === "shipping") {
      isFreeShipping = true;
      discountAmount = baseShipFee;
    } else if (appliedVoucher.type === "fixed") {
      discountAmount = Math.min(appliedVoucher.amount, subtotal);
    } else if (appliedVoucher.type === "percent") {
      const calculated = Math.round(subtotal * (appliedVoucher.percent / 100));
      discountAmount = Math.min(
        calculated,
        appliedVoucher.maxAmount || calculated,
      );
    }
  }

  const effectiveShipFee = isFreeShipping ? 0 : baseShipFee;
  const finalTotal = Math.max(0, subtotal + baseShipFee - discountAmount);

  // Cập nhật giao diện tóm tắt
  const countEl = document.getElementById("checkoutModalItemCount");
  if (countEl)
    countEl.textContent = `${count} sản phẩm • ${formatCurrency(subtotal)}`;

  const shipLabelEl = document.getElementById("checkoutShippingLabel");
  if (shipLabelEl)
    shipLabelEl.textContent = `Vận chuyển (${shipName.split(" ")[0]}):`;

  const shipFeeEl = document.getElementById("checkoutShippingFeeText");
  if (shipFeeEl) {
    if (isFreeShipping) {
      shipFeeEl.innerHTML = `<span style="color: #10b981; font-weight: 700;">Miễn phí (${appliedVoucher.code})</span>`;
    } else {
      shipFeeEl.textContent = formatCurrency(baseShipFee);
    }
  }

  const discountRow = document.getElementById("checkoutDiscountRow");
  const discountLabel = document.getElementById("checkoutDiscountLabel");
  const discountAmountEl = document.getElementById(
    "checkoutDiscountAmountText",
  );
  if (discountRow) {
    if (appliedVoucher && discountAmount > 0) {
      discountRow.style.display = "flex";
      if (discountLabel)
        discountLabel.textContent = `Mã giảm (${appliedVoucher.code}):`;
      if (discountAmountEl)
        discountAmountEl.textContent = `-${formatCurrency(discountAmount)}`;
    } else {
      discountRow.style.display = "none";
    }
  }

  const totalSumEl = document.getElementById("checkoutModalTotalSum");
  if (totalSumEl) totalSumEl.textContent = formatCurrency(finalTotal);

  return {
    subtotal,
    baseShipFee,
    effectiveShipFee,
    discountAmount,
    finalTotal,
    shipName,
  };
}

function selectQuickVoucher(code) {
  const input = document.getElementById("checkoutVoucherInput");
  if (input) input.value = code;
  applyVoucherCode();
}

function applyVoucherCode() {
  const input = document.getElementById("checkoutVoucherInput");
  const code = (input ? input.value : "").trim().toUpperCase();
  const statusEl = document.getElementById("voucherStatusText");

  if (!code) {
    appliedVoucher = null;
    if (statusEl) statusEl.style.display = "none";
    updateCheckoutTotals();
    return;
  }

  const v = AVAILABLE_VOUCHERS[code];
  if (!v) {
    if (statusEl) {
      statusEl.style.display = "inline";
      statusEl.style.color = "#ef4444";
      statusEl.textContent = "✕ Mã không tồn tại hoặc đã hết lượt!";
    }
    appliedVoucher = null;
    updateCheckoutTotals();
    return;
  }

  const subtotal = cartItems.reduce(
    (sum, item) => sum + item.price * (item.qty || 1),
    0,
  );
  if (v.minOrder && subtotal < v.minOrder) {
    if (statusEl) {
      statusEl.style.display = "inline";
      statusEl.style.color = "#ef4444";
      statusEl.textContent = `✕ Mã ${code} chỉ áp dụng cho đơn từ ${formatCurrency(v.minOrder)}!`;
    }
    appliedVoucher = null;
    updateCheckoutTotals();
    return;
  }

  appliedVoucher = v;
  if (statusEl) {
    statusEl.style.display = "inline";
    statusEl.style.color = "#10b981";
    statusEl.innerHTML = `✓ Đã áp dụng <strong>${code}</strong> <button type="button" onclick="cancelVoucher()" style="background: none; border: none; color: #ef4444; font-size: 11px; font-weight: 700; cursor: pointer; text-decoration: underline; margin-left: 4px;">Hủy mã</button>`;
  }
  updateCheckoutTotals();
  showToast("Áp dụng mã thành công", `Mã ${code} đã được áp dụng: ${v.desc}!`);
}

function cancelVoucher() {
  appliedVoucher = null;
  const input = document.getElementById("checkoutVoucherInput");
  if (input) input.value = "";
  const statusEl = document.getElementById("voucherStatusText");
  if (statusEl) statusEl.style.display = "none";
  updateCheckoutTotals();
  showToast("Đã hủy voucher", "Đã gỡ bỏ mã giảm giá khỏi đơn hàng.");
}

async function confirmCheckoutOrder(e) {
  if (e) e.preventDefault();

  const name = (
    document.getElementById("checkoutBuyerName")?.value || "Khách mua hàng"
  ).trim();
  const phone = (
    document.getElementById("checkoutBuyerPhone")?.value || "0908123456"
  ).trim();
  const address = (
    document.getElementById("checkoutBuyerAddress")?.value || "Quận 1, TP.HCM"
  ).trim();

  const totals = updateCheckoutTotals();
  const totalNum = totals.finalTotal;
  const totalFormatted = formatCurrency(totalNum);
  const feeFormatted = "-" + formatCurrency(Math.round(totalNum * 0.07));
  const netFormatted = formatCurrency(Math.round(totalNum * 0.93));

  const orderShopName = cartItems[0]?.shopName || "JML Official Store";
  const shippingMethod = totals.shipName;
  const voucherCode = appliedVoucher ? appliedVoucher.code : "";
  const discountAmount = totals.discountAmount;
  const paymentMethod =
    document.getElementById("checkoutPaymentMethod")?.value || "cod";

  const itemsPayload = cartItems.map((item) => ({
    name: item.title,
    variant: "Chính hãng • Shop: " + (item.shopName || orderShopName),
    price: formatCurrency(item.price),
    qty: String(item.qty || 1),
    subtotal: formatCurrency(item.price * (item.qty || 1)),
  }));

  let orderId = "#MP-" + Math.floor(1000 + Math.random() * 9000);

  // 1. Gọi FastAPI lưu đơn hàng vào Database
  try {
    const res = await fetch(`${API_BASE_URL}/api/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        buyer_name: name,
        buyer_phone: phone,
        buyer_address: address,
        shop_name: orderShopName,
        total: totalFormatted,
        numeric_total: totalNum,
        fee: feeFormatted,
        net: netFormatted,
        shipping_method: shippingMethod,
        shipping_fee: totals.baseShipFee,
        discount_code: voucherCode,
        discount_amount: discountAmount,
        payment_method: paymentMethod,
        items: itemsPayload,
      }),
    });

    if (res.status === 403) {
      const errData = await res.json();
      alert(
        "❌ TÀI KHOẢN ĐÃ BỊ KHÓA!\n\n" +
          (errData.detail || "Tài khoản này đã bị Ban Quản Trị Sàn khóa."),
      );
      return;
    }

    if (res.ok) {
      const data = await res.json();
      if (data.order_id) orderId = data.order_id;
    }
  } catch (err) {
    // Fallback kiểm tra banned trong localStorage nếu chưa bật port 8000
    const bannedList = JSON.parse(
      localStorage.getItem("JML_BANNED_CUSTOMERS") || "[]",
    );
    if (bannedList.includes(phone) || bannedList.includes(name)) {
      alert(
        "❌ TÀI KHOẢN ĐÃ BỊ KHÓA!\n\nSố điện thoại/Tài khoản (" +
          phone +
          ") đã bị Ban Quản Trị Sàn tạm khóa.",
      );
      return;
    }
  }

  // 2. Đồng bộ dự phòng vào localStorage để tab Admin nhận tín hiệu tức thì
  const newOrder = {
    id: orderId,
    key: orderId.replace("#", ""),
    escrowBadge: "🔒 Sàn đang giữ tiền",
    escrowClass: "bg-primary-50 text-primary-500",
    time:
      "Thời gian đặt: " +
      new Date().toLocaleString("vi-VN") +
      " • Vận chuyển: " +
      shippingMethod +
      (voucherCode ? " • Voucher: " + voucherCode : ""),
    shopName: orderShopName,
    shopAddress: "Kho lấy hàng: Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
    buyerName: name + " (" + phone + ")",
    buyerPhone: phone,
    buyerAddress: address,
    total: totalFormatted,
    numericTotal: totalNum,
    fee: feeFormatted,
    net: netFormatted,
    shippingMethod: shippingMethod,
    voucherCode: voucherCode,
    status: "escrow",
    items: itemsPayload,
  };

  const orders = JSON.parse(localStorage.getItem("JML_ORDERS") || "[]");
  orders.unshift(newOrder);
  localStorage.setItem("JML_ORDERS", JSON.stringify(orders));
  window.dispatchEvent(new Event("storage"));

  cartItems = [];
  updateCartDisplay();
  closeCheckoutModal();
  if (cartDropdown) cartDropdown.classList.remove("active");

  showToast(
    "Đặt hàng thành công",
    `Đơn hàng ${orderId} (${totalFormatted}) đã được lưu vào hệ thống!`,
  );
  openUserOrdersModal();
}

// --------------------------------------------------------------------------
// MODAL: LỊCH SỬ ĐƠN HÀNG ĐÃ ĐẶT CỦA KHÁCH HÀNG
// --------------------------------------------------------------------------
async function openUserOrdersModal() {
  const modal = document.getElementById("userOrdersModal");
  if (!modal) return;
  modal.style.display = "flex";
  await loadUserOrdersList();
}

function closeUserOrdersModal() {
  const modal = document.getElementById("userOrdersModal");
  if (modal) modal.style.display = "none";
}

async function loadUserOrdersList() {
  const container = document.getElementById("userOrdersListBody");
  if (!container) return;

  container.innerHTML = `
          <div style="padding: 40px; text-align: center; color: #94a3b8;">
            <div style="font-size: 24px; margin-bottom: 8px;">⏳</div>
            <p style="font-size: 13px;">Đang tải lịch sử đơn hàng của bạn...</p>
          </div>
        `;

  let phone = "";
  let name = "";
  const rawCust =
    localStorage.getItem("JML_CUSTOMER_USER") ||
    localStorage.getItem("JML_AUTH_USER");
  if (rawCust) {
    try {
      const u = JSON.parse(rawCust);
      if (u.phone) phone = u.phone;
      if (u.full_name) name = u.full_name;
    } catch (e) {}
  }

  try {
    const res = await fetch(
      `${API_BASE_URL}/api/user/orders?phone=${encodeURIComponent(phone)}&name=${encodeURIComponent(name)}`,
    );
    if (res.ok) {
      const data = await res.json();
      renderUserOrders(data.orders || []);
      return;
    }
  } catch (err) {}

  // Fallback từ localStorage
  const localOrders = JSON.parse(localStorage.getItem("JML_ORDERS") || "[]");
  renderUserOrders(
    localOrders.map((o) => ({
      order_key: o.key,
      id_display: o.id,
      created_at: o.time || "Hôm nay",
      shop_name: o.shopName,
      status: o.status || "preparing",
      escrow_badge: o.escrowBadge || "📦 Shop đang chuẩn bị đơn",
      total: o.total,
      items: o.items || [],
    })),
  );
}

function renderUserOrders(orders) {
  const container = document.getElementById("userOrdersListBody");
  const countBadge = document.getElementById("userOrdersTotalCount");
  if (countBadge) countBadge.textContent = `${orders.length} đơn hàng`;

  if (!container) return;

  if (!orders || orders.length === 0) {
    container.innerHTML = `
            <div style="padding: 48px 20px; text-align: center; color: #64748b; background: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1;">
              <div style="font-size: 36px; margin-bottom: 10px;">📦</div>
              <p style="font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 4px;">Bạn chưa có đơn hàng nào</p>
              <p style="font-size: 12px; color: #94a3b8;">Hãy dạo một vòng trang chủ và chọn món đồ yêu thích để đặt hàng ngay!</p>
            </div>
          `;
    return;
  }

  container.innerHTML = orders
    .map((o) => {
      // Trạng thái theo phong cách Shopee
      let badgeText = o.escrow_badge || "📦 Shop đang chuẩn bị đơn";
      let badgeBg = "#fffbeb";
      let badgeColor = "#d97706";
      let badgeBorder = "#fde68a";

      if (o.status === "shipping" || badgeText.includes("vận chuyển")) {
        badgeText = "🚚 Đang vận chuyển";
        badgeBg = "#eff6ff";
        badgeColor = "#2563eb";
        badgeBorder = "#bfdbfe";
      } else if (
        o.status === "delivered" ||
        o.status === "released" ||
        badgeText.includes("giao hàng") ||
        badgeText.includes("hoàn tất")
      ) {
        badgeText = "✓ Đã giao hàng thành công";
        badgeBg = "#ecfdf5";
        badgeColor = "#059669";
        badgeBorder = "#a7f3d0";
      } else if (o.status === "dispute" || badgeText.includes("tranh chấp")) {
        badgeText = "⚠️ Đang xử lý khiếu nại";
        badgeBg = "#fef2f2";
        badgeColor = "#dc2626";
        badgeBorder = "#fecaca";
      } else {
        badgeText = "📦 Shop đang chuẩn bị đơn";
        badgeBg = "#fffbeb";
        badgeColor = "#d97706";
        badgeBorder = "#fde68a";
      }

      return `
            <div class="user-order-card" data-order-key="${o.order_key}" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.04); flex-shrink: 0; width: 100%;">
              <!-- Order Header -->
              <div style="padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; font-size: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span style="font-weight: 800; color: #0f172a;">${o.id_display || "#" + o.order_key}</span>
                  <span style="color: #cbd5e1;">•</span>
                  <span style="color: #64748b;">Shop: <strong style="color: #ea580c;">${o.shop_name || "Trungshop"}</strong></span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span class="order-status-badge" style="padding: 4px 12px; border-radius: 99px; font-weight: 700; font-size: 11px; background: ${badgeBg}; color: ${badgeColor}; border: 1px solid ${badgeBorder};">
                    ${badgeText}
                  </span>
                </div>
              </div>

              <!-- Order Items List -->
              <div style="padding: 14px 16px; display: flex; flex-direction: column; gap: 10px;">
                ${(o.items || [])
                  .map(
                    (it) => `
                  <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 13px;">
                    <div style="min-width: 0;">
                      <p style="font-weight: 700; color: #1e293b; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${it.name}</p>
                      <p style="font-size: 11px; color: #64748b; margin: 2px 0 0 0;">${it.variant || "Chính hãng"} • Số lượng: <strong>x${it.qty || 1}</strong></p>
                    </div>
                    <span style="font-weight: 700; color: #0f172a; white-space: nowrap;">${it.subtotal || it.price}</span>
                  </div>
                `,
                  )
                  .join("")}
              </div>

              <!-- Order Footer -->
              <div style="padding: 12px 16px; background: #fafafa; border-top: 1px dashed #e2e8f0; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; font-size: 12px;">
                <span style="color: #64748b;">${o.time_info || o.created_at || ""}</span>
                <div style="display: flex; align-items: center; gap: 12px; margin-left: auto;">
                  <div>
                    <span style="color: #64748b; margin-right: 6px;">Tổng thanh toán:</span>
                    <strong style="font-size: 15px; color: #ea580c; font-weight: 800;">${o.total}</strong>
                  </div>
                  <!-- Duy Nhất 1 Nút Xác Nhận Ở Chân Đơn Hàng -->
                  ${
                    o.status === "shipping" ||
                    (o.escrow_badge && o.escrow_badge.includes("vận chuyển"))
                      ? `
                    <button onclick="handleUserConfirmReceived(this, '${o.order_key}')" style="padding: 7px 16px; border-radius: 8px; border: none; background: #16a34a; color: #fff; font-weight: 700; font-size: 12px; cursor: pointer; box-shadow: 0 2px 6px rgba(22,163,74,0.3); display: inline-flex; align-items: center; gap: 5px;">
                      <span>✓ Đã Nhận Được Hàng</span>
                    </button>
                  `
                      : o.status === "delivered" || o.status === "released"
                        ? `
                    <span style="padding: 4px 10px; border-radius: 6px; background: #ecfdf5; color: #15803d; font-weight: 700; font-size: 11px; border: 1px solid #bbf7d0;">
                      ✓ Đã nhận hàng thành công
                    </span>
                  `
                        : `
                    <span style="padding: 4px 10px; border-radius: 6px; background: #fef3c7; color: #b45309; font-weight: 600; font-size: 11px;">
                      Chờ shop gửi hàng
                    </span>
                  `
                  }
                </div>
              </div>
            </div>
          `;
    })
    .join("");
}

async function handleUserConfirmReceived(arg1, arg2) {
  let btn = null;
  let orderKey = "";
  if (arg1 && arg1.nodeType === 1) {
    btn = arg1;
    orderKey = arg2;
  } else {
    orderKey = arg1;
  }

  const card = btn
    ? btn.closest(".user-order-card")
    : document.querySelector(`.user-order-card[data-order-key="${orderKey}"]`);

  // Cập nhật trạng thái trực tiếp trên giao diện tức thì (KHÔNG reload lại modal)
  if (btn) {
    btn.outerHTML = `
            <span style="padding: 5px 12px; border-radius: 8px; background: #ecfdf5; color: #15803d; font-weight: 700; font-size: 12px; border: 1px solid #bbf7d0; display: inline-flex; align-items: center; gap: 4px;">
              <span>✓ Đã nhận hàng thành công</span>
            </span>
          `;
  }

  if (card) {
    const badge = card.querySelector(".order-status-badge");
    if (badge) {
      badge.textContent = "✓ Đã giao hàng thành công";
      badge.style.background = "#ecfdf5";
      badge.style.color = "#059669";
      badge.style.border = "1px solid #a7f3d0";
    }
  }

  showToast("Thành công", "Bạn đã xác nhận nhận hàng thành công!");
  window.dispatchEvent(new Event("storage"));

  // Gửi lệnh ngầm đến FastAPI Backend
  try {
    await fetch(
      `${API_BASE_URL}/api/user/orders/${orderKey}/confirm-received`,
      {
        method: "PUT",
      },
    );
  } catch (e) {}
}

// --------------------------------------------------------------------------
// 6. TOAST NOTIFICATION SYSTEM
// --------------------------------------------------------------------------
const toastContainer = document.getElementById("toastContainer");

function showToast(title, message) {
  if (!toastContainer) return;
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
        <div class="toast-icon">✓</div>
        <div class="toast-content">
          <div class="toast-title">${title}</div>
          <div class="toast-msg">${message}</div>
        </div>
        <button style="border: none; background: transparent; color: #94a3b8; font-size: 14px; cursor: pointer; padding: 2px 6px;">✕</button>
      `;

  toast.onclick = () => {
    toast.classList.remove("show");
    toast.classList.add("hide");
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 250);
  };

  toastContainer.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  setTimeout(() => {
    toast.classList.remove("show");
    toast.classList.add("hide");
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 350);
  }, 3200);
}

// --------------------------------------------------------------------------
// 7. SCROLL REVEAL ANIMATIONS (INTERSECTION OBSERVER)
// --------------------------------------------------------------------------
const observerOptions = {
  threshold: 0.12,
  rootMargin: "0px 0px -40px 0px",
};

const revealObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("revealed");
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll(".reveal-on-scroll").forEach((el) => {
  revealObserver.observe(el);
});

// --------------------------------------------------------------------------
// 8. TÌM KIẾM THÔNG MINH
// --------------------------------------------------------------------------
function handleSearch() {
  const input = document.getElementById("searchInput");
  const query = (input ? input.value : "").trim().toLowerCase();

  // Đảm bảo đang ở view home khi tìm kiếm
  showHomeView();

  if (!query) {
    renderRecommendProducts("all");
    return;
  }

  const matched = RECOMMEND_PRODUCTS.filter(
    (p) =>
      p.title.toLowerCase().includes(query) ||
      p.category.toLowerCase().includes(query),
  );

  const container = document.getElementById("recommendProductsContainer");
  if (container) {
    if (matched.length === 0) {
      container.innerHTML = `
              <div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; background: #fff; border-radius: var(--radius-md); border: 1px dashed var(--border);">
                <div style="font-size: 36px; margin-bottom: 12px;">🔍</div>
                <h3 style="font-size: 16px; font-weight: 700; color: var(--secondary);">Không tìm thấy sản phẩm phù hợp</h3>
                <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">Thử tìm với từ khóa: "ipad", "tai nghe", "đồng hồ", "ví da", "loa"...</p>
              </div>
            `;
    } else {
      container.innerHTML = matched
        .map((product) => {
          const mainImg = product.images ? product.images[0] : product.image;
          return `
              <div class="product-card" onclick="openProductDetail(${product.id})">
                ${createCarouselMarkup(product)}
                <div class="product-body">
                  <h3 class="product-title" title="${product.title}">${product.title}</h3>
                  <div class="product-meta">
                    <span class="rating-stars">★ ${product.rating}</span>
                    <span>• Đã bán ${product.soldCount}</span>
                  </div>
                  <div class="price-row">
                    <span class="current-price">${formatCurrency(product.price)}</span>
                    <span class="original-price">${formatCurrency(product.originalPrice)}</span>
                  </div>
                  <div style="margin-top: auto;">
                    <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${product.title.replace(/'/g, "\\'")}', ${product.price}, '${mainImg}', '${(product.shopName || "").replace(/'/g, "\\'")}')">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                      Thêm Vào Giỏ
                    </button>
                  </div>
                </div>
              </div>
            `;
        })
        .join("");
      attachHoverCarouselListeners(container);
    }
  }

  scrollToRecommend();
  showToast("Tìm kiếm", `Tìm thấy ${matched.length} sản phẩm phù hợp`);
}

function applyQuickSearch(term) {
  const input = document.getElementById("searchInput");
  if (input) {
    input.value = term;
    handleSearch();
  }
}

// Khởi chạy render ban đầu và đồng bộ dữ liệu từ FastAPI + SQL
renderFlashSaleProducts();
renderRecommendProducts("all");
loadProductsFromFastAPI();

// Kiểm tra URL hash khi mở trang lần đầu
if (window.location.hash.startsWith("#product/") || window.location.hash === "#cart") {
  checkUrlHash();
}


/* ============================================================
   CART VIEW (SPA) - Trang giỏ hàng nhúng trong index.html
   - showCartView(): chuyển sang view giỏ hàng
   - Tăng/giảm số lượng (tối thiểu 1), cập nhật tức thì
   - Xóa từng item (confirm), xóa tất cả (confirm)
   - Tổng tiền cập nhật real-time
   - Kết nối API backend + localStorage fallback
============================================================ */

// ─── Thêm vào cuối file buyer-index.js ───

const API_BASE = 'http://127.0.0.1:8000';
let cvApiOnline = false;
let cvPendingAction = null; // { type: 'remove'|'clear', idx? }

// Inject HTML confirm overlay một lần
function injectCartConfirmOverlay() {
  if (document.getElementById('cvConfirmOverlay')) return;
  const el = document.createElement('div');
  el.id = 'cvConfirmOverlay';
  el.className = 'cv-confirm-overlay';
  el.innerHTML = `
    <div class="cv-confirm-box">
      <div class="cv-confirm-icon" id="cvConfirmIcon">🗑️</div>
      <div class="cv-confirm-title" id="cvConfirmTitle">Xác nhận</div>
      <div class="cv-confirm-desc" id="cvConfirmDesc"></div>
      <div class="cv-confirm-actions">
        <button class="cv-btn-cancel" onclick="cvCloseConfirm()">Hủy</button>
        <button class="cv-btn-confirm" id="cvConfirmOkBtn">Xác nhận</button>
      </div>
    </div>`;
  document.body.appendChild(el);
  el.addEventListener('click', (e) => { if (e.target === el) cvCloseConfirm(); });
}

function cvShowConfirm(icon, title, desc, onOk) {
  injectCartConfirmOverlay();
  document.getElementById('cvConfirmIcon').textContent = icon;
  document.getElementById('cvConfirmTitle').textContent = title;
  document.getElementById('cvConfirmDesc').innerHTML = desc;
  document.getElementById('cvConfirmOkBtn').onclick = () => { cvCloseConfirm(); onOk(); };
  document.getElementById('cvConfirmOverlay').classList.add('show');
}
function cvCloseConfirm() {
  const el = document.getElementById('cvConfirmOverlay');
  if (el) el.classList.remove('show');
}

// ─── Chuyển sang view giỏ hàng ───
async function showCartView() {
  const homeView   = document.getElementById('view-home');
  const detailView = document.getElementById('view-product-detail');
  const cartView   = document.getElementById('view-cart');
  if (!cartView) return;

  if (homeView)   homeView.classList.remove('active');
  if (detailView) detailView.classList.remove('active');
  cartView.classList.add('active');
  window.location.hash = 'cart';
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Đóng dropdown giỏ hàng nếu đang mở
  closeAllDropdowns();

  // Kiểm tra API
  try {
    const r = await fetch(`${API_BASE}/`, { signal: AbortSignal.timeout(1500) });
    cvApiOnline = r.ok;
  } catch { cvApiOnline = false; }

  cvLoadAndRender();
}

// ─── Tải dữ liệu giỏ từ API hoặc localStorage ───
async function cvLoadAndRender() {
  cvSetLoading(true);
  const user = typeof Auth !== 'undefined' ? Auth.getUser() : null;

  if (cvApiOnline && user && user.id) {
    try {
      const r = await fetch(`${API_BASE}/api/cart/${user.id}`);
      if (r.ok) {
        const data = await r.json();
        if (data.items && data.items.length > 0) {
          cartItems = data.items.map(it => ({
            cartItemId: it.cart_item_id,
            id: it.product_id,
            title: it.title,
            price: it.cart_price || it.product_price,
            originalPrice: it.product_price,
            image: cvParseImg(it.images_json),
            shopName: it.shop_name || 'JML Store',
            qty: it.quantity
          }));
          localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
        }
      }
    } catch (e) { console.log('Cart API load failed:', e); }
  } else {
    // Đọc từ localStorage — đảm bảo đồng bộ cartItems
    cartItems = readStoredCart();
  }

  cvSetLoading(false);
  cvRender();
}

function cvParseImg(raw) {
  const fb = 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=200&q=60';
  if (!raw) return fb;
  try {
    const arr = typeof raw === 'string' ? JSON.parse(raw) : raw;
    return Array.isArray(arr) ? (arr[0] || fb) : fb;
  } catch { return typeof raw === 'string' ? raw : fb; }
}

function cvSetLoading(show) {
  const lo = document.getElementById('cartViewLoading');
  const li = document.getElementById('cartViewList');
  const em = document.getElementById('cartViewEmpty');
  if (lo) lo.style.display = show ? 'flex' : 'none';
  if (li) li.style.display = 'none';
  if (em) em.style.display = 'none';
}

// ─── Render toàn bộ giỏ hàng ───
function cvRender() {
  const list   = document.getElementById('cartViewList');
  const empty  = document.getElementById('cartViewEmpty');
  const clrBtn = document.getElementById('cartClearAllBtn');
  const ckBtn  = document.getElementById('cvCheckoutBtn');
  const pill   = document.getElementById('cartViewCountPill');

  if (!list) return;

  const totalQty = cartItems.reduce((s, it) => s + (it.qty || 1), 0);
  if (pill) pill.textContent = cartItems.length;

  if (cartItems.length === 0) {
    list.style.display   = 'none';
    empty.style.display  = 'block';
    if (clrBtn) clrBtn.style.display = 'none';
    if (ckBtn)  ckBtn.disabled = true;
    cvUpdateSummary();
    updateCartDisplay(); // sync badge header
    return;
  }

  empty.style.display = 'none';
  list.style.display  = 'block';
  if (clrBtn) clrBtn.style.display = 'flex';
  if (ckBtn)  ckBtn.disabled = false;

  list.innerHTML = cartItems.map((item, idx) => `
    <div class="cv-cart-item" id="cv-item-${idx}">
      <img class="cv-item-img"
        src="${item.image || ''}"
        alt="${escHtml(item.title)}"
        onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=200&q=60'"
      />
      <div class="cv-item-info">
        <div class="cv-item-shop">🏪 ${escHtml(item.shopName || 'JML Store')}</div>
        <div class="cv-item-title" title="${escHtml(item.title)}">${escHtml(item.title)}</div>
        <div class="cv-item-price">${formatCurrency(item.price)}</div>
        ${item.originalPrice && item.originalPrice > item.price
          ? `<div class="cv-item-orig">${formatCurrency(item.originalPrice)}</div>`
          : ''}
      </div>
      <div class="cv-item-actions">
        <div class="cv-qty-ctrl">
          <button class="cv-qty-btn" onclick="cvChangeQty(${idx}, -1)"
            ${(item.qty || 1) <= 1 ? 'disabled' : ''} title="Giảm">−</button>
          <input type="number" class="cv-qty-num" value="${item.qty || 1}"
            min="1" onchange="cvSetQtyDirect(${idx}, this.value)" />
          <button class="cv-qty-btn" onclick="cvChangeQty(${idx}, 1)" title="Tăng">+</button>
        </div>
        <div class="cv-item-subtotal">${formatCurrency(item.price * (item.qty || 1))}</div>
        <button class="cv-remove-btn" onclick="cvConfirmRemove(${idx})">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6l-1 14H6L5 6"></path>
            <path d="M10 11v6M14 11v6"></path>
          </svg>Xóa
        </button>
      </div>
    </div>
  `).join('');

  cvUpdateSummary();
  updateCartDisplay(); // sync badge + dropdown header
}

function escHtml(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ─── Tổng tiền tức thì ───
function cvUpdateSummary() {
  const totalQty  = cartItems.reduce((s, it) => s + (it.qty || 1), 0);
  const subtotal  = cartItems.reduce((s, it) => s + it.price * (it.qty || 1), 0);
  const origTotal = cartItems.reduce((s, it) => s + (it.originalPrice || it.price) * (it.qty || 1), 0);
  const savings   = Math.max(0, origTotal - subtotal);

  const setTxt = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  setTxt('cvSummaryCount',   totalQty);
  setTxt('cvSummarySubtotal', formatCurrency(subtotal));
  setTxt('cvSummaryTotal',    formatCurrency(subtotal));

  const svRow = document.getElementById('cvSavingsRow');
  if (svRow) svRow.style.display = savings > 0 ? 'flex' : 'none';
  setTxt('cvSavingsAmt', formatCurrency(savings));
}

// ─── Tăng / Giảm số lượng ───
async function cvChangeQty(idx, delta) {
  if (idx < 0 || idx >= cartItems.length) return;
  const item = cartItems[idx];
  const newQty = Math.max(1, (item.qty || 1) + delta);
  cartItems[idx].qty = newQty;
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
  cvRender();

  // Gọi API nếu online (xóa + add lại với qty mới)
  const user = typeof Auth !== 'undefined' ? Auth.getUser() : null;
  if (cvApiOnline && user && user.id && item.cartItemId) {
    try {
      await fetch(`${API_BASE}/api/cart/items/${item.cartItemId}`, { method: 'DELETE' });
      await fetch(`${API_BASE}/api/cart/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, product_id: item.id, quantity: newQty })
      });
    } catch(e) { console.log('API qty update failed:', e); }
  }
}

function cvSetQtyDirect(idx, raw) {
  const val = parseInt(raw);
  cartItems[idx].qty = isNaN(val) || val < 1 ? 1 : val;
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
  cvRender();
}

// ─── Xóa item ───
function cvConfirmRemove(idx) {
  const item = cartItems[idx];
  cvShowConfirm('🗑️', 'Xóa sản phẩm?',
    `Bạn có chắc muốn xóa <strong>"${escHtml(item.title.substring(0, 45))}..."</strong> khỏi giỏ hàng?`,
    () => cvDoRemove(idx)
  );
}

async function cvDoRemove(idx) {
  const item = cartItems[idx];
  if (cvApiOnline && item.cartItemId) {
    try {
      await fetch(`${API_BASE}/api/cart/items/${item.cartItemId}`, { method: 'DELETE' });
    } catch(e) {}
  }
  cartItems.splice(idx, 1);
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
  cvRender();
  showToast('Đã xóa', `"${item.title.substring(0, 30)}..." đã được xóa khỏi giỏ`);
}

// ─── Xóa tất cả ───
function cartViewClearAll() {
  if (cartItems.length === 0) return;
  cvShowConfirm('🗑️', 'Xóa toàn bộ giỏ hàng?',
    `Bạn có chắc muốn xóa tất cả <strong>${cartItems.length} sản phẩm</strong> khỏi giỏ không?`,
    cvDoClearAll
  );
}

async function cvDoClearAll() {
  const user = typeof Auth !== 'undefined' ? Auth.getUser() : null;
  if (cvApiOnline && user && user.id) {
    try {
      const r = await fetch(`${API_BASE}/api/cart/${user.id}`);
      if (r.ok) {
        const data = await r.json();
        if (data.cart && data.cart.id) {
          await fetch(`${API_BASE}/api/cart/${data.cart.id}/clear`, { method: 'DELETE' });
        }
      }
    } catch(e) {}
  }
  cartItems = [];
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
  cvRender();
  showToast('Giỏ hàng', 'Đã xóa toàn bộ sản phẩm khỏi giỏ hàng');
}

// ─── Checkout ───
async function cartViewCheckout() {
  if (cartItems.length === 0) return;
  const user = typeof Auth !== 'undefined' ? Auth.getUser() : null;
  if (!user) {
    showToast('⚠️ Chưa đăng nhập', 'Vui lòng đăng nhập để tiến hành thanh toán!');
    setTimeout(() => openCustomerAuthModal('login'), 1500);
    return;
  }

  if (cvApiOnline) {
    try {
      const r = await fetch(`${API_BASE}/api/cart/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: cartItems.map(it => ({ product_id: it.id, qty: it.qty })) })
      });
      if (r.ok) {
        const v = await r.json();
        if (!v.valid) {
          showToast('⚠️ Lỗi giỏ hàng', v.errors.join(' | '));
          return;
        }
      }
    } catch(e) {}
  }

  // Mở modal checkout hiện có
  if (typeof handleCheckout === 'function') {
    handleCheckout();
  } else {
    showToast('Thanh toán', 'Đang chuyển tới trang thanh toán...');
  }
}
