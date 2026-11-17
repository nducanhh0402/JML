/**
 * ==========================================================================
 * TF16E1F - HEADER SEARCH & LIVE KEYWORD SUGGESTIONS CONTROLLER
 * Ô tìm kiếm thông minh ở Header:
 *   1. Gợi ý từ khóa & sản phẩm realtime khi gõ (debounce + AbortController)
 *   2. Lưu & hiển thị lịch sử tìm kiếm gần đây (LocalStorage)
 *   3. Điều hướng bàn phím (ArrowUp / ArrowDown / Enter / Escape)
 *   4. Chuyển hướng sang trang kết quả (products.html?q=...)
 * ==========================================================================
 */

(function (global) {
  const HISTORY_KEY = "JML_SEARCH_HISTORY";
  const MAX_HISTORY = 6;
  const POPULAR_KEYWORDS = [
    "iPad Pro",
    "AirPods Max",
    "Card màn hình RTX",
    "Chuột Logitech MX Master",
    "Bàn phím cơ GMMK",
    "Màn hình Dell UltraSharp",
    "Đồng hồ Tissot",
    "Loa Marshall",
    "Áo Blazer Ý",
    "Ví da nam",
  ];

  // Danh mục fallback cục bộ giúp gợi ý tức thì kể cả khi backend offline
  const FALLBACK_CATALOG = [
    { id: 1, title: "Tai Nghe Chụp Tai Apple AirPods Max Siêu Chống Ồn ANC", brand: "Apple", category: "audio", price: 12490000, image: "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=200&q=80" },
    { id: 2, title: "Loa Bluetooth Di Động Marshall Emberton II Âm Thanh Đa Hướng", brand: "Marshall", category: "audio", price: 3950000, image: "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=200&q=80" },
    { id: 3, title: "Tai Nghe Chống Ồn Cao Cấp Sony WH-1000XM5 Pin 30 Giờ", brand: "Sony", category: "audio", price: 7690000, image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=200&q=80" },
    { id: 5, title: "Đồng Hồ Cơ Nam Tissot Le Locle Powermatic 80 Thụy Sĩ", brand: "Tissot", category: "watch", price: 15800000, image: "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=200&q=80" },
    { id: 8, title: "Đồng Hồ Thông Minh Apple Watch Ultra 2 GPS + Cellular 49mm", brand: "Apple", category: "watch", price: 20490000, image: "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=200&q=80" },
    { id: 9, title: "Áo Blazer Nam May Đo Phong Cách Ý Aristino Premium Wool", brand: "Aristino", category: "fashion", price: 2450000, image: "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=200&q=80" },
    { id: 10, title: "Ví Da Nam Bò Ý Cầm Tay Khóa Kéo Cao Cấp Giovanni Leather", brand: "Giovanni", category: "fashion", price: 1850000, image: "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=200&q=80" },
    { id: 13, title: "Card Màn Hình VGA ASUS ROG Strix GeForce RTX 5090 OC 32GB", brand: "ASUS", category: "tech", price: 68900000, image: "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=200&q=80" },
    { id: 14, title: "Bàn Phím Cơ Không Dây Custom GMMK Pro 75% Switch Gateron", brand: "Glorious", category: "tech", price: 4250000, image: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=200&q=80" },
    { id: 15, title: "Chuột Công Thái Học Không Dây Logitech MX Master 3S Siêu Nhạy", brand: "Logitech", category: "tech", price: 2490000, image: "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=200&q=80" },
    { id: 16, title: "Màn Hình Chuyên Nghiệp Dell UltraSharp U2724D 27 inch 2K 120Hz", brand: "Dell", category: "tech", price: 10890000, image: "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=200&q=80" },
  ];

  const state = {
    inputEl: null,
    wrapperEl: null,
    dropdownEl: null,
    clearBtnEl: null,
    debounceTimer: null,
    abortController: null,
    activeIndex: -1,
    isResultsPage: false,
    resultsUrl: "products.html",
    onSearchResults: null,
    apiBaseUrl: "http://127.0.0.1:8000",
  };

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function highlightMatch(text, query) {
    const safeText = escapeHtml(text);
    const trimmed = (query || "").trim();
    if (!trimmed) return safeText;
    const escapedReg = trimmed.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(${escapedReg})`, "ig");
    return safeText.replace(regex, '<mark class="search-highlight">$1</mark>');
  }

  function formatVnd(amount) {
    return Number(amount || 0).toLocaleString("vi-VN") + " ₫";
  }

  function getHistory() {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      return [];
    }
  }

  function saveToHistory(keyword) {
    const clean = (keyword || "").trim();
    if (!clean) return;
    const history = getHistory().filter((item) => item.toLowerCase() !== clean.toLowerCase());
    history.unshift(clean);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)));
  }

  function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    renderEmptyFocusDropdown();
  }

  function getLocalCatalog() {
    const pool = [];
    if (Array.isArray(global.allProducts)) pool.push(...global.allProducts);
    if (Array.isArray(global.FLASH_PRODUCTS)) pool.push(...global.FLASH_PRODUCTS);
    if (Array.isArray(global.RECOMMEND_PRODUCTS)) pool.push(...global.RECOMMEND_PRODUCTS);

    const byKey = new Map();
    [...pool, ...FALLBACK_CATALOG].forEach((p) => {
      if (!p || !p.title) return;
      const key = String(p.id || p.title).toLowerCase();
      if (!byKey.has(key)) {
        const img = Array.isArray(p.images) && p.images[0] ? p.images[0] : p.image;
        byKey.set(key, {
          id: p.id,
          title: p.title,
          brand: p.brand || p.shopName || "",
          category: p.category || "",
          price: p.price || 0,
          image: img || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=200&q=80",
        });
      }
    });
    return Array.from(byKey.values());
  }

  function buildSuggestionsLocally(query) {
    const qLower = query.toLowerCase();
    const catalog = getLocalCatalog();
    const history = getHistory();

    const keywordCandidates = Array.from(
      new Set([
        ...history,
        ...POPULAR_KEYWORDS,
        ...catalog.map((p) => p.brand).filter(Boolean),
      ])
    );

    const matchedKeywords = keywordCandidates
      .filter((kw) => kw.toLowerCase().includes(qLower))
      .slice(0, 5);

    const matchedProducts = catalog
      .filter(
        (p) =>
          p.title.toLowerCase().includes(qLower) ||
          (p.brand && p.brand.toLowerCase().includes(qLower)) ||
          (p.category && p.category.toLowerCase().includes(qLower))
      )
      .slice(0, 5);

    return { matchedKeywords, matchedProducts };
  }

  async function fetchApiSuggestions(query) {
    if (state.abortController) {
      state.abortController.abort();
    }
    state.abortController = new AbortController();

    try {
      const url = `${state.apiBaseUrl}/api/products/search?q=${encodeURIComponent(query)}&limit=5`;
      const res = await fetch(url, { signal: state.abortController.signal });
      if (!res.ok) return null;
      const data = await res.json();
      if (!data || !Array.isArray(data.items)) return null;
      return data.items.map((p) => ({
        id: p.id,
        title: p.title,
        brand: p.brand || p.shopName || "",
        category: p.category || "",
        price: p.price || 0,
        image: (Array.isArray(p.images) && p.images[0]) || p.image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=200&q=80",
      }));
    } catch (err) {
      return null;
    }
  }

  function renderEmptyFocusDropdown() {
    if (!state.dropdownEl) return;
    const history = getHistory();
    state.activeIndex = -1;

    let html = "";
    if (history.length > 0) {
      html += `
        <div class="suggestion-section-header">
          <span>Tìm kiếm gần đây</span>
          <button type="button" class="suggestion-clear-history" data-action="clear-history">Xóa lịch sử</button>
        </div>
        <ul class="suggestion-list">
          ${history
            .map(
              (kw) => `
            <li class="suggestion-item" data-suggest-keyword="${escapeHtml(kw)}">
              <span class="suggestion-item-icon">🕒</span>
              <span class="suggestion-item-text">${escapeHtml(kw)}</span>
              <span class="suggestion-item-badge">Gần đây</span>
            </li>`
            )
            .join("")}
        </ul>`;
    }

    html += `
      <div class="suggestion-section-header">
        <span>Từ khóa nổi bật</span>
      </div>
      <ul class="suggestion-list">
        ${POPULAR_KEYWORDS.slice(0, 6)
          .map(
            (kw) => `
          <li class="suggestion-item" data-suggest-keyword="${escapeHtml(kw)}">
            <span class="suggestion-item-icon">🔥</span>
            <span class="suggestion-item-text">${escapeHtml(kw)}</span>
            <span class="suggestion-item-badge">Phổ biến</span>
          </li>`
          )
          .join("")}
      </ul>`;

    state.dropdownEl.innerHTML = html;
    openDropdown();
  }

  function renderTypedSuggestions(query, matchedKeywords, matchedProducts) {
    if (!state.dropdownEl) return;
    state.activeIndex = -1;

    let html = "";

    if (matchedKeywords.length > 0) {
      html += `
        <div class="suggestion-section-header">
          <span>Gợi ý từ khóa</span>
        </div>
        <ul class="suggestion-list">
          ${matchedKeywords
            .map(
              (kw) => `
            <li class="suggestion-item" data-suggest-keyword="${escapeHtml(kw)}">
              <span class="suggestion-item-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </span>
              <span class="suggestion-item-text">${highlightMatch(kw, query)}</span>
            </li>`
            )
            .join("")}
        </ul>`;
    }

    if (matchedProducts.length > 0) {
      html += `
        <div class="suggestion-section-header">
          <span>Sản phẩm gợi ý (${matchedProducts.length})</span>
        </div>
        <div class="suggestion-products">
          ${matchedProducts
            .map(
              (p) => `
            <div class="suggestion-product-item" data-suggest-keyword="${escapeHtml(p.title)}" data-product-id="${escapeHtml(p.id)}">
              <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.title)}" class="suggestion-product-thumb" />
              <div class="suggestion-product-info">
                <div class="suggestion-product-title">${highlightMatch(p.title, query)}</div>
                <div class="suggestion-product-meta">
                  <span class="suggestion-product-price">${formatVnd(p.price)}</span>
                  ${p.brand ? `<span class="suggestion-product-brand">• ${escapeHtml(p.brand)}</span>` : ""}
                </div>
              </div>
            </div>`
            )
            .join("")}
        </div>`;
    }

    if (matchedKeywords.length === 0 && matchedProducts.length === 0) {
      html += `
        <div class="suggestion-empty">
          Không có gợi ý sẵn cho "<strong>${escapeHtml(query)}</strong>". Nhấn Enter để tìm trên toàn sàn.
        </div>`;
    }

    html += `
      <div class="suggestion-footer-action" data-suggest-keyword="${escapeHtml(query)}">
        <span>Tìm kiếm tất cả kết quả cho "${escapeHtml(query)}"</span>
        <span>→</span>
      </div>`;

    state.dropdownEl.innerHTML = html;
    openDropdown();
  }

  function openDropdown() {
    if (state.dropdownEl) state.dropdownEl.classList.add("open");
  }

  function closeDropdown() {
    if (state.dropdownEl) state.dropdownEl.classList.remove("open");
    state.activeIndex = -1;
  }

  function updateClearBtnVisibility() {
    if (!state.clearBtnEl || !state.inputEl) return;
    const hasValue = state.inputEl.value.trim().length > 0;
    state.clearBtnEl.classList.toggle("visible", hasValue);
  }

  function submitSearch(rawQuery) {
    const query = (typeof rawQuery === "string" ? rawQuery : state.inputEl?.value || "").trim();
    if (state.inputEl && typeof rawQuery === "string") {
      state.inputEl.value = rawQuery;
    }
    updateClearBtnVisibility();
    closeDropdown();

    if (query) {
      saveToHistory(query);
    }

    if (state.isResultsPage && typeof state.onSearchResults === "function") {
      const nextUrl = query ? `${state.resultsUrl}?q=${encodeURIComponent(query)}` : state.resultsUrl;
      try {
        window.history.pushState({ q: query }, "", nextUrl);
      } catch (e) {
        // file:// origin fallback: tiếp tục cập nhật kết quả trực tiếp
      }
      state.onSearchResults(query);
      return;
    }

    const targetUrl = query ? `${state.resultsUrl}?q=${encodeURIComponent(query)}` : state.resultsUrl;
    window.location.href = targetUrl;
  }

  function handleKeyboardNav(e) {
    if (!state.dropdownEl || !state.dropdownEl.classList.contains("open")) {
      if (e.key === "Enter") {
        e.preventDefault();
        submitSearch();
      }
      return;
    }

    const selectableItems = Array.from(
      state.dropdownEl.querySelectorAll(".suggestion-item, .suggestion-product-item, .suggestion-footer-action")
    );

    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (selectableItems.length === 0) return;
      state.activeIndex = (state.activeIndex + 1) % selectableItems.length;
      updateActiveSuggestionItem(selectableItems);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (selectableItems.length === 0) return;
      state.activeIndex = (state.activeIndex - 1 + selectableItems.length) % selectableItems.length;
      updateActiveSuggestionItem(selectableItems);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (state.activeIndex >= 0 && selectableItems[state.activeIndex]) {
        const chosen = selectableItems[state.activeIndex].getAttribute("data-suggest-keyword");
        submitSearch(chosen);
      } else {
        submitSearch();
      }
    } else if (e.key === "Escape") {
      closeDropdown();
    }
  }

  function updateActiveSuggestionItem(items) {
    items.forEach((el, idx) => el.classList.toggle("active", idx === state.activeIndex));
    const current = items[state.activeIndex];
    if (current) {
      current.scrollIntoView({ block: "nearest" });
      const kw = current.getAttribute("data-suggest-keyword");
      if (kw && state.inputEl) state.inputEl.value = kw;
    }
  }

  function ensureSearchDomStructure(inputEl) {
    const searchBox = inputEl.closest(".search-box");
    let wrapper = inputEl.closest(".search-wrapper");

    if (!wrapper && searchBox) {
      wrapper = document.createElement("div");
      wrapper.className = "search-wrapper";
      searchBox.parentNode.insertBefore(wrapper, searchBox);
      wrapper.appendChild(searchBox);
    }

    if (searchBox && !searchBox.querySelector(".search-clear-btn")) {
      const clearBtn = document.createElement("button");
      clearBtn.type = "button";
      clearBtn.className = "search-clear-btn";
      clearBtn.title = "Xóa từ khóa";
      clearBtn.setAttribute("aria-label", "Xóa từ khóa tìm kiếm");
      clearBtn.innerHTML = "&times;";
      const submitBtn = searchBox.querySelector(".search-btn");
      if (submitBtn) {
        searchBox.insertBefore(clearBtn, submitBtn);
      } else {
        searchBox.appendChild(clearBtn);
      }
      state.clearBtnEl = clearBtn;
    } else if (searchBox) {
      state.clearBtnEl = searchBox.querySelector(".search-clear-btn");
    }

    if (wrapper) {
      let dropdown = wrapper.querySelector(".search-suggestions-dropdown");
      if (!dropdown) {
        dropdown = document.createElement("div");
        dropdown.id = "searchSuggestionsDropdown";
        dropdown.className = "search-suggestions-dropdown";
        const keywordsBar = wrapper.querySelector(".search-keywords");
        if (keywordsBar) {
          wrapper.insertBefore(dropdown, keywordsBar);
        } else {
          wrapper.appendChild(dropdown);
        }
      }
      state.wrapperEl = wrapper;
      state.dropdownEl = dropdown;
    }
  }

  function init(options = {}) {
    const inputEl = document.getElementById(options.inputId || "searchInput");
    if (!inputEl) return;

    state.inputEl = inputEl;
    state.isResultsPage = Boolean(options.isResultsPage);
    state.resultsUrl = options.resultsUrl || "products.html";
    state.onSearchResults = options.onSearchResults || null;
    if (options.apiBaseUrl) state.apiBaseUrl = options.apiBaseUrl;

    inputEl.setAttribute("autocomplete", "off");
    ensureSearchDomStructure(inputEl);
    updateClearBtnVisibility();

    // Focus -> hiện lịch sử + từ khóa nổi bật nếu đang trống, hoặc hiện lại gợi ý
    inputEl.addEventListener("focus", () => {
      const val = inputEl.value.trim();
      if (!val) {
        renderEmptyFocusDropdown();
      } else {
        const local = buildSuggestionsLocally(val);
        renderTypedSuggestions(val, local.matchedKeywords, local.matchedProducts);
      }
    });

    // Input -> gợi ý realtime khi gõ (local tức thì + gọi API backend debounce)
    inputEl.addEventListener("input", () => {
      const val = inputEl.value.trim();
      updateClearBtnVisibility();

      if (!val) {
        renderEmptyFocusDropdown();
        return;
      }

      const local = buildSuggestionsLocally(val);
      renderTypedSuggestions(val, local.matchedKeywords, local.matchedProducts);

      clearTimeout(state.debounceTimer);
      state.debounceTimer = setTimeout(async () => {
        const apiItems = await fetchApiSuggestions(val);
        if (!apiItems || inputEl.value.trim() !== val) return;

        // Gộp từ khóa từ tên/thương hiệu API trả về cùng danh sách sản phẩm thực từ SQL
        const extraKeywords = apiItems
          .flatMap((p) => [p.brand, p.title])
          .filter(Boolean);
        const mergedKeywords = Array.from(new Set([...local.matchedKeywords, ...extraKeywords])).slice(0, 5);
        const mergedProducts = apiItems.length > 0 ? apiItems : local.matchedProducts;

        renderTypedSuggestions(val, mergedKeywords, mergedProducts);
      }, 180);
    });

    inputEl.addEventListener("keydown", handleKeyboardNav);

    // Xử lý click vào nút xóa nhanh
    if (state.clearBtnEl) {
      state.clearBtnEl.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        inputEl.value = "";
        updateClearBtnVisibility();
        inputEl.focus();
        renderEmptyFocusDropdown();
        if (state.isResultsPage && typeof state.onSearchResults === "function") {
          submitSearch("");
        }
      });
    }

    // Xử lý click trên các item trong dropdown
    if (state.dropdownEl) {
      state.dropdownEl.addEventListener("mousedown", (e) => {
        const clearHistBtn = e.target.closest("[data-action='clear-history']");
        if (clearHistBtn) {
          e.preventDefault();
          clearHistory();
          return;
        }
        const suggestTarget = e.target.closest("[data-suggest-keyword]");
        if (suggestTarget) {
          e.preventDefault();
          const kw = suggestTarget.getAttribute("data-suggest-keyword");
          submitSearch(kw);
        }
      });
    }

    // Click bên ngoài -> đóng dropdown
    document.addEventListener("click", (e) => {
      if (state.wrapperEl && !state.wrapperEl.contains(e.target)) {
        closeDropdown();
      }
    });
  }

  function getQueryFromUrl() {
    try {
      const params = new URLSearchParams(window.location.search);
      return (params.get("q") || "").trim();
    } catch (e) {
      return "";
    }
  }

  global.HeaderSearch = {
    init,
    submitSearch,
    getQueryFromUrl,
    closeDropdown,
  };
})(window);
