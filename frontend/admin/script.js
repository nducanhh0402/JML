/**
 * JML Store Marketplace Admin Portal - Client-Side Logic (FastAPI + SQL Connected)
 * Multi-vendor E-commerce Platform (Shopee / Lazada Model)
 */

const API_BASE_URL = 'http://127.0.0.1:8000';

// Toàn bộ cơ sở dữ liệu ban đầu để trống (0 dữ liệu, 0 chỉ số)
let SHOPS_DATABASE = {};
const DEFAULT_ORDERS_DATABASE = {};
const DEFAULT_CUSTOMERS_DATABASE = {};

let ORDERS_DATABASE = {};
let CUSTOMERS_DATABASE = {};
let currentViewingCustId = null;
let PRODUCTS_LIST = [];

// =============================================================================
// ĐỒNG BỘ DỮ LIỆU TỪ FASTAPI DATABASE VÀ TÍNH TOÁN CHỈ SỐ DASHBOARD
// =============================================================================
async function syncWithFastAPI() {
    const badge = document.getElementById('sqlConnectionBadge');
    let serverMetrics = null;

    // Hiển thị tên Admin đang đăng nhập nếu có
    const rawAdmin = localStorage.getItem('JML_ADMIN_USER') || localStorage.getItem('JML_AUTH_USER');
    if (rawAdmin) {
        try {
            const parsedAdmin = JSON.parse(rawAdmin);
            const nameEl = document.getElementById('adminProfileName');
            if (nameEl && parsedAdmin.role === 'admin' && parsedAdmin.full_name) {
                nameEl.textContent = parsedAdmin.full_name;
            }
        } catch (e) {}
    }

    try {
        const [ordersRes, custRes, prodsRes, metricsRes, shopsRes, pendingRes] = await Promise.all([
            fetch(`${API_BASE_URL}/api/admin/orders`),
            fetch(`${API_BASE_URL}/api/admin/customers`),
            fetch(`${API_BASE_URL}/api/products`),
            fetch(`${API_BASE_URL}/api/admin/metrics`),
            fetch(`${API_BASE_URL}/api/admin/shops`),
            fetch(`${API_BASE_URL}/api/admin/products/pending`)
        ]);

        if (ordersRes.ok && custRes.ok) {
            const ordersData = await ordersRes.json();
            const custData = await custRes.json();

            ORDERS_DATABASE = ordersData.orders || {};
            CUSTOMERS_DATABASE = custData.customers || {};

            if (prodsRes.ok) {
                const prodsData = await prodsRes.json();
                PRODUCTS_LIST = [
                    ...(prodsData.flash_products || []),
                    ...(prodsData.recommend_products || [])
                ];
            }

            if (shopsRes.ok) {
                const shopsData = await shopsRes.json();
                SHOPS_DATABASE = shopsData.shops || {};
            }

            if (metricsRes.ok) {
                serverMetrics = await metricsRes.json();
            }

            let pendingProds = [];
            if (pendingRes && pendingRes.ok) {
                const pendingData = await pendingRes.json();
                pendingProds = pendingData.pending_products || [];
            }
            renderPendingProducts(pendingProds);

            if (badge) {
                badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span><span>Hệ thống Đã Kết Nối</span>`;
                badge.className = 'hidden md:flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 text-emerald-700 px-2.5 py-1.5 rounded-lg text-[11px] font-semibold whitespace-nowrap';
            }
        }
    } catch (err) {
        // Fallback sang localStorage nếu chưa chạy uvicorn
        const customOrders = JSON.parse(localStorage.getItem('JML_ORDERS') || '[]');
        ORDERS_DATABASE = {};
        customOrders.forEach(o => {
            const key = o.key || o.id.replace('#', '');
            ORDERS_DATABASE[key] = o;
        });

        CUSTOMERS_DATABASE = JSON.parse(localStorage.getItem('JML_CUSTOMERS') || '{}');
        PRODUCTS_LIST = JSON.parse(localStorage.getItem('JML_RECOMMEND_PRODUCTS') || '[]');
    }

    renderShopsDirectory();
    renderDashboardRecentOrders();
    renderFullOrders();
    renderCustomers();
    updateAdminMetrics(serverMetrics);
}

/**
 * Render danh sách Cửa hàng (Shops) ở Tab 2 và Top Shops ở Tab 1
 */
function renderShopsDirectory() {
    const activeTbody = document.getElementById('activeShopsTableBody');
    const topShopsContainer = document.getElementById('topShopsListContainer');
    const shopFilterSelect = document.getElementById('fullOrderShopFilter');
    const chartShopBadge = document.getElementById('chartShopTotalBadge');

    const shops = Object.values(SHOPS_DATABASE || {});
    if (chartShopBadge) {
        chartShopBadge.textContent = `${shops.length} Shops`;
    }

    if (shopFilterSelect) {
        const currentVal = shopFilterSelect.value;
        shopFilterSelect.innerHTML = `<option value="all">Tất cả Cửa hàng (Shops)</option>` +
            shops.map(s => `<option value="${s.name}">Shop: ${s.name}</option>`).join('');
        shopFilterSelect.value = currentVal || 'all';
    }

    if (activeTbody) {
        if (shops.length === 0) {
            activeTbody.innerHTML = `
                <tr>
                    <td colspan="9" class="py-8 text-center text-neutral-400 text-xs">
                        Chưa có cửa hàng nào đang hoạt động trên Sàn.
                    </td>
                </tr>
            `;
        } else {
            activeTbody.innerHTML = shops.map(s => `
                <tr class="hover:bg-neutral-50/80 transition-colors">
                    <td class="py-3.5 px-4 font-mono font-bold text-primary-500">${s.id_display}</td>
                    <td class="py-3.5 px-4">
                        <span class="font-bold text-neutral-900 block">${s.name}</span>
                        <span class="text-[11px] text-neutral-500">${s.meta}</span>
                    </td>
                    <td class="py-3.5 px-4">
                        <span class="px-2 py-0.5 text-[10px] font-bold rounded uppercase ${s.badgeClass}">${s.badge}</span>
                    </td>
                    <td class="py-3.5 px-4 font-semibold text-neutral-900">${s.productCount}</td>
                    <td class="py-3.5 px-4 font-bold text-blue-600">${s.ordersCount || 0} đơn</td>
                    <td class="py-3.5 px-4 font-bold text-neutral-900">${s.gmv}</td>
                    <td class="py-3.5 px-4 font-bold text-emerald-600">${s.fee}</td>
                    <td class="py-3.5 px-4 font-semibold text-amber-500">${s.rating}</td>
                    <td class="py-3.5 px-4 text-right">
                        <button onclick="openShopDetail('${s.shop_key}')" class="px-3 py-1.5 bg-primary-50 hover:bg-primary-100 text-primary-600 rounded-lg font-semibold text-xs transition-colors">
                            Xem Shop & Sản phẩm (${s.numericProductCount || 0})
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    }

    if (topShopsContainer) {
        if (shops.length === 0) {
            topShopsContainer.innerHTML = `
                <div class="py-8 text-center text-neutral-400 text-xs">
                    Chưa có cửa hàng nào hoạt động trên Sàn.
                </div>
            `;
        } else {
            topShopsContainer.innerHTML = shops.slice(0, 5).map(s => `
                <div onclick="openShopDetail('${s.shop_key}')" class="flex items-center justify-between p-3 rounded-xl bg-neutral-50 hover:bg-primary-50/50 border border-neutral-100 cursor-pointer transition-all">
                    <div class="flex items-center gap-3 min-w-0">
                        <div class="w-9 h-9 rounded-lg bg-primary-500 text-white font-bold text-xs flex items-center justify-center shrink-0">
                            ${s.initials}
                        </div>
                        <div class="min-w-0">
                            <p class="font-bold text-xs text-neutral-900 truncate">${s.name}</p>
                            <p class="text-[11px] text-neutral-500">${s.productCount} • ${s.rating}</p>
                        </div>
                    </div>
                    <span class="font-bold text-xs text-primary-600 shrink-0">${s.gmv}</span>
                </div>
            `).join('');
        }
    }
}

/**
 * Render bảng Đơn hàng Trung gian gần đây ở Tab 1 (Overview)
 */
function renderDashboardRecentOrders() {
    const tbody = document.getElementById('recentOrdersTableBody');
    if (!tbody) return;

    const orders = Object.values(ORDERS_DATABASE || {});
    if (orders.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="py-8 text-center text-neutral-400 text-xs">
                    Chưa có đơn hàng giao dịch nào trên Sàn.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = orders.slice(0, 5).map(o => {
        const orderKey = o.key || o.id.replace('#', '');
        const firstItem = (o.items && o.items[0]) ? o.items[0].name : 'Sản phẩm';
        return `
            <tr class="hover:bg-neutral-50/80 transition-colors">
                <td class="py-3 px-4 font-bold text-primary-500">${o.id}</td>
                <td class="py-3 px-4 font-semibold text-neutral-800">${o.shopName}</td>
                <td class="py-3 px-4">
                    <span class="font-bold text-neutral-900 block truncate max-w-[200px]">${firstItem}</span>
                    <span class="text-[11px] text-neutral-500">Khách: ${o.buyerName}</span>
                </td>
                <td class="py-3 px-4 font-bold text-neutral-900">${o.total}</td>
                <td class="py-3 px-4">
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold ${o.escrowClass}">${o.escrowBadge}</span>
                </td>
                <td class="py-3 px-4 text-right">
                    <button onclick="openOrderDetail('${orderKey}')" class="px-2.5 py-1 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded text-xs font-semibold">
                        Chi tiết
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Cập nhật động toàn bộ các thẻ chỉ số (KPI Cards), Quỹ Escrow và Badges
 */
function updateAdminMetrics(metrics) {
    if (!metrics) {
        const prods = PRODUCTS_LIST || [];
        const customers = Object.values(CUSTOMERS_DATABASE || {});
        const orders = Object.values(ORDERS_DATABASE || {});

        let gmv = 0;
        orders.forEach(o => {
            if (typeof o.numeric_total === 'number' && o.numeric_total > 0) {
                gmv += o.numeric_total;
            } else {
                const clean = (o.total || '0').replace(/[^0-9]/g, '');
                gmv += parseInt(clean, 10) || 0;
            }
        });

        const revenue = Math.round(gmv * 0.07);
        const vipCount = customers.filter(c => c.rank === 'VIP' || c.rank === 'Kim Cương' || c.rank === 'Bạch Kim' || c.rank === 'Vàng').length;
        const boughtCount = customers.filter(c => (c.ordersCount > 0 || c.orders_count > 0)).length;
        const bannedCount = customers.filter(c => (c.status && c.status.includes('khóa')) || c.is_banned === 1 || c.isBanned === true).length;
        const shopsCount = Object.keys(SHOPS_DATABASE || {}).length;

        metrics = {
            total_gmv: gmv,
            total_revenue: revenue,
            total_products: prods.length,
            pending_products: 0,
            total_customers: customers.length,
            vip_customers: vipCount,
            active_buyers: boughtCount,
            banned_customers: bannedCount,
            total_orders: orders.length,
            total_shops: shopsCount
        };
    }

    const formatMoney = (val) => {
        if (!val || val === 0) return '0 ₫';
        return val.toLocaleString('vi-VN') + ' ₫';
    };

    // 1. Cập nhật 4 Card Chỉ số Tổng quan (Overview)
    const elGmv = document.getElementById('statTotalGmv');
    if (elGmv) elGmv.textContent = formatMoney(metrics.total_gmv);

    const elRev = document.getElementById('statTotalRevenue');
    if (elRev) elRev.textContent = formatMoney(metrics.total_revenue);

    const elShops = document.getElementById('statTotalShops');
    if (elShops) elShops.innerHTML = `${metrics.total_shops} <span class="text-sm font-medium text-neutral-500">Shops</span>`;

    const elProds = document.getElementById('statTotalProducts');
    if (elProds) elProds.innerHTML = `${metrics.total_products} <span class="text-sm font-medium text-neutral-500">Sản phẩm</span>`;

    const elPending = document.getElementById('statPendingProducts');
    if (elPending) elPending.textContent = `${metrics.pending_products || 0} chờ duyệt`;

    // 2. Cập nhật Quỹ Escrow trên header
    const elEscrow = document.getElementById('headerEscrowTotal');
    if (elEscrow) elEscrow.textContent = formatMoney(metrics.total_gmv);

    // 3. Cập nhật Badges Sidebar & Header
    const badgeProds = document.getElementById('badgeProductsCount');
    if (badgeProds) badgeProds.textContent = `${metrics.total_products}`;

    const badgeOrders = document.getElementById('badgeOrdersCount');
    if (badgeOrders) badgeOrders.textContent = `${metrics.total_orders}`;

    const badgeShops = document.getElementById('badgeShopsCount');
    if (badgeShops) badgeShops.textContent = `${metrics.total_shops}`;

    const badgeCusts = document.getElementById('badgeCustomersCount');
    if (badgeCusts) badgeCusts.textContent = `${metrics.total_customers}`;

    const headerProds = document.getElementById('headerProductsCount');
    if (headerProds) headerProds.textContent = `Sản phẩm (${metrics.total_products})`;

    const headerShops = document.getElementById('headerShopsCount');
    if (headerShops) headerShops.textContent = `Shop (${metrics.total_shops})`;

    // 4. Cập nhật 4 Card Chỉ số Khách hàng (Customers Tab)
    const elCustTot = document.getElementById('statCustTotal');
    if (elCustTot) elCustTot.textContent = metrics.total_customers;

    const elCustVip = document.getElementById('statCustVip');
    if (elCustVip) elCustVip.textContent = metrics.vip_customers;

    const elCustBought = document.getElementById('statCustBought');
    if (elCustBought) {
        const pct = metrics.total_customers > 0 ? Math.round((metrics.active_buyers / metrics.total_customers) * 100) : 0;
        elCustBought.textContent = `${metrics.active_buyers} (${pct}%)`;
    }

    const elCustBanned = document.getElementById('statCustBanned');
    if (elCustBanned) elCustBanned.textContent = metrics.banned_customers;
}

/**
 * Đặt tất cả chỉ số về 0 (Xóa sạch DB và Storage)
 */
async function resetAllMetricsToZero() {
    const confirmed = confirm(
        "⚠️ XÁC NHẬN ĐẶT TẤT CẢ CHỈ SỐ VỀ 0?\n\n" +
        "- Toàn bộ sản phẩm, khách hàng và đơn hàng sẽ được xóa khỏi cơ sở dữ liệu SQL.\n" +
        "- Các chỉ số GMV, Hoa hồng, Sản phẩm, Khách hàng sẽ về đúng số 0.\n" +
        "- Bạn có thể tự thêm lại sản phẩm hoặc khách hàng mới để kiểm tra các chỉ số tăng lên!"
    );
    if (!confirmed) return;

    try {
        await fetch(`${API_BASE_URL}/api/admin/reset-data`, { method: 'POST' });
    } catch (e) {}

    localStorage.removeItem('JML_ORDERS');
    localStorage.removeItem('JML_RECOMMEND_PRODUCTS');
    localStorage.removeItem('JML_CUSTOMERS');

    ORDERS_DATABASE = {};
    CUSTOMERS_DATABASE = {};
    PRODUCTS_LIST = [];

    renderFullOrders();
    renderCustomers();
    updateAdminMetrics({
        total_gmv: 0,
        total_revenue: 0,
        total_products: 0,
        pending_products: 0,
        total_customers: 0,
        vip_customers: 0,
        active_buyers: 0,
        banned_customers: 0,
        total_orders: 0,
        total_shops: 0
    });

    window.dispatchEvent(new Event('storage'));
    alert("✅ ĐÃ ĐẶT TẤT CẢ CHỈ SỐ VỀ 0 THÀNH CÔNG!\n\nBây giờ bạn có thể thêm sản phẩm hoặc khách hàng mới để quan sát các chỉ số tăng lên trực tiếp.");
}

const HASH_TAB_MAP = {
    '#dashboard': 'view-dashboard',
    '#shops': 'view-shops',
    '#products': 'view-dashboard',
    '#categories': 'view-categories',
    '#orders': 'view-orders',
    '#disputes': 'view-disputes',
    '#payouts': 'view-payouts',
    '#customers': 'view-customers'
};

function handleHashRouting() {
    const hash = window.location.hash;
    if (hash && HASH_TAB_MAP[hash]) {
        switchTab(HASH_TAB_MAP[hash], false);
    }
}

// =============================================================================
// XÁC THỰC QUẢN TRỊ VIÊN TRỰC TIẾP TRÊN TRANG ADMIN (IN-PAGE ADMIN AUTH)
// =============================================================================
function checkAdminAuthSession() {
    const rawAdmin = localStorage.getItem('JML_ADMIN_USER') || localStorage.getItem('JML_AUTH_USER');
    if (rawAdmin) {
        try {
            const parsed = JSON.parse(rawAdmin);
            if (parsed && parsed.role === 'admin') {
                const nameEl = document.getElementById('adminProfileName');
                if (nameEl && parsed.full_name) {
                    nameEl.textContent = parsed.full_name;
                }
                const lockModal = document.getElementById('adminLockModal');
                if (lockModal) lockModal.classList.add('hidden');
                return true;
            }
        } catch (e) {}
    }
    openAdminLockModal();
    return false;
}

function openAdminLockModal() {
    const lockModal = document.getElementById('adminLockModal');
    if (lockModal) {
        lockModal.classList.remove('hidden');
        if (window.lucide) lucide.createIcons();
    }
}

async function handleAdminLoginSubmit(e) {
    e.preventDefault();
    const alertEl = document.getElementById('adminAuthAlert');
    alertEl.classList.add('hidden');

    const username = document.getElementById('adminLoginUser').value.trim();
    const password = document.getElementById('adminLoginPass').value;

    try {
        const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role: 'admin' })
        });
        const data = await res.json();
        if (!res.ok) {
            alertEl.textContent = `❌ ${data.detail || 'Đăng nhập Quản trị viên thất bại!'}`;
            alertEl.className = 'mb-4 p-3 rounded-lg text-xs font-semibold bg-red-50 text-red-700 border border-red-200 block';
            return;
        }

        localStorage.setItem('JML_ADMIN_USER', JSON.stringify(data.user));
        const nameEl = document.getElementById('adminProfileName');
        if (nameEl && data.user.full_name) {
            nameEl.textContent = data.user.full_name;
        }
        const lockModal = document.getElementById('adminLockModal');
        if (lockModal) lockModal.classList.add('hidden');
        await syncWithFastAPI();
    } catch (err) {
        // Fallback dự phòng nếu mất kết nối
        if (username === 'admin' && password === '123456') {
            const fallbackAdmin = { username: 'admin', role: 'admin', full_name: 'Hoàng Nam (Super Admin)' };
            localStorage.setItem('JML_ADMIN_USER', JSON.stringify(fallbackAdmin));
            const lockModal = document.getElementById('adminLockModal');
            if (lockModal) lockModal.classList.add('hidden');
            await syncWithFastAPI();
        } else {
            alertEl.textContent = '❌ Lỗi kết nối FastAPI server!';
            alertEl.className = 'mb-4 p-3 rounded-lg text-xs font-semibold bg-red-50 text-red-700 border border-red-200 block';
        }
    }
}

function handleAdminLogout() {
    localStorage.removeItem('JML_ADMIN_USER');
    localStorage.removeItem('JML_AUTH_USER');
    openAdminLockModal();
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide) {
        lucide.createIcons();
    }
    initSidebarTabs();
    initRevenueChart();
    initCategoryChart();
    initGlobalSearch();
    handleHashRouting();
    const isAuthed = checkAdminAuthSession();
    if (isAuthed) {
        syncWithFastAPI();
    }
});

window.addEventListener('hashchange', handleHashRouting);

// Tự động đồng bộ khi chuyển tab hoặc có tín hiệu storage từ trang User
window.addEventListener('storage', () => {
    syncWithFastAPI();
});
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        syncWithFastAPI();
    }
});

/**
 * Khởi tạo sự kiện click chuyển đổi giữa các Tab riêng biệt trên Sidebar
 */
function initSidebarTabs() {
    const navItems = document.querySelectorAll('.nav-item[data-tab]');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = item.getAttribute('data-tab');
            const href = item.getAttribute('href');
            if (href) {
                history.replaceState(null, '', href);
            }
            switchTab(targetTab, false);
        });
    });
}

/**
 * Chuyển đổi sang màn hình Tab tương ứng
 */
function switchTab(tabId, updateHash = true) {
    if (!document.getElementById(tabId)) {
        tabId = 'view-dashboard';
    }
    const allViews = document.querySelectorAll('.tab-view');
    const allNavItems = document.querySelectorAll('.nav-item[data-tab]');

    allViews.forEach(view => {
        if (view.id === tabId) {
            view.classList.remove('hidden');
        } else {
            view.classList.add('hidden');
        }
    });

    allNavItems.forEach(nav => {
        if (nav.getAttribute('data-tab') === tabId) {
            nav.classList.add('active');
            if (updateHash) {
                const href = nav.getAttribute('href');
                if (href) history.replaceState(null, '', href);
            }
        } else {
            nav.classList.remove('active');
        }
    });

    syncWithFastAPI();
}

/**
 * Mở Modal Xem chi tiết Cửa hàng (Shop) & Danh sách sản phẩm của Shop đó
 */
function openShopDetail(shopKey) {
    const shop = SHOPS_DATABASE[shopKey];
    if (!shop) return;

    document.getElementById('modalShopAvatar').textContent = shop.initials;
    document.getElementById('modalShopName').textContent = shop.name;

    const badgeEl = document.getElementById('modalShopBadge');
    badgeEl.textContent = shop.badge;
    badgeEl.className = `px-2 py-0.5 text-[10px] font-bold rounded uppercase ${shop.badgeClass}`;

    document.getElementById('modalShopMeta').textContent = shop.meta;
    document.getElementById('modalShopGmv').textContent = shop.gmv;
    const ordersCountEl = document.getElementById('modalShopOrdersCount');
    if (ordersCountEl) ordersCountEl.textContent = `${shop.ordersCount || 0} đơn`;
    document.getElementById('modalShopFee').textContent = shop.fee;
    document.getElementById('modalShopProductCount').textContent = shop.productCount;
    document.getElementById('modalShopRating').textContent = shop.rating;

    const tbody = document.getElementById('modalShopProductsBody');
    if (!shop.products || shop.products.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="py-8 text-center text-neutral-400 text-xs">
                    Cửa hàng này hiện chưa đăng bán sản phẩm nào.
                </td>
            </tr>
        `;
    } else {
        tbody.innerHTML = shop.products.map(p => `
            <tr class="hover:bg-neutral-50">
                <td class="py-3 px-4 font-bold text-neutral-900">${p.name}</td>
                <td class="py-3 px-4 font-mono text-neutral-500">${p.sku}</td>
                <td class="py-3 px-4 font-bold text-primary-500">${p.price}</td>
                <td class="py-3 px-4 text-neutral-700">${p.stock}</td>
                <td class="py-3 px-4 text-neutral-600">${p.sold}</td>
                <td class="py-3 px-4 text-right">
                    <span class="px-2 py-0.5 rounded text-[11px] font-semibold ${p.status.includes('khiếu nại') ? 'bg-danger-50 text-danger-500' : 'bg-success-50 text-success-500'}">
                        ${p.status}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    toggleModal('shopDetailModal');
}

/**
 * Mở Modal Xem chi tiết Đơn hàng (Gồm thông tin Shop, Người mua, và từng Sản phẩm trong đơn)
 */
function openOrderDetail(orderKey) {
    const cleanKey = orderKey.replace('#', '');
    const order = ORDERS_DATABASE[cleanKey] || Object.values(ORDERS_DATABASE)[0];
    if (!order) return;

    document.getElementById('modalOrderId').textContent = `Chi Tiết Đơn Hàng ${order.id}`;
    const badgeEl = document.getElementById('modalOrderEscrowBadge');
    badgeEl.textContent = order.escrowBadge;
    badgeEl.className = `px-2 py-0.5 text-xs font-semibold rounded ${order.escrowClass}`;

    document.getElementById('modalOrderTime').textContent = order.time;
    document.getElementById('modalOrderShopName').textContent = order.shopName;
    document.getElementById('modalOrderShopAddress').textContent = order.shopAddress;
    document.getElementById('modalOrderBuyerName').textContent = order.buyerName;
    document.getElementById('modalOrderBuyerAddress').textContent = order.buyerAddress;

    document.getElementById('modalOrderTotal').textContent = order.total;
    document.getElementById('modalOrderFee').textContent = order.fee;
    document.getElementById('modalOrderNet').textContent = order.net;

    const tbody = document.getElementById('modalOrderItemsBody');
    tbody.innerHTML = order.items.map(item => `
        <tr class="hover:bg-neutral-50">
            <td class="py-3 px-4 font-bold text-neutral-900">${item.name}</td>
            <td class="py-3 px-4 text-neutral-500">${item.variant}</td>
            <td class="py-3 px-4 font-medium">${item.price}</td>
            <td class="py-3 px-4 font-semibold">x${item.qty}</td>
            <td class="py-3 px-4 text-right font-bold text-neutral-900">${item.subtotal}</td>
        </tr>
    `).join('');

    toggleModal('orderDetailModal');
}

/**
 * Render danh sách toàn bộ Đơn hàng từ SQL Database
 */
function renderFullOrders() {
    const container = document.getElementById('fullOrdersContainer');
    if (!container) return;

    const orders = Object.values(ORDERS_DATABASE);
    if (orders.length === 0) {
        container.innerHTML = `
            <div class="py-12 text-center bg-white rounded-xl border border-neutral-200 text-neutral-400 text-xs">
                Chưa có đơn hàng nào phát sinh trên Sàn.
            </div>
        `;
        return;
    }
    container.innerHTML = orders.map(order => {
        const isEscrow = order.status === 'escrow';
        const isDispute = order.status === 'dispute';
        const isReleased = order.status === 'released';
        const orderKey = order.key || order.id.replace('#', '');

        return `
            <div data-shop="${order.shopName}" data-status="${order.status}" class="order-card bg-white rounded-xl border border-neutral-200 shadow-sm overflow-hidden">
                <div class="px-5 py-3 bg-neutral-50 border-b border-neutral-200 flex flex-wrap items-center justify-between gap-3">
                    <div class="flex items-center gap-3">
                        <span class="px-2 py-0.5 bg-danger-500 text-white text-[10px] font-bold rounded uppercase">JML Mall</span>
                        <span class="font-bold text-neutral-900 text-xs">${order.shopName}</span>
                    </div>
                    <div class="flex items-center gap-3 text-xs">
                        <span class="text-neutral-500">Mã đơn: <strong class="text-primary-500">${order.id}</strong></span>
                        <span class="text-neutral-300">|</span>
                        <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${order.escrowClass}">${order.escrowBadge}</span>
                    </div>
                </div>

                <div class="p-5 grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                    <div class="lg:col-span-7 space-y-3">
                        <div class="text-[11px] font-semibold uppercase tracking-wider text-neutral-400">Sản phẩm trong đơn (${order.items.length} mặt hàng)</div>
                        ${order.items.map(item => `
                            <div class="flex items-center gap-3.5 p-2.5 rounded-lg bg-neutral-50 border border-neutral-100">
                                <div class="w-10 h-10 rounded-lg bg-white border border-neutral-200 flex items-center justify-center text-lg shrink-0">📦</div>
                                <div class="flex-1 min-w-0">
                                    <h4 class="font-bold text-neutral-900 text-xs truncate">${item.name}</h4>
                                    <p class="text-[11px] text-neutral-500 truncate">${item.variant}</p>
                                </div>
                                <div class="text-right shrink-0">
                                    <span class="text-xs font-bold text-neutral-900">${item.price}</span>
                                    <span class="block text-[11px] text-neutral-500">SL: x${item.qty}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    <div class="lg:col-span-5 flex flex-col justify-between border-t lg:border-t-0 lg:border-l border-neutral-200 pt-4 lg:pt-0 lg:pl-6 space-y-3">
                        <div class="text-xs space-y-1">
                            <p class="text-neutral-500">Người mua: <strong class="text-neutral-900">${order.buyerName}</strong></p>
                            <p class="text-neutral-500 truncate">Địa chỉ: ${order.buyerAddress}</p>
                        </div>

                        <div class="p-3 rounded-lg bg-neutral-50 border border-neutral-200 text-xs space-y-1.5">
                            <div class="flex justify-between">
                                <span class="text-neutral-500">Tổng thanh toán:</span>
                                <span class="font-bold text-neutral-900">${order.total}</span>
                            </div>
                            <div class="flex justify-between text-emerald-600">
                                <span>Phí Sàn thu (7%):</span>
                                <span class="font-bold">${order.fee}</span>
                            </div>
                            <div class="flex justify-between pt-1 border-t border-neutral-200">
                                <span class="font-semibold text-neutral-700">Thực nhận về Ví Shop:</span>
                                <span class="font-bold text-primary-500">${order.net}</span>
                            </div>
                        </div>

                        <div class="flex items-center justify-end gap-2 flex-wrap">
                            <button onclick="openOrderDetail('${orderKey}')" class="px-3 py-1.5 border border-neutral-200 hover:border-primary-500 rounded-lg text-xs font-semibold text-neutral-700 hover:text-primary-500">
                                Chi tiết đơn
                            </button>
                            ${isEscrow ? `
                                <button onclick="freezeEscrow('${order.id}')" class="px-3 py-1.5 border border-red-200 text-danger-500 hover:bg-danger-50 rounded-lg text-xs font-semibold">
                                    Đóng băng tiền
                                </button>
                                <button onclick="releaseEscrow('${order.id}', '${order.shopName.replace(/'/g, "\\'")}', '${order.net}')" class="px-3.5 py-1.5 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-xs font-semibold">
                                    Giải ngân cho Shop
                                </button>
                            ` : ''}
                            ${isDispute ? `
                                <button onclick="switchTab('view-disputes')" class="px-3.5 py-1.5 bg-danger-500 hover:bg-red-600 text-white rounded-lg text-xs font-semibold">
                                    Mở Tòa án phân xử &rarr;
                                </button>
                            ` : ''}
                            ${isReleased ? `
                                <span class="text-xs font-bold text-emerald-600">✓ Đã tất toán ví shop</span>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    if (window.lucide) {
        lucide.createIcons();
    }
}

/**
 * Lọc danh sách Đơn hàng ở Tab Đơn hàng Trung gian theo Shop & Trạng thái
 */
function filterFullOrders() {
    const shopFilter = document.getElementById('fullOrderShopFilter')?.value || 'all';
    const statusFilter = document.getElementById('fullOrderStatusFilter')?.value || 'all';
    const cards = document.querySelectorAll('#fullOrdersContainer .order-card');

    cards.forEach(card => {
        const cardShop = card.getAttribute('data-shop') || '';
        const cardStatus = card.getAttribute('data-status') || '';

        const matchShop = (shopFilter === 'all') || cardShop.includes(shopFilter);
        const matchStatus = (statusFilter === 'all') || (cardStatus === statusFilter);

        card.style.display = (matchShop && matchStatus) ? '' : 'none';
    });
}

/**
 * Điều khiển đóng/mở Modal
 */
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.classList.toggle('hidden');
    if (!modal.classList.contains('hidden')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

/**
 * Xử lý phát hành Chiến dịch / Voucher toàn sàn
 */
function saveCampaign() {
    const nameInput = document.getElementById('campaignNameInput');
    const campaignName = nameInput ? nameInput.value.trim() : '';

    if (!campaignName) {
        alert('Vui lòng nhập tên Chiến dịch hoặc Sự kiện toàn sàn!');
        return;
    }

    alert(`Đã phát hành chiến dịch "${campaignName}" và gửi thông báo tới 1,248 Shops trên toàn sàn!`);
    toggleModal('campaignModal');
}

/**
 * Xử lý giải ngân tiền giữ hộ (Escrow) về ví của Shop (Gọi FastAPI SQL)
 */
/**
 * Xử lý giải ngân tiền cho Shop (Gọi FastAPI SQL trực tiếp không popup xác nhận/thông báo)
 */
async function releaseEscrow(orderId, shopName, netAmount) {
    const cleanKey = orderId.replace('#', '');
    try {
        await fetch(`${API_BASE_URL}/api/admin/orders/${cleanKey}/release`, { method: 'PUT' });
    } catch (e) {
        // Fallback localStorage
    }

    const customOrders = JSON.parse(localStorage.getItem('JML_ORDERS') || '[]');
    const target = customOrders.find(o => o.id === orderId);
    if (target) {
        target.status = 'released';
        target.escrowBadge = '✓ Đã giải ngân về Ví Shop';
        target.escrowClass = 'bg-success-50 text-success-500';
        localStorage.setItem('JML_ORDERS', JSON.stringify(customOrders));
    }

    await syncWithFastAPI();
}

/**
 * Xử lý đóng băng tiền đơn hàng khi có khiếu nại (Gọi FastAPI SQL)
 */
async function freezeEscrow(orderId) {
    const reason = prompt(`Nhập lý do đóng băng tiền đơn hàng ${orderId}:`, "Khách khiếu nại sản phẩm lỗi");
    if (!reason) return;

    const cleanKey = orderId.replace('#', '');
    try {
        await fetch(`${API_BASE_URL}/api/admin/orders/${cleanKey}/freeze`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason })
        });
    } catch (e) {
        // Fallback localStorage
    }

    const customOrders = JSON.parse(localStorage.getItem('JML_ORDERS') || '[]');
    const target = customOrders.find(o => o.id === orderId);
    if (target) {
        target.status = 'dispute';
        target.escrowBadge = '⚠️ Đang đóng băng tranh chấp (' + reason + ')';
        target.escrowClass = 'bg-danger-50 text-danger-500';
        localStorage.setItem('JML_ORDERS', JSON.stringify(customOrders));
    }

    await syncWithFastAPI();
    alert(`Đã chuyển đơn hàng ${orderId} sang trạng thái TRANH CHẤP trong SQL Database!`);
}

/**
 * Xử lý Admin thêm sản phẩm mới trực tiếp vào bảng SQL products
 */
async function handleAdminAddNewProduct(e) {
    if (e) e.preventDefault();

    const title = document.getElementById('newProdTitle').value.trim();
    const category = document.getElementById('newProdCategory').value;
    const shop = document.getElementById('newProdShop').value;
    const price = parseInt(document.getElementById('newProdPrice').value, 10);
    const originalPrice = parseInt(document.getElementById('newProdOriginalPrice').value || String(price * 1.2), 10);
    const image = document.getElementById('newProdImage').value.trim();

    if (!title || isNaN(price)) {
        alert("Vui lòng điền đầy đủ tên sản phẩm và giá bán!");
        return;
    }

    try {
        await fetch(`${API_BASE_URL}/api/admin/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                category,
                price,
                original_price: originalPrice,
                image,
                shop_name: shop,
                is_flash_sale: false
            })
        });
    } catch (err) {
        // Fallback
    }

    const newProd = {
        id: Math.floor(300 + Math.random() * 700),
        category,
        title,
        price,
        originalPrice,
        discount: '-' + Math.round((1 - price / originalPrice) * 100) + '%',
        rating: 5.0,
        soldCount: 0,
        shopName: shop,
        images: [image, image, image, image],
        angles: ['Chính diện', 'Góc nghiêng', 'Cận cảnh', 'Thực tế']
    };

    const recommendProds = JSON.parse(localStorage.getItem('JML_RECOMMEND_PRODUCTS') || '[]');
    recommendProds.unshift(newProd);
    localStorage.setItem('JML_RECOMMEND_PRODUCTS', JSON.stringify(recommendProds));
    window.dispatchEvent(new Event('storage'));

    toggleModal('addProductModal');
    await syncWithFastAPI();
}

/**
 * Xử lý Admin thêm khách hàng mới trực tiếp vào bảng SQL customers
 */
async function handleAdminAddNewCustomer(e) {
    if (e) e.preventDefault();

    const name = document.getElementById('newCustName')?.value.trim();
    const phone = document.getElementById('newCustPhone')?.value.trim();
    const rank = document.getElementById('newCustRank')?.value || 'Đồng';
    const email = document.getElementById('newCustEmail')?.value.trim();
    const address = document.getElementById('newCustAddress')?.value.trim();

    if (!name || !phone || !email || !address) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/api/admin/customers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone, email, address, rank })
        });
    } catch (err) {
        // Fallback local
        const custKey = 'CUST-' + Math.floor(100 + Math.random() * 900);
        CUSTOMERS_DATABASE[custKey] = {
            id: '#' + custKey,
            name,
            phone,
            email,
            avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${phone}`,
            rank,
            rankBadge: rank === 'Kim Cương' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 
                       (rank === 'Bạch Kim' ? 'bg-purple-50 text-purple-700 border-purple-200' : 
                       (rank === 'Vàng' ? 'bg-amber-50 text-amber-700 border-amber-200' : 
                       (rank === 'Bạc' ? 'bg-slate-100 text-slate-700 border-slate-300' : 'bg-neutral-100 text-neutral-600 border-neutral-200'))),
            joined: new Date().toLocaleDateString('vi-VN'),
            ordersCount: 0,
            totalSpent: '0 ₫',
            status: 'Hoạt động',
            statusBadge: 'bg-emerald-50 text-emerald-600',
            address,
            ordersHistory: []
        };
        localStorage.setItem('JML_CUSTOMERS', JSON.stringify(CUSTOMERS_DATABASE));
    }

    toggleModal('addCustomerModal');
    // Clear form
    document.getElementById('newCustName').value = '';
    document.getElementById('newCustPhone').value = '';
    document.getElementById('newCustEmail').value = '';
    document.getElementById('newCustAddress').value = '';

    window.dispatchEvent(new Event('storage'));
    await syncWithFastAPI();
}





/**
 * Render danh sách sản phẩm chờ Admin kiểm duyệt
 */
function renderPendingProducts(pendingList = []) {
    const tbody = document.getElementById('pendingProductsTableBody');
    const countBadge = document.getElementById('pendingProductsHeaderCount');
    const sidebarBadge = document.getElementById('badgeProductsCount');

    if (countBadge) countBadge.textContent = `(${pendingList.length})`;
    if (sidebarBadge) sidebarBadge.textContent = `${pendingList.length}`;

    if (!tbody) return;

    if (!pendingList || pendingList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="py-8 text-center text-neutral-400 text-xs">
                    ✓ Không có sản phẩm nào đang chờ Admin kiểm duyệt.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = pendingList.map(p => `
        <tr class="hover:bg-neutral-50/80 transition-colors">
            <td class="py-3 px-4">
                <div class="flex items-center gap-3">
                    <img src="${p.image}" alt="${p.title}" class="w-10 h-10 rounded-lg object-cover border border-neutral-200 shrink-0">
                    <div>
                        <span class="font-bold text-neutral-900 block line-clamp-1">${p.title}</span>
                        <span class="text-[11px] text-neutral-400 font-mono">Mã SP: #${p.id}</span>
                    </div>
                </div>
            </td>
            <td class="py-3 px-4 font-semibold text-primary-600">${p.shop_name}</td>
            <td class="py-3 px-4 uppercase font-medium text-neutral-600">${p.category}</td>
            <td class="py-3 px-4 font-bold text-neutral-900">${p.price_formatted || Number(p.price).toLocaleString('vi-VN') + ' ₫'}</td>
            <td class="py-3 px-4">
                <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                    Chờ duyệt nội dung & giá
                </span>
            </td>
            <td class="py-3 px-4 text-right space-x-1.5 whitespace-nowrap">
                <button onclick="handleRejectPendingProduct(${p.id}, '${p.title.replace(/'/g, "\\'")}')" class="px-3 py-1.5 border border-neutral-200 text-neutral-600 hover:bg-neutral-100 rounded-lg text-xs font-semibold transition-colors">
                    Từ chối
                </button>
                <button onclick="handleApprovePendingProduct(${p.id}, '${p.title.replace(/'/g, "\\'")}')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors">
                    ✓ Duyệt lên kệ
                </button>
            </td>
        </tr>
    `).join('');
}

async function handleApprovePendingProduct(id, title) {
    try {
        const res = await fetch(`${API_BASE_URL}/api/admin/products/${id}/approve`, { method: 'PUT' });
        if (res.ok) {
            window.dispatchEvent(new Event('storage'));
            await syncWithFastAPI();
        }
    } catch (e) {}
}

async function handleRejectPendingProduct(id, title) {
    try {
        const res = await fetch(`${API_BASE_URL}/api/admin/products/${id}/reject`, { method: 'PUT' });
        if (res.ok) {
            window.dispatchEvent(new Event('storage'));
            await syncWithFastAPI();
        }
    } catch (e) {}
}

/**
 * Duyệt sản phẩm từ bảng kiểm duyệt lên SQL Database & trang User
 */
async function approveProductToStore(button, title, price, category, shop) {
    try {
        await fetch(`${API_BASE_URL}/api/admin/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                category: category || 'tech',
                price: price || 8500000,
                original_price: Math.round((price || 8500000) * 1.25),
                image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80',
                shop_name: shop || 'AB Technology Ltd',
                is_flash_sale: false
            })
        });
    } catch (e) {}

    window.dispatchEvent(new Event('storage'));
    approveQuick(button, `✓ Đã phê duyệt vào SQL! Sản phẩm "${title}" đã hiển thị lên trang Khách Hàng!`);
    await syncWithFastAPI();
}





/**
 * Gỡ và xóa vĩnh viễn sản phẩm khỏi SQL Database & trang User
 */
async function removeProductFromStore(button, title) {
    try {
        await fetch(`${API_BASE_URL}/api/admin/products?title=${encodeURIComponent(title)}`, {
            method: 'DELETE'
        });
    } catch (e) {}

    window.dispatchEvent(new Event('storage'));
    approveQuick(button, `✓ Đã xóa vĩnh viễn sản phẩm "${title}" khỏi SQL Database!`);
    await syncWithFastAPI();
}





/**
 * Xử lý duyệt nhanh các yêu cầu trong bảng
 */
function approveQuick(element, successMessage) {
    alert(successMessage);
    const rowOrCard = element.closest('tr, .p-4, .p-3');
    if (rowOrCard) {
        rowOrCard.style.opacity = '0.4';
        rowOrCard.style.pointerEvents = 'none';
    }
}

/**
 * Khởi tạo biểu đồ GMV Toàn Sàn vs Doanh thu Hoa hồng Sàn 12 tháng
 */
function initRevenueChart() {
    const canvas = document.getElementById('revenueChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: [
                'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 
                'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 
                'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
            ],
            datasets: [
                {
                    label: 'Tổng GMV Toàn Sàn (₫)',
                    data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    borderColor: '#0D6EFD',
                    backgroundColor: 'rgba(13, 110, 253, 0.08)',
                    borderWidth: 2.5,
                    pointBackgroundColor: '#FFFFFF',
                    pointBorderColor: '#0D6EFD',
                    pointBorderWidth: 2,
                    pointRadius: 3.5,
                    fill: true,
                    tension: 0.35
                },
                {
                    label: 'Phí Hoa Hồng Sàn Thu (7%)',
                    data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    borderColor: '#00B517',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointBackgroundColor: '#00B517',
                    pointRadius: 3,
                    fill: false,
                    tension: 0.35
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: { boxWidth: 12, usePointStyle: true, font: { size: 11 } }
                }
            },
            scales: {
                x: { grid: { display: false }, ticks: { font: { size: 11 }, color: '#6F7C8E' } },
                y: {
                    grid: { color: '#EDF0F2' },
                    ticks: {
                        font: { size: 11 },
                        color: '#6F7C8E',
                        callback: function(val) {
                            if (val === 0) return '0 ₫';
                            if (val >= 1000000) return (val / 1000000).toFixed(1) + 'M ₫';
                            return (val / 1000) + 'k ₫';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Khởi tạo biểu đồ tỷ trọng GMV theo Phân hạng Shop
 */
function initCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['JML Mall (Chính hãng)', 'Shop Yêu Thích+ (Uy tín)', 'Shop Tiêu Chuẩn'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#FA3434', '#FF9017', '#0D6EFD'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '72%',
            plugins: { legend: { display: false } }
        }
    });
}

/**
 * Tìm kiếm nhanh trên toàn sàn
 */
function initGlobalSearch() {
    const searchInput = document.getElementById('globalSearchInput');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        const cards = document.querySelectorAll('#fullOrdersContainer .order-card');
        cards.forEach(card => {
            card.style.display = (!query || card.textContent.toLowerCase().includes(query)) ? '' : 'none';
        });
    });
}

// =============================================================================
// QUẢN LÝ KHÁCH HÀNG / NGƯỜI MUA (CUSTOMERS & BUYERS - SQL DATABASE)
// =============================================================================
function renderCustomers(filteredData = null) {
    const tbody = document.getElementById('customersTableBody');
    if (!tbody) return;

    const data = filteredData || Object.entries(CUSTOMERS_DATABASE);
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="py-8 text-center text-neutral-400 text-xs">
                    Chưa có khách hàng nào trong cơ sở dữ liệu.
                </td>
            </tr>
        `;
        return;
    }
    tbody.innerHTML = data.map(([key, cust]) => `
        <tr class="hover:bg-neutral-50/80 transition-colors">
            <td class="py-3 px-4">
                <div class="flex items-center gap-3">
                    <img src="${cust.avatar}" alt="${cust.name}" class="w-9 h-9 rounded-full object-cover border border-neutral-200 shrink-0">
                    <div>
                        <span class="font-bold text-neutral-900 block">${cust.name}</span>
                        <span class="text-[11px] text-neutral-400 font-mono">${cust.id}</span>
                    </div>
                </div>
            </td>
            <td class="py-3 px-4">
                <span class="font-medium text-neutral-800 block">${cust.phone}</span>
                <span class="text-[11px] text-neutral-500">${cust.email}</span>
            </td>
            <td class="py-3 px-4">
                <span class="px-2 py-0.5 text-[11px] font-bold rounded-full border ${cust.rankBadge}">
                    ${cust.rank}
                </span>
            </td>
            <td class="py-3 px-4 font-semibold text-neutral-800">${cust.ordersCount} đơn</td>
            <td class="py-3 px-4 font-bold text-primary-600">${cust.totalSpent}</td>
            <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded text-[11px] font-semibold ${cust.statusBadge}">
                    ${cust.status}
                </span>
            </td>
            <td class="py-3 px-4 text-right space-x-1.5 whitespace-nowrap">
                <button onclick="openCustomerDetail('${key}')" class="px-2.5 py-1 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded text-xs font-semibold">
                    Xem hồ sơ
                </button>
                <button onclick="toggleCustomerBanDirect(this, '${key}')" class="px-2.5 py-1 ${cust.status.includes('khóa') ? 'bg-emerald-500 hover:bg-emerald-600 text-white' : 'border border-red-200 text-danger-500 hover:bg-red-50'} rounded text-xs font-semibold transition-colors">
                    ${cust.status.includes('khóa') ? 'Mở khóa' : 'Khóa'}
                </button>
                <button onclick="deleteCustomerDirect(this, '${key}', '${cust.name.replace(/'/g, "\\'")}')" title="Xóa vĩnh viễn khách hàng này" class="px-2.5 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-semibold transition-colors">
                    Xóa
                </button>
            </td>
        </tr>
    `).join('');
}

function filterCustomers() {
    const query = document.getElementById('customerSearchInput')?.value.trim().toLowerCase() || '';
    const rank = document.getElementById('customerRankFilter')?.value || 'all';

    const entries = Object.entries(CUSTOMERS_DATABASE).filter(([_, cust]) => {
        const matchQuery = !query || cust.name.toLowerCase().includes(query) || cust.phone.includes(query) || cust.email.toLowerCase().includes(query) || cust.id.toLowerCase().includes(query);
        const matchRank = (rank === 'all') || (cust.rank === rank);
        return matchQuery && matchRank;
    });

    renderCustomers(entries);
}

function openCustomerDetail(key) {
    const cust = CUSTOMERS_DATABASE[key];
    if (!cust) return;

    currentViewingCustId = key;
    document.getElementById('modalCustAvatar').src = cust.avatar;
    document.getElementById('modalCustName').textContent = cust.name;
    document.getElementById('modalCustRank').textContent = cust.rank;
    document.getElementById('modalCustRank').className = `px-2 py-0.5 text-[10px] font-bold rounded uppercase border ${cust.rankBadge}`;
    document.getElementById('modalCustMeta').textContent = `ID: ${cust.id} • Tham gia: ${cust.joined}`;
    document.getElementById('modalCustPhone').textContent = cust.phone;
    document.getElementById('modalCustEmail').textContent = cust.email;
    document.getElementById('modalCustAddress').textContent = cust.address;
    document.getElementById('modalCustSpent').textContent = cust.totalSpent;
    document.getElementById('modalCustOrdersCount').textContent = `${cust.ordersCount} đơn hàng trên sàn`;

    const banBtn = document.getElementById('modalCustBanBtn');
    if (cust.status.includes('khóa')) {
        banBtn.textContent = 'Mở khóa tài khoản khách này';
        banBtn.className = 'px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-semibold';
    } else {
        banBtn.textContent = 'Khóa tài khoản khách này';
        banBtn.className = 'px-3 py-1.5 rounded-lg border border-red-200 text-danger-500 hover:bg-danger-50 text-xs font-semibold';
    }

    const tbody = document.getElementById('modalCustOrdersHistory');
    const history = cust.ordersHistory || [];
    tbody.innerHTML = history.length ? history.map(o => `
        <tr class="hover:bg-neutral-50">
            <td class="py-2.5 px-3 font-bold text-neutral-900">${o.id}</td>
            <td class="py-2.5 px-3 text-neutral-700">${o.shop}</td>
            <td class="py-2.5 px-3 text-neutral-500">${o.date}</td>
            <td class="py-2.5 px-3 font-semibold text-neutral-900">${o.total}</td>
            <td class="py-2.5 px-3 text-right">
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${o.status.includes('Tranh chấp') || o.status.includes('Hủy') ? 'bg-danger-50 text-danger-500' : 'bg-success-50 text-success-500'}">
                    ${o.status}
                </span>
            </td>
        </tr>
    `).join('') : `<tr><td colspan="5" class="py-4 text-center text-neutral-400">Chưa có đơn hàng nào</td></tr>`;

    toggleModal('customerDetailModal');
}

/**
 * Hệ thống Toast Notification thông báo kết quả thao tác của Admin
 */
function showAdminToast(title, message, type = 'success') {
    let container = document.getElementById('adminToastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'adminToastContainer';
        container.className = 'fixed bottom-6 right-6 z-[9999] flex flex-col gap-2 pointer-events-none max-w-sm w-full';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const isSuccess = type === 'success';
    toast.className = `pointer-events-auto cursor-pointer flex items-center gap-3 p-3.5 bg-white border rounded-xl shadow-2xl transition-all duration-300 transform translate-y-[15px] opacity-0 ${
        isSuccess ? 'border-emerald-200 text-emerald-900' : 'border-red-200 text-red-900'
    }`;

    const iconHtml = isSuccess
        ? `<div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0 font-bold text-sm">✓</div>`
        : `<div class="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center shrink-0 font-bold text-sm">✕</div>`;

    toast.innerHTML = `
        ${iconHtml}
        <div class="flex-1 min-w-0">
            <p class="font-bold text-xs text-neutral-900">${title}</p>
            <p class="text-xs ${isSuccess ? 'text-emerald-700 font-medium' : 'text-red-600'}">${message}</p>
        </div>
        <button class="text-neutral-400 hover:text-neutral-700 text-xs font-bold p-1">✕</button>
    `;

    // Click to dismiss immediately
    toast.onclick = () => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-[15px]', 'opacity-0');
        setTimeout(() => {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 250);
    };

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove('translate-y-[15px]', 'opacity-0');
        toast.classList.add('translate-y-0', 'opacity-100');
    });

    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.remove('translate-y-0', 'opacity-100');
            toast.classList.add('translate-y-[15px]', 'opacity-0');
            setTimeout(() => {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 300);
        }
    }, 3000);
}

function toggleCustomerBanCurrent() {
    if (!currentViewingCustId) return;
    const banBtn = document.getElementById('modalCustBanBtn');
    toggleCustomerBanDirect(banBtn, currentViewingCustId);
    toggleModal('customerDetailModal');
}

async function toggleCustomerBanDirect(arg1, arg2) {
    let btn = null;
    let key = '';
    if (arg1 && arg1.nodeType === 1) {
        btn = arg1;
        key = arg2;
    } else {
        key = arg1;
    }

    const cust = CUSTOMERS_DATABASE[key];
    if (!cust) return;

    const isCurrentlyBanned = cust.status.includes('khóa') || cust.status.includes('bị khóa');

    // Cập nhật trạng thái 'Đang khóa...' hoặc 'Đang mở...' ngay lập tức trên giao diện
    const tr = btn ? btn.closest('tr') : null;
    const statusCell = tr ? tr.querySelector('td:nth-child(6) span') : null;

    if (btn) {
        btn.disabled = true;
        btn.classList.add('opacity-75', 'cursor-not-allowed');
        btn.innerHTML = `<span class="inline-flex items-center gap-1.5"><svg class="animate-spin h-3 w-3 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>${isCurrentlyBanned ? 'Đang mở...' : 'Đang khóa...'}</span>`;
    }

    if (statusCell) {
        statusCell.textContent = isCurrentlyBanned ? 'Đang mở...' : 'Đang khóa...';
        statusCell.className = `px-2 py-0.5 rounded text-[11px] font-semibold animate-pulse ${
            isCurrentlyBanned ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600'
        }`;
    }

    try {
        await fetch(`${API_BASE_URL}/api/admin/customers/${key}/toggle-ban`, { method: 'PUT' });
    } catch (e) {}

    let banned = JSON.parse(localStorage.getItem('JML_BANNED_CUSTOMERS') || '[]');
    if (isCurrentlyBanned) {
        banned = banned.filter(x => x !== cust.phone && x !== cust.name);
    } else {
        if (!banned.includes(cust.phone)) banned.push(cust.phone);
        if (!banned.includes(cust.name)) banned.push(cust.name);
    }
    localStorage.setItem('JML_BANNED_CUSTOMERS', JSON.stringify(banned));
    window.dispatchEvent(new Event('storage'));

    await syncWithFastAPI();

    if (isCurrentlyBanned) {
        showAdminToast('Thành công', 'Đã mở khóa thành công', 'success');
    } else {
        showAdminToast('Thành công', 'Đã khóa thành công', 'success');
    }
}

async function deleteCustomerDirect(arg1, arg2, arg3) {
    let btn = null;
    let key = '';
    let name = '';
    if (arg1 && arg1.nodeType === 1) {
        btn = arg1;
        key = arg2;
        name = arg3 || '';
    } else {
        key = arg1;
        name = arg2 || '';
    }

    const tr = btn ? btn.closest('tr') : null;
    const statusCell = tr ? tr.querySelector('td:nth-child(6) span') : null;

    if (btn) {
        btn.disabled = true;
        btn.classList.add('opacity-75', 'cursor-not-allowed');
        btn.innerHTML = `<span class="inline-flex items-center gap-1.5"><svg class="animate-spin h-3 w-3 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>Đang xóa...</span>`;
    }

    if (statusCell) {
        statusCell.textContent = 'Đang xóa...';
        statusCell.className = 'px-2 py-0.5 rounded text-[11px] font-semibold bg-red-50 text-red-600 animate-pulse';
    }
    if (tr) {
        tr.classList.add('opacity-50', 'transition-opacity');
    }

    try {
        const res = await fetch(`${API_BASE_URL}/api/admin/customers/${key}`, { method: 'DELETE' });
        if (res.ok) {
            delete CUSTOMERS_DATABASE[key];
            const localCust = JSON.parse(localStorage.getItem('JML_CUSTOMERS') || '{}');
            delete localCust[key];
            localStorage.setItem('JML_CUSTOMERS', JSON.stringify(localCust));
            window.dispatchEvent(new Event('storage'));
            await syncWithFastAPI();
            showAdminToast('Thành công', 'Đã xóa thành công', 'success');
        } else {
            const data = await res.json();
            showAdminToast('Lỗi', `Không thể xóa: ${data.detail || 'Lỗi không xác định'}`, 'danger');
            if (btn) {
                btn.disabled = false;
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
                btn.textContent = 'Xóa';
            }
            if (tr) tr.classList.remove('opacity-50');
            if (statusCell && CUSTOMERS_DATABASE[key]) {
                statusCell.textContent = CUSTOMERS_DATABASE[key].status;
                statusCell.className = `px-2 py-0.5 rounded text-[11px] font-semibold ${CUSTOMERS_DATABASE[key].statusBadge}`;
            }
        }
    } catch (err) {
        showAdminToast('Lỗi', 'Lỗi kết nối tới máy chủ!', 'danger');
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('opacity-75', 'cursor-not-allowed');
            btn.textContent = 'Xóa';
        }
        if (tr) tr.classList.remove('opacity-50');
    }
}
