// Dá»¯ liá»‡u sáº£n pháº©m máº«u phong phÃº (16 sáº£n pháº©m thuá»™c 4 ngÃ nh hÃ ng chÃ­nh)
      const MOCK_PRODUCTS = [
        // Audio
        {
          id: 1,
          category: "audio",
          title: "Tai Nghe Chá»¥p Tai Apple AirPods Max SiÃªu Chá»‘ng á»’n ANC",
          price: 12490000,
          originalPrice: 14990000,
          discount: "-17%",
          rating: 5.0,
          sold: 28,
          totalStock: 45,
          image: "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
          shopName: "SoundMax & Marshall Audio",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: true
        },
        {
          id: 2,
          category: "audio",
          title: "Loa Bluetooth Di Äá»™ng Marshall Emberton II Ã‚m Thanh Äa HÆ°á»›ng",
          price: 3950000,
          originalPrice: 4600000,
          discount: "-14%",
          rating: 4.9,
          sold: 86,
          totalStock: 60,
          image: "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
          shopName: "SoundMax & Marshall Audio",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 3,
          category: "audio",
          title: "Tai Nghe Chá»‘ng á»’n Cao Cáº¥p Sony WH-1000XM5 Pin 30 Giá»",
          price: 7690000,
          originalPrice: 8990000,
          discount: "-14%",
          rating: 4.9,
          sold: 54,
          totalStock: 30,
          image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
          shopName: "SoundMax & Marshall Audio",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 4,
          category: "audio",
          title: "Loa Marshall Stanmore III Bluetooth Home Speaker CÃ´ng Suáº¥t 80W",
          price: 8990000,
          originalPrice: 10500000,
          discount: "-14%",
          rating: 5.0,
          sold: 42,
          totalStock: 25,
          image: "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80",
          shopName: "SoundMax & Marshall Audio",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },

        // Watch
        {
          id: 5,
          category: "watch",
          title: "Äá»“ng Há»“ CÆ¡ Nam Tissot Le Locle Powermatic 80 Thá»¥y SÄ©",
          price: 15800000,
          originalPrice: 18500000,
          discount: "-15%",
          rating: 5.0,
          sold: 19,
          totalStock: 20,
          image: "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80",
          shopName: "Luxury Watch Vietnam",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 6,
          category: "watch",
          title: "Äá»“ng Há»“ Nam Thá»ƒ Thao Seiko 5 Sports Automatic Chá»‘ng NÆ°á»›c 100m",
          price: 6200000,
          originalPrice: 7500000,
          discount: "-17%",
          rating: 4.8,
          sold: 73,
          totalStock: 50,
          image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
          shopName: "Luxury Watch Vietnam",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 7,
          category: "watch",
          title: "Äá»“ng Há»“ Ná»¯ DÃ¢y Da Cao Cáº¥p Daniel Wellington Petite Melrose",
          price: 3600000,
          originalPrice: 4500000,
          discount: "-20%",
          rating: 4.9,
          sold: 112,
          totalStock: 80,
          image: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
          shopName: "Luxury Watch Vietnam",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 8,
          category: "watch",
          title: "Äá»“ng Há»“ ThÃ´ng Minh Apple Watch Ultra 2 GPS + Cellular 49mm Titan",
          price: 20490000,
          originalPrice: 22990000,
          discount: "-11%",
          rating: 5.0,
          sold: 35,
          totalStock: 18,
          image: "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=800&q=80",
          shopName: "Luxury Watch Vietnam",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: true
        },

        // Fashion
        {
          id: 9,
          category: "fashion",
          title: "Ão Blazer Nam May Äo Phong CÃ¡ch Ã Aristino Premium Wool",
          price: 2450000,
          originalPrice: 3200000,
          discount: "-23%",
          rating: 4.8,
          sold: 65,
          totalStock: 40,
          image: "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80",
          shopName: "Aristino & Gentleman Store",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 10,
          category: "fashion",
          title: "VÃ­ Da Nam BÃ² Ã Cáº§m Tay KhÃ³a KÃ©o Cao Cáº¥p Giovanni Leather",
          price: 1850000,
          originalPrice: 2500000,
          discount: "-26%",
          rating: 4.9,
          sold: 88,
          totalStock: 55,
          image: "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=80",
          shopName: "Aristino & Gentleman Store",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 11,
          category: "fashion",
          title: "TÃºi XÃ¡ch Ná»¯ Da Tháº­t Cao Cáº¥p Thiáº¿t Káº¿ Paris Sang Trá»ng",
          price: 3200000,
          originalPrice: 4200000,
          discount: "-24%",
          rating: 4.9,
          sold: 47,
          totalStock: 35,
          image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80",
          shopName: "Luxe Paris & Bags",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 12,
          category: "fashion",
          title: "Tháº¯t LÆ°ng Nam Da BÃ² Tháº­t KhÃ³a Tá»± Äá»™ng Máº¡ VÃ ng 18K",
          price: 950000,
          originalPrice: 1350000,
          discount: "-30%",
          rating: 4.8,
          sold: 140,
          totalStock: 70,
          image: "https://images.unsplash.com/photo-1624222247344-550fb60583dc?auto=format&fit=crop&w=800&q=80",
          shopName: "Luxe Paris & Bags",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },

        // Tech
        {
          id: 13,
          category: "tech",
          title: "Card MÃ n HÃ¬nh VGA ASUS ROG Strix GeForce RTX 5090 OC 32GB",
          price: 68900000,
          originalPrice: 75000000,
          discount: "-8%",
          rating: 5.0,
          sold: 14,
          totalStock: 10,
          image: "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
          shopName: "GearVN Official Store",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: true
        },
        {
          id: 14,
          category: "tech",
          title: "BÃ n PhÃ­m CÆ¡ KhÃ´ng DÃ¢y Custom GMMK Pro 75% Switch Gateron",
          price: 4250000,
          originalPrice: 4950000,
          discount: "-14%",
          rating: 4.9,
          sold: 95,
          totalStock: 40,
          image: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80",
          shopName: "GearVN Official Store",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 15,
          category: "tech",
          title: "Chuá»™t CÃ´ng ThÃ¡i Há»c KhÃ´ng DÃ¢y Logitech MX Master 3S SiÃªu Nháº¡y",
          price: 2490000,
          originalPrice: 2990000,
          discount: "-17%",
          rating: 5.0,
          sold: 180,
          totalStock: 60,
          image: "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=800&q=80",
          shopName: "GearVN Official Store",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        },
        {
          id: 16,
          category: "tech",
          title: "MÃ n HÃ¬nh ChuyÃªn Nghiá»‡p Dell UltraSharp U2724D 27 inch 2K 120Hz IPS",
          price: 10890000,
          originalPrice: 12500000,
          discount: "-13%",
          rating: 4.9,
          sold: 38,
          totalStock: 25,
          image: "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80",
          shopName: "GearVN Official Store",
          exclusive: "ChÃ­nh HÃ£ng",
          isFlashSale: false
        }
      ];

      // Biáº¿n tráº¡ng thÃ¡i toÃ n cá»¥c
      let allProducts = [...MOCK_PRODUCTS];
      let filteredProducts = [...MOCK_PRODUCTS];
      let currentCategory = "all";
      let currentPriceRange = "all";
      let currentRating = "all";
      let currentSort = "popular";
      let searchQuery = "";
      let currentPage = 1;
      const pageSize = 8;

      // Khá»Ÿi táº¡o trang
      document.addEventListener("DOMContentLoaded", () => {
        // Cá»‘ gáº¯ng fetch tá»« API náº¿u backend Ä‘ang cháº¡y
        fetchProductsFromAPI();
        updateCartBadge();
      });

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
                exclusive: p.exclusive || "ChÃ­nh HÃ£ng",
                isFlashSale: Boolean(p.is_flash_sale)
              }));
            }
          }
        } catch (e) {
          console.log("Sá»­ dá»¥ng bá»™ dá»¯ liá»‡u Mock tÄ©nh Ä‘áº§y Ä‘á»§ 16 sáº£n pháº©m.");
        }
        applyAllFilters();
      }

      // =========================================================================
      // Bá»˜ Lá»ŒC (FILTERS LOGIC)
      // =========================================================================
      function selectCategory(cat, el) {
        currentCategory = cat;
        document.querySelectorAll(".category-item").forEach(item => item.classList.remove("active"));
        if (el) el.classList.add("active");

        const catNames = {
          "all": "Táº¥t cáº£ ngÃ nh hÃ ng",
          "audio": "Thiáº¿t Bá»‹ Ã‚m Thanh",
          "watch": "Äá»“ng Há»“ Cao Cáº¥p",
          "fashion": "Thá»i Trang & Äá»“ Da",
          "tech": "Thiáº¿t Bá»‹ Sá»‘ & PC"
        };
        document.getElementById("breadcrumbCurrentCategory").textContent = catNames[cat] || cat;
        applyAllFilters();

        // Tá»± Ä‘á»™ng Ä‘Ã³ng drawer trÃªn mobile sau khi chá»n
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

        // Bá» chá»n cÃ¡c radio button giÃ¡
        document.querySelectorAll('input[name="priceRange"]').forEach(r => r.checked = false);
        currentPriceRange = { custom: true, min: minVal, max: maxVal };
        applyAllFilters();
        showToast("ÄÃ£ Ã¡p dá»¥ng khoáº£ng giÃ¡: " + formatCurrency(minVal) + " - " + (maxVal === Infinity ? "Trá»Ÿ lÃªn" : formatCurrency(maxVal)));
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
        document.getElementById("breadcrumbCurrentCategory").textContent = "Táº¥t cáº£ ngÃ nh hÃ ng";
        applyAllFilters();
        showToast("ÄÃ£ Ä‘áº·t láº¡i táº¥t cáº£ bá»™ lá»c");
      }

      // Ãp dá»¥ng tá»•ng há»£p táº¥t cáº£ tiÃªu chÃ­ lá»c
      function applyAllFilters() {
        const isFlashOnly = document.getElementById("chkFlashSale")?.checked;
        const isExclusiveOnly = document.getElementById("chkExclusive")?.checked;

        filteredProducts = allProducts.filter(p => {
          // 1. Danh má»¥c
          if (currentCategory !== "all" && p.category !== currentCategory) return false;

          // 2. TÃ¬m kiáº¿m tÃªn sáº£n pháº©m / shop
          if (searchQuery) {
            const matchTitle = p.title.toLowerCase().includes(searchQuery);
            const matchShop = p.shopName.toLowerCase().includes(searchQuery);
            if (!matchTitle && !matchShop) return false;
          }

          // 3. Khoáº£ng giÃ¡
          if (currentPriceRange === "under-1m" && p.price >= 1000000) return false;
          if (currentPriceRange === "1m-5m" && (p.price < 1000000 || p.price > 5000000)) return false;
          if (currentPriceRange === "5m-15m" && (p.price < 5000000 || p.price > 15000000)) return false;
          if (currentPriceRange === "above-15m" && p.price <= 15000000) return false;
          if (typeof currentPriceRange === "object" && currentPriceRange.custom) {
            if (p.price < currentPriceRange.min || p.price > currentPriceRange.max) return false;
          }

          // 4. ÄÃ¡nh giÃ¡
          if (currentRating === "5" && p.rating < 5.0) return false;
          if (currentRating === "4" && p.rating < 4.0) return false;
          if (currentRating === "3" && p.rating < 3.0) return false;

          // 5. Khuyáº¿n mÃ£i khÃ¡c
          if (isFlashOnly && !p.isFlashSale) return false;
          if (isExclusiveOnly && p.exclusive !== "ChÃ­nh HÃ£ng") return false;

          return true;
        });

        // Ãp dá»¥ng sáº¯p xáº¿p
        sortProducts();

        // Cáº­p nháº­t sá»‘ lÆ°á»£ng
        document.getElementById("productCountText").textContent = filteredProducts.length;
        document.getElementById("countAll").textContent = allProducts.length;

        // Äáº¿m bá»™ lá»c Ä‘ang kÃ­ch hoáº¡t
        let activeCount = 0;
        if (currentCategory !== "all") activeCount++;
        if (currentPriceRange !== "all") activeCount++;
        if (currentRating !== "all") activeCount++;
        if (isFlashOnly) activeCount++;
        if (isExclusiveOnly) activeCount++;
        document.getElementById("mobileActiveCount").textContent = activeCount;

        currentPage = 1;
        renderProducts();
      }

      // =========================================================================
      // Sáº®P Xáº¾P (SORTING LOGIC)
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
          // popular: Æ°u tiÃªn rating vÃ  sold
          filteredProducts.sort((a, b) => (b.rating * 10 + b.sold) - (a.rating * 10 + a.sold));
        }
      }

      // =========================================================================
      // RENDER LÆ¯á»šI Sáº¢N PHáº¨M & PHÃ‚N TRANG
      // =========================================================================
      function renderProducts() {
        const grid = document.getElementById("productsGrid");
        if (!grid) return;

        if (filteredProducts.length === 0) {
          grid.innerHTML = `
            <div class="empty-state">
              <div class="empty-state-icon">ðŸ”</div>
              <div class="empty-state-title">KhÃ´ng tÃ¬m tháº¥y sáº£n pháº©m phÃ¹ há»£p</div>
              <p class="empty-state-desc">HÃ£y thá»­ thay Ä‘á»•i danh má»¥c hoáº·c má»Ÿ rá»™ng khoáº£ng giÃ¡ tÃ¬m kiáº¿m cá»§a báº¡n.</p>
              <button class="btn-apply-price" style="width: auto; padding: 8px 20px; display: inline-block;" onclick="resetAllFilters()">XÃ³a Táº¥t Cáº£ Bá»™ Lá»c</button>
            </div>
          `;
          document.getElementById("paginationWrapper").style.display = "none";
          return;
        }

        document.getElementById("paginationWrapper").style.display = "flex";

        // Cáº¯t theo trang
        const start = (currentPage - 1) * pageSize;
        const pageItems = filteredProducts.slice(start, start + pageSize);

        grid.innerHTML = pageItems.map(p => `
          <div class="product-card" onclick="goToDetail(${p.id})">
            <div class="product-img-wrap">
              <img src="${p.image}" alt="${p.title}" class="product-img" loading="lazy" />
              ${p.discount ? `<span class="discount-tag">${p.discount}</span>` : ""}
              <span class="shop-tag">ðŸª ${p.shopName || "JML Mall"}</span>
            </div>
            <div class="product-info">
              <h3 class="product-title" title="${p.title}">${p.title}</h3>
              <div class="product-price-row">
                <span class="price-current">${formatCurrency(p.price)}</span>
                ${p.originalPrice > p.price ? `<span class="price-original">${formatCurrency(p.originalPrice)}</span>` : ""}
              </div>
              <div class="product-meta-row">
                <span class="stars-yellow">â˜… ${p.rating.toFixed(1)}</span>
                <span>ÄÃ£ bÃ¡n ${p.sold || 0}</span>
              </div>
              <button class="btn-add-cart" onclick="addToCart(event, ${p.id})">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 5v14M5 12h14"></path>
                </svg>
                ThÃªm VÃ o Giá»
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
        let html = `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">â€¹</button>`;

        for (let i = 1; i <= totalPages; i++) {
          html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
        }

        html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">â€º</button>`;
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
      // MOBILE DRAWER LOGIC (Má»ž / ÄÃ“NG PANEL Bá»˜ Lá»ŒC TRÃŠN ÄIá»†N THOáº I)
      // =========================================================================
      function openFilterDrawer() {
        const sidebar = document.getElementById("filterSidebar");
        const backdrop = document.getElementById("drawerBackdrop");
        if (sidebar) sidebar.classList.add("drawer-open");
        if (backdrop) backdrop.classList.add("active");
        document.body.style.overflow = "hidden"; // KhÃ³a cuá»™n trang khi drawer má»Ÿ
      }

      function closeFilterDrawer() {
        const sidebar = document.getElementById("filterSidebar");
        const backdrop = document.getElementById("drawerBackdrop");
        if (sidebar) sidebar.classList.remove("drawer-open");
        if (backdrop) backdrop.classList.remove("active");
        document.body.style.overflow = ""; // Má»Ÿ láº¡i cuá»™n trang
      }

      // =========================================================================
      // TIá»†N ÃCH & GIá»Ž HÃ€NG
      // =========================================================================
      function formatCurrency(amount) {
        return Number(amount).toLocaleString("vi-VN") + " â‚«";
      }

      function goToDetail(id) {
        window.location.href = `index.html?productId=${id}`;
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
        showToast(`ÄÃ£ thÃªm "${p.title.substring(0, 24)}..." vÃ o giá» hÃ ng!`);
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
        box.innerHTML = `<span>âœ“</span><span>${msg}</span>`;
        box.style.display = "flex";
        setTimeout(() => {
          box.style.display = "none";
        }, 3000);
      }
