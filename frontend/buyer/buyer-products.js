// Dữ liệu sản phẩm mẫu phong phú (16 sản phẩm thuộc 4 ngành hàng chính)
      const MOCK_PRODUCTS = [
        // Audio
        {
          id: 1,
          category: "audio",
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
          isFlashSale: true
        },
        {
          id: 2,
          category: "audio",
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
          isFlashSale: false
        },
        {
          id: 3,
          category: "audio",
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
          isFlashSale: false
        },
        {
          id: 4,
          category: "audio",
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
          isFlashSale: false
        },

        // Watch
        {
          id: 5,
          category: "watch",
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
          isFlashSale: false
        },
        {
          id: 6,
          category: "watch",
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
          isFlashSale: false
        },
        {
          id: 7,
          category: "watch",
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
          isFlashSale: false
        },
        {
          id: 8,
          category: "watch",
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
          isFlashSale: true
        },

        // Fashion
        {
          id: 9,
          category: "fashion",
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
          isFlashSale: false
        },
        {
          id: 10,
          category: "fashion",
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
          isFlashSale: false
        },
        {
          id: 11,
          category: "fashion",
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
          isFlashSale: false
        },
        {
          id: 12,
          category: "fashion",
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
          isFlashSale: false
        },

        // Tech
        {
          id: 13,
          category: "tech",
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
          isFlashSale: true
        },
        {
          id: 14,
          category: "tech",
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
          isFlashSale: false
        },
        {
          id: 15,
          category: "tech",
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
          isFlashSale: false
        },
        {
          id: 16,
          category: "tech",
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
          isFlashSale: false
        }
      ];

      // Biến trạng thái toàn cục (đồng bộ với API /api/products/filter & URL)
      const API_BASE_URL = (window.location.origin && window.location.origin.startsWith("http"))
        ? window.location.origin
        : "http://127.0.0.1:8000";

      let allProducts = [...MOCK_PRODUCTS];
      let filteredProducts = [...MOCK_PRODUCTS];
      let currentCategory = "all";
      let currentBrand = "all";
      let currentPriceRange = "all";
      let currentRating = "all";
      let currentSort = "popular";
      let searchQuery = "";
      let currentPage = 1;
      const pageSize = 8;

      let serverPagination = { page: 1, page_size: pageSize, total: MOCK_PRODUCTS.length, total_pages: 2, has_next: false, has_prev: false };
      let isApiConnected = true;
      let searchDebounceTimer = null;
      let activeFilterController = null;

      const CATEGORY_NAMES = {
        all: "Tất cả ngành hàng",
        audio: "Thiết Bị Âm Thanh",
        watch: "Đồng Hồ Cao Cấp",
        fashion: "Thời Trang & Đồ Da",
        tech: "Thiết Bị Số & PC",
        shoes: "Giày & Sneakers",
        beauty: "Mỹ Phẩm & Nước Hoa"
      };
      const CATEGORY_LABELS = CATEGORY_NAMES;

      const PRICE_RANGE_LABELS = {
        "under-1m": "Dưới 1.000.000 ₫",
        "1m-5m": "1.000.000 ₫ - 5.000.000 ₫",
        "5m-15m": "5.000.000 ₫ - 15.000.000 ₫",
        "above-15m": "Trên 15.000.000 ₫"
      };

      function escapeHtml(str) {
        return String(str || "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#39;");
      }

      const SORT_UI_TO_API = {
        popular: "rating_desc",
        newest: "newest",
        bestseller: "bestselling",
        "price-asc": "price_asc",
        "price-desc": "price_desc"
      };

      // Khởi tạo trang
      document.addEventListener("DOMContentLoaded", () => {
        hydrateStateFromUrl();
        loadFilterFacetsFromAPI();
        fetchFilteredProductsFromAPI({ updateUrl: false });
        updateCartBadge();
        loadRecentSearches();
      });

      window.addEventListener("popstate", () => {
        hydrateStateFromUrl();
        fetchFilteredProductsFromAPI({ updateUrl: false });
      });

      function mapApiProduct(p) {
        return {
          id: p.id,
          category: p.category,
          brand: p.brand || "Khác",
          title: p.title,
          price: p.price,
          originalPrice: p.originalPrice || Math.round(p.price * 1.2),
          discount: p.discount || "-15%",
          rating: p.rating || 5.0,
          sold: p.sold || 0,
          totalStock: p.totalStock || 50,
          image: (p.images && p.images[0]) ? p.images[0] : "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
          shopName: p.shopName || "JML Official Store",
          exclusive: p.exclusive || "Chính Hãng",
          isFlashSale: Boolean(p.isFlashSale || p.is_flash_sale)
        };
      }

      function computePriceBounds() {
        if (currentPriceRange === "under-1m") return { min: null, max: 999999 };
        if (currentPriceRange === "1m-5m") return { min: 1000000, max: 5000000 };
        if (currentPriceRange === "5m-15m") return { min: 5000000, max: 15000000 };
        if (currentPriceRange === "above-15m") return { min: 15000001, max: null };
        if (typeof currentPriceRange === "object" && currentPriceRange.custom) {
          return {
            min: currentPriceRange.min > 0 ? currentPriceRange.min : null,
            max: currentPriceRange.max !== Infinity ? currentPriceRange.max : null
          };
        }
        return { min: null, max: null };
      }

      function buildApiQueryParams() {
        const params = new URLSearchParams();
        const isFlashOnly = document.getElementById("chkFlashSale")?.checked;
        const isExclusiveOnly = document.getElementById("chkExclusive")?.checked;
        const { min, max } = computePriceBounds();

        if (currentCategory && currentCategory !== "all") params.set("category", currentCategory);
        if (currentBrand && currentBrand !== "all") params.set("brand", currentBrand);
        if (searchQuery) params.set("q", document.getElementById("searchInput")?.value.trim() || searchQuery);
        if (min !== null) params.set("min_price", String(min));
        if (max !== null) params.set("max_price", String(max));
        if (currentRating && currentRating !== "all") params.set("min_rating", String(currentRating));
        if (isFlashOnly) params.set("flash_sale", "true");
        if (isExclusiveOnly) params.set("exclusive", "true");

        params.set("sort", SORT_UI_TO_API[currentSort] || "rating_desc");
        params.set("page", String(currentPage));
        params.set("page_size", String(pageSize));
        return params;
      }

      function syncStateToUrl() {
        const urlParams = new URLSearchParams();
        const isFlashOnly = document.getElementById("chkFlashSale")?.checked;
        const isExclusiveOnly = document.getElementById("chkExclusive")?.checked;
        const rawSearch = (document.getElementById("searchInput")?.value || "").trim();

        if (rawSearch) urlParams.set("q", rawSearch);
        if (currentCategory && currentCategory !== "all") urlParams.set("category", currentCategory);
        if (currentBrand && currentBrand !== "all") urlParams.set("brand", currentBrand);

        if (typeof currentPriceRange === "string" && currentPriceRange !== "all") {
          urlParams.set("price", currentPriceRange);
        } else if (typeof currentPriceRange === "object" && currentPriceRange.custom) {
          if (currentPriceRange.min > 0) urlParams.set("min_price", String(currentPriceRange.min));
          if (currentPriceRange.max !== Infinity) urlParams.set("max_price", String(currentPriceRange.max));
        }

        if (currentRating && currentRating !== "all") urlParams.set("rating", currentRating);
        if (isFlashOnly) urlParams.set("flash_sale", "1");
        if (isExclusiveOnly) urlParams.set("exclusive", "1");
        if (currentSort && currentSort !== "popular") urlParams.set("sort", currentSort);
        if (currentPage > 1) urlParams.set("page", String(currentPage));

        const qs = urlParams.toString();
        const newUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
        window.history.replaceState(null, "", newUrl);
      }

      function hydrateStateFromUrl() {
        const params = new URLSearchParams(window.location.search);

        const q = (params.get("q") || "").trim();
        searchQuery = q.toLowerCase();
        const searchEl = document.getElementById("searchInput");
        if (searchEl) searchEl.value = q;

        const cat = (params.get("category") || "all").trim().toLowerCase();
        currentCategory = CATEGORY_NAMES[cat] ? cat : "all";
        document.querySelectorAll(".category-item[data-cat]").forEach(item => {
          item.classList.toggle("active", item.getAttribute("data-cat") === currentCategory);
        });
        const bc = document.getElementById("breadcrumbCurrentCategory");
        if (bc) bc.textContent = CATEGORY_NAMES[currentCategory] || currentCategory;

        currentBrand = (params.get("brand") || "all").trim() || "all";
        const brandSelect = document.getElementById("brandFilterSelect");
        if (brandSelect) brandSelect.value = currentBrand;

        const pricePreset = params.get("price");
        const minPriceParam = params.get("min_price");
        const maxPriceParam = params.get("max_price");
        const minEl = document.getElementById("minPriceInput");
        const maxEl = document.getElementById("maxPriceInput");

        if (pricePreset && ["under-1m", "1m-5m", "5m-15m", "above-15m"].includes(pricePreset)) {
          currentPriceRange = pricePreset;
          if (minEl) minEl.value = "";
          if (maxEl) maxEl.value = "";
          document.querySelectorAll('input[name="priceRange"]').forEach(r => {
            r.checked = (r.value === pricePreset);
          });
        } else if (minPriceParam !== null || maxPriceParam !== null) {
          const minV = parseInt(minPriceParam || "0", 10) || 0;
          const maxV = maxPriceParam ? (parseInt(maxPriceParam, 10) || Infinity) : Infinity;
          currentPriceRange = { custom: true, min: minV, max: maxV };
          if (minEl) minEl.value = minV > 0 ? String(minV) : "";
          if (maxEl) maxEl.value = maxV !== Infinity ? String(maxV) : "";
          document.querySelectorAll('input[name="priceRange"]').forEach(r => { r.checked = false; });
        } else {
          currentPriceRange = "all";
          if (minEl) minEl.value = "";
          if (maxEl) maxEl.value = "";
          const allPrice = document.querySelector('input[name="priceRange"][value="all"]');
          if (allPrice) allPrice.checked = true;
        }

        const ratingParam = params.get("rating") || params.get("min_rating") || "all";
        currentRating = ["5", "4", "3"].includes(ratingParam) ? ratingParam : "all";
        document.querySelectorAll('input[name="ratingFilter"]').forEach(r => {
          r.checked = (r.value === currentRating);
        });

        const flashParam = params.get("flash_sale") || params.get("flash");
        const chkFlash = document.getElementById("chkFlashSale");
        if (chkFlash) chkFlash.checked = (flashParam === "1" || flashParam === "true");

        const exParam = params.get("exclusive");
        const chkEx = document.getElementById("chkExclusive");
        if (chkEx) chkEx.checked = (exParam === "1" || exParam === "true");

        const sortParam = params.get("sort") || "popular";
        currentSort = SORT_UI_TO_API[sortParam] ? sortParam : "popular";
        document.querySelectorAll(".sort-tab").forEach(tab => {
          tab.classList.toggle("active", tab.getAttribute("data-sort") === currentSort);
        });
        const priceSelect = document.getElementById("priceSortSelect");
        if (priceSelect) {
          priceSelect.value = (currentSort === "price-asc" || currentSort === "price-desc") ? currentSort : "default";
        }

        const pageParam = parseInt(params.get("page") || "1", 10);
        currentPage = Number.isFinite(pageParam) && pageParam >= 1 ? pageParam : 1;
      }

      async function loadFilterFacetsFromAPI() {
        try {
          const res = await fetch(`${API_BASE_URL}/api/products/facets`);
          if (!res.ok) return;
          const facets = await res.json();

          const allCountEl = document.getElementById("countAll");
          if (allCountEl && typeof facets.total === "number") {
            allCountEl.textContent = facets.total;
          }
          const catCounts = facets.categories || {};
          document.querySelectorAll(".category-item[data-cat]").forEach(item => {
            const cat = item.getAttribute("data-cat");
            const badge = item.querySelector(".category-count");
            if (!badge || cat === "all") return;
            badge.textContent = catCounts[cat] || 0;
          });

          const brandSelect = document.getElementById("brandFilterSelect");
          if (brandSelect && Array.isArray(facets.brands)) {
            const optionsHtml = [`<option value="all">Tất cả thương hiệu</option>`]
              .concat(facets.brands.map(b => `<option value="${escapeHtml(b)}">${escapeHtml(b)}</option>`))
              .join("");
            brandSelect.innerHTML = optionsHtml;
            brandSelect.value = currentBrand;
          }
        } catch (e) {
          console.log("Không tải được facets từ API.");
        }
      }

      async function fetchFilteredProductsFromAPI({ updateUrl = true } = {}) {
        if (updateUrl) {
          syncStateToUrl();
        }

        if (activeFilterController) {
          activeFilterController.abort();
        }
        activeFilterController = new AbortController();

        const apiParams = buildApiQueryParams();
        try {
          const res = await fetch(`${API_BASE_URL}/api/products/filter?${apiParams.toString()}`, {
            signal: activeFilterController.signal
          });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);

          const data = await res.json();
          isApiConnected = true;
          filteredProducts = (data.items || []).map(mapApiProduct);
          serverPagination = data.pagination || {
            page: currentPage,
            page_size: pageSize,
            total: filteredProducts.length,
            total_pages: Math.ceil(filteredProducts.length / pageSize) || 0,
            has_next: false,
            has_prev: false
          };
          currentPage = serverPagination.page || currentPage;

          updateActiveFilterCounts(serverPagination.total ?? filteredProducts.length);
          renderProducts();
          return;
        } catch (err) {
          if (err && err.name === "AbortError") return;
          console.warn("Chuyển sang lọc dữ liệu cục bộ do lỗi API:", err);
          isApiConnected = false;
          applyLocalFiltersFallback();
        }
      }

      function updateActiveFilterCounts(totalCount) {
        const countEl = document.getElementById("productCountText");
        if (countEl) countEl.textContent = totalCount;

        const drawerCountEl = document.getElementById("drawerResultCount");
        if (drawerCountEl) drawerCountEl.textContent = totalCount;

        const activeChips = getActiveFilterChips();
        const mobileBadge = document.getElementById("mobileActiveCount");
        if (mobileBadge) mobileBadge.textContent = activeChips.length;
        renderActiveFilterChips(activeChips);
      }

      // =========================================================================
      // BỘ LỌC (FILTERS LOGIC -> NỐI API + GIỮ TRẠNG THÁI URL)
      // =========================================================================
      function selectCategory(cat, el) {
        currentCategory = cat;
        document.querySelectorAll(".category-item").forEach(item => item.classList.remove("active"));
        if (el) el.classList.add("active");
        document.getElementById("breadcrumbCurrentCategory").textContent = CATEGORY_NAMES[cat] || cat;

        currentPage = 1;
        applyAllFilters();

        if (window.innerWidth <= 900) {
          closeFilterDrawer();
        }
      }

      function handleBrandFilter(brand) {
        currentBrand = brand || "all";
        currentPage = 1;
        applyAllFilters();
      }

      function handlePriceFilter(range) {
        currentPriceRange = range;
        document.getElementById("minPriceInput").value = "";
        document.getElementById("maxPriceInput").value = "";
        currentPage = 1;
        applyAllFilters();
      }

      function applyCustomPriceRange() {
        const rawMin = document.getElementById("minPriceInput").value;
        const rawMax = document.getElementById("maxPriceInput").value;
        const minVal = rawMin ? Math.max(0, parseInt(rawMin, 10) || 0) : 0;
        const maxVal = rawMax ? Math.max(0, parseInt(rawMax, 10) || 0) : Infinity;

        if (rawMax && minVal > maxVal) {
          showToast("Giá tối thiểu không được lớn hơn giá tối đa!");
          return;
        }

        document.querySelectorAll('input[name="priceRange"]').forEach(r => r.checked = false);
        currentPriceRange = { custom: true, min: minVal, max: maxVal };
        currentPage = 1;
        applyAllFilters();
        showToast("Đã áp dụng khoảng giá: " + formatCurrency(minVal) + " - " + (maxVal === Infinity ? "Trở lên" : formatCurrency(maxVal)));
        if (window.innerWidth <= 900) closeFilterDrawer();
      }

      function handleRatingFilter(rating) {
        currentRating = rating;
        currentPage = 1;
        applyAllFilters();
      }

      function applyOtherFilters() {
        currentPage = 1;
        applyAllFilters();
      }

      function getProductsSearchSessionId() {
        let sid = localStorage.getItem("JML_SEARCH_SESSION_ID");
        if (!sid) {
          sid = "sess_" + Math.random().toString(36).slice(2, 11) + Date.now().toString(36);
          localStorage.setItem("JML_SEARCH_SESSION_ID", sid);
        }
        return sid;
      }

      function getProductsAuthHeaders(includeJson = false) {
        const headers = {};
        if (includeJson) headers["Content-Type"] = "application/json";
        const token = typeof Auth !== "undefined"
          ? Auth.getToken()
          : (localStorage.getItem("JML_ACCESS_TOKEN") || localStorage.getItem("access_token"));
        if (token) headers["Authorization"] = `Bearer ${token}`;
        return headers;
      }

      async function saveRecentSearchKeyword(keyword) {
        const clean = String(keyword || "").trim();
        if (!clean) return;
        try {
          await fetch(`${API_BASE_URL}/api/products/recent-searches`, {
            method: "POST",
            headers: getProductsAuthHeaders(true),
            body: JSON.stringify({
              keyword: clean,
              session_id: getProductsSearchSessionId(),
            }),
          });
          await loadRecentSearches();
        } catch (e) {
          // Không chặn tìm kiếm nếu API lịch sử gặp lỗi tạm thời
        }
      }

      async function loadRecentSearches(prefix = "") {
        const searchBox = document.querySelector(".search-box");
        if (!searchBox) return;
        let container = document.getElementById("productsRecentSearches");
        if (!container) {
          container = document.createElement("div");
          container.id = "productsRecentSearches";
          container.style.cssText = "display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:6px;font-size:12px;";
          searchBox.parentNode.insertBefore(container, searchBox.nextSibling);
        }
        try {
          const qs = new URLSearchParams({
            limit: "6",
            session_id: getProductsSearchSessionId(),
          });
          if (prefix) qs.set("prefix", prefix);
          const res = await fetch(`${API_BASE_URL}/api/products/recent-searches?${qs.toString()}`, {
            headers: getProductsAuthHeaders(false),
          });
          if (!res.ok) return;
          const data = await res.json();
          const items = data.items || [];
          if (!items.length) {
            container.innerHTML = "";
            return;
          }
          container.innerHTML = `<span style="color:var(--text-muted);font-weight:600;">Tìm gần đây:</span>` + items.map((item) => `
            <span style="display:inline-flex;align-items:center;gap:4px;background:var(--surface-dim,#f3f4f6);border:1px solid var(--border,#e5e7eb);border-radius:99px;padding:2px 9px;color:var(--text-main);">
              <button type="button" onclick="applyRecentSearchKeyword('${escapeHtml(item.keyword)}')" style="background:none;border:none;color:inherit;font-size:12px;cursor:pointer;padding:0;">${escapeHtml(item.keyword)}</button>
              <button type="button" onclick="removeRecentSearchKeyword(${Number(item.id)})" aria-label="Xóa từ khóa" style="background:none;border:none;color:var(--text-muted);font-size:12px;cursor:pointer;padding:0 2px;line-height:1;">×</button>
            </span>
          `).join("");
        } catch (e) {
          // Bỏ qua nếu backend chưa chạy
        }
      }

      function applyRecentSearchKeyword(keyword) {
        const searchEl = document.getElementById("searchInput");
        if (searchEl) searchEl.value = keyword;
        executeSearch();
      }

      async function removeRecentSearchKeyword(id) {
        try {
          await fetch(`${API_BASE_URL}/api/products/recent-searches/${id}?session_id=${encodeURIComponent(getProductsSearchSessionId())}`, {
            method: "DELETE",
            headers: getProductsAuthHeaders(false),
          });
          await loadRecentSearches();
        } catch (e) {}
      }

      function handleSearch(val) {
        searchQuery = val.trim().toLowerCase();
        currentPage = 1;
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
          applyAllFilters();
        }, 250);
      }

      function executeSearch() {
        clearTimeout(searchDebounceTimer);
        const rawVal = (document.getElementById("searchInput")?.value || "").trim();
        searchQuery = rawVal.toLowerCase();
        currentPage = 1;
        applyAllFilters();
        if (rawVal) {
          saveRecentSearchKeyword(rawVal);
        }
        const searchEl = document.getElementById("searchInput");
        if (searchEl && window.innerWidth <= 900) {
          searchEl.blur();
        }
        if (window.innerWidth <= 900) closeFilterDrawer();
      }

      function resetAllFilters() {
        currentCategory = "all";
        currentBrand = "all";
        currentPriceRange = "all";
        currentRating = "all";
        currentSort = "popular";
        searchQuery = "";
        currentPage = 1;

        document.getElementById("searchInput").value = "";
        document.getElementById("minPriceInput").value = "";
        document.getElementById("maxPriceInput").value = "";
        document.getElementById("chkFlashSale").checked = false;
        document.getElementById("chkExclusive").checked = false;

        const brandSelect = document.getElementById("brandFilterSelect");
        if (brandSelect) brandSelect.value = "all";

        const allPriceRadio = document.querySelector('input[name="priceRange"][value="all"]');
        if (allPriceRadio) allPriceRadio.checked = true;
        const allRatingRadio = document.querySelector('input[name="ratingFilter"][value="all"]');
        if (allRatingRadio) allRatingRadio.checked = true;

        document.querySelectorAll(".category-item").forEach((it, idx) => {
          it.classList.toggle("active", idx === 0);
        });
        document.querySelectorAll(".sort-tab").forEach(tab => {
          tab.classList.toggle("active", tab.getAttribute("data-sort") === "popular");
        });
        const priceSelect = document.getElementById("priceSortSelect");
        if (priceSelect) priceSelect.value = "default";

        document.getElementById("breadcrumbCurrentCategory").textContent = "Tất cả ngành hàng";
        applyAllFilters();
        showToast("Đã đặt lại tất cả bộ lọc");
      }

      function applyAllFilters() {
        fetchFilteredProductsFromAPI({ updateUrl: true });
      }

      // Fallback cục bộ khi API không kết nối được
      function applyLocalFiltersFallback() {
        const isFlashOnly = document.getElementById("chkFlashSale")?.checked;
        const isExclusiveOnly = document.getElementById("chkExclusive")?.checked;

        filteredProducts = allProducts.filter(p => {
          if (currentCategory !== "all" && p.category !== currentCategory) return false;
          if (currentBrand !== "all" && (p.brand || "").toLowerCase() !== currentBrand.toLowerCase()) return false;
          if (searchQuery) {
            const matchTitle = p.title.toLowerCase().includes(searchQuery);
            const matchShop = p.shopName.toLowerCase().includes(searchQuery);
            if (!matchTitle && !matchShop) return false;
          }
          if (currentPriceRange === "under-1m" && p.price >= 1000000) return false;
          if (currentPriceRange === "1m-5m" && (p.price < 1000000 || p.price > 5000000)) return false;
          if (currentPriceRange === "5m-15m" && (p.price < 5000000 || p.price > 15000000)) return false;
          if (currentPriceRange === "above-15m" && p.price <= 15000000) return false;
          if (typeof currentPriceRange === "object" && currentPriceRange.custom) {
            if (p.price < currentPriceRange.min || p.price > currentPriceRange.max) return false;
          }
          if (currentRating === "5" && p.rating < 5.0) return false;
          if (currentRating === "4" && p.rating < 4.0) return false;
          if (currentRating === "3" && p.rating < 3.0) return false;
          if (isFlashOnly && !p.isFlashSale) return false;
          if (isExclusiveOnly && !(p.exclusive || "").toLowerCase().includes("chính hãng")) return false;
          return true;
        });

        sortProducts();
        serverPagination = {
          page: currentPage,
          page_size: pageSize,
          total: filteredProducts.length,
          total_pages: Math.ceil(filteredProducts.length / pageSize) || 0,
          has_next: currentPage < (Math.ceil(filteredProducts.length / pageSize) || 0),
          has_prev: currentPage > 1
        };
        updateActiveFilterCounts(filteredProducts.length);
        renderProducts();
      }

      // Lấy danh sách chip bộ lọc đang áp dụng (TF16EBF)
      function getActiveFilterChips() {
        const chips = [];
        const rawInput = (document.getElementById("searchInput")?.value || "").trim();
        const isFlashOnly = document.getElementById("chkFlashSale")?.checked;
        const isExclusiveOnly = document.getElementById("chkExclusive")?.checked;

        if (searchQuery) {
          chips.push({
            type: "search",
            label: `Từ khóa: "${rawInput || searchQuery}"`
          });
        }
        if (currentCategory !== "all") {
          chips.push({
            type: "category",
            label: `Danh mục: ${CATEGORY_LABELS[currentCategory] || currentCategory}`
          });
        }
        if (currentBrand !== "all") {
          chips.push({
            type: "brand",
            label: `Thương hiệu: ${currentBrand}`
          });
        }
        if (currentPriceRange !== "all") {
          let priceText = PRICE_RANGE_LABELS[currentPriceRange] || "";
          if (typeof currentPriceRange === "object" && currentPriceRange.custom) {
            const minText = formatCurrency(currentPriceRange.min);
            const maxText = currentPriceRange.max === Infinity ? "Trở lên" : formatCurrency(currentPriceRange.max);
            priceText = `${minText} - ${maxText}`;
          }
          if (priceText) {
            chips.push({
              type: "price",
              label: `Giá: ${priceText}`
            });
          }
        }
        if (currentRating !== "all") {
          const ratingLabel = currentRating === "5" ? "5 sao" : `Từ ${currentRating} sao`;
          chips.push({
            type: "rating",
            label: `Đánh giá: ${ratingLabel}`
          });
        }
        if (isFlashOnly) {
          chips.push({
            type: "flash",
            label: "⚡ Đang Giảm Giá Sốc"
          });
        }
        if (isExclusiveOnly) {
          chips.push({
            type: "exclusive",
            label: "🛡️ Hàng Chính Hãng 100%"
          });
        }
        return chips;
      }

      // Render thanh chip bộ lọc đang áp dụng & nút Xóa tất cả (TF16EBF)
      function renderActiveFilterChips(chips = getActiveFilterChips()) {
        const bar = document.getElementById("activeFiltersBar");
        if (!bar) return;

        if (!chips || chips.length === 0) {
          bar.style.display = "none";
          bar.innerHTML = "";
          return;
        }

        const chipsHtml = chips.map(chip => `
          <span class="filter-chip" data-filter-type="${chip.type}">
            <span>${escapeHtml(chip.label)}</span>
            <button
              type="button"
              class="filter-chip-remove"
              aria-label="Xóa ${escapeHtml(chip.label)}"
              title="Xóa bộ lọc này"
              onclick="removeFilterChip('${chip.type}')"
            >×</button>
          </span>
        `).join("");

        bar.innerHTML = `
          <span class="active-filters-label">
            <span>Đang lọc</span>
            <span class="active-filters-count">${chips.length}</span>
          </span>
          ${chipsHtml}
          <button type="button" class="btn-clear-all-chips" onclick="resetAllFilters()">
            ✕ Xóa tất cả
          </button>
        `;
        bar.style.display = "flex";
      }

      // Xóa từng chip bộ lọc riêng lẻ (TF16EBF)
      function removeFilterChip(type) {
        if (type === "category") {
          currentCategory = "all";
          document.querySelectorAll(".category-item").forEach(item => {
            item.classList.toggle("active", item.getAttribute("data-cat") === "all");
          });
          const bc = document.getElementById("breadcrumbCurrentCategory");
          if (bc) bc.textContent = CATEGORY_LABELS.all;
        } else if (type === "brand") {
          currentBrand = "all";
          const brandSelect = document.getElementById("brandFilterSelect");
          if (brandSelect) brandSelect.value = "all";
        } else if (type === "search") {
          searchQuery = "";
          const searchEl = document.getElementById("searchInput");
          if (searchEl) searchEl.value = "";
        } else if (type === "price") {
          currentPriceRange = "all";
          const minEl = document.getElementById("minPriceInput");
          const maxEl = document.getElementById("maxPriceInput");
          if (minEl) minEl.value = "";
          if (maxEl) maxEl.value = "";
          const allPriceRadio = document.querySelector('input[name="priceRange"][value="all"]');
          if (allPriceRadio) allPriceRadio.checked = true;
        } else if (type === "rating") {
          currentRating = "all";
          const allRatingRadio = document.querySelector('input[name="ratingFilter"][value="all"]');
          if (allRatingRadio) allRatingRadio.checked = true;
        } else if (type === "flash") {
          const chkFlash = document.getElementById("chkFlashSale");
          if (chkFlash) chkFlash.checked = false;
        } else if (type === "exclusive") {
          const chkEx = document.getElementById("chkExclusive");
          if (chkEx) chkEx.checked = false;
        }
        applyAllFilters();
      }

      function applyQuickRecoveryFilter(preset) {
        resetAllFilters();
        if (preset === "flash") {
          const chkFlash = document.getElementById("chkFlashSale");
          if (chkFlash) chkFlash.checked = true;
          applyAllFilters();
        } else if (preset === "audio") {
          const audioItem = document.querySelector('.category-item[data-cat="audio"]');
          selectCategory("audio", audioItem);
        }
      }

      // =========================================================================
      // SẮP XẾP (SORTING LOGIC -> GỌI API & GIỮ TRẠNG THÁI URL)
      // =========================================================================
      function changeSort(sortType, el) {
        currentSort = sortType;
        document.querySelectorAll(".sort-tab").forEach(tab => tab.classList.remove("active"));
        if (el) el.classList.add("active");
        const priceSelect = document.getElementById("priceSortSelect");
        if (priceSelect) priceSelect.value = "default";
        currentPage = 1;
        applyAllFilters();
      }

      function handlePriceSortSelect(val) {
        if (val === "price-asc" || val === "price-desc") {
          currentSort = val;
          document.querySelectorAll(".sort-tab").forEach(tab => tab.classList.remove("active"));
        } else {
          currentSort = "popular";
          document.querySelector('.sort-tab[data-sort="popular"]')?.classList.add("active");
        }
        currentPage = 1;
        applyAllFilters();
      }

      function sortProducts() {
        if (currentSort === "price-asc") {
          filteredProducts.sort((a, b) => a.price - b.price);
        } else if (currentSort === "price-desc") {
          filteredProducts.sort((a, b) => b.price - a.price);
        } else if (currentSort === "newest") {
          filteredProducts.sort((a, b) => b.id - a.id);
        } else if (currentSort === "bestseller") {
          filteredProducts.sort((a, b) => (b.sold || 0) - (a.sold || 0));
        } else {
          filteredProducts.sort((a, b) => (b.rating * 10 + b.sold) - (a.rating * 10 + a.sold));
        }
      }

      // =========================================================================
      // RENDER LƯỚI SẢN PHẨM & PHÂN TRANG TỪ API
      // =========================================================================
      function renderProducts() {
        const grid = document.getElementById("productsGrid");
        if (!grid) return;

        if (filteredProducts.length === 0) {
          const activeChips = getActiveFilterChips();
          const summaryPills = activeChips.map(chip => `
            <span class="filter-chip" style="font-size: 11.5px;">
              <span>${escapeHtml(chip.label)}</span>
              <button
                type="button"
                class="filter-chip-remove"
                aria-label="Xóa ${escapeHtml(chip.label)}"
                onclick="removeFilterChip('${chip.type}')"
              >×</button>
            </span>
          `).join("");

          grid.innerHTML = `
            <div class="empty-state" id="emptyStateContainer">
              <div class="empty-state-icon" aria-hidden="true">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  <line x1="8" y1="11" x2="14" y2="11"></line>
                </svg>
              </div>
              <div class="empty-state-title">Không tìm thấy sản phẩm phù hợp</div>
              <p class="empty-state-desc">
                ${searchQuery
                  ? `Không có sản phẩm nào khớp với từ khóa <strong>"${escapeHtml(document.getElementById("searchInput")?.value.trim() || searchQuery)}"</strong> và các điều kiện lọc hiện tại.`
                  : "Không có sản phẩm nào đáp ứng toàn bộ bộ lọc bạn đang chọn. Hãy thử bớt một vài tiêu chí."}
              </p>
              ${activeChips.length > 0 ? `<div class="empty-state-summary">${summaryPills}</div>` : ""}
              <div class="empty-state-actions">
                <button type="button" class="btn-empty-primary" onclick="resetAllFilters()">✕ Xóa Tất Cả Bộ Lọc</button>
                ${searchQuery ? `<button type="button" class="btn-empty-secondary" onclick="removeFilterChip('search')">Xóa từ khóa tìm kiếm</button>` : ""}
              </div>
              <div class="empty-state-suggestions">
                <span>Gợi ý nhanh:</span>
                <button type="button" class="empty-suggest-pill" onclick="applyQuickRecoveryFilter('all')">Xem tất cả sản phẩm</button>
                <button type="button" class="empty-suggest-pill" onclick="applyQuickRecoveryFilter('flash')">⚡ Đang giảm giá sốc</button>
                <button type="button" class="empty-suggest-pill" onclick="applyQuickRecoveryFilter('audio')">🎧 Thiết bị âm thanh</button>
              </div>
            </div>
          `;
          document.getElementById("paginationWrapper").style.display = "none";
          return;
        }

        document.getElementById("paginationWrapper").style.display = "flex";

        const pageItems = isApiConnected
          ? filteredProducts
          : filteredProducts.slice((currentPage - 1) * pageSize, currentPage * pageSize);

        grid.innerHTML = pageItems.map(p => `
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
                <span class="stars-yellow">★ ${p.rating.toFixed(1)}</span>
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
        `).join("");

        updatePagination();
      }

      function getVisiblePages(current, total, isCompact) {
        if (total <= (isCompact ? 5 : 7)) {
          return Array.from({ length: total }, (_, idx) => idx + 1);
        }
        const radius = isCompact ? 1 : 2;
        const pages = [1];
        const start = Math.max(2, current - radius);
        const end = Math.min(total - 1, current + radius);

        if (start > 2) pages.push("...");
        for (let i = start; i <= end; i++) pages.push(i);
        if (end < total - 1) pages.push("...");
        pages.push(total);
        return pages;
      }

      function updatePagination() {
        const totalPages = isApiConnected
          ? (serverPagination.total_pages || 1)
          : (Math.ceil(filteredProducts.length / pageSize) || 1);
        const pagWrapper = document.getElementById("paginationWrapper");
        if (!pagWrapper) return;

        const isCompact = window.innerWidth <= 640;
        const visiblePages = getVisiblePages(currentPage, totalPages, isCompact);

        let html = `<button class="page-btn" aria-label="Trang trước" ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">‹</button>`;

        visiblePages.forEach(p => {
          if (p === "...") {
            html += `<span class="page-ellipsis" aria-hidden="true">…</span>`;
          } else {
            html += `<button class="page-btn ${p === currentPage ? 'active' : ''}" aria-label="Trang ${p}" ${p === currentPage ? 'aria-current="page"' : ''} onclick="changePage(${p})">${p}</button>`;
          }
        });

        html += `<button class="page-btn" aria-label="Trang sau" ${currentPage >= totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">›</button>`;
        pagWrapper.innerHTML = html;
      }

      function changePage(page) {
        const totalPages = isApiConnected
          ? (serverPagination.total_pages || 1)
          : (Math.ceil(filteredProducts.length / pageSize) || 1);
        if (page < 1 || page > totalPages) return;
        currentPage = page;
        applyAllFilters();
        window.scrollTo({ top: 120, behavior: "smooth" });
      }

      // =========================================================================
      // MOBILE DRAWER LOGIC (MỞ / ĐÓNG PANEL BỘ LỌC TRÊN ĐIỆN THOẠI)
      // =========================================================================
      function openFilterDrawer() {
        const sidebar = document.getElementById("filterSidebar");
        const backdrop = document.getElementById("drawerBackdrop");
        const triggerBtn = document.querySelector(".btn-mobile-filter");
        if (sidebar) sidebar.classList.add("drawer-open");
        if (backdrop) backdrop.classList.add("active");
        if (triggerBtn) triggerBtn.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden"; // Khóa cuộn trang khi drawer mở
      }

      function closeFilterDrawer() {
        const sidebar = document.getElementById("filterSidebar");
        const backdrop = document.getElementById("drawerBackdrop");
        const triggerBtn = document.querySelector(".btn-mobile-filter");
        if (sidebar) sidebar.classList.remove("drawer-open");
        if (backdrop) backdrop.classList.remove("active");
        if (triggerBtn) triggerBtn.setAttribute("aria-expanded", "false");
        document.body.style.overflow = ""; // Mở lại cuộn trang
      }

      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          const sidebar = document.getElementById("filterSidebar");
          if (sidebar && sidebar.classList.contains("drawer-open")) {
            closeFilterDrawer();
          }
        }
      });

      window.addEventListener("resize", () => {
        if (window.innerWidth > 900) {
          closeFilterDrawer();
        } else if (filteredProducts && filteredProducts.length > 0) {
          updatePagination();
        }
      });

      // =========================================================================
      // TIỆN ÍCH & GIỎ HÀNG
      // =========================================================================
      function formatCurrency(amount) {
        return Number(amount).toLocaleString("vi-VN") + " ₫";
      }

      function goToDetail(id) {
        window.location.href = `product-detail.html?id=${id}`;
      }

      function goToCart() {
        window.location.href = 'cart.html';
      }

      async function addToCart(event, id) {
        event.stopPropagation();
        const p = allProducts.find(item => item.id === id);
        if (!p) return;

        let cart = JSON.parse(localStorage.getItem("JML_CART_ITEMS") || "[]");
        const existing = cart.find(item => item.id === id || item.product_id === id);
        if (existing) {
          existing.qty = (existing.qty || 1) + 1;
        } else {
          cart.push({
            id: p.id,
            product_id: p.id,
            title: p.title,
            price: p.price,
            image: p.image,
            shopName: p.shopName,
            stock: p.totalStock || 100,
            qty: 1
          });
        }
        localStorage.setItem("JML_CART_ITEMS", JSON.stringify(cart));
        updateCartBadge();

        // Đồng bộ với Backend /api/cart/items nếu người dùng đã đăng nhập
        const user = typeof Auth !== "undefined"
          ? Auth.getUser()
          : JSON.parse(localStorage.getItem("JML_AUTH_USER") || localStorage.getItem("user") || "null");
        if (user && user.id) {
          try {
            await fetch(`${API_BASE_URL}/api/cart/items`, {
              method: "POST",
              headers: getProductsAuthHeaders(true),
              body: JSON.stringify({
                user_id: Number(user.id),
                product_id: Number(p.id),
                quantity: 1,
              }),
            });
          } catch (e) {
            console.warn("Không đồng bộ được giỏ hàng lên API:", e);
          }
        }

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
