/* ==============================================================================
   JML STORE — MIDNIGHT SAPPHIRE & CORAL HORIZON BANNER AMBIENT
   Hiệu ứng ánh sáng Aurora, hạt tinh vân & vòng quỹ đạo nhẹ đồng bộ với
   trang Đăng nhập/Đăng ký mới (thuần CSS/2D Parallax, không dùng 3D WebGL).
   ============================================================================== */
(function () {
  'use strict';
  if (window.__JML_BANNER_AMBIENT_LOADED__) return;
  window.__JML_BANNER_AMBIENT_LOADED__ = true;

  const REDUCED_MOTION =
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const BANNER_SELECTOR = [
    '.hero',
    '.main-slider .slide',
    '.side-banner',
    '.promo-banner',
    '.page-header',
    '[data-jml-banner]',
    '[class*="bg-gradient-to-"]',
  ].join(', ');

  function isValidBannerTarget(el) {
    if (!el || el.nodeType !== 1) return false;
    if (el.dataset.jmlAmbientMounted === '1') return false;
    if (el.closest('.auth-shell') || el.closest('.top-bar') || el.closest('.topbar')) return false;
    if (['BUTTON', 'A', 'SPAN', 'IMG', 'INPUT', 'SELECT'].includes(el.tagName)) return false;

    const rect = el.getBoundingClientRect();
    if (rect.width < 180 || rect.height < 76) return false;

    const parentMounted =
      el.parentElement && el.parentElement.closest('[data-jml-ambient-mounted="1"]');
    if (parentMounted && !el.classList.contains('side-banner')) return false;

    return true;
  }

  function mountBannerAmbient(el) {
    if (!isValidBannerTarget(el)) return;
    el.dataset.jmlAmbientMounted = '1';

    const cs = window.getComputedStyle(el);
    if (cs.position === 'static') el.style.position = 'relative';
    if (cs.overflow === 'visible') el.style.overflow = 'hidden';

    const isSlide = el.classList.contains('slide');
    Array.from(el.children).forEach((child) => {
      if (child.classList && child.classList.contains('jml-banner-ambient')) return;
      const ccs = window.getComputedStyle(child);
      if (ccs.position === 'static') child.style.position = 'relative';
      const minZ = isSlide ? 4 : 3;
      if (!child.style.zIndex || ccs.zIndex === 'auto' || Number(ccs.zIndex) < minZ) {
        child.style.zIndex = String(minZ);
      }
    });

    const overlay = document.createElement('div');
    overlay.className = 'jml-banner-ambient';
    overlay.setAttribute('aria-hidden', 'true');

    const glow = document.createElement('div');
    glow.className = 'jml-banner-glow';

    const particles = document.createElement('div');
    particles.className = 'jml-banner-particles';

    const orbit = document.createElement('div');
    orbit.className = 'jml-banner-orbit';

    overlay.appendChild(glow);
    overlay.appendChild(particles);
    if (el.getBoundingClientRect().height >= 120) {
      overlay.appendChild(orbit);
    }

    el.insertBefore(overlay, el.firstChild);

    if (!REDUCED_MOTION) {
      el.addEventListener(
        'pointermove',
        (e) => {
          if (window.innerWidth < 768) return;
          const rect = el.getBoundingClientRect();
          if (!rect.width || !rect.height) return;
          const dx = ((e.clientX - rect.left) / rect.width - 0.5) * 24;
          const dy = ((e.clientY - rect.top) / rect.height - 0.5) * 18;
          glow.style.transform = `translate3d(${dx.toFixed(1)}px, calc(-50% + ${dy.toFixed(1)}px), 0)`;
        },
        { passive: true }
      );
      el.addEventListener('pointerleave', () => {
        glow.style.transform = 'translate3d(0, -50%, 0)';
      });
    }
  }

  function scanBanners() {
    document.querySelectorAll(BANNER_SELECTOR).forEach(mountBannerAmbient);
  }

  function init() {
    scanBanners();
    if (window.MutationObserver && document.body) {
      const mo = new MutationObserver(() => scanBanners());
      mo.observe(document.body, { childList: true, subtree: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
