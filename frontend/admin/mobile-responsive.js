/**
 * JML Store Admin – Mobile Sidebar Responsive
 * File MỚI – Không chỉnh sửa script.js hoặc index.html gốc
 */

(function () {
    'use strict';

    // ── 1. Inject CSS link (mobile-responsive.css) vào <head> ──
    function injectCSS() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'mobile-responsive.css';
        document.head.appendChild(link);
    }

    // ── 2. Inject overlay element ──
    function injectOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'sidebarOverlay';
        overlay.setAttribute('aria-hidden', 'true');
        document.body.appendChild(overlay);
        return overlay;
    }

    // ── 3. Inject nút hamburger vào đầu header ──
    function injectHamburger() {
        const header = document.querySelector('header');
        if (!header) return null;

        const btn = document.createElement('button');
        btn.id = 'mobileMenuToggle';
        btn.setAttribute('aria-label', 'Mở/đóng menu');
        btn.setAttribute('aria-expanded', 'false');
        btn.innerHTML = `
            <svg id="hamburgerIcon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
                <line x1="3" y1="6" x2="21" y2="6"/>
                <line x1="3" y1="12" x2="21" y2="12"/>
                <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
        `;
        // Chèn vào đầu header (trước mọi content hiện có)
        header.insertBefore(btn, header.firstChild);
        return btn;
    }

    // ── 4. Logic toggle sidebar ──
    function setupSidebarToggle(btn, overlay) {
        const sidebar = document.querySelector('body > aside');
        if (!sidebar || !btn || !overlay) return;

        let isOpen = false;

        function openSidebar() {
            isOpen = true;
            sidebar.classList.add('sidebar-open');
            overlay.classList.add('active');
            btn.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden'; // chặn scroll nền
            // Đổi icon thành X
            btn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                     fill="none" stroke="currentColor" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            `;
        }

        function closeSidebar() {
            isOpen = false;
            sidebar.classList.remove('sidebar-open');
            overlay.classList.remove('active');
            btn.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
            // Đổi lại icon hamburger
            btn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                     fill="none" stroke="currentColor" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <line x1="3" y1="6" x2="21" y2="6"/>
                    <line x1="3" y1="12" x2="21" y2="12"/>
                    <line x1="3" y1="18" x2="21" y2="18"/>
                </svg>
            `;
        }

        // Click nút toggle
        btn.addEventListener('click', function () {
            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });

        // Click overlay đóng sidebar
        overlay.addEventListener('click', closeSidebar);

        // Click nav link → đóng sidebar (khi trên mobile)
        sidebar.querySelectorAll('a[data-tab], a[href^="#"]').forEach(function (link) {
            link.addEventListener('click', function () {
                if (window.innerWidth <= 768) {
                    closeSidebar();
                }
            });
        });

        // Phím ESC đóng sidebar
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && isOpen) {
                closeSidebar();
            }
        });

        // Resize: reset nếu trở lại desktop
        window.addEventListener('resize', function () {
            if (window.innerWidth > 768 && isOpen) {
                closeSidebar();
            }
        });
    }

    // ── 5. Khởi chạy sau khi DOM ready ──
    function init() {
        injectCSS();
        const overlay = injectOverlay();
        const btn = injectHamburger();
        setupSidebarToggle(btn, overlay);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
