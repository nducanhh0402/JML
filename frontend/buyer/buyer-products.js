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

      // Biến trạng thái toàn cục
      let allProducts = [...MOCK_PRODUCTS];
      let filteredProducts = [...MOCK_PRODUCTS];
      let currentCategory = "all";
      let currentPriceRange = "all";
      let currentRating = "all";
      let currentSort = "popular";
      let searchQuery = "";
      let currentPage = 1;
      const pageSize = 8;

      const CATEGORY_LABELS = {
        all: "Tất cả ngành hàng",
        audio: "Thiết Bị Âm Thanh",
        watch: "Đồng Hồ Cao Cấp",
        fashion: "Thời Trang & Đồ Da",
        tech: "Thiết Bị Số & PC",
        shoes: "Giày & Sneakers",
        beauty: "Mỹ Phẩm & Nước Hoa"
      };

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

      // Khởi tạo trang
      document.addEventListener("DOMContentLoaded", () => {
        hydrateFiltersFromUrl();
        updateCategoryCounts();
        // Cố gắng fetch từ API nếu backend đang chạy
        fetchProductsFromAPI();
        updateCartBadge();
      });

      function hydrateFiltersFromUrl() {
        const params = new URLSearchParams(window.location.search);
        const q = (params.get("q") || "").trim();
        const cat = (params.get("category") || "").trim().toLowerCase();
        const flash = params.get("flash");

        if (q) {
          searchQuery = q.toLowerCase();
          const input = document.getElementById("searchInput");
          if (input) input.value = q;
        }
        if (cat && CATEGORY_LABELS[cat]) {
          currentCategory = cat;
          document.querySelectorAll(".category-item").forEach(item => {
            item.classList.toggle("active", item.getAttribute("data-cat") === cat);
          });
          const bc = document.getElementById("breadcrumbCurrentCategory");
          if (bc) bc.textContent = CATEGORY_LABELS[cat];
        }
        if (flash === "1" || flash === "true") {
          const chk = document.getElementById("chkFlashSale");
          if (chk) chk.checked = true;
        }
      }

      function updateCategoryCounts() {
        const counts = {};
        allProducts.forEach(p => {
          const c = (p.category || "").toLowerCase();
          counts[c] = (counts[c] || 0) + 1;
        });
        document.querySelectorAll(".category-item[data-cat]").forEach(item => {
          const cat = item.getAttribute("data-cat");
          const badge = item.querySelector(".category-count");
          if (!badge) return;
          badge.textContent = cat === "all" ? allProducts.length : (counts[cat] || 0);
        });
      }

      async function fetchProductsFromAPI() {
        try {
          const res = await fetch("http://127.0.0.1:8000/api/products");
          if (res.ok) {
            const data = await res.json();
            const list = [...(data.flash_products || []), ...(data.recommend_products || [])];
            if (list.length > 0) {
              allProducts = list.map(p => ({
                id: p.id,
                category: p.category,
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
              }));
              updateCategoryCounts();
            }
          }
        } catch (e) {
          console.log("Sử dụng bộ dữ liệu Mock tĩnh.");
        }
        applyAllFilters();
      }

      // =========================================================================
      // BỘ LỌC (FILTERS LOGIC)
      // =========================================================================
      function selectCategory(cat, el) {
        currentCategory = cat;
        document.querySelectorAll(".category-item").forEach(item => item.classList.remove("active"));
        if (el) el.classList.add("active");

        document.getElementById("breadcrumbCurrentCategory").textContent = CATEGORY_LABELS[cat] || cat;
        applyAllFilters();

        // Tự động đóng drawer trên mobile sau khi chọn
        if (window.innerWidth <= 900) {
          closeFilterDrawer();
        }
      }

      function handlePriceFilter(range) {
        currentPriceRange = range;
        document.getElementById("minPriceInput").value = "";
        document.getElementById("maxPriceInput").value = "";
        applyAllFilters();
      }

      function applyCustomPriceRange() {
        const minVal = parseInt(document.getElementById("minPriceInput").value) || 0;
        const maxVal = parseInt(document.getElementById("maxPriceInput").value) || Infinity;

        // Bỏ chọn các radio button giá
        document.querySelectorAll('input[name="priceRange"]').forEach(r => r.checked = false);
        currentPriceRange = { custom: true, min: minVal, max: maxVal };
        applyAllFilters();
        showToast("Đã áp dụng khoảng giá: " + formatCurrency(minVal) + " - " + (maxVal === Infinity ? "Trở lên" : formatCurrency(maxVal)));
        if (window.innerWidth <= 900) closeFilterDrawer();
      }

      function handleRatingFilter(rating) {
        currentRating = rating;
        applyAllFilters();
      }

      function applyOtherFilters() {
        applyAllFilters();
      }

      function handleSearch(val) {
        searchQuery = val.trim().toLowerCase();
        applyAllFilters();
      }

      function executeSearch() {
        applyAllFilters();
        if (window.innerWidth <= 900) closeFilterDrawer();
      }

      function resetAllFilters() {
        currentCategory = "all";
        currentPriceRange = "all";
        currentRating = "all";
        searchQuery = "";
        document.getElementById("searchInput").value = "";
        document.getElementById("minPriceInput").value = "";
        document.getElementById("maxPriceInput").value = "";
        document.getElementById("chkFlashSale").checked = false;
        document.getElementById("chkExclusive").checked = false;
        document.querySelectorAll('input[name="priceRange"]')[0].checked = true;
        document.querySelectorAll('input[name="ratingFilter"]')[0].checked = true;
        document.querySelectorAll(".category-item").forEach((it, idx) => {
          it.classList.toggle("active", idx === 0);
        });
        document.getElementById("breadcrumbCurrentCategory").textContent = "Tất cả ngành hàng";
        applyAllFilters();
        showToast("Đã đặt lại tất cả bộ lọc");
      }

      // Áp dụng tổng hợp tất cả tiêu chí lọc
      function applyAllFilters() {
        const isFlashOnly = document.getElementById("chkFlashSale")?.checked;
        const isExclusiveOnly = document.getElementById("chkExclusive")?.checked;

        filteredProducts = allProducts.filter(p => {
          // 1. Danh mục
          if (currentCategory !== "all" && p.category !== currentCategory) return false;

          // 2. Tìm kiếm tên sản phẩm / shop
          if (searchQuery) {
            const matchTitle = p.title.toLowerCase().includes(searchQuery);
            const matchShop = p.shopName.toLowerCase().includes(searchQuery);
            if (!matchTitle && !matchShop) return false;
          }

          // 3. Khoảng giá
          if (currentPriceRange === "under-1m" && p.price >= 1000000) return false;
          if (currentPriceRange === "1m-5m" && (p.price < 1000000 || p.price > 5000000)) return false;
          if (currentPriceRange === "5m-15m" && (p.price < 5000000 || p.price > 15000000)) return false;
          if (currentPriceRange === "above-15m" && p.price <= 15000000) return false;
          if (typeof currentPriceRange === "object" && currentPriceRange.custom) {
            if (p.price < currentPriceRange.min || p.price > currentPriceRange.max) return false;
          }

          // 4. Đánh giá
          if (currentRating === "5" && p.rating < 5.0) return false;
          if (currentRating === "4" && p.rating < 4.0) return false;
          if (currentRating === "3" && p.rating < 3.0) return false;

          // 5. Khuyến mãi khác
          if (isFlashOnly && !p.isFlashSale) return false;
          if (isExclusiveOnly && p.exclusive !== "Chính Hãng") return false;

          return true;
        });

        // Áp dụng sắp xếp
        sortProducts();

        // Cập nhật số lượng & thanh chip bộ lọc
        document.getElementById("productCountText").textContent = filteredProducts.length;
        document.getElementById("countAll").textContent = allProducts.length;

        const activeChips = getActiveFilterChips();
        document.getElementById("mobileActiveCount").textContent = activeChips.length;
        renderActiveFilterChips(activeChips);

        currentPage = 1;
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
      // SẮP XẾP (SORTING LOGIC)
      // =========================================================================
      function changeSort(sortType, el) {
        currentSort = sortType;
        document.querySelectorAll(".sort-tab").forEach(tab => tab.classList.remove("active"));
        if (el) el.classList.add("active");
        sortProducts();
        renderProducts();
      }

      function handlePriceSortSelect(val) {
        if (val === "price-asc" || val === "price-desc") {
          currentSort = val;
          document.querySelectorAll(".sort-tab").forEach(tab => tab.classList.remove("active"));
        } else {
          currentSort = "popular";
          document.querySelector('.sort-tab[data-sort="popular"]').classList.add("active");
        }
        sortProducts();
        renderProducts();
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
          // popular: ưu tiên rating và sold
          filteredProducts.sort((a, b) => (b.rating * 10 + b.sold) - (a.rating * 10 + a.sold));
        }
      }

      // =========================================================================
      // RENDER LƯỚI SẢN PHẨM & PHÂN TRANG
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

        // Cắt theo trang
        const start = (currentPage - 1) * pageSize;
        const pageItems = filteredProducts.slice(start, start + pageSize);

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

      function updatePagination() {
        const totalPages = Math.ceil(filteredProducts.length / pageSize) || 1;
        const prevBtn = document.getElementById("btnPrevPage");
        const nextBtn = document.getElementById("btnNextPage");

        if (prevBtn) prevBtn.disabled = (currentPage === 1);
        if (nextBtn) nextBtn.disabled = (currentPage === totalPages);

        const pagWrapper = document.getElementById("paginationWrapper");
        let html = `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">‹</button>`;

        for (let i = 1; i <= totalPages; i++) {
          html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
        }

        html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">›</button>`;
        pagWrapper.innerHTML = html;
      }

      function changePage(page) {
        const totalPages = Math.ceil(filteredProducts.length / pageSize) || 1;
        if (page < 1 || page > totalPages) return;
        currentPage = page;
        renderProducts();
        window.scrollTo({ top: 120, behavior: "smooth" });
      }

      // =========================================================================
      // MOBILE DRAWER LOGIC (MỞ / ĐÓNG PANEL BỘ LỌC TRÊN ĐIỆN THOẠI)
      // =========================================================================
      function openFilterDrawer() {
        const sidebar = document.getElementById("filterSidebar");
        const backdrop = document.getElementById("drawerBackdrop");
        if (sidebar) sidebar.classList.add("drawer-open");
        if (backdrop) backdrop.classList.add("active");
        document.body.style.overflow = "hidden"; // Khóa cuộn trang khi drawer mở
      }

      function closeFilterDrawer() {
        const sidebar = document.getElementById("filterSidebar");
        const backdrop = document.getElementById("drawerBackdrop");
        if (sidebar) sidebar.classList.remove("drawer-open");
        if (backdrop) backdrop.classList.remove("active");
        document.body.style.overflow = ""; // Mở lại cuộn trang
      }

      // =========================================================================
      // TIỆN ÍCH & GIỎ HÀNG
      // =========================================================================
      function formatCurrency(amount) {
        return Number(amount).toLocaleString("vi-VN") + " ₫";
      }

      function goToDetail(id) {
        window.location.href = `index.html?productId=${id}`;
      }

      function goToCart() {
        window.location.href = 'index.html#cart';
      }

      function addToCart(event, id) {
        event.stopPropagation();
        const p = allProducts.find(item => item.id === id);
        if (!p) return;

        let cart = JSON.parse(localStorage.getItem("JML_CART_ITEMS") || "[]");
        const existing = cart.find(item => item.id === id);
        if (existing) {
          existing.qty = (existing.qty || 1) + 1;
        } else {
          cart.push({
            id: p.id,
            title: p.title,
            price: p.price,
            image: p.image,
            shopName: p.shopName,
            qty: 1
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
