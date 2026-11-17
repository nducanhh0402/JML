/**
 * ==========================================================================
 * TF16E55 - TRANG DANH SÁCH & KẾT QUẢ TÌM KIẾM SẢN PHẨM
 * Nối toàn bộ Bộ lọc, Sắp xếp, Phân trang với Backend API (/api/products/filter)
 * và đồng bộ 2 chiều trạng thái bộ lọc trên URL (URLSearchParams + History API)
 * ==========================================================================
 */

const API_BASE_URL = "http://127.0.0.1:8000";

const MOCK_PRODUCTS = [
  // Audio
  {
    id: 1,
    category: "audio",
    brand: "Apple",
    description: "Tai nghe chống ồn chủ động ANC, âm thanh không gian Spatial Audio",
    title: "Tai Nghe Chụp Tai Apple AirPods Max Siêu Chống Ồn ANC",
    price: 12490000,
    originalPrice: 14990000,
    discount: "-17%",
    rating: 5.0,
    sold: 28,
    totalStock: 45,
    image: "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
    shopName: "SoundMax & Marshall Audio",
    exclusive: "Chính Hãng",
    isFlashSale: true,
  },
  {
    id: 2,
    category: "audio",
    brand: "Marshall",
    description: "Loa bluetooth di động chống nước IP67 công suất lớn",
    title: "Loa Bluetooth Di Động Marshall Emberton II Âm Thanh Đa Hướng",
    price: 3950000,
    originalPrice: 4600000,
    discount: "-14%",
    rating: 4.9,
    sold: 86,
    totalStock: 60,
    image: "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
    shopName: "SoundMax & Marshall Audio",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 3,
    category: "audio",
    brand: "Sony",
    description: "Tai nghe chống ồn flagship Sony pin 30 giờ sạc nhanh USB-C",
    title: "Tai Nghe Chống Ồn Cao Cấp Sony WH-1000XM5 Pin 30 Giờ",
    price: 7690000,
    originalPrice: 8990000,
    discount: "-14%",
    rating: 4.9,
    sold: 54,
    totalStock: 30,
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
    shopName: "SoundMax & Marshall Audio",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 4,
    category: "audio",
    brand: "Marshall",
    description: "Loa đặt bàn cổ điển Marshall Stanmore III công suất 80W",
    title: "Loa Marshall Stanmore III Bluetooth Home Speaker Công Suất 80W",
    price: 8990000,
    originalPrice: 10500000,
    discount: "-14%",
    rating: 5.0,
    sold: 42,
    totalStock: 25,
    image: "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80",
    shopName: "SoundMax & Marshall Audio",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },

  // Watch
  {
    id: 5,
    category: "watch",
    brand: "Tissot 1853",
    description: "Đồng hồ cơ Thụy Sĩ Powermatic 80 trữ cót 80 giờ kính Sapphire",
    title: "Đồng Hồ Cơ Nam Tissot Le Locle Powermatic 80 Thụy Sĩ",
    price: 15800000,
    originalPrice: 18500000,
    discount: "-15%",
    rating: 5.0,
    sold: 19,
    totalStock: 20,
    image: "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80",
    shopName: "Luxury Watch Vietnam",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 6,
    category: "watch",
    brand: "Seiko",
    description: "Đồng hồ automatic chống nước 100m thể thao nam tính",
    title: "Đồng Hồ Nam Thể Thao Seiko 5 Sports Automatic Chống Nước 100m",
    price: 6200000,
    originalPrice: 7500000,
    discount: "-17%",
    rating: 4.8,
    sold: 73,
    totalStock: 50,
    image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
    shopName: "Luxury Watch Vietnam",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 7,
    category: "watch",
    brand: "Daniel Wellington",
    description: "Đồng hồ nữ dây da thanh lịch mặt tối giản",
    title: "Đồng Hồ Nữ Dây Da Cao Cấp Daniel Wellington Petite Melrose",
    price: 3600000,
    originalPrice: 4500000,
    discount: "-20%",
    rating: 4.9,
    sold: 112,
    totalStock: 80,
    image: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
    shopName: "Luxury Watch Vietnam",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 8,
    category: "watch",
    brand: "Apple",
    description: "Đồng hồ thông minh vỏ Titan GPS Cellular đo nhịp tim",
    title: "Đồng Hồ Thông Minh Apple Watch Ultra 2 GPS + Cellular 49mm Titan",
    price: 20490000,
    originalPrice: 22990000,
    discount: "-11%",
    rating: 5.0,
    sold: 35,
    totalStock: 18,
    image: "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=800&q=80",
    shopName: "Luxury Watch Vietnam",
    exclusive: "Chính Hãng",
    isFlashSale: true,
  },

  // Fashion
  {
    id: 9,
    category: "fashion",
    brand: "Aristino Sartoriale",
    description: "Áo blazer len lông cừu may đo phong cách Ý lịch lãm",
    title: "Áo Blazer Nam May Đo Phong Cách Ý Aristino Premium Wool",
    price: 2450000,
    originalPrice: 3200000,
    discount: "-23%",
    rating: 4.8,
    sold: 65,
    totalStock: 40,
    image: "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80",
    shopName: "Aristino & Gentleman Store",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 10,
    category: "fashion",
    brand: "Giovanni",
    description: "Ví da bò Ý thật 100% thiết kế khóa kéo sang trọng",
    title: "Ví Da Nam Bò Ý Cầm Tay Khóa Kéo Cao Cấp Giovanni Leather",
    price: 1850000,
    originalPrice: 2500000,
    discount: "-26%",
    rating: 4.9,
    sold: 88,
    totalStock: 55,
    image: "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=80",
    shopName: "Aristino & Gentleman Store",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 11,
    category: "fashion",
    brand: "Dior Paris",
    description: "Túi xách nữ da thật thiết kế Paris cao cấp",
    title: "Túi Xách Nữ Da Thật Cao Cấp Thiết Kế Paris Sang Trọng",
    price: 3200000,
    originalPrice: 4200000,
    discount: "-24%",
    rating: 4.9,
    sold: 47,
    totalStock: 35,
    image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80",
    shopName: "Luxe Paris & Bags",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 12,
    category: "fashion",
    brand: "Giovanni",
    description: "Thắt lưng nam da bò thật khóa tự động mạ vàng 18K",
    title: "Thắt Lưng Nam Da Bò Thật Khóa Tự Động Mạ Vàng 18K",
    price: 950000,
    originalPrice: 1350000,
    discount: "-30%",
    rating: 4.8,
    sold: 140,
    totalStock: 70,
    image: "https://images.unsplash.com/photo-1624222247344-550fb60583dc?auto=format&fit=crop&w=800&q=80",
    shopName: "Luxe Paris & Bags",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },

  // Tech
  {
    id: 13,
    category: "tech",
    brand: "ASUS",
    description: "Card đồ họa RTX 5090 OC 32GB hỗ trợ Ray Tracing và DLSS",
    title: "Card Màn Hình VGA ASUS ROG Strix GeForce RTX 5090 OC 32GB",
    price: 68900000,
    originalPrice: 75000000,
    discount: "-8%",
    rating: 5.0,
    sold: 14,
    totalStock: 10,
    image: "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
    shopName: "GearVN Official Store",
    exclusive: "Chính Hãng",
    isFlashSale: true,
  },
  {
    id: 14,
    category: "tech",
    brand: "GMMK",
    description: "Bàn phím cơ không dây 75% hot-swap switch Gateron",
    title: "Bàn Phím Cơ Không Dây Custom GMMK Pro 75% Switch Gateron",
    price: 4250000,
    originalPrice: 4950000,
    discount: "-14%",
    rating: 4.9,
    sold: 95,
    totalStock: 40,
    image: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80",
    shopName: "GearVN Official Store",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 15,
    category: "tech",
    brand: "Logitech",
    description: "Chuột công thái học USB-C / 2.4G / Bluetooth 8000 DPI",
    title: "Chuột Công Thái Học Không Dây Logitech MX Master 3S Siêu Nhạy",
    price: 2490000,
    originalPrice: 2990000,
    discount: "-17%",
    rating: 5.0,
    sold: 180,
    totalStock: 60,
    image: "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=800&q=80",
    shopName: "GearVN Official Store",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
  {
    id: 16,
    category: "tech",
    brand: "Dell",
    description: "Màn hình 27 inch 2K 120Hz tấm nền IPS Black chuẩn màu đồ họa",
    title: "Màn Hình Chuyên Nghiệp Dell UltraSharp U2724D 27 inch 2K 120Hz IPS",
    price: 10890000,
    originalPrice: 12500000,
    discount: "-13%",
    rating: 4.9,
    sold: 38,
    totalStock: 25,
    image: "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80",
    shopName: "GearVN Official Store",
    exclusive: "Chính Hãng",
    isFlashSale: false,
  },
];

const CATEGORY_LABELS = {
  all: "Tất cả ngành hàng",
  audio: "Thiết Bị Âm Thanh",
  watch: "Đồng Hồ Cao Cấp",
  fashion: "Thời Trang & Đồ Da",
  tech: "Thiết Bị Số & PC",
  shoes: "Giày & Sneakers",
  beauty: "Làm Đẹp & Nước Hoa",
};

const PRICE_PRESET_BOUNDS = {
  "under-1m": { min: null, max: 999999, label: "Dưới 1.000.000 ₫" },
  "1m-5m": { min: 1000000, max: 5000000, label: "1M - 5M ₫" },
  "5m-15m": { min: 5000000, max: 15000000, label: "5M - 15M ₫" },
  "above-15m": { min: 15000001, max: null, label: "Trên 15.000.000 ₫" },
};

const SORT_LABELS = {
  rating_desc: "Phổ biến",
  newest: "Mới nhất",
  bestselling: "Bán chạy",
  price_asc: "Giá: Thấp → Cao",
  price_desc: "Giá: Cao → Thấp",
};

const VALID_CATEGORIES = new Set(["all", "audio", "watch", "fashion", "tech", "shoes", "beauty"]);
const DEFAULT_PAGE_SIZE = 8;
const DEFAULT_SORT = "rating_desc";

// Trạng thái bộ lọc chuẩn hóa đồng bộ với API & URL
const filterState = {
  q: "",
  category: "all",
  brands: [],
  priceRange: "all",
  minPrice: null,
  maxPrice: null,
  rating: "all",
  flashSale: false,
  exclusive: false,
  sort: DEFAULT_SORT,
  page: 1,
  pageSize: DEFAULT_PAGE_SIZE,
};

let currentPage = 1;
let totalPagesGlobal = 1;
let currentPageItems = [];
let availableBrands = Array.from(new Set(MOCK_PRODUCTS.map((p) => p.brand).filter(Boolean))).sort();
let filterAbortController = null;

// =========================================================================
// 1. ĐỌC & GHI TRẠNG THÁI TRÊN URL (HISTORY API + URLSEARCHPARAMS)
// =========================================================================
function normalizeSortParam(rawSort) {
  const s = (rawSort || "").trim().toLowerCase();
  const aliases = {
    popular: "rating_desc",
    rating_desc: "rating_desc",
    newest: "newest",
    bestseller: "bestselling",
    bestselling: "bestselling",
    sold_desc: "bestselling",
    "price-asc": "price_asc",
    price_asc: "price_asc",
    "price-desc": "price_desc",
    price_desc: "price_desc",
  };
  return aliases[s] || DEFAULT_SORT;
}

function parsePositiveInt(val) {
  if (val === null || val === undefined || val === "") return null;
  const n = Number(val);
  return Number.isFinite(n) && n >= 0 ? Math.floor(n) : null;
}

function readStateFromUrl() {
  const params = new URLSearchParams(window.location.search);

  filterState.q = (params.get("q") || "").trim();

  const rawCat = (params.get("category") || "all").trim().toLowerCase();
  filterState.category = VALID_CATEGORIES.has(rawCat) ? rawCat : "all";

  const rawBrand = (params.get("brand") || "").trim();
  filterState.brands = rawBrand
    ? Array.from(new Set(rawBrand.split(",").map((b) => b.trim()).filter(Boolean)))
    : [];

  const rawMin = parsePositiveInt(params.get("min_price"));
  const rawMax = parsePositiveInt(params.get("max_price"));
  const rawPreset = (params.get("price_range") || "").trim();

  if (rawPreset && PRICE_PRESET_BOUNDS[rawPreset]) {
    filterState.priceRange = rawPreset;
    filterState.minPrice = PRICE_PRESET_BOUNDS[rawPreset].min;
    filterState.maxPrice = PRICE_PRESET_BOUNDS[rawPreset].max;
  } else if (rawMin !== null || rawMax !== null) {
    filterState.priceRange = "custom";
    filterState.minPrice = rawMin;
    filterState.maxPrice = rawMax;
  } else {
    filterState.priceRange = "all";
    filterState.minPrice = null;
    filterState.maxPrice = null;
  }

  const rawRating = (params.get("rating") || "all").trim();
  filterState.rating = ["5", "4", "3"].includes(rawRating) ? rawRating : "all";

  filterState.flashSale = ["1", "true"].includes((params.get("flash_sale") || "").toLowerCase());
  filterState.exclusive = ["1", "true"].includes((params.get("exclusive") || "").toLowerCase());
  filterState.sort = normalizeSortParam(params.get("sort"));

  const rawPage = parsePositiveInt(params.get("page"));
  filterState.page = rawPage && rawPage >= 1 ? rawPage : 1;
  currentPage = filterState.page;

  const rawSize = parsePositiveInt(params.get("page_size"));
  filterState.pageSize = rawSize && [8, 12, 24].includes(rawSize) ? rawSize : DEFAULT_PAGE_SIZE;
}

function buildUrlSearchParams() {
  const params = new URLSearchParams();
  if (filterState.q) params.set("q", filterState.q);
  if (filterState.category && filterState.category !== "all") params.set("category", filterState.category);
  if (filterState.brands.length > 0) params.set("brand", filterState.brands.join(","));

  if (filterState.priceRange !== "all") {
    if (filterState.priceRange !== "custom") {
      params.set("price_range", filterState.priceRange);
    }
    if (filterState.minPrice !== null) params.set("min_price", String(filterState.minPrice));
    if (filterState.maxPrice !== null) params.set("max_price", String(filterState.maxPrice));
  }

  if (filterState.rating !== "all") params.set("rating", filterState.rating);
  if (filterState.flashSale) params.set("flash_sale", "1");
  if (filterState.exclusive) params.set("exclusive", "1");
  if (filterState.sort && filterState.sort !== DEFAULT_SORT) params.set("sort", filterState.sort);
  if (filterState.page > 1) params.set("page", String(filterState.page));
  if (filterState.pageSize !== DEFAULT_PAGE_SIZE) params.set("page_size", String(filterState.pageSize));

  return params;
}

function syncStateToUrl(replace = false) {
  const params = buildUrlSearchParams();
  const qs = params.toString();
  const basePath = window.location.pathname.split("/").pop() || "products.html";
  const nextUrl = qs ? `${basePath}?${qs}` : basePath;

  try {
    if (replace) {
      window.history.replaceState({ ...filterState }, "", nextUrl);
    } else {
      window.history.pushState({ ...filterState }, "", nextUrl);
    }
  } catch (e) {
    // file:// origin guard
  }
}

// =========================================================================
// 2. ĐỒNG BỘ GIAO DIỆN SIDEBAR, SORT BAR, CHIPS VỚI STATE
// =========================================================================
function renderBrandCheckboxes() {
  const container = document.getElementById("brandFilterList");
  if (!container) return;

  const mergedBrands = Array.from(new Set([...availableBrands, ...filterState.brands])).sort();
  container.innerHTML = mergedBrands
    .map((brand) => {
      const checked = filterState.brands.includes(brand) ? "checked" : "";
      const safeVal = brand.replace(/"/g, "&quot;");
      return `
        <label class="filter-option">
          <input type="checkbox" class="brand-checkbox" value="${safeVal}" ${checked} onchange="handleBrandCheckboxChange()" />
          <span>${safeVal}</span>
        </label>
      `;
    })
    .join("");
}

function syncUIFromState() {
  const searchEl = document.getElementById("searchInput");
  if (searchEl) searchEl.value = filterState.q;

  document.querySelectorAll(".category-item").forEach((el) => {
    const cat = el.getAttribute("data-cat");
    el.classList.toggle("active", cat === filterState.category);
  });

  renderBrandCheckboxes();

  document.querySelectorAll('input[name="priceRange"]').forEach((radio) => {
    radio.checked = radio.value === filterState.priceRange;
  });

  const minEl = document.getElementById("minPriceInput");
  const maxEl = document.getElementById("maxPriceInput");
  if (filterState.priceRange === "custom") {
    if (minEl) minEl.value = filterState.minPrice !== null ? filterState.minPrice : "";
    if (maxEl) maxEl.value = filterState.maxPrice !== null ? filterState.maxPrice : "";
  } else {
    if (minEl) minEl.value = "";
    if (maxEl) maxEl.value = "";
  }

  document.querySelectorAll('input[name="ratingFilter"]').forEach((radio) => {
    radio.checked = radio.value === filterState.rating;
  });

  const chkFlash = document.getElementById("chkFlashSale");
  const chkExcl = document.getElementById("chkExclusive");
  if (chkFlash) chkFlash.checked = filterState.flashSale;
  if (chkExcl) chkExcl.checked = filterState.exclusive;

  document.querySelectorAll(".sort-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.getAttribute("data-sort") === filterState.sort);
  });

  const priceSelect = document.getElementById("priceSortSelect");
  if (priceSelect) {
    priceSelect.value =
      filterState.sort === "price_asc" || filterState.sort === "price_desc"
        ? filterState.sort
        : "default";
  }

  const pageSizeSelect = document.getElementById("pageSizeSelect");
  if (pageSizeSelect) {
    pageSizeSelect.value = String(filterState.pageSize);
  }

  const breadcrumbCat = document.getElementById("breadcrumbCurrentCategory");
  if (breadcrumbCat) {
    breadcrumbCat.textContent = filterState.q
      ? `Tìm kiếm: "${filterState.q}"`
      : CATEGORY_LABELS[filterState.category] || filterState.category;
  }

  updateActiveCountBadge();
  renderActiveFilterChips();
}

function updateActiveCountBadge() {
  let count = 0;
  if (filterState.category !== "all") count++;
  if (filterState.brands.length > 0) count += filterState.brands.length;
  if (filterState.priceRange !== "all") count++;
  if (filterState.rating !== "all") count++;
  if (filterState.flashSale) count++;
  if (filterState.exclusive) count++;
  const badge = document.getElementById("mobileActiveCount");
  if (badge) badge.textContent = count;
}

function renderActiveFilterChips() {
  const bar = document.getElementById("activeFiltersBar");
  if (!bar) return;

  const chips = [];
  if (filterState.q) {
    chips.push({ label: `Từ khóa: "${filterState.q}"`, action: "clearSingleFilter('q')" });
  }
  if (filterState.category !== "all") {
    chips.push({
      label: `Danh mục: ${CATEGORY_LABELS[filterState.category] || filterState.category}`,
      action: "clearSingleFilter('category')",
    });
  }
  filterState.brands.forEach((b) => {
    const escaped = b.replace(/'/g, "\\'");
    chips.push({ label: `Hãng: ${b}`, action: `clearSingleFilter('brand', '${escaped}')` });
  });
  if (filterState.priceRange !== "all") {
    const priceLabel =
      filterState.priceRange !== "custom"
        ? PRICE_PRESET_BOUNDS[filterState.priceRange]?.label
        : `${filterState.minPrice !== null ? formatCurrency(filterState.minPrice) : "0 ₫"} - ${
            filterState.maxPrice !== null ? formatCurrency(filterState.maxPrice) : "Trở lên"
          }`;
    chips.push({ label: `Giá: ${priceLabel}`, action: "clearSingleFilter('price')" });
  }
  if (filterState.rating !== "all") {
    chips.push({ label: `Đánh giá: Từ ${filterState.rating}★`, action: "clearSingleFilter('rating')" });
  }
  if (filterState.flashSale) {
    chips.push({ label: "⚡ Flash Sale", action: "clearSingleFilter('flashSale')" });
  }
  if (filterState.exclusive) {
    chips.push({ label: "🛡️ Chính Hãng", action: "clearSingleFilter('exclusive')" });
  }
  if (filterState.sort !== DEFAULT_SORT) {
    chips.push({
      label: `Sắp xếp: ${SORT_LABELS[filterState.sort] || filterState.sort}`,
      action: "clearSingleFilter('sort')",
    });
  }

  if (chips.length === 0) {
    bar.classList.remove("visible");
    bar.innerHTML = "";
    return;
  }

  bar.classList.add("visible");
  bar.innerHTML = `
    <span class="active-filters-label">Đang lọc:</span>
    ${chips
      .map(
        (c) => `
      <span class="filter-chip">
        <span>${c.label}</span>
        <button type="button" onclick="${c.action}" title="Bỏ bộ lọc này">&times;</button>
      </span>
    `
      )
      .join("")}
    <button type="button" class="btn-clear-all-chips" onclick="resetAllFilters()">Xóa tất cả</button>
  `;
}

// =========================================================================
// 3. KHỞI TẠO TRANG & GỌI API BACKEND (/api/products/filter + /facets)
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
  readStateFromUrl();
  syncUIFromState();

  if (window.HeaderSearch && typeof window.HeaderSearch.init === "function") {
    window.HeaderSearch.init({
      inputId: "searchInput",
      isResultsPage: true,
      resultsUrl: "products.html",
      onSearchResults: (kw) => {
        filterState.q = (kw || "").trim();
        filterState.page = 1;
        syncStateToUrl(false);
        syncUIFromState();
        loadProductsFromApi();
      },
    });
  }

  loadFilterFacets();
  loadProductsFromApi();
  updateCartBadge();
});

window.addEventListener("popstate", () => {
  readStateFromUrl();
  syncUIFromState();
  loadProductsFromApi();
});

async function loadFilterFacets() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/products/facets`);
    if (!res.ok) return;
    const data = await res.json();

    const countAllEl = document.getElementById("countAll");
    if (countAllEl && typeof data.total === "number") {
      countAllEl.textContent = data.total;
    }

    if (data.categories && typeof data.categories === "object") {
      Object.entries(data.categories).forEach(([cat, cnt]) => {
        const el = document.getElementById(`countCat-${cat}`);
        if (el) el.textContent = cnt;
      });
    }

    if (Array.isArray(data.brands) && data.brands.length > 0) {
      availableBrands = data.brands;
      renderBrandCheckboxes();
    }
  } catch (e) {
    // Fallback counts from MOCK_PRODUCTS when backend is offline
    const countAllEl = document.getElementById("countAll");
    if (countAllEl) countAllEl.textContent = MOCK_PRODUCTS.length;
  }
}

function mapApiProductItem(p) {
  return {
    id: p.id,
    category: p.category || "tech",
    brand: p.brand || "",
    description: p.description || "",
    title: p.title,
    price: p.price,
    originalPrice: p.originalPrice || Math.round(p.price * 1.2),
    discount: p.discount || "-15%",
    rating: Number(p.rating || 5.0),
    sold: Number(p.sold || p.soldCount || 0),
    totalStock: p.totalStock || 50,
    image:
      Array.isArray(p.images) && p.images[0]
        ? p.images[0]
        : p.image ||
          "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
    shopName: p.shopName || "JML Official Store",
    exclusive: p.exclusive || "Chính Hãng",
    isFlashSale: Boolean(p.isFlashSale || p.is_flash_sale),
  };
}

function buildBackendFilterUrl() {
  const apiParams = new URLSearchParams();
  if (filterState.category !== "all") apiParams.set("category", filterState.category);
  if (filterState.brands.length > 0) apiParams.set("brand", filterState.brands.join(","));
  if (filterState.minPrice !== null) apiParams.set("min_price", String(filterState.minPrice));
  if (filterState.maxPrice !== null) apiParams.set("max_price", String(filterState.maxPrice));
  if (filterState.rating !== "all") apiParams.set("min_rating", filterState.rating);
  if (filterState.flashSale) apiParams.set("flash_sale", "true");
  if (filterState.exclusive) apiParams.set("exclusive", "true");
  if (filterState.q) apiParams.set("q", filterState.q);

  apiParams.set("sort", filterState.sort);
  apiParams.set("page", String(filterState.page));
  apiParams.set("page_size", String(filterState.pageSize));

  return `${API_BASE_URL}/api/products/filter?${apiParams.toString()}`;
}

function updateApiSourceBadge(isOnline) {
  const badge = document.getElementById("apiSourceBadge");
  if (!badge) return;
  if (isOnline) {
    badge.className = "api-source-badge online";
    badge.textContent = "🟢 API Backend Live";
  } else {
    badge.className = "api-source-badge offline";
    badge.textContent = "🟡 Demo Offline";
  }
}

async function loadProductsFromApi() {
  const grid = document.getElementById("productsGrid");
  if (grid) grid.classList.add("is-loading");

  if (filterAbortController) {
    filterAbortController.abort();
  }
  filterAbortController = new AbortController();

  try {
    const url = buildBackendFilterUrl();
    const res = await fetch(url, { signal: filterAbortController.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    const items = Array.isArray(data.items) ? data.items.map(mapApiProductItem) : [];
    const pagination = data.pagination || {
      page: filterState.page,
      page_size: filterState.pageSize,
      total: Number(data.total || items.length),
      total_pages: Math.ceil(Number(data.total || items.length) / filterState.pageSize),
      has_next: false,
      has_prev: filterState.page > 1,
    };

    // Nếu trang trên URL vượt quá total_pages của kết quả mới -> lùi về trang 1
    if (pagination.total > 0 && filterState.page > pagination.total_pages) {
      filterState.page = 1;
      currentPage = 1;
      syncStateToUrl(true);
      await loadProductsFromApi();
      return;
    }

    currentPage = pagination.page;
    totalPagesGlobal = Math.max(pagination.total_pages || 1, 1);
    currentPageItems = items;

    updateApiSourceBadge(true);
    renderProductsResponse(items, pagination);
  } catch (err) {
    if (err && err.name === "AbortError") return;
    console.warn("Backend API offline, dùng chế độ lọc/sắp xếp/phân trang cục bộ:", err.message);
    updateApiSourceBadge(false);
    runOfflineFilterSortPaginate();
  } finally {
    if (grid) grid.classList.remove("is-loading");
  }
}

function runOfflineFilterSortPaginate() {
  const kw = filterState.q.toLowerCase();
  const minRating = filterState.rating !== "all" ? Number(filterState.rating) : null;

  let matched = MOCK_PRODUCTS.filter((p) => {
    if (filterState.category !== "all" && p.category !== filterState.category) return false;
    if (
      filterState.brands.length > 0 &&
      !filterState.brands.some((b) => b.toLowerCase() === (p.brand || "").toLowerCase())
    ) {
      return false;
    }
    if (filterState.minPrice !== null && p.price < filterState.minPrice) return false;
    if (filterState.maxPrice !== null && p.price > filterState.maxPrice) return false;
    if (minRating !== null && p.rating < minRating) return false;
    if (filterState.flashSale && !p.isFlashSale) return false;
    if (filterState.exclusive && !(p.exclusive || "").toLowerCase().includes("chính hãng")) return false;
    if (kw) {
      const hay = `${p.title} ${p.description} ${p.brand} ${p.shopName} ${p.category}`.toLowerCase();
      if (!hay.includes(kw)) return false;
    }
    return true;
  });

  if (filterState.sort === "price_asc") {
    matched.sort((a, b) => a.price - b.price);
  } else if (filterState.sort === "price_desc") {
    matched.sort((a, b) => b.price - a.price);
  } else if (filterState.sort === "newest") {
    matched.sort((a, b) => b.id - a.id);
  } else if (filterState.sort === "bestselling") {
    matched.sort((a, b) => (b.sold || 0) - (a.sold || 0));
  } else {
    matched.sort((a, b) => b.rating * 10 + b.sold - (a.rating * 10 + a.sold));
  }

  const total = matched.length;
  const totalPages = total > 0 ? Math.ceil(total / filterState.pageSize) : 0;
  if (total > 0 && filterState.page > totalPages) {
    filterState.page = 1;
    syncStateToUrl(true);
  }

  currentPage = filterState.page;
  totalPagesGlobal = Math.max(totalPages, 1);

  const start = (filterState.page - 1) * filterState.pageSize;
  const pageItems = matched.slice(start, start + filterState.pageSize);
  currentPageItems = pageItems;

  renderProductsResponse(pageItems, {
    page: filterState.page,
    page_size: filterState.pageSize,
    total,
    total_pages: totalPages,
    has_prev: filterState.page > 1 && total > 0,
    has_next: filterState.page < totalPages,
  });
}

// =========================================================================
// 4. SỰ KIỆN TƯƠNG TÁC BỘ LỌC, SẮP XẾP, PHÂN TRANG -> CẬP NHẬT URL & API
// =========================================================================
function applyFilterChange(resetPage = true) {
  if (resetPage) filterState.page = 1;
  currentPage = filterState.page;
  syncStateToUrl(false);
  syncUIFromState();
  loadProductsFromApi();
}

function selectCategory(cat) {
  filterState.category = VALID_CATEGORIES.has(cat) ? cat : "all";
  applyFilterChange(true);
  if (window.innerWidth <= 900) closeFilterDrawer();
}

function handleBrandCheckboxChange() {
  const selected = [];
  document.querySelectorAll(".brand-checkbox:checked").forEach((cb) => {
    if (cb.value) selected.push(cb.value);
  });
  filterState.brands = selected;
  applyFilterChange(true);
}

function handlePriceFilter(range) {
  filterState.priceRange = PRICE_PRESET_BOUNDS[range] ? range : "all";
  if (PRICE_PRESET_BOUNDS[range]) {
    filterState.minPrice = PRICE_PRESET_BOUNDS[range].min;
    filterState.maxPrice = PRICE_PRESET_BOUNDS[range].max;
  } else {
    filterState.minPrice = null;
    filterState.maxPrice = null;
  }
  applyFilterChange(true);
}

function applyCustomPriceRange() {
  const minRaw = document.getElementById("minPriceInput")?.value;
  const maxRaw = document.getElementById("maxPriceInput")?.value;
  const minVal = parsePositiveInt(minRaw);
  const maxVal = parsePositiveInt(maxRaw);

  if (minVal === null && maxVal === null) {
    handlePriceFilter("all");
    return;
  }
  if (minVal !== null && maxVal !== null && minVal > maxVal) {
    showToast("Khoảng giá không hợp lệ: Giá tối thiểu phải nhỏ hơn giá tối đa!");
    return;
  }

  filterState.priceRange = "custom";
  filterState.minPrice = minVal;
  filterState.maxPrice = maxVal;
  applyFilterChange(true);
  showToast(
    `Đã lọc giá: ${minVal !== null ? formatCurrency(minVal) : "0 ₫"} - ${
      maxVal !== null ? formatCurrency(maxVal) : "Trở lên"
    }`
  );
  if (window.innerWidth <= 900) closeFilterDrawer();
}

function handleRatingFilter(rating) {
  filterState.rating = ["5", "4", "3"].includes(rating) ? rating : "all";
  applyFilterChange(true);
}

function applyOtherFilters() {
  filterState.flashSale = Boolean(document.getElementById("chkFlashSale")?.checked);
  filterState.exclusive = Boolean(document.getElementById("chkExclusive")?.checked);
  applyFilterChange(true);
}

function changeSort(sortType) {
  filterState.sort = normalizeSortParam(sortType);
  applyFilterChange(true);
}

function handlePriceSortSelect(val) {
  if (val === "price_asc" || val === "price_desc" || val === "price-asc" || val === "price-desc") {
    filterState.sort = normalizeSortParam(val);
  } else {
    filterState.sort = DEFAULT_SORT;
  }
  applyFilterChange(true);
}

function changePageSize(size) {
  const num = Number(size);
  filterState.pageSize = [8, 12, 24].includes(num) ? num : DEFAULT_PAGE_SIZE;
  applyFilterChange(true);
}

function changePage(page) {
  const target = Number(page);
  if (!Number.isFinite(target) || target < 1 || target > totalPagesGlobal || target === filterState.page) {
    return;
  }
  filterState.page = target;
  currentPage = target;
  syncStateToUrl(false);
  loadProductsFromApi();
  window.scrollTo({ top: 120, behavior: "smooth" });
}

function executeSearch() {
  const inputEl = document.getElementById("searchInput");
  const kw = (inputEl ? inputEl.value : "").trim();
  if (window.HeaderSearch && typeof window.HeaderSearch.submitSearch === "function") {
    window.HeaderSearch.submitSearch(kw);
  } else {
    filterState.q = kw;
    applyFilterChange(true);
  }
  if (window.innerWidth <= 900) closeFilterDrawer();
}

function clearSearchKeyword() {
  filterState.q = "";
  applyFilterChange(true);
}

function clearSingleFilter(type, value = null) {
  if (type === "q") filterState.q = "";
  else if (type === "category") filterState.category = "all";
  else if (type === "brand" && value) {
    filterState.brands = filterState.brands.filter((b) => b !== value);
  } else if (type === "price") {
    filterState.priceRange = "all";
    filterState.minPrice = null;
    filterState.maxPrice = null;
  } else if (type === "rating") filterState.rating = "all";
  else if (type === "flashSale") filterState.flashSale = false;
  else if (type === "exclusive") filterState.exclusive = false;
  else if (type === "sort") filterState.sort = DEFAULT_SORT;

  applyFilterChange(true);
}

function resetAllFilters() {
  filterState.q = "";
  filterState.category = "all";
  filterState.brands = [];
  filterState.priceRange = "all";
  filterState.minPrice = null;
  filterState.maxPrice = null;
  filterState.rating = "all";
  filterState.flashSale = false;
  filterState.exclusive = false;
  filterState.sort = DEFAULT_SORT;
  filterState.page = 1;
  currentPage = 1;

  syncStateToUrl(false);
  syncUIFromState();
  loadProductsFromApi();
  showToast("Đã đặt lại tất cả bộ lọc & trạng thái URL");
}

// =========================================================================
// 5. RENDER LƯỚI SẢN PHẨM & PHÂN TRANG DỰA TRÊN METADATA API
// =========================================================================
function updateSearchBannerUI(totalCount) {
  const banner = document.getElementById("searchResultsBanner");
  const kwDisplay = document.getElementById("searchKeywordDisplay");
  const countDisplay = document.getElementById("searchBannerCount");

  if (filterState.q) {
    if (banner) banner.classList.add("visible");
    if (kwDisplay) kwDisplay.textContent = `"${filterState.q}"`;
    if (countDisplay) countDisplay.textContent = totalCount;
    document.title = `Tìm kiếm "${filterState.q}" - JML Store`;
  } else {
    if (banner) banner.classList.remove("visible");
    document.title =
      filterState.category !== "all"
        ? `${CATEGORY_LABELS[filterState.category] || filterState.category} - JML Store`
        : "Danh Sách Sản Phẩm - JML Store";
  }
}

function renderProductsResponse(items, pagination) {
  const total = Number(pagination.total || 0);
  const countEl = document.getElementById("productCountText");
  if (countEl) countEl.textContent = total;
  updateSearchBannerUI(total);

  const grid = document.getElementById("productsGrid");
  const pagWrapper = document.getElementById("paginationWrapper");
  if (!grid) return;

  if (!items || items.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-title">Không tìm thấy sản phẩm phù hợp</div>
        <p class="empty-state-desc">Hãy thử thay đổi từ khóa, danh mục, thương hiệu hoặc mở rộng khoảng giá tìm kiếm của bạn.</p>
        <button class="btn-apply-price" style="width: auto; padding: 8px 20px; display: inline-block;" onclick="resetAllFilters()">Xóa Tất Cả Bộ Lọc</button>
      </div>
    `;
    if (pagWrapper) pagWrapper.style.display = "none";
    return;
  }

  grid.innerHTML = items
    .map(
      (p) => `
      <div class="product-card" onclick="goToDetail(${p.id})">
        <div class="product-img-wrap">
          <img src="${p.image}" alt="${p.title}" class="product-img" loading="lazy" />
          ${p.discount ? `<span class="discount-tag">${p.discount}</span>` : ""}
          <span class="shop-tag">🏪 ${p.shopName || "JML Mall"}</span>
        </div>
        <div class="product-info">
          <h3 class="product-title" title="${p.title}">${p.title}</h3>
          <div class="product-price-row">
            <span class="price-current">${formatCurrency(p.price)}</span>
            ${p.originalPrice > p.price ? `<span class="price-original">${formatCurrency(p.originalPrice)}</span>` : ""}
          </div>
          <div class="product-meta-row">
            <span class="stars-yellow">★ ${Number(p.rating || 5).toFixed(1)}</span>
            <span>Đã bán ${p.sold || 0}</span>
          </div>
          <button class="btn-add-cart" onclick="addToCart(event, ${p.id})">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M12 5v14M5 12h14"></path>
            </svg>
            Thêm Vào Giỏ
          </button>
        </div>
      </div>
    `
    )
    .join("");

  renderPaginationControls(pagination);
}

function getVisiblePageNumbers(current, totalPages) {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, idx) => idx + 1);
  }
  const pages = [1];
  const left = Math.max(2, current - 1);
  const right = Math.min(totalPages - 1, current + 1);

  if (left > 2) pages.push("...");
  for (let i = left; i <= right; i++) pages.push(i);
  if (right < totalPages - 1) pages.push("...");
  pages.push(totalPages);
  return pages;
}

function renderPaginationControls(pagination) {
  const pagWrapper = document.getElementById("paginationWrapper");
  if (!pagWrapper) return;

  const totalPages = Math.max(Number(pagination.total_pages || 1), 1);
  const page = Number(pagination.page || 1);

  if (totalPages <= 1) {
    pagWrapper.style.display = "none";
    return;
  }

  pagWrapper.style.display = "flex";
  const pageTokens = getVisiblePageNumbers(page, totalPages);

  let html = `<button class="page-btn" ${!pagination.has_prev ? "disabled" : ""} onclick="changePage(${page - 1})">‹</button>`;
  pageTokens.forEach((tok) => {
    if (tok === "...") {
      html += `<span class="page-ellipsis">...</span>`;
    } else {
      html += `<button class="page-btn ${tok === page ? "active" : ""}" onclick="changePage(${tok})">${tok}</button>`;
    }
  });
  html += `<button class="page-btn" ${!pagination.has_next ? "disabled" : ""} onclick="changePage(${page + 1})">›</button>`;
  html += `<span class="pagination-meta">Trang ${page} / ${totalPages}</span>`;

  pagWrapper.innerHTML = html;
}

// =========================================================================
// 6. MOBILE DRAWER & TIỆN ÍCH GIỎ HÀNG
// =========================================================================
function openFilterDrawer() {
  const sidebar = document.getElementById("filterSidebar");
  const backdrop = document.getElementById("drawerBackdrop");
  if (sidebar) sidebar.classList.add("drawer-open");
  if (backdrop) backdrop.classList.add("active");
  document.body.style.overflow = "hidden";
}

function closeFilterDrawer() {
  const sidebar = document.getElementById("filterSidebar");
  const backdrop = document.getElementById("drawerBackdrop");
  if (sidebar) sidebar.classList.remove("drawer-open");
  if (backdrop) backdrop.classList.remove("active");
  document.body.style.overflow = "";
}

function formatCurrency(amount) {
  return Number(amount || 0).toLocaleString("vi-VN") + " ₫";
}

function goToDetail(id) {
  window.location.href = `index.html?productId=${id}`;
}

function addToCart(event, id) {
  event.stopPropagation();
  const p =
    currentPageItems.find((item) => item.id === id) ||
    MOCK_PRODUCTS.find((item) => item.id === id);
  if (!p) return;

  let cart = JSON.parse(localStorage.getItem("JML_CART_ITEMS") || "[]");
  const existing = cart.find((item) => item.id === id);
  if (existing) {
    existing.qty = (existing.qty || 1) + 1;
  } else {
    cart.push({
      id: p.id,
      title: p.title,
      price: p.price,
      image: p.image,
      shopName: p.shopName,
      qty: 1,
    });
  }
  localStorage.setItem("JML_CART_ITEMS", JSON.stringify(cart));
  updateCartBadge();
  showToast(`Đã thêm "${p.title.substring(0, 24)}..." vào giỏ hàng!`);
}

function updateCartBadge() {
  const cart = JSON.parse(localStorage.getItem("JML_CART_ITEMS") || "[]");
  const count = cart.reduce((sum, it) => sum + (it.qty || 1), 0);
  const badge = document.getElementById("cartBadgeCount");
  if (badge) badge.textContent = count;
}

function showToast(msg) {
  const box = document.getElementById("toastBox");
  if (!box) return;
  box.className = "toast-msg";
  box.innerHTML = `<span>✓</span><span>${msg}</span>`;
  box.style.display = "flex";
  setTimeout(() => {
    box.style.display = "none";
  }, 3000);
}
