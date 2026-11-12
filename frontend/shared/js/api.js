/**
 * API WRAPPER - JML STORE MULTI-VENDOR MARKETPLACE
 * Quản lý các cuộc gọi RESTful API tới FastAPI backend (http://127.0.0.1:8000)
 */

const API_BASE_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000'
    : '';

async function apiClient(endpoint, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };

    const token = localStorage.getItem('JML_ACCESS_TOKEN');
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

    try {
        const response = await fetch(url, config);

        if (response.status === 401) {
            console.warn('Phiên đăng nhập đã hết hạn');
        }

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            const errorMsg = data && data.detail ? data.detail : `Lỗi yêu cầu HTTP: ${response.status}`;
            throw new Error(errorMsg);
        }

        return data;
    } catch (err) {
        console.error(`API Error [${endpoint}]:`, err);
        throw err;
    }
}

// Các hàm tiện ích gọi API thường dùng
const API = {
    get: (endpoint) => apiClient(endpoint, { method: 'GET' }),
    post: (endpoint, body) => apiClient(endpoint, { method: 'POST', body: JSON.stringify(body) }),
    put: (endpoint, body) => apiClient(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
    delete: (endpoint) => apiClient(endpoint, { method: 'DELETE' }),
};

window.API = API;
window.API_BASE_URL = API_BASE_URL;

