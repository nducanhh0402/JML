/**
 * AUTH & RBAC CONTROLLER - JML STORE MULTI-VENDOR MARKETPLACE
 * Quản lý trạng thái đăng nhập và phân quyền hiển thị (Buyer, Seller, Admin)
 */

const Auth = {
    // Lấy thông tin user hiện tại
    getUser: function() {
        try {
            const raw = localStorage.getItem('JML_AUTH_USER') || localStorage.getItem('JML_CUSTOMER_USER');
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    },

    // Kiểm tra đã đăng nhập chưa
    isAuthenticated: function() {
        return this.getUser() !== null;
    },

    // Kiểm tra vai trò
    hasRole: function(role) {
        const user = this.getUser();
        if (!user) return false;
        if (user.role === 'admin') return true; // Admin có mọi quyền
        return user.role === role;
    },

    // Lưu session đăng nhập
    setSession: function(user, token = null) {
        localStorage.setItem('JML_AUTH_USER', JSON.stringify(user));
        if (token) localStorage.setItem('JML_ACCESS_TOKEN', token);
        if (user.role === 'customer') {
            localStorage.setItem('JML_CUSTOMER_USER', JSON.stringify(user));
        }
        window.dispatchEvent(new Event('auth_state_changed'));
    },

    // Đăng xuất
    logout: function() {
        localStorage.removeItem('JML_AUTH_USER');
        localStorage.removeItem('JML_CUSTOMER_USER');
        localStorage.removeItem('JML_ACCESS_TOKEN');
        window.dispatchEvent(new Event('auth_state_changed'));
        window.location.reload();
    }
};

window.Auth = Auth;

