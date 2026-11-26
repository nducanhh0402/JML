/**
 * AUTH & RBAC CONTROLLER - JML STORE MULTI-VENDOR MARKETPLACE
 * Quản lý trạng thái đăng nhập, phân quyền truy cập (Admin / Seller / Customer),
 * bảo vệ trang quản trị, ẩn hiện menu theo vai trò và chức năng đăng xuất toàn diện.
 */

const Auth = {
    // -------------------------------------------------------------------------
    // 1. TRUY VẤN VÀ ĐỒNG BỘ TRẠNG THÁI NGƯỜI DÙNG & TOKEN
    // -------------------------------------------------------------------------
    getUser: function() {
        try {
            const raw = localStorage.getItem('JML_AUTH_USER') || 
                        localStorage.getItem('JML_ADMIN_USER') || 
                        localStorage.getItem('JML_SELLER_USER') || 
                        localStorage.getItem('JML_CUSTOMER_USER') || 
                        localStorage.getItem('user');
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            console.error('Lỗi phân tích cú pháp thông tin user:', e);
            return null;
        }
    },

    getToken: function() {
        return localStorage.getItem('JML_ACCESS_TOKEN') || 
               localStorage.getItem('access_token') || 
               null;
    },

    isAuthenticated: function() {
        return this.getUser() !== null && this.getToken() !== null;
    },

    getRole: function() {
        const user = this.getUser();
        if (!user || !user.role) return '';
        return String(user.role).trim().toLowerCase();
    },

    isAdmin: function() {
        return this.getRole() === 'admin';
    },

    isSeller: function() {
        return this.getRole() === 'seller';
    },

    isCustomer: function() {
        const role = this.getRole();
        return role === 'customer' || role === 'buyer';
    },

    hasRole: function(requiredRole) {
        const currentRole = this.getRole();
        if (!currentRole) return false;
        if (currentRole === 'admin') return true; // Admin có mọi quyền
        return currentRole === String(requiredRole).trim().toLowerCase();
    },

    // -------------------------------------------------------------------------
    // 2. LƯU PHIÊN & ĐĂNG XUẤT ĐỒNG BỘ
    // -------------------------------------------------------------------------
    setSession: function(user, token = null) {
        if (!user) return;
        const userStr = JSON.stringify(user);
        localStorage.setItem('JML_AUTH_USER', userStr);
        localStorage.setItem('user', userStr);

        const role = String(user.role || '').toLowerCase();
        if (role === 'admin') {
            localStorage.setItem('JML_ADMIN_USER', userStr);
        } else if (role === 'seller') {
            localStorage.setItem('JML_SELLER_USER', userStr);
        } else {
            localStorage.setItem('JML_CUSTOMER_USER', userStr);
        }

        if (token) {
            localStorage.setItem('JML_ACCESS_TOKEN', token);
            localStorage.setItem('access_token', token);
            localStorage.setItem('token_type', 'Bearer');
        }

        localStorage.setItem('auth_login_at', new Date().toISOString());
        window.dispatchEvent(new Event('auth_state_changed'));
    },

    logout: function(redirectUrl = null) {
        // Xóa sạch toàn bộ key session trong LocalStorage
        const keysToRemove = [
            'JML_AUTH_USER',
            'JML_ADMIN_USER',
            'JML_SELLER_USER',
            'JML_CUSTOMER_USER',
            'user',
            'JML_ACCESS_TOKEN',
            'access_token',
            'token_type',
            'auth_login_at'
        ];
        keysToRemove.forEach(k => localStorage.removeItem(k));

        window.dispatchEvent(new Event('auth_state_changed'));

        // Chuyển hướng theo yêu cầu
        if (redirectUrl === false) {
            return;
        }

        if (typeof redirectUrl === 'string' && redirectUrl) {
            window.location.href = redirectUrl;
        } else {
            // Mặc định chuyển về trang đăng nhập kèm thông báo
            const isInSubDir = window.location.pathname.includes('/admin/') || 
                               window.location.pathname.includes('/user/') || 
                               window.location.pathname.includes('/buyer/') || 
                               window.location.pathname.includes('/seller/');
            const targetLogin = isInSubDir ? '../auth/index.html?message=logged_out' : 'frontend/auth/index.html?message=logged_out';
            window.location.href = targetLogin;
        }
    },

    // -------------------------------------------------------------------------
    // 3. BẢO VỆ ROUTE (ROUTE GUARDS): CHẶN KHÁCH VÀO TRANG QUẢN TRỊ
    // -------------------------------------------------------------------------
    requireAdmin: function(options = {}) {
        const loginUrl = options.loginUrl || '../auth/index.html';
        const forbiddenRedirect = options.forbiddenRedirect || '../user/index.html';
        const user = this.getUser();
        const token = this.getToken();

        // 1. Chưa đăng nhập -> Chuyển ngay về trang đăng nhập
        if (!user || !token) {
            console.warn('Chưa đăng nhập! Đang chuyển hướng về trang đăng nhập...');
            window.location.href = `${loginUrl}?redirect=admin&error=unauthorized`;
            return false;
        }

        // 2. Đã đăng nhập nhưng không phải admin -> Chặn khách vào trang quản trị
        const role = this.getRole();
        if (role !== 'admin') {
            console.warn(`Chặn truy cập: Vai trò '${role}' không có quyền Admin.`);
            // Hiển thị thông báo chặn và chuyển hướng
            alert(`⛔ TRUY CẬP BỊ TỪ CHỐI!\n\nTrang quản trị chỉ dành riêng cho Quản Trị Viên (Admin).\nTài khoản hiện tại của bạn là: "${user.full_name || user.username}" (Vai trò: ${role.toUpperCase()}).\nBạn sẽ được chuyển về trang mua sắm.`);
            window.location.href = `${forbiddenRedirect}?error=forbidden&role=${encodeURIComponent(role)}`;
            return false;
        }

        return true;
    },

    requireAuth: function(options = {}) {
        const loginUrl = options.loginUrl || '../auth/index.html';
        if (!this.isAuthenticated()) {
            const redirectParam = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = `${loginUrl}?redirect=${redirectParam}&error=unauthorized`;
            return false;
        }
        return true;
    },

    // -------------------------------------------------------------------------
    // 4. HIỂN THỊ MENU ĐIỀU HƯỚNG THEO VAI TRÒ (DYNAMIC ROLE-BASED NAVIGATION)
    // -------------------------------------------------------------------------
    getProfilePath: function() {
        const p = window.location.pathname;
        if (p.includes('/user/')) return 'profile.html';
        if (p.includes('/buyer/') || p.includes('/admin/') || p.includes('/seller/')) return '../user/profile.html';
        return 'frontend/user/profile.html';
    },

    renderUserTopLinks: function(targetElementId = 'topAuthLinks') {
        const container = document.getElementById(targetElementId);
        if (!container) return;

        const user = this.getUser();
        const isAuthenticated = this.isAuthenticated();
        const role = this.getRole();

        // Xác định đường dẫn tương đối
        const isUserDir = window.location.pathname.includes('/user/') || window.location.pathname.includes('/buyer/');
        const authPath = isUserDir ? '../auth/index.html' : 'frontend/auth/index.html';
        const adminPath = isUserDir ? '../admin/index.html' : 'frontend/admin/index.html';
        const sellerPath = isUserDir ? '../seller/index.html' : 'frontend/seller/index.html';
        const userPath = isUserDir ? 'index.html' : 'frontend/user/index.html';

        if (!isAuthenticated || !user) {
            // ================= TRƯỜNG HỢP: KHÁCH CHƯA ĐĂNG NHẬP =================
            container.innerHTML = `
                <span>Hotline: <strong style="color: #fff;">1900 8888</strong></span>
                <span style="opacity: 0.3;">|</span>
                <a href="${authPath}" style="color: #ffb347; font-weight: 700; text-decoration: none;">Đăng Nhập / Đăng Ký</a>
            `;
            this.updateAccountButtonAction('guest', authPath);
            return;
        }

        // ================= TRƯỜNG HỢP: ĐÃ ĐĂNG NHẬP THEO VAI TRÒ =================
        let roleBadge = '';
        let roleLinks = '';
        const displayName = user.full_name || user.username || 'Thành viên';

        if (role === 'admin') {
            roleBadge = `<span style="background: #ff4267; color: #fff; padding: 2px 7px; border-radius: 9999px; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-left: 4px;">👑 Admin</span>`;
            roleLinks = `
                <a href="${adminPath}" style="color: #ffb347; font-weight: 800; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;" title="Vào Bảng Điều Khiển Quản Trị Hệ Thống">
                    <span>👑 Trang Quản Trị</span>
                </a>
                <span style="opacity: 0.3;">|</span>
                <a href="${sellerPath}" style="text-decoration: none; color: #cbd5e1;">Kênh Shop</a>
            `;
        } else if (role === 'seller') {
            const shopName = user.shop_name || 'Kênh Shop';
            roleBadge = `<span style="background: #f59e0b; color: #fff; padding: 2px 7px; border-radius: 9999px; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-left: 4px;">🏪 Seller</span>`;
            roleLinks = `
                <a href="${sellerPath}" style="color: #ffb347; font-weight: 800; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;" title="Vào Kênh Quản Lý Cửa Hàng">
                    <span>🏪 Kênh Người Bán</span>
                </a>
            `;
        } else {
            // Customer / Client
            const rank = user.rank || 'Đồng';
            roleBadge = `<span style="background: #0a55ab; color: #fff; padding: 2px 7px; border-radius: 9999px; font-size: 10px; font-weight: 700; margin-left: 4px;">${rank}</span>`;
            roleLinks = `
                <a href="${userPath}#my-orders" onclick="if(window.openOrdersModal) openOrdersModal();" style="text-decoration: none; color: #cbd5e1;">Đơn Mua</a>
                <span style="opacity: 0.3;">|</span>
                <a href="${sellerPath}" style="text-decoration: none; color: #cbd5e1;" title="Đăng ký mở gian hàng trên JML Store">Mở Shop</a>
            `;
        }

        container.innerHTML = `
            <div style="display: inline-flex; align-items: center; gap: 6px;">
                <span>Xin chào, <strong style="color: #fff;">${displayName}</strong></span>
                ${roleBadge}
            </div>
            <span style="opacity: 0.3;">|</span>
            ${roleLinks}
            <span style="opacity: 0.3;">|</span>
            <a href="${this.getProfilePath()}" style="text-decoration: none; color: #cbd5e1;">Hồ Sơ</a>
            <span style="opacity: 0.3;">|</span>
            <button type="button" onclick="Auth.logout('${authPath}?message=logged_out')" style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#ef4444'; this.style.color='#fff';" onmouseout="this.style.background='rgba(239, 68, 68, 0.15)'; this.style.color='#fca5a5';">
                🚪 Đăng Xuất
            </button>
        `;

        this.updateAccountButtonAction(role, authPath, adminPath, sellerPath);
    },

    updateAccountButtonAction: function(role, authPath, adminPath = '', sellerPath = '') {
        const accBtn = document.querySelector('.header-actions .btn-action[title="Tài khoản"]');
        if (!accBtn) return;

        if (role === 'guest') {
            accBtn.onclick = function() {
                window.location.href = authPath;
            };
            accBtn.title = 'Đăng nhập / Đăng ký tài khoản';
        } else {
            accBtn.onclick = function() {
                Auth.openAccountDropdownMenu(role, adminPath, sellerPath, authPath);
            };
            accBtn.title = 'Tài khoản & Phân quyền';
        }
    },

    openAccountDropdownMenu: function(role, adminPath, sellerPath, authPath) {
        let menu = document.getElementById('authAccountDropdown');
        if (menu) {
            menu.classList.toggle('hidden');
            return;
        }

        const user = this.getUser() || {};
        menu = document.createElement('div');
        menu.id = 'authAccountDropdown';
        menu.style.cssText = `
            position: absolute;
            top: 70px;
            right: 80px;
            width: 260px;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
            z-index: 1000;
            padding: 12px;
            font-family: inherit;
        `;

        let roleLabel = 'Khách Mua Hàng (Buyer)';
        let roleBadgeColor = '#0a55ab';
        let specialLinks = '';

        if (role === 'admin') {
            roleLabel = 'Quản Trị Viên (Super Admin)';
            roleBadgeColor = '#ff4267';
            specialLinks = `
                <a href="${adminPath}" style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 8px; color: #0a55ab; background: #eff6ff; text-decoration: none; font-weight: 700; font-size: 12px; margin-bottom: 6px;">
                    👑 Vào Bảng Điều Khiển Admin
                </a>
                <a href="${sellerPath}" style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 8px; color: #334155; text-decoration: none; font-size: 12px;">
                    🏪 Kênh Người Bán (Shop)
                </a>
            `;
        } else if (role === 'seller') {
            roleLabel = 'Chủ Cửa Hàng (Seller)';
            roleBadgeColor = '#f59e0b';
            specialLinks = `
                <a href="${sellerPath}" style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 8px; color: #e11d48; background: #fff1f2; text-decoration: none; font-weight: 700; font-size: 12px; margin-bottom: 6px;">
                    🏪 Vào Kênh Người Bán (Dashboard)
                </a>
            `;
        } else {
            specialLinks = `
                <a href="#orders" onclick="if(window.openOrdersModal) openOrdersModal();" style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 8px; color: #334155; text-decoration: none; font-size: 12px;">
                    📦 Đơn Hàng Của Tôi
                </a>
                <a href="${sellerPath}" style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 8px; color: #334155; text-decoration: none; font-size: 12px;">
                    🏪 Đăng Ký Mở Gian Hàng
                </a>
            `;
        }

        menu.innerHTML = `
            <div style="padding-bottom: 10px; margin-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
                <div style="font-weight: 700; color: #0f172a; font-size: 13px;">${user.full_name || user.username || 'Người dùng'}</div>
                <div style="color: #64748b; font-size: 11px;">${user.phone || user.email || 'Chưa cập nhật SĐT'}</div>
                <div style="margin-top: 4px; display: inline-block; padding: 2px 8px; border-radius: 9999px; background: ${roleBadgeColor}15; color: ${roleBadgeColor}; font-size: 10px; font-weight: 700;">
                    ${roleLabel}
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 2px;">
                <a href="${this.getProfilePath()}" style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 8px; color: #334155; text-decoration: none; font-size: 12px;">
                    👤 Hồ Sơ Cá Nhân &amp; Đổi Mật Khẩu
                </a>
                ${specialLinks}
                <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 6px 0;">
                <button type="button" onclick="Auth.logout('${authPath}?message=logged_out')" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px; border-radius: 8px; background: #fee2e2; color: #dc2626; border: 0; font-size: 12px; font-weight: 700; cursor: pointer; transition: background 0.2s;">
                    🚪 Đăng Xuất Khỏi Hệ Thống
                </button>
            </div>
        `;

        document.body.appendChild(menu);

        // Đóng dropdown khi click ra ngoài
        setTimeout(() => {
            function closeMenu(e) {
                if (!menu.contains(e.target) && !e.target.closest('.header-actions .btn-action')) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            }
            document.addEventListener('click', closeMenu);
        }, 10);
    }
};

// Đăng ký toàn cục
window.Auth = Auth;

// Tự động kích hoạt cập nhật menu khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
    // 1. Nếu có phần tử top-bar auth
    if (document.getElementById('topAuthLinks') || document.querySelector('.top-links')) {
        Auth.renderUserTopLinks('topAuthLinks');
    }

    // 2. Bắt thông báo lỗi từ query params URL (ví dụ chuyển từ trang quản trị về)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('error') === 'forbidden') {
        const forbiddenRole = urlParams.get('role') || 'Khách';
        console.warn('Bị chặn quyền truy cập trang quản trị!');
        if (typeof showToast === 'function') {
            showToast(`⛔ Bạn không có quyền truy cập trang Quản Trị! (Vai trò: ${forbiddenRole.toUpperCase()})`);
        }
    } else if (urlParams.get('message') === 'logged_out') {
        if (typeof showToast === 'function') {
            showToast('✅ Đã đăng xuất thành công khỏi hệ thống!');
        }
    }
});

// Lắng nghe sự kiện thay đổi đăng nhập trên toàn ứng dụng
window.addEventListener('auth_state_changed', () => {
    if (document.getElementById('topAuthLinks') || document.querySelector('.top-links')) {
        Auth.renderUserTopLinks('topAuthLinks');
    }
});
