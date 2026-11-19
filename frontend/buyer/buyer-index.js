// --------------------------------------------------------------------------
      // Dá»® LIá»†U Sáº¢N PHáº¨M MáºªU (DATA STORE KÃˆM Bá»˜ SÆ¯U Táº¬P áº¢NH ÄA GÃ“C CHá»¤P CHO Má»–I Sáº¢N PHáº¨M)
      // --------------------------------------------------------------------------
      const API_BASE_URL = "http://127.0.0.1:8000";
      const DEFAULT_FLASH_PRODUCTS = [
        {
          id: 101,
          category: "audio",
          title: "Tai Nghe Chá»‘ng á»’n Cao Cáº¥p Sony WH-1000XM5 Black Edition",
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
            "ChÃ­nh diá»‡n",
            "GÃ³c nghiÃªng",
            "Cáº­n cáº£nh Ä‘á»‡m da",
            "TrÃªn tay lifestyle",
          ],
          exclusive: "BÃ¡n Cháº¡y",
        },
        {
          id: 102,
          category: "watch",
          title: "Äá»“ng Há»“ Nam CÆ¡ Tá»± Äá»™ng Tissot Le Locle Powermatic 80",
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
            "Máº·t sá»‘ Guilloche",
            "GÃ³c nghiÃªng viá»n",
            "Náº¯p lÆ°ng lá»™ cÆ¡",
            "Äeo trÃªn cá»• tay",
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
            "VÃ²m Acrylic",
            "ÄÃ¨n Ambient LED",
            "MÃ ng Subwoofer",
            "PhÃ²ng khÃ¡ch tá»‘i giáº£n",
          ],
          exclusive: "Flash",
        },
        {
          id: 104,
          category: "fashion",
          title: "KÃ­nh MÃ¡t PhÃ¢n Cá»±c Ray-Ban Aviator Classic Gold Frame",
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
            "Khung máº¡ vÃ ng",
            "Máº·t nghiÃªng gá»ng",
            "TrÃ²ng kÃ­nh rÃ¢m",
            "Phá»‘i Ä‘á»“ phong cÃ¡ch",
          ],
          exclusive: "Trend",
        },
        {
          id: 105,
          category: "tech",
          title: "BÃ n PhÃ­m CÆ¡ KhÃ´ng DÃ¢y NuPhy Air75 V2 Low-Profile",
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
            "Máº·t phÃ­m PBT",
            "Äá»™ má»ng hÃ´ng",
            "Switch cÆ¡ há»c",
            "BÃ n lÃ m viá»‡c Desk",
          ],
          exclusive: "Sáº¯p ChÃ¡y HÃ ng",
        },
      ];

      const DEFAULT_RECOMMEND_PRODUCTS = [
        {
          id: 201,
          category: "tech",
          title: "iPad Pro M4 11-inch OLED SiÃªu Má»ng 256GB Space Black",
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
            "MÃ n hÃ¬nh Ultra OLED",
            "Cáº¡nh vÃ¡t má»ng 5.1mm",
            "Máº·t lÆ°ng Space Black",
            "Tráº£i nghiá»‡m Apple Pencil",
          ],
        },
        {
          id: 202,
          category: "watch",
          title: "Apple Watch Ultra 2 GPS + Cellular DÃ¢y Alpine Loop",
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
            "MÃ n hÃ¬nh 3000 nits",
            "NÃºt Action Titanium",
            "KhÃ³a dá»‡t Alpine",
            "Äeo dÃ£ ngoáº¡i ngoÃ i trá»i",
          ],
        },
        {
          id: 203,
          category: "audio",
          title: "Tai Nghe Airpods Max Apple Báº£n KhÃ´ng Gian Chá»‘ng á»’n",
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
            "Chá»¥p tai vÃ²m lÆ°á»›i",
            "Khung thÃ©p khÃ´ng gá»‰",
            "NÃºm xoay Digital Crown",
            "Phá»‘i trang phá»¥c thá»i thÆ°á»£ng",
          ],
        },
        {
          id: 204,
          category: "fashion",
          title: "VÃ­ Da Nam Cáº§m Tay Epsom Äen Thá»§ CÃ´ng Phong CÃ¡ch PhÃ¡p",
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
            "VÃ¢n da dáº­p Epsom",
            "ÄÆ°á»ng may chá»‰ sÃ¡p",
            "NgÄƒn tháº» & tiá»n",
            "Cáº§m tay phong cÃ¡ch quÃ½ Ã´ng",
          ],
        },
        {
          id: 205,
          category: "tech",
          title: "MÃ¡y áº¢nh Mirrorless Fujifilm X-T5 Cá»• Äiá»ƒn KÃ¨m á»ng KÃ­nh Kit",
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
            "Máº·t trÆ°á»›c phong cÃ¡ch Retro",
            "VÃ²ng xoay kim loáº¡i cÆ¡",
            "MÃ n hÃ¬nh láº­t Ä‘a hÆ°á»›ng",
            "Chá»¥p thá»±c Ä‘á»‹a Ä‘Æ°á»ng phá»‘",
          ],
        },
        {
          id: 206,
          category: "fashion",
          title: "Ão Blazer Dáº¡ Nam Thiáº¿t Káº¿ Slimfit Chuáº©n Phong CÃ¡ch Ã",
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
            "DÃ¡ng Ã¡o Slimfit",
            "Cáº­n cáº£nh ve Ã¡o & cÃºc sá»«ng",
            "Cháº¥t dáº¡ cá»«u dá»‡t má»‹n",
            "Phá»‘i tá»•ng thá»ƒ thanh lá»‹ch",
          ],
        },
        {
          id: 207,
          category: "watch",
          title:
            "Äá»“ng Há»“ Ná»¯ DÃ¢y Kim Loáº¡i Citizen Eco-Drive NÄƒng LÆ°á»£ng Ãnh SÃ¡ng",
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
            "Kháº£m xÃ  cá»« máº·t sá»‘",
            "GÃ³c nghiÃªng viá»n Ä‘Ã¡",
            "DÃ¢y thÃ©p Ä‘an máº¯t nhá»",
            "Äeo tay dáº¡ tiá»‡c sang trá»ng",
          ],
        },
        {
          id: 208,
          category: "audio",
          title: "Loa Di Äá»™ng Marshall Emberton II Ã‚m Thanh Äa HÆ°á»›ng",
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
            "LÆ°á»›i táº£n nhiá»‡t Ä‘á»“ng thau",
            "NÃºm Ä‘iá»u hÆ°á»›ng kim loáº¡i",
            "Máº·t sau chá»‘ng nÆ°á»›c IP67",
            "Cáº§m tay picnic dÃ£ ngoáº¡i",
          ],
        },
        {
          id: 209,
          category: "fashion",
          title: "TÃºi XÃ¡ch Ná»¯ Da Tháº­t Quai XÃ¡ch Sang Trá»ng Tone Beige",
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
            "ChÃ­nh diá»‡n tone Beige",
            "KhÃ³a kim loáº¡i máº¡ vÃ ng",
            "Cáº­n cáº£nh vÃ¢n da bÃ²",
            "Mix outfit dáº¡o phá»‘",
          ],
        },
        {
          id: 210,
          category: "tech",
          title: "Chuá»™t CÃ´ng ThÃ¡i Há»c KhÃ´ng DÃ¢y Logitech MX Master 3S",
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
            "Form dÃ¡ng Ergonomic",
            "Con lÄƒn MagSpeed thÃ©p",
            "Cá»¥m nÃºt ngÃ³n cÃ¡i",
            "Setup bÃ n lÃ m viá»‡c tá»‘i giáº£n",
          ],
        },
      ];

      // --------------------------------------------------------------------------
      // Äá»’NG Bá»˜ Dá»® LIá»†U Sáº¢N PHáº¨M Tá»ª FASTAPI + SQL DATABASE
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
              </div>`
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
            </div>`
          )
          .join("");
      }

      function renderSectionErrorState(section, errorMsg) {
        const safeMsg = escapeHomepageHtml(errorMsg || "Không thể kết nối máy chủ API.");
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
          categories: { id: "categoriesGrid", title: "Không tải được danh mục nổi bật" },
          flash: { id: "flashProductsContainer", title: "Không tải được sản phẩm Flash Sale" },
          recommend: { id: "recommendProductsContainer", title: "Không tải được sản phẩm gợi ý / nổi bật" },
          latest: { id: "latestProductsContainer", title: "Không tải được sản phẩm mới nhất" },
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

        const heroBanners = HOMEPAGE_BANNERS.slice(0, Math.max(1, HOMEPAGE_BANNERS.length - 2));
        const subBanners = HOMEPAGE_BANNERS.length > 2 ? HOMEPAGE_BANNERS.slice(-2) : [];

        if (slidesEl) {
          slidesEl.innerHTML = heroBanners
            .map((b, idx) => {
              const title = escapeHomepageHtml(b.title || "Ưu đãi JML Store");
              const desc = escapeHomepageHtml(b.description || "Khám phá các sản phẩm chính hãng trên JML Store.");
              const imgUrl = escapeHomepageHtml(
                b.imageUrl ||
                  b.image_url ||
                  "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=1200&q=80"
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
                .map((_, idx) => `<div class="slider-dot ${idx === 0 ? "active" : ""}" data-index="${idx}"></div>`)
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
          ["banners", "categories", "flash", "recommend", "latest"].forEach(renderSectionLoadingState);
          return;
        }
        if (forcedState === "empty") {
          ["banners", "categories", "flash", "recommend", "latest"].forEach((s) => renderSectionEmptyState(s));
          return;
        }
        if (forcedState === "error") {
          ["banners", "categories", "flash", "recommend", "latest"].forEach((s) =>
            renderSectionErrorState(s, "Chế độ kiểm thử trạng thái lỗi API.")
          );
          return;
        }

        ["banners", "categories", "flash", "recommend", "latest"].forEach(renderSectionLoadingState);

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
          if (err.status === 404) {
            await Promise.all([
              retryHomepageSection("banners"),
              retryHomepageSection("categories"),
              loadProductsFallbackFromAPI(),
            ]);
          } else {
            ["banners", "categories", "flash", "recommend", "latest"].forEach((s) =>
              renderSectionErrorState(s, err.message)
            );
          }
        }
      }

      async function loadProductsFallbackFromAPI() {
        try {
          const data = await fetchHomepageJson(`${API_BASE_URL}/api/products`);
          FLASH_PRODUCTS = Array.isArray(data.flash_products) ? data.flash_products : [];
          RECOMMEND_PRODUCTS = Array.isArray(data.recommend_products) ? data.recommend_products : [];
          LATEST_PRODUCTS = [...RECOMMEND_PRODUCTS, ...FLASH_PRODUCTS].sort((a, b) => (b.id || 0) - (a.id || 0));
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
            const data = await fetchHomepageJson(`${API_BASE_URL}/api/homepage/banners`);
            renderHomepageBanners(data.banners || []);
          } else if (section === "categories") {
            try {
              const data = await fetchHomepageJson(`${API_BASE_URL}/api/homepage/categories`);
              renderHomepageCategories(data.categories || []);
            } catch (e) {
              if (e.status === 404) {
                const catData = await fetchHomepageJson(`${API_BASE_URL}/api/categories`);
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
              const data = await fetchHomepageJson(`${API_BASE_URL}/api/homepage/featured-products`);
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
              const data = await fetchHomepageJson(`${API_BASE_URL}/api/homepage/latest-products`);
              LATEST_PRODUCTS = data.latest_products || [];
              renderLatestProducts(LATEST_PRODUCTS);
            } catch (e) {
              if (e.status === 404) {
                const data = await fetchHomepageJson(`${API_BASE_URL}/api/products`);
                LATEST_PRODUCTS = [...(data.recommend_products || []), ...(data.flash_products || [])].sort(
                  (a, b) => (b.id || 0) - (a.id || 0)
                );
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

      const PRODUCT_EXTRA_INFO = {
        101: {
          brand: "Sony",
          origin: "Nháº­t Báº£n / Láº¯p rÃ¡p Malaysia",
          warranty: "12 thÃ¡ng chÃ­nh hÃ£ng Sony Viá»‡t Nam",
          desc: "Tai nghe chá»‘ng á»“n khÃ´ng dÃ¢y Sony WH-1000XM5 sá»Ÿ há»¯u cÃ´ng nghá»‡ dáº«n Ä‘áº§u ngÃ nh vá»›i hai bá»™ xá»­ lÃ½ chuyÃªn dá»¥ng V1 vÃ  HD QN1, kiá»ƒm soÃ¡t 8 micro Ä‘á»ƒ triá»‡t tiÃªu tiáº¿ng á»“n má»™t cÃ¡ch triá»‡t Ä‘á»ƒ nháº¥t. Thiáº¿t káº¿ driver 30mm sá»­ dá»¥ng mÃ ng vÃ²m sá»£i carbon siÃªu cá»©ng cho cháº¥t Ã¢m tinh táº¿, truyá»n táº£i chuáº©n xÃ¡c tá»«ng ná»‘t nháº¡c Hi-Res Audio Wireless LDAC.",
          specs: [
            { key: "ThÆ°Æ¡ng hiá»‡u", val: "Sony" },
            { key: "DÃ²ng sáº£n pháº©m", val: "WH-1000XM5 Flagship Series" },
            {
              key: "Bá»™ xá»­ lÃ½ chá»‘ng á»“n",
              val: "Dual Processor V1 & HD Noise Cancelling QN1",
            },
            {
              key: "Thá»i lÆ°á»£ng pin",
              val: "30 giá» (báº­t ANC), 40 giá» (táº¯t ANC)",
            },
            { key: "Cá»•ng sáº¡c", val: "USB Type-C há»— trá»£ chuáº©n Power Delivery" },
            { key: "Trá»ng lÆ°á»£ng", val: "250g (thiáº¿t káº¿ siÃªu nháº¹ Ä‘á»‡m da má»m)" },
            {
              key: "TÃ­nh nÄƒng thÃ´ng minh",
              val: "Speak-to-Chat, Quick Attention, Auto NC Optimizer",
            },
          ],
          colors: [
            "Äen Black Edition",
            "Báº¡c Silver White",
            "Xanh Midnight Blue",
          ],
        },
        102: {
          brand: "Tissot 1853",
          origin: "Thá»¥y SÄ© (Swiss Made)",
          warranty: "24 thÃ¡ng quá»‘c táº¿ chÃ­nh hÃ£ng",
          desc: "Tissot Le Locle Powermatic 80 lÃ  dÃ²ng Ä‘á»“ng há»“ cÆ¡ tá»± Ä‘á»™ng kinh Ä‘iá»ƒn tÃ´n vinh thá»‹ tráº¥n Le Locle - cÃ¡i nÃ´i Ä‘á»“ng há»“ Thá»¥y SÄ©. Máº·t sá»‘ Ä‘Æ°á»£c cháº¡m trá»• hoa vÄƒn Guilloche Clous de Paris tinh xáº£o, cá»c sá»‘ La MÃ£ mang Ä‘áº­m phong thÃ¡i quÃ½ tá»™c cá»• Ä‘iá»ƒn. TrÃ¡i tim lÃ  cá»— mÃ¡y cÆ¡ Powermatic 80 trá»¯ cÃ³t lÃªn Ä‘áº¿n 80 giá» hoáº¡t Ä‘á»™ng bá»n bá»‰.",
          specs: [
            { key: "ThÆ°Æ¡ng hiá»‡u", val: "Tissot 1853" },
            { key: "Xuáº¥t xá»©", val: "Thá»¥y SÄ© (Swiss Made)" },
            {
              key: "Bá»™ mÃ¡y cÆ¡",
              val: "Automatic Powermatic 80.111 (23 chÃ¢n kÃ­nh)",
            },
            { key: "Thá»i gian trá»¯ cÃ³t", val: "80 giá» bá»n bá»‰" },
            { key: "ÄÆ°á»ng kÃ­nh máº·t", val: "39.3 mm â€¢ Äá»™ dÃ y 9.8 mm" },
            {
              key: "KÃ­nh báº£o vá»‡",
              val: "Sapphire nguyÃªn khá»‘i chá»‘ng tráº§y xÆ°á»›c tuyá»‡t Ä‘á»‘i",
            },
            {
              key: "Cháº¥t liá»‡u vá» & dÃ¢y",
              val: "ThÃ©p khÃ´ng gá»‰ 316L máº¡ cÃ´ng nghá»‡ PVD cao cáº¥p",
            },
          ],
          colors: [
            "Báº¡c Máº·t Tráº¯ng Cá»• Äiá»ƒn",
            "VÃ ng Demi HoÃ ng Gia",
            "Máº·t Äen Lá»‹ch LÃ£m",
          ],
        },
        201: {
          brand: "Apple Inc.",
          origin: "Hoa Ká»³ / Láº¯p rÃ¡p chÃ­nh hÃ£ng",
          warranty: "12 thÃ¡ng Apple Care toÃ n quá»‘c",
          desc: "iPad Pro M4 11-inch hoÃ n toÃ n má»›i lÃ  bÆ°á»›c nháº£y vá»t cÃ´ng nghá»‡ vá»›i Ä‘á»™ má»ng khÃ³ tin chá»‰ 5.1mm, tÃ­ch há»£p vi xá»­ lÃ½ Apple M4 tháº¿ há»‡ tiáº¿p theo mang láº¡i hiá»‡u nÄƒng Ä‘á»“ há»a vÃ  trÃ­ tuá»‡ nhÃ¢n táº¡o vÆ°á»£t trá»™i. MÃ n hÃ¬nh Ultra Retina XDR sá»­ dá»¥ng cÃ´ng nghá»‡ Tandem OLED Ä‘á»™t phÃ¡ vá»›i Ä‘á»™ sÃ¡ng tá»‘i Ä‘a 1600 nits.",
          specs: [
            { key: "ThÆ°Æ¡ng hiá»‡u", val: "Apple" },
            {
              key: "Vi xá»­ lÃ½",
              val: "Apple M4 Chip (10-core CPU, 10-core GPU, 16-core NPU)",
            },
            {
              key: "MÃ n hÃ¬nh",
              val: "11 inch Ultra Retina XDR Tandem OLED 120Hz ProMotion",
            },
            {
              key: "Äá»™ sÃ¡ng tá»‘i Ä‘a",
              val: "1600 nits (HDR content), 1000 nits tiÃªu chuáº©n",
            },
            { key: "Bá»™ nhá»›", val: "256GB / 512GB / 1TB / 2TB Ultra Fast SSD" },
            {
              key: "Äá»™ má»ng",
              val: "5.1 mm (Chiáº¿c iPad má»ng nháº¥t lá»‹ch sá»­ Apple)",
            },
            {
              key: "Há»— trá»£ phá»¥ kiá»‡n",
              val: "Apple Pencil Pro, Magic Keyboard M4",
            },
          ],
          colors: ["Äen KhÃ´ng Gian (Space Black)", "Báº¡c Ãnh Kim (Silver)"],
        },
      };

      // Tráº¡ng thÃ¡i Giá» hÃ ng (Cart state)
      let cartItems = [];

      // Helper format tiá»n tá»‡ VNÄ
      function formatCurrency(amount) {
        return new Intl.NumberFormat("vi-VN", {
          style: "currency",
          currency: "VND",
        }).format(amount);
      }

      function getCategoryName(cat) {
        switch (cat) {
          case "audio":
            return "Thiáº¿t Bá»‹ Ã‚m Thanh";
          case "watch":
            return "Äá»“ng Há»“ Cao Cáº¥p";
          case "fashion":
            return "Thá»i Trang & Äá»“ Da";
          case "tech":
            return "Thiáº¿t Bá»‹ Sá»‘ & CÃ´ng Nghá»‡";
          default:
            return "Sáº£n Pháº©m Cao Cáº¥p";
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

      // Helper táº¡o cáº¥u trÃºc Multi-Image Carousel bÃªn trong khung áº£nh sáº£n pháº©m
      function createCarouselMarkup(product) {
        const images = product.images || [product.image];
        const angles = product.angles || [
          "ChÃ­nh diá»‡n",
          "GÃ³c nghiÃªng",
          "Cáº­n cáº£nh",
          "Thá»±c táº¿",
        ];

        const imagesHtml = images
          .map(
            (img, idx) => `
        <img src="${img}" alt="${product.title} - ${angles[idx] || "GÃ³c " + (idx + 1)}" class="product-slide-img ${idx === 0 ? "active" : ""}" data-index="${idx}" loading="lazy">
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
        <span class="product-angle-badge" data-badge>${angles[0] || "áº¢nh 1"}</span>
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
      // 1. RENDER Sáº¢N PHáº¨M FLASH SALE & Gá»¢I Ã
      // --------------------------------------------------------------------------
      function renderFlashSaleProducts() {
        const container = document.getElementById("flashProductsContainer");
        if (!container) return;
        if (!FLASH_PRODUCTS || FLASH_PRODUCTS.length === 0) {
          container.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 36px 16px; background: #fff; border-radius: 16px; border: 1px dashed #cbd5e1; margin: 8px 0;">
              <p style="font-weight: 600; font-size: 14px; color: #64748b;">ChÆ°a cÃ³ sáº£n pháº©m Flash Sale nÃ o Ä‘ang cháº¡y</p>
            </div>
          `;
          return;
        }
        container.innerHTML = FLASH_PRODUCTS.map((product) => {
          const percentSold = Math.round(
            (product.sold / product.totalStock) * 100,
          );
          const mainImg = product.images ? product.images[0] : product.image;
          return `
          <div class="product-card" onclick="openProductDetail(${product.id})">
            ${createCarouselMarkup(product)}
            <div class="product-body">
              <h3 class="product-title" title="${product.title}">${product.title}</h3>
              <div class="product-meta">
                <span class="rating-stars">â˜… ${product.rating}</span>
                <span>â€¢ ÄÃ£ bÃ¡n ${product.sold}</span>
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
                  <span>ÄÃ£ bÃ¡n ${product.sold}/${product.totalStock}</span>
                  <span>${percentSold}%</span>
                </div>
              </div>
              <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${product.title.replace(/'/g, "\\'")}', ${product.price}, '${mainImg}', '${(product.shopName || "").replace(/'/g, "\\'")}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                ThÃªm VÃ o Giá»
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
              <div style="font-size: 36px; margin-bottom: 8px;">ðŸ“¦</div>
              <p style="font-weight: 700; font-size: 15px; color: #334155; margin-bottom: 4px;">Hiá»‡n chÆ°a cÃ³ sáº£n pháº©m nÃ o trÃªn ká»‡</p>
              <p style="font-size: 13px; color: #64748b;">Admin cÃ³ thá»ƒ thÃªm sáº£n pháº©m má»›i tá»« trang Quáº£n trá»‹ SÃ n Ä‘á»ƒ xuáº¥t hiá»‡n táº¡i Ä‘Ã¢y.</p>
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
                <span class="rating-stars">â˜… ${product.rating}</span>
                <span>â€¢ ÄÃ£ bÃ¡n ${product.soldCount}</span>
              </div>
              <div class="price-row">
                <span class="current-price">${formatCurrency(product.price)}</span>
                <span class="original-price">${formatCurrency(product.originalPrice)}</span>
              </div>
              <div style="margin-top: auto;">
                <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${product.title.replace(/'/g, "\\'")}', ${product.price}, '${mainImg}', '${(product.shopName || "").replace(/'/g, "\\'")}')">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                  ThÃªm VÃ o Giá»
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
      // CÆ  CHáº¾ HOVER CAROUSEL Tá»° Äá»˜NG CHUYá»‚N GÃ“C CHá»¤P Sáº¢N PHáº¨M TRÃŠN CARD (1.1s/láº§n)
      // --------------------------------------------------------------------------
      function attachHoverCarouselListeners(parentContainer) {
        const wrappers = parentContainer.querySelectorAll(
          ".product-img-wrapper",
        );

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

          // Cho phÃ©p hover vÃ o tá»«ng dot Ä‘á»ƒ chuyá»ƒn gÃ³c ngay tá»©c kháº¯c
          dots.forEach((dot, dotIdx) => {
            dot.addEventListener("mouseenter", (e) => {
              e.stopPropagation();
              clearInterval(timer);
              setSlide(dotIdx);
            });
          });

          // Tá»± Ä‘á»™ng chuyá»ƒn láº§n lÆ°á»£t má»—i 1.1 giÃ¢y khi ngÆ°á»i dÃ¹ng hover chuá»™t
          wrapper.addEventListener("mouseenter", () => {
            clearInterval(timer);
            timer = setInterval(() => {
              setSlide(activeIdx + 1);
            }, 1100);
          });

          // Khi rÃª chuá»™t ra ngoÃ i (mouseleave), tá»± Ä‘á»™ng trá»Ÿ vá» áº£nh Ä‘áº¡i diá»‡n ban Ä‘áº§u
          wrapper.addEventListener("mouseleave", () => {
            clearInterval(timer);
            setSlide(0);
          });
        });
      }

      // --------------------------------------------------------------------------
      // 2. MÃ€N HÃŒNH CHI TIáº¾T Sáº¢N PHáº¨M (SINGLE PAGE APPLICATION DETAIL VIEW)
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

        // Láº¥y thÃ´ng tin má»Ÿ rá»™ng hoáº·c táº¡o thÃ´ng sá»‘ máº·c Ä‘á»‹nh phÃ¹ há»£p
        const extra = PRODUCT_EXTRA_INFO[product.id] || {
          brand: "ThÆ°Æ¡ng Hiá»‡u Cao Cáº¥p",
          origin: "Nháº­p kháº©u chÃ­nh hÃ£ng",
          warranty: "24 thÃ¡ng chÃ­nh hÃ£ng JML Store",
          desc: `${product.title} lÃ  sáº£n pháº©m hÃ ng Ä‘áº§u trong bá»™ sÆ°u táº­p cao cáº¥p, Ä‘Æ°á»£c cháº¿ tÃ¡c tá»‰ má»‰ tá»« nhá»¯ng váº­t liá»‡u tinh hoa nháº¥t. Sáº£n pháº©m Ä‘Ã¡p á»©ng tiÃªu chuáº©n kháº¯t khe vá» Ä‘á»™ hoÃ n thiá»‡n, tÃ­nh tháº©m má»¹ vÃ  Ä‘á»™ bá»n bá»‰ dÃ i lÃ¢u.`,
          specs: [
            { key: "TÃªn sáº£n pháº©m", val: product.title },
            { key: "Danh má»¥c", val: getCategoryName(product.category) },
            {
              key: "TiÃªu chuáº©n kiá»ƒm duyá»‡t",
              val: "100% ChÃ­nh hÃ£ng phÃ¢n phá»‘i Ä‘á»™c quyá»n",
            },
            { key: "TÃ¬nh tráº¡ng", val: "Má»›i 100% nguyÃªn há»™p kÃ¨m tháº» báº£o hÃ nh" },
            { key: "Báº£o hÃ nh", val: "24 thÃ¡ng Ä‘á»•i má»›i trong 30 ngÃ y náº¿u lá»—i" },
          ],
          colors: ["MÃ u TiÃªu Chuáº©n (Máº·c Ä‘á»‹nh)", "PhiÃªn Báº£n Giá»›i Háº¡n"],
        };

        const images = product.images || [product.image];
        const angles = product.angles || [
          "ChÃ­nh diá»‡n",
          "GÃ³c nghiÃªng",
          "Cáº­n cáº£nh",
          "Thá»±c táº¿",
        ];
        currentSelectedColor = extra.colors[0];
        currentSelectedVersion = "Báº£n TiÃªu Chuáº©n";

        const detailContainer = document.getElementById("view-product-detail");
        const homeContainer = document.getElementById("view-home");

        // Gá»£i Ã½ 4 sáº£n pháº©m cÃ¹ng phÃ¢n khÃºc
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
                  <span class="rating-stars">â˜… ${rel.rating}</span>
                  <span>â€¢ ÄÃ£ bÃ¡n ${rel.soldCount}</span>
                </div>
                <div class="price-row">
                  <span class="current-price">${formatCurrency(rel.price)}</span>
                  <span class="original-price">${formatCurrency(rel.originalPrice)}</span>
                </div>
                <div style="margin-top: auto;">
                  <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${rel.title.replace(/'/g, "\\'")}', ${rel.price}, '${relImg}', '${(rel.shopName || "").replace(/'/g, "\\'")}')">
                    ThÃªm VÃ o Giá»
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
                Quay Láº¡i Danh SÃ¡ch
              </button>
              <div class="breadcrumb-trail">
                <a href="#" onclick="showHomeView(); return false;">Trang Chá»§</a>
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
                    <div class="gallery-thumb-item ${idx === 0 ? "active" : ""}" onclick="switchDetailImage(${idx}, '${img}', '${angles[idx] || "GÃ³c " + (idx + 1)}')">
                      <img src="${img}" alt="${angles[idx]}">
                      <span>${angles[idx] || "áº¢nh " + (idx + 1)}</span>
                    </div>
                  `,
                    )
                    .join("")}
                </div>

                <!-- Trust Guarantees Box -->
                <div class="trust-features-grid">
                  <div class="trust-item">
                    <div class="trust-icon">ðŸ›¡ï¸</div>
                    <div>
                      <strong>100% ChÃ­nh HÃ£ng</strong>
                      <span>Äá»n bÃ¹ 200% náº¿u phÃ¡t hiá»‡n giáº£</span>
                    </div>
                  </div>
                  <div class="trust-item">
                    <div class="trust-icon">ðŸ”„</div>
                    <div>
                      <strong>Äá»•i Tráº£ 30 NgÃ y</strong>
                      <span>Miá»…n phÃ­ 100% náº¿u cÃ³ lá»—i tá»« NSX</span>
                    </div>
                  </div>
                  <div class="trust-item">
                    <div class="trust-icon">ðŸš€</div>
                    <div>
                      <strong>Giao Há»a Tá»‘c 2H</strong>
                      <span>Ná»™i thÃ nh HÃ  Ná»™i & TP.HCM</span>
                    </div>
                  </div>
                  <div class="trust-item">
                    <div class="trust-icon">ðŸ’Ž</div>
                    <div>
                      <strong>Báº£o HÃ nh 24 ThÃ¡ng</strong>
                      <span>Báº£o hÃ nh Ä‘iá»‡n tá»­ chÃ­nh hÃ£ng</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right Column: Purchasing & Details -->
              <div class="showcase-info">
                <div class="detail-mall-badge">
                  <span class="mall-pill">âœ“ JML OFFICIAL MALL</span>
                  <span class="sku-pill">MÃƒ SP: #LX-${product.id}</span>
                </div>

                <h1 class="detail-product-title">${product.title}</h1>

                <div class="detail-meta-row">
                  <div class="meta-rating">
                    <span class="stars">â˜…â˜…â˜…â˜…â˜…</span>
                    <strong>${product.rating}</strong>
                  </div>
                  <span>â€¢</span>
                  <span class="meta-reviews">184 ÄÃ¡nh giÃ¡ thá»±c táº¿</span>
                  <span>â€¢</span>
                  <span class="meta-sold">ÄÃ£ bÃ¡n ${product.sold || product.soldCount || 120}</span>
                </div>

                <!-- Price Box -->
                <div class="detail-price-box">
                  <div class="price-header">
                    <span class="price-label">GiÃ¡ Æ¯u ÄÃ£i Äá»™c Quyá»n</span>
                    <span class="deal-pill">âš¡ FLASH SALE TIáº¾T KIá»†M</span>
                  </div>
                  <div class="price-numbers">
                    <span class="detail-current-price">${formatCurrency(product.price)}</span>
                    <span class="detail-original-price">${formatCurrency(product.originalPrice)}</span>
                    <span class="detail-save-badge">Tiáº¿t kiá»‡m ${formatCurrency(product.originalPrice - product.price)} (${product.discount})</span>
                  </div>
                  <div class="price-voucher-notice">
                    ðŸŽ Táº·ng Voucher 100K cho thÃ nh viÃªn VIP â€¢ Miá»…n phÃ­ váº­n chuyá»ƒn toÃ n quá»‘c
                  </div>
                </div>

                <!-- Variant: MÃ u Sáº¯c -->
                <div class="variant-section">
                  <div class="variant-title">
                    <span>Chá»n MÃ u Sáº¯c:</span>
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

                <!-- Variant: PhiÃªn Báº£n -->
                <div class="variant-section">
                  <div class="variant-title">
                    <span>PhiÃªn Báº£n / Dung LÆ°á»£ng:</span>
                    <strong id="selectedVersionLabel">Báº£n TiÃªu Chuáº©n (Fullbox)</strong>
                  </div>
                  <div class="variant-options">
                    <button class="variant-btn active" onclick="selectVariant(this, 'selectedVersionLabel', 'Báº£n TiÃªu Chuáº©n (Fullbox)')">
                      Báº£n TiÃªu Chuáº©n (Fullbox)
                    </button>
                    <button class="variant-btn" onclick="selectVariant(this, 'selectedVersionLabel', 'Báº£n NÃ¢ng Cáº¥p KÃ¨m QuÃ  Táº·ng')">
                      Báº£n NÃ¢ng Cáº¥p KÃ¨m QuÃ  Táº·ng
                    </button>
                  </div>
                </div>

                <!-- Quantity Picker -->
                <div class="quantity-section">
                  <span class="qty-label">Sá»‘ LÆ°á»£ng:</span>
                  <div class="qty-picker">
                    <button type="button" onclick="changeDetailQty(-1)">âˆ’</button>
                    <input type="number" id="detailQtyInput" value="1" min="1" max="10" readonly>
                    <button type="button" onclick="changeDetailQty(1)">+</button>
                  </div>
                  <span class="stock-remain">CÃ²n láº¡i <strong>${product.totalStock || 45}</strong> sáº£n pháº©m trong kho</span>
                </div>

                <!-- CTA Action Buttons -->
                <div class="detail-actions-row">
                  <button class="btn-detail-add-cart" onclick="addCurrentDetailToCart()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                    ThÃªm VÃ o Giá» HÃ ng
                  </button>
                  <button class="btn-detail-buy-now" onclick="buyCurrentDetailNow()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                    Mua Ngay Vá»›i GiÃ¡ Æ¯u ÄÃ£i
                  </button>
                </div>

                <!-- Shipping Summary Box -->
                <div class="shipping-info-card">
                  <div class="shipping-row">
                    <span>ðŸ“ Äá»‹a chá»‰ nháº­n hÃ ng:</span>
                    <strong>TÃ²a nhÃ  Discovery Complex, Cáº§u Giáº¥y, HÃ  Ná»™i</strong>
                    <a href="#" onclick="showToast('Vá»‹ trÃ­', 'Cáº­p nháº­t Ä‘á»‹a chá»‰ nháº­n hÃ ng'); return false;" style="color: var(--primary); font-weight: 600; margin-left: auto;">Thay Ä‘á»•i</a>
                  </div>
                  <div class="shipping-row">
                    <span>ðŸšš Váº­n chuyá»ƒn:</span>
                    <strong style="color: var(--success);">Miá»…n phÃ­ váº­n chuyá»ƒn há»a tá»‘c</strong>
                    <span style="color: var(--text-muted);">(Dá»± kiáº¿n nháº­n hÃ ng trong ngÃ y mai)</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tabbed Detailed Info Section -->
            <div class="detail-tabs-section">
              <div class="detail-tab-nav">
                <button class="detail-tab-btn active" onclick="switchDetailTab('tab-desc', this)">MÃ´ Táº£ Sáº£n Pháº©m</button>
                <button class="detail-tab-btn" onclick="switchDetailTab('tab-specs', this)">ThÃ´ng Sá»‘ Ká»¹ Thuáº­t</button>
                <button class="detail-tab-btn" onclick="switchDetailTab('tab-reviews', this)">ÄÃ¡nh GiÃ¡ KhÃ¡ch HÃ ng (184)</button>
                <button class="detail-tab-btn" onclick="switchDetailTab('tab-policy', this)">ChÃ­nh SÃ¡ch & Báº£o HÃ nh</button>
              </div>

              <!-- Tab 1: MÃ´ táº£ -->
              <div id="tab-desc" class="detail-tab-pane active">
                <p style="margin-bottom: 16px; font-size: 15px;">${extra.desc}</p>
                <h4 style="font-size: 16px; font-weight: 700; color: var(--secondary); margin: 20px 0 10px;">Äáº·c Äiá»ƒm Ná»•i Báº­t</h4>
                <ul style="padding-left: 20px; display: flex; flex-direction: column; gap: 8px;">
                  <li>Thiáº¿t káº¿ cÃ´ng thÃ¡i há»c hiá»‡n Ä‘áº¡i, tÃ´n vinh Ä‘áº³ng cáº¥p ngÆ°á»i sá»­ dá»¥ng.</li>
                  <li>Sá»­ dá»¥ng linh kiá»‡n cao cáº¥p tá»« nhÃ  sáº£n xuáº¥t uy tÃ­n toÃ n cáº§u.</li>
                  <li>Kiá»ƒm Ä‘á»‹nh cháº¥t lÆ°á»£ng nghiÃªm ngáº·t trÆ°á»›c khi xuáº¥t xÆ°á»Ÿng vÃ  giao Ä‘áº¿n tay ngÆ°á»i tiÃªu dÃ¹ng.</li>
                  <li>TÃ­ch há»£p Ä‘áº§y Ä‘á»§ phá»¥ kiá»‡n chÃ­nh hÃ£ng nguyÃªn há»™p.</li>
                </ul>
              </div>

              <!-- Tab 2: ThÃ´ng sá»‘ ká»¹ thuáº­t -->
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

              <!-- Tab 3: ÄÃ¡nh giÃ¡ -->
              <div id="tab-reviews" class="detail-tab-pane">
                <div style="display: flex; align-items: center; gap: 20px; background: var(--surface-dim); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
                  <div style="font-size: 38px; font-weight: 800; color: var(--secondary); line-height: 1;">4.9<span style="font-size: 18px; color: var(--text-muted); font-weight: 500;">/5</span></div>
                  <div>
                    <div style="color: #f59e0b; font-size: 16px; margin-bottom: 4px;">â˜…â˜…â˜…â˜…â˜…</div>
                    <div style="font-size: 12px; color: var(--text-muted);">Dá»±a trÃªn 184 lÆ°á»£t Ä‘Ã¡nh giÃ¡ tá»« ngÆ°á»i mua Ä‘Ã£ xÃ¡c thá»±c</div>
                  </div>
                </div>

                <div class="review-card">
                  <div class="review-header">
                    <span class="reviewer-name">Nguyá»…n VÄƒn HoÃ ng <span class="verified-badge">âœ“ ÄÃ£ mua hÃ ng táº¡i JML Store</span></span>
                    <span class="review-date">3 ngÃ y trÆ°á»›c</span>
                  </div>
                  <div class="review-stars">â˜…â˜…â˜…â˜…â˜…</div>
                  <p>HÃ ng chÃ­nh hÃ£ng Ä‘Ã³ng gÃ³i ráº¥t ká»¹ lÆ°á»¡ng. Giao hÃ ng chá»‰ máº¥t 2 tiáº¿ng á»Ÿ HÃ  Ná»™i, Ä‘Ãºng chuáº©n mÃ´ táº£ vÃ  mÃ u sáº¯c trÃªn áº£nh. Ráº¥t hÃ i lÃ²ng!</p>
                </div>

                <div class="review-card">
                  <div class="review-header">
                    <span class="reviewer-name">Tráº§n ThÃ¹y Linh <span class="verified-badge">âœ“ ÄÃ£ mua hÃ ng táº¡i JML Store</span></span>
                    <span class="review-date">1 tuáº§n trÆ°á»›c</span>
                  </div>
                  <div class="review-stars">â˜…â˜…â˜…â˜…â˜…</div>
                  <p>Sáº£n pháº©m cao cáº¥p, cháº¥t lÆ°á»£ng hoÃ n thiá»‡n tuyá»‡t vá»i. NhÃ¢n viÃªn há»— trá»£ tÆ° váº¥n ráº¥t nhiá»‡t tÃ¬nh vÃ  kÃ­ch hoáº¡t báº£o hÃ nh Ä‘iá»‡n tá»­ nhanh chÃ³ng.</p>
                </div>
              </div>

              <!-- Tab 4: ChÃ­nh sÃ¡ch -->
              <div id="tab-policy" class="detail-tab-pane">
                <div style="display: flex; flex-direction: column; gap: 14px;">
                  <div>
                    <strong style="color: var(--secondary);">1. ChÃ­nh sÃ¡ch báº£o hÃ nh chÃ­nh hÃ£ng:</strong>
                    <p style="margin-top: 4px;">Báº£o hÃ nh 12 - 24 thÃ¡ng theo quy chuáº©n cá»§a nhÃ  sáº£n xuáº¥t. KÃ­ch hoáº¡t báº£o hÃ nh Ä‘iá»‡n tá»­ thÃ´ng minh qua sá»‘ Ä‘iá»‡n thoáº¡i mua hÃ ng.</p>
                  </div>
                  <div>
                    <strong style="color: var(--secondary);">2. ChÃ­nh sÃ¡ch Ä‘á»•i má»›i 30 ngÃ y:</strong>
                    <p style="margin-top: 4px;">Äá»•i má»›i 1:1 miá»…n phÃ­ trong 30 ngÃ y Ä‘áº§u tiÃªn náº¿u sáº£n pháº©m phÃ¡t sinh lá»—i tá»« nhÃ  sáº£n xuáº¥t (yÃªu cáº§u giá»¯ nguyÃªn há»™p vÃ  phá»¥ kiá»‡n).</p>
                  </div>
                  <div>
                    <strong style="color: var(--secondary);">3. Cam káº¿t nguá»“n gá»‘c:</strong>
                    <p style="margin-top: 4px;">100% sáº£n pháº©m phÃ¢n phá»‘i bá»Ÿi JML Store lÃ  hÃ ng chÃ­nh ngáº¡ch cÃ³ hÃ³a Ä‘Æ¡n VAT vÃ  tem chá»‘ng hÃ ng giáº£ cá»§a Bá»™ CÃ´ng An.</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Related Products Section -->
            <div class="related-products-section">
              <div class="section-title-wrap">
                <div>
                  <h2 class="section-title">Sáº£n Pháº©m CÃ¹ng Bá»™ SÆ°u Táº­p</h2>
                  <p class="section-subtitle">Gá»£i Ã½ sáº£n pháº©m tÆ°Æ¡ng tá»± cÃ³ thá»ƒ báº¡n cÅ©ng quan tÃ¢m</p>
                </div>
              </div>
              <div class="recommend-grid">${relatedCardsHtml}</div>
            </div>
          </div>
        `;

        // Chuyá»ƒn SPA view
        homeContainer.classList.remove("active");
        detailContainer.classList.add("active");
        window.location.hash = "product/" + product.id;
        window.scrollTo({ top: 0, behavior: "smooth" });

        // Gáº¯n listener hover cho cÃ¡c card liÃªn quan
        attachHoverCarouselListeners(detailContainer);
      }

      function showHomeView() {
        const detailContainer = document.getElementById("view-product-detail");
        const homeContainer = document.getElementById("view-home");
        if (detailContainer && homeContainer) {
          detailContainer.classList.remove("active");
          homeContainer.classList.add("active");
          window.location.hash = "";
          window.scrollTo({ top: 0, behavior: "smooth" });
        }
      }

      function switchDetailImage(index, imgSrc, angleName) {
        const mainImg = document.getElementById("detailMainImg");
        const angleBadge = document.getElementById("detailAngleBadge");
        if (mainImg) mainImg.src = imgSrc;
        if (angleBadge) angleBadge.textContent = angleName;

        document
          .querySelectorAll(".gallery-thumb-item")
          .forEach((thumb, idx) => {
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

      function changeDetailQty(delta) {
        const input = document.getElementById("detailQtyInput");
        if (!input) return;
        let val = parseInt(input.value, 10) || 1;
        val += delta;
        if (val < 1) val = 1;
        if (val > 10) val = 10;
        input.value = val;
        currentDetailQty = val;
      }

      function addCurrentDetailToCart() {
        if (!currentDetailProduct) return;
        const mainImg = currentDetailProduct.images
          ? currentDetailProduct.images[0]
          : currentDetailProduct.image;
        const titleWithVariant = `${currentDetailProduct.title} (${currentSelectedColor || "TiÃªu chuáº©n"})`;
        const shopName = currentDetailProduct.shopName || "Trungshop";

        for (let i = 0; i < currentDetailQty; i++) {
          cartItems.push({
            title: titleWithVariant,
            price: currentDetailProduct.price,
            image: mainImg,
            qty: 1,
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
          "ÄÃ£ thÃªm vÃ o giá» hÃ ng!",
          `${currentDetailQty}x ${titleWithVariant}`,
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

      // Xá»­ lÃ½ URL hash Ä‘á»ƒ Ä‘á»“ng bá»™ SPA (nÃºt Back/Forward cá»§a trÃ¬nh duyá»‡t)
      function checkUrlHash() {
        const hash = window.location.hash;
        if (hash.startsWith("#product/")) {
          const id = hash.replace("#product/", "");
          if (id) openProductDetail(id);
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
      // 5. GIá»Ž HÃ€NG (SHOPPING CART) & HIá»†U á»¨NG BOUNCE BADGE
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

      // NgÄƒn cháº·n sá»± kiá»‡n click bÃªn trong dropdown lÃ m Ä‘Ã³ng chÃ­nh nÃ³
      [cartDropdown, notifDropdown, userDropdown].forEach((dd) => {
        if (dd) {
          dd.addEventListener("click", (e) => e.stopPropagation());
        }
      });

      // Click ra bÃªn ngoÃ i Ä‘á»ƒ Ä‘Ã³ng toÃ n bá»™ popups/dropdowns
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

        // KÃ­ch hoáº¡t hiá»‡u á»©ng náº£y icon giá» hÃ ng
        if (cartCountBadge) {
          cartCountBadge.classList.remove("bounce");
          void cartCountBadge.offsetWidth; // Trigger reflow
          cartCountBadge.classList.add("bounce");
        }

        // Báº­t Toast notification
        showToast("ÄÃ£ thÃªm vÃ o giá» hÃ ng!", title);
      }

      function removeFromCart(index) {
        const removed = cartItems.splice(index, 1)[0];
        updateCartDisplay();
        showToast("ÄÃ£ xÃ³a khá»i giá»", removed ? removed.title : "");
      }

      function updateCartDisplay() {
        const totalQty = cartItems.reduce(
          (acc, item) => acc + (item.qty || 1),
          0,
        );
        if (cartCountBadge) cartCountBadge.textContent = totalQty;
        if (cartCountHeader)
          cartCountHeader.textContent = `${totalQty} sáº£n pháº©m`;

        if (!cartItemsList || !cartTotalSum) return;

        if (cartItems.length === 0) {
          cartItemsList.innerHTML =
            '<p style="font-size: 13px; color: var(--text-muted); text-align: center; padding: 24px 0;">ChÆ°a cÃ³ sáº£n pháº©m nÃ o trong giá» hÃ ng</p>';
          cartTotalSum.textContent = "0 â‚«";
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
              <span class="cart-item-price">${formatCurrency(item.price)} ${item.qty > 1 ? `<span style="font-size: 11px; color: var(--text-muted); font-weight: 500;">x${item.qty}</span>` : ""}</span>
              <button onclick="removeFromCart(${idx})" title="XÃ³a khá»i giá»" style="color: #ef4444; font-size: 14px; padding: 2px 6px; cursor: pointer; border-radius: 4px;">âœ•</button>
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
            "ThÃ´ng bÃ¡o",
            "Giá» hÃ ng Ä‘ang trá»‘ng! Vui lÃ²ng chá»n sáº£n pháº©m trÆ°á»›c khi thanh toÃ¡n.",
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
                      ? "Chá»§ Shop"
                      : user.rank || "ThÃ nh viÃªn";
                dropNameEl.textContent = `${user.full_name} (${roleLabel})`;
              }
              return;
            }
          } catch (e) {}
        }
        if (avatarEl) avatarEl.textContent = "KH";
        if (nameEl) nameEl.textContent = "ÄÄƒng nháº­p";
        if (dropNameEl)
          dropNameEl.textContent = "KhÃ¡ch vÃ£ng lai (ChÆ°a Ä‘Äƒng nháº­p)";
      }

      function handleUserLogout() {
        localStorage.removeItem("JML_CUSTOMER_USER");
        localStorage.removeItem("JML_AUTH_USER");
        syncCustomerAuthHeader();
        showToast("ÄÄƒng xuáº¥t", "Báº¡n Ä‘Ã£ Ä‘Äƒng xuáº¥t tÃ i khoáº£n thÃ nh cÃ´ng!");
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
            alertEl.textContent = data.detail || "ÄÄƒng nháº­p tháº¥t báº¡i!";
            return;
          }
          localStorage.setItem("JML_CUSTOMER_USER", JSON.stringify(data.user));
          syncCustomerAuthHeader();
          closeCustomerAuthModal();
          showToast(
            "ÄÄƒng nháº­p thÃ nh cÃ´ng",
            `ChÃ o má»«ng ${data.user.full_name} quay trá»Ÿ láº¡i!`,
          );
        } catch (err) {
          alertEl.style.display = "block";
          alertEl.style.background = "#fef2f2";
          alertEl.style.color = "#ef4444";
          alertEl.textContent = "KhÃ´ng thá»ƒ káº¿t ná»‘i mÃ¡y chá»§!";
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
            alertEl.textContent = data.detail || "ÄÄƒng kÃ½ tháº¥t báº¡i!";
            return;
          }
          localStorage.setItem("JML_CUSTOMER_USER", JSON.stringify(data.user));
          syncCustomerAuthHeader();
          closeCustomerAuthModal();
          showToast(
            "ÄÄƒng kÃ½ thÃ nh cÃ´ng",
            `ChÃºc má»«ng ${data.user.full_name} Ä‘Ã£ táº¡o tÃ i khoáº£n thÃ nh cÃ´ng!`,
          );
        } catch (err) {
          alertEl.style.display = "block";
          alertEl.style.background = "#fef2f2";
          alertEl.style.color = "#ef4444";
          alertEl.textContent = "KhÃ´ng thá»ƒ káº¿t ná»‘i mÃ¡y chá»§!";
        }
      }

      document.addEventListener("DOMContentLoaded", () => {
        syncCustomerAuthHeader();
      });

      // Quáº£n lÃ½ Voucher & PhÆ°Æ¡ng Thá»©c Váº­n Chuyá»ƒn
      let appliedVoucher = null;

      const AVAILABLE_VOUCHERS = {
        FREESHIP: {
          code: "FREESHIP",
          type: "shipping",
          desc: "Miá»…n phÃ­ 100% tiá»n váº­n chuyá»ƒn",
          minOrder: 0,
        },
        JML50K: {
          code: "JML50K",
          type: "fixed",
          amount: 50000,
          desc: "Giáº£m ngay 50.000 â‚«",
          minOrder: 100000,
        },
        GIAM10: {
          code: "GIAM10",
          type: "percent",
          percent: 10,
          maxAmount: 100000,
          desc: "Giáº£m 10% (tá»‘i Ä‘a 100.000 â‚«)",
          minOrder: 0,
        },
        VIP100K: {
          code: "VIP100K",
          type: "fixed",
          amount: 100000,
          desc: "Giáº£m 100.000 â‚« cho Ä‘Æ¡n tá»« 1.000.000 â‚«",
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

        // Tá»± Ä‘á»™ng Ä‘iá»n thÃ´ng tin KhÃ¡ch hÃ ng Ä‘ang Ä‘Äƒng nháº­p náº¿u cÃ³
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
          ? selectedOpt.getAttribute("data-name") || "TiÃªu Chuáº©n (GHN Express)"
          : "TiÃªu Chuáº©n (GHN Express)";

        let discountAmount = 0;
        let isFreeShipping = false;

        if (appliedVoucher) {
          if (appliedVoucher.type === "shipping") {
            isFreeShipping = true;
            discountAmount = baseShipFee;
          } else if (appliedVoucher.type === "fixed") {
            discountAmount = Math.min(appliedVoucher.amount, subtotal);
          } else if (appliedVoucher.type === "percent") {
            const calculated = Math.round(
              subtotal * (appliedVoucher.percent / 100),
            );
            discountAmount = Math.min(
              calculated,
              appliedVoucher.maxAmount || calculated,
            );
          }
        }

        const effectiveShipFee = isFreeShipping ? 0 : baseShipFee;
        const finalTotal = Math.max(0, subtotal + baseShipFee - discountAmount);

        // Cáº­p nháº­t giao diá»‡n tÃ³m táº¯t
        const countEl = document.getElementById("checkoutModalItemCount");
        if (countEl)
          countEl.textContent = `${count} sáº£n pháº©m â€¢ ${formatCurrency(subtotal)}`;

        const shipLabelEl = document.getElementById("checkoutShippingLabel");
        if (shipLabelEl)
          shipLabelEl.textContent = `Váº­n chuyá»ƒn (${shipName.split(" ")[0]}):`;

        const shipFeeEl = document.getElementById("checkoutShippingFeeText");
        if (shipFeeEl) {
          if (isFreeShipping) {
            shipFeeEl.innerHTML = `<span style="color: #10b981; font-weight: 700;">Miá»…n phÃ­ (${appliedVoucher.code})</span>`;
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
              discountLabel.textContent = `MÃ£ giáº£m (${appliedVoucher.code}):`;
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
            statusEl.textContent = "âœ• MÃ£ khÃ´ng tá»“n táº¡i hoáº·c Ä‘Ã£ háº¿t lÆ°á»£t!";
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
            statusEl.textContent = `âœ• MÃ£ ${code} chá»‰ Ã¡p dá»¥ng cho Ä‘Æ¡n tá»« ${formatCurrency(v.minOrder)}!`;
          }
          appliedVoucher = null;
          updateCheckoutTotals();
          return;
        }

        appliedVoucher = v;
        if (statusEl) {
          statusEl.style.display = "inline";
          statusEl.style.color = "#10b981";
          statusEl.innerHTML = `âœ“ ÄÃ£ Ã¡p dá»¥ng <strong>${code}</strong> <button type="button" onclick="cancelVoucher()" style="background: none; border: none; color: #ef4444; font-size: 11px; font-weight: 700; cursor: pointer; text-decoration: underline; margin-left: 4px;">Há»§y mÃ£</button>`;
        }
        updateCheckoutTotals();
        showToast(
          "Ãp dá»¥ng mÃ£ thÃ nh cÃ´ng",
          `MÃ£ ${code} Ä‘Ã£ Ä‘Æ°á»£c Ã¡p dá»¥ng: ${v.desc}!`,
        );
      }

      function cancelVoucher() {
        appliedVoucher = null;
        const input = document.getElementById("checkoutVoucherInput");
        if (input) input.value = "";
        const statusEl = document.getElementById("voucherStatusText");
        if (statusEl) statusEl.style.display = "none";
        updateCheckoutTotals();
        showToast("ÄÃ£ há»§y voucher", "ÄÃ£ gá»¡ bá» mÃ£ giáº£m giÃ¡ khá»i Ä‘Æ¡n hÃ ng.");
      }

      async function confirmCheckoutOrder(e) {
        if (e) e.preventDefault();

        const name = (
          document.getElementById("checkoutBuyerName")?.value ||
          "KhÃ¡ch mua hÃ ng"
        ).trim();
        const phone = (
          document.getElementById("checkoutBuyerPhone")?.value || "0908123456"
        ).trim();
        const address = (
          document.getElementById("checkoutBuyerAddress")?.value ||
          "Quáº­n 1, TP.HCM"
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
          variant: "ChÃ­nh hÃ£ng â€¢ Shop: " + (item.shopName || orderShopName),
          price: formatCurrency(item.price),
          qty: String(item.qty || 1),
          subtotal: formatCurrency(item.price * (item.qty || 1)),
        }));

        let orderId = "#MP-" + Math.floor(1000 + Math.random() * 9000);

        // 1. Gá»i FastAPI lÆ°u Ä‘Æ¡n hÃ ng vÃ o Database
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
              "âŒ TÃ€I KHOáº¢N ÄÃƒ Bá»Š KHÃ“A!\n\n" +
                (errData.detail ||
                  "TÃ i khoáº£n nÃ y Ä‘Ã£ bá»‹ Ban Quáº£n Trá»‹ SÃ n khÃ³a."),
            );
            return;
          }

          if (res.ok) {
            const data = await res.json();
            if (data.order_id) orderId = data.order_id;
          }
        } catch (err) {
          // Fallback kiá»ƒm tra banned trong localStorage náº¿u chÆ°a báº­t port 8000
          const bannedList = JSON.parse(
            localStorage.getItem("JML_BANNED_CUSTOMERS") || "[]",
          );
          if (bannedList.includes(phone) || bannedList.includes(name)) {
            alert(
              "âŒ TÃ€I KHOáº¢N ÄÃƒ Bá»Š KHÃ“A!\n\nSá»‘ Ä‘iá»‡n thoáº¡i/TÃ i khoáº£n (" +
                phone +
                ") Ä‘Ã£ bá»‹ Ban Quáº£n Trá»‹ SÃ n táº¡m khÃ³a.",
            );
            return;
          }
        }

        // 2. Äá»“ng bá»™ dá»± phÃ²ng vÃ o localStorage Ä‘á»ƒ tab Admin nháº­n tÃ­n hiá»‡u tá»©c thÃ¬
        const newOrder = {
          id: orderId,
          key: orderId.replace("#", ""),
          escrowBadge: "ðŸ”’ SÃ n Ä‘ang giá»¯ tiá»n",
          escrowClass: "bg-primary-50 text-primary-500",
          time:
            "Thá»i gian Ä‘áº·t: " +
            new Date().toLocaleString("vi-VN") +
            " â€¢ Váº­n chuyá»ƒn: " +
            shippingMethod +
            (voucherCode ? " â€¢ Voucher: " + voucherCode : ""),
          shopName: orderShopName,
          shopAddress: "Kho láº¥y hÃ ng: Nguyá»…n Thá»‹ Minh Khai, Quáº­n 1, TP.HCM",
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
          "Äáº·t hÃ ng thÃ nh cÃ´ng",
          `ÄÆ¡n hÃ ng ${orderId} (${totalFormatted}) Ä‘Ã£ Ä‘Æ°á»£c lÆ°u vÃ o há»‡ thá»‘ng!`,
        );
        openUserOrdersModal();
      }

      // --------------------------------------------------------------------------
      // MODAL: Lá»ŠCH Sá»¬ ÄÆ N HÃ€NG ÄÃƒ Äáº¶T Cá»¦A KHÃCH HÃ€NG
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
            <div style="font-size: 24px; margin-bottom: 8px;">â³</div>
            <p style="font-size: 13px;">Äang táº£i lá»‹ch sá»­ Ä‘Æ¡n hÃ ng cá»§a báº¡n...</p>
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

        // Fallback tá»« localStorage
        const localOrders = JSON.parse(
          localStorage.getItem("JML_ORDERS") || "[]",
        );
        renderUserOrders(
          localOrders.map((o) => ({
            order_key: o.key,
            id_display: o.id,
            created_at: o.time || "HÃ´m nay",
            shop_name: o.shopName,
            status: o.status || "preparing",
            escrow_badge: o.escrowBadge || "ðŸ“¦ Shop Ä‘ang chuáº©n bá»‹ Ä‘Æ¡n",
            total: o.total,
            items: o.items || [],
          })),
        );
      }

      function renderUserOrders(orders) {
        const container = document.getElementById("userOrdersListBody");
        const countBadge = document.getElementById("userOrdersTotalCount");
        if (countBadge) countBadge.textContent = `${orders.length} Ä‘Æ¡n hÃ ng`;

        if (!container) return;

        if (!orders || orders.length === 0) {
          container.innerHTML = `
            <div style="padding: 48px 20px; text-align: center; color: #64748b; background: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1;">
              <div style="font-size: 36px; margin-bottom: 10px;">ðŸ“¦</div>
              <p style="font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 4px;">Báº¡n chÆ°a cÃ³ Ä‘Æ¡n hÃ ng nÃ o</p>
              <p style="font-size: 12px; color: #94a3b8;">HÃ£y dáº¡o má»™t vÃ²ng trang chá»§ vÃ  chá»n mÃ³n Ä‘á»“ yÃªu thÃ­ch Ä‘á»ƒ Ä‘áº·t hÃ ng ngay!</p>
            </div>
          `;
          return;
        }

        container.innerHTML = orders
          .map((o) => {
            // Tráº¡ng thÃ¡i theo phong cÃ¡ch Shopee
            let badgeText = o.escrow_badge || "ðŸ“¦ Shop Ä‘ang chuáº©n bá»‹ Ä‘Æ¡n";
            let badgeBg = "#fffbeb";
            let badgeColor = "#d97706";
            let badgeBorder = "#fde68a";

            if (o.status === "shipping" || badgeText.includes("váº­n chuyá»ƒn")) {
              badgeText = "ðŸšš Äang váº­n chuyá»ƒn";
              badgeBg = "#eff6ff";
              badgeColor = "#2563eb";
              badgeBorder = "#bfdbfe";
            } else if (
              o.status === "delivered" ||
              o.status === "released" ||
              badgeText.includes("giao hÃ ng") ||
              badgeText.includes("hoÃ n táº¥t")
            ) {
              badgeText = "âœ“ ÄÃ£ giao hÃ ng thÃ nh cÃ´ng";
              badgeBg = "#ecfdf5";
              badgeColor = "#059669";
              badgeBorder = "#a7f3d0";
            } else if (
              o.status === "dispute" ||
              badgeText.includes("tranh cháº¥p")
            ) {
              badgeText = "âš ï¸ Äang xá»­ lÃ½ khiáº¿u náº¡i";
              badgeBg = "#fef2f2";
              badgeColor = "#dc2626";
              badgeBorder = "#fecaca";
            } else {
              badgeText = "ðŸ“¦ Shop Ä‘ang chuáº©n bá»‹ Ä‘Æ¡n";
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
                  <span style="color: #cbd5e1;">â€¢</span>
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
                      <p style="font-size: 11px; color: #64748b; margin: 2px 0 0 0;">${it.variant || "ChÃ­nh hÃ£ng"} â€¢ Sá»‘ lÆ°á»£ng: <strong>x${it.qty || 1}</strong></p>
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
                    <span style="color: #64748b; margin-right: 6px;">Tá»•ng thanh toÃ¡n:</span>
                    <strong style="font-size: 15px; color: #ea580c; font-weight: 800;">${o.total}</strong>
                  </div>
                  <!-- Duy Nháº¥t 1 NÃºt XÃ¡c Nháº­n á»ž ChÃ¢n ÄÆ¡n HÃ ng -->
                  ${
                    o.status === "shipping" ||
                    (o.escrow_badge && o.escrow_badge.includes("váº­n chuyá»ƒn"))
                      ? `
                    <button onclick="handleUserConfirmReceived(this, '${o.order_key}')" style="padding: 7px 16px; border-radius: 8px; border: none; background: #16a34a; color: #fff; font-weight: 700; font-size: 12px; cursor: pointer; box-shadow: 0 2px 6px rgba(22,163,74,0.3); display: inline-flex; align-items: center; gap: 5px;">
                      <span>âœ“ ÄÃ£ Nháº­n ÄÆ°á»£c HÃ ng</span>
                    </button>
                  `
                      : o.status === "delivered" || o.status === "released"
                        ? `
                    <span style="padding: 4px 10px; border-radius: 6px; background: #ecfdf5; color: #15803d; font-weight: 700; font-size: 11px; border: 1px solid #bbf7d0;">
                      âœ“ ÄÃ£ nháº­n hÃ ng thÃ nh cÃ´ng
                    </span>
                  `
                        : `
                    <span style="padding: 4px 10px; border-radius: 6px; background: #fef3c7; color: #b45309; font-weight: 600; font-size: 11px;">
                      Chá» shop gá»­i hÃ ng
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
          : document.querySelector(
              `.user-order-card[data-order-key="${orderKey}"]`,
            );

        // Cáº­p nháº­t tráº¡ng thÃ¡i trá»±c tiáº¿p trÃªn giao diá»‡n tá»©c thÃ¬ (KHÃ”NG reload láº¡i modal)
        if (btn) {
          btn.outerHTML = `
            <span style="padding: 5px 12px; border-radius: 8px; background: #ecfdf5; color: #15803d; font-weight: 700; font-size: 12px; border: 1px solid #bbf7d0; display: inline-flex; align-items: center; gap: 4px;">
              <span>âœ“ ÄÃ£ nháº­n hÃ ng thÃ nh cÃ´ng</span>
            </span>
          `;
        }

        if (card) {
          const badge = card.querySelector(".order-status-badge");
          if (badge) {
            badge.textContent = "âœ“ ÄÃ£ giao hÃ ng thÃ nh cÃ´ng";
            badge.style.background = "#ecfdf5";
            badge.style.color = "#059669";
            badge.style.border = "1px solid #a7f3d0";
          }
        }

        showToast("ThÃ nh cÃ´ng", "Báº¡n Ä‘Ã£ xÃ¡c nháº­n nháº­n hÃ ng thÃ nh cÃ´ng!");
        window.dispatchEvent(new Event("storage"));

        // Gá»­i lá»‡nh ngáº§m Ä‘áº¿n FastAPI Backend
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
        <div class="toast-icon">âœ“</div>
        <div class="toast-content">
          <div class="toast-title">${title}</div>
          <div class="toast-msg">${message}</div>
        </div>
        <button style="border: none; background: transparent; color: #94a3b8; font-size: 14px; cursor: pointer; padding: 2px 6px;">âœ•</button>
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
      // 8. TÃŒM KIáº¾M THÃ”NG MINH
      // --------------------------------------------------------------------------
      function handleSearch() {
        const input = document.getElementById("searchInput");
        const query = (input ? input.value : "").trim().toLowerCase();

        // Äáº£m báº£o Ä‘ang á»Ÿ view home khi tÃ¬m kiáº¿m
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
                <div style="font-size: 36px; margin-bottom: 12px;">ðŸ”</div>
                <h3 style="font-size: 16px; font-weight: 700; color: var(--secondary);">KhÃ´ng tÃ¬m tháº¥y sáº£n pháº©m phÃ¹ há»£p</h3>
                <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">Thá»­ tÃ¬m vá»›i tá»« khÃ³a: "ipad", "tai nghe", "Ä‘á»“ng há»“", "vÃ­ da", "loa"...</p>
              </div>
            `;
          } else {
            container.innerHTML = matched
              .map((product) => {
                const mainImg = product.images
                  ? product.images[0]
                  : product.image;
                return `
              <div class="product-card" onclick="openProductDetail(${product.id})">
                ${createCarouselMarkup(product)}
                <div class="product-body">
                  <h3 class="product-title" title="${product.title}">${product.title}</h3>
                  <div class="product-meta">
                    <span class="rating-stars">â˜… ${product.rating}</span>
                    <span>â€¢ ÄÃ£ bÃ¡n ${product.soldCount}</span>
                  </div>
                  <div class="price-row">
                    <span class="current-price">${formatCurrency(product.price)}</span>
                    <span class="original-price">${formatCurrency(product.originalPrice)}</span>
                  </div>
                  <div style="margin-top: auto;">
                    <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${product.title.replace(/'/g, "\\'")}', ${product.price}, '${mainImg}', '${(product.shopName || "").replace(/'/g, "\\'")}')">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                      ThÃªm VÃ o Giá»
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
        showToast("TÃ¬m kiáº¿m", `TÃ¬m tháº¥y ${matched.length} sáº£n pháº©m phÃ¹ há»£p`);
      }

      function applyQuickSearch(term) {
        const input = document.getElementById("searchInput");
        if (input) {
          input.value = term;
          handleSearch();
        }
      }

      // Khá»Ÿi cháº¡y render ban Ä‘áº§u vÃ  Ä‘á»“ng bá»™ dá»¯ liá»‡u tá»« FastAPI + SQL
      loadProductsFromFastAPI();

      // Kiá»ƒm tra URL hash khi má»Ÿ trang láº§n Ä‘áº§u
      if (window.location.hash.startsWith("#product/")) {
        checkUrlHash();
      }
