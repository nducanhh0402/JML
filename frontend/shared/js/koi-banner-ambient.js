/* ==============================================================================
   JML STORE — 3D WEBGL MINI KOI FOR COLORED BANNERS
   Đưa chính những chú cá Koi 3D điêu khắc (Taisho Sanke, Vàng Kim 24K, Tancho,
   Showa) từ sảnh đăng nhập vào bơi uyển chuyển trên nền mọi banner màu của dự án.
   Kiến trúc: 1 Shared WebGLRenderer duy nhất + blit sang từng banner đang hiển thị
   -> không bao giờ hết WebGL context, giữ nguyên màu nền & chữ sắc nét, mượt 60fps.
   ============================================================================== */
(function () {
  'use strict';
  if (window.__JML_KOI_BANNER_LOADED__) return;
  window.__JML_KOI_BANNER_LOADED__ = true;

  const THREE_CDN = 'https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js';
  const REDUCED_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const BANNER_SELECTOR = [
    '.hero',
    '.main-slider .slide',
    '.side-banner',
    '.flash-sale-header',
    '.promo-banner',
    '.page-header',
    '.top-bar',
    '.topbar',
    '[data-koi-banner]',
    '[class*="bg-gradient-to-"]',
  ].join(', ');

  function ensureThree(cb) {
    if (window.THREE) { cb(window.THREE); return; }
    const existing = document.querySelector('script[data-jml-three]');
    if (existing) {
      existing.addEventListener('load', () => window.THREE && cb(window.THREE));
      return;
    }
    const sc = document.createElement('script');
    sc.src = THREE_CDN;
    sc.async = true;
    sc.dataset.jmlThree = '1';
    sc.onload = () => window.THREE && cb(window.THREE);
    document.head.appendChild(sc);
  }

  function start3DBannerEngine(THREE) {
    // ------------------------------------------------------------------
    // 1. SHARED WEBGL RENDERER & STUDIO IBL ENVIRONMENT (CHỈ 1 CONTEXT!)
    // ------------------------------------------------------------------
    let sharedRenderer;
    try {
      sharedRenderer = new THREE.WebGLRenderer({ antialias: false, alpha: true, powerPreference: 'high-performance' });
    } catch (e) {
      return; // Trình duyệt không hỗ trợ WebGL
    }
    sharedRenderer.setClearColor(0x000000, 0);
    sharedRenderer.shadowMap.enabled = false;
    sharedRenderer.outputEncoding = THREE.sRGBEncoding;
    sharedRenderer.toneMapping = THREE.ACESFilmicToneMapping;
    sharedRenderer.toneMappingExposure = 1.18;
    sharedRenderer.setPixelRatio(1);
    const maxAniso = Math.min(4, sharedRenderer.capabilities.getMaxAnisotropy());
    let curBufW = 0, curBufH = 0;

    // Bản đồ môi trường IBL tạo độ bóng ướt & ánh kim 24K cho cá Koi Vàng Kim
    const sharedEnvMap = (function buildEnv() {
      const ew = 256, eh = 128;
      const ecv = document.createElement('canvas'); ecv.width = ew; ecv.height = eh;
      const eg = ecv.getContext('2d');
      const g = eg.createLinearGradient(0, 0, 0, eh);
      g.addColorStop(0.0,  '#f4fbff');
      g.addColorStop(0.35, '#d6f0ff');
      g.addColorStop(0.55, '#96c4d8');
      g.addColorStop(0.80, '#4a5430');
      g.addColorStop(1.0,  '#242816');
      eg.fillStyle = g; eg.fillRect(0, 0, ew, eh);

      const sunG = eg.createRadialGradient(ew * 0.28, eh * 0.22, 2, ew * 0.28, eh * 0.22, 42);
      sunG.addColorStop(0.0, 'rgba(255,254,238,1)');
      sunG.addColorStop(0.45, 'rgba(255,246,210,0.65)');
      sunG.addColorStop(1.0, 'rgba(255,246,210,0)');
      eg.fillStyle = sunG; eg.fillRect(0, 0, ew, eh);

      const tex = new THREE.CanvasTexture(ecv);
      tex.mapping = THREE.EquirectangularReflectionMapping;
      tex.encoding = THREE.sRGBEncoding;
      const pmrem = new THREE.PMREMGenerator(sharedRenderer);
      pmrem.compileEquirectangularShader();
      const env = pmrem.fromEquirectangular(tex).texture;
      tex.dispose(); pmrem.dispose();
      return env;
    })();

    // ------------------------------------------------------------------
    // 2. TEXTURE 3D CÁ KOI (VẢY GINRIN + SOBEL NORMAL MAP + 4 DÒNG KOI THUẦN CHỦNG)
    // ------------------------------------------------------------------
    function heightToNormal(heightCanvas, strength = 2.6, wrapS = true) {
      const w = heightCanvas.width, h = heightCanvas.height;
      const hd = heightCanvas.getContext('2d').getImageData(0, 0, w, h).data;
      const nv = document.createElement('canvas'); nv.width = w; nv.height = h;
      const nCtx = nv.getContext('2d');
      const nImg = nCtx.createImageData(w, h);
      const nd = nImg.data;
      for (let y = 0; y < h; y++) {
        const ym = Math.max(0, y - 1), yp = Math.min(h - 1, y + 1);
        for (let x = 0; x < w; x++) {
          const xm = wrapS ? (x - 1 + w) % w : Math.max(0, x - 1);
          const xp = wrapS ? (x + 1) % w : Math.min(w - 1, x + 1);
          const tl = hd[(ym * w + xm) * 4] / 255, t = hd[(ym * w + x) * 4] / 255, tr = hd[(ym * w + xp) * 4] / 255;
          const l  = hd[(y  * w + xm) * 4] / 255, r = hd[(y  * w + xp) * 4] / 255;
          const bl = hd[(yp * w + xm) * 4] / 255, b = hd[(yp * w + x) * 4] / 255, br = hd[(yp * w + xp) * 4] / 255;
          const dx = (tr + 2 * r + br - tl - 2 * l - bl) * strength;
          const dy = (bl + 2 * b + br - tl - 2 * t - tr) * strength;
          const inv = 1 / Math.hypot(dx, dy, 1);
          const idx = (y * w + x) * 4;
          nd[idx]     = Math.round((-dx * inv * 0.5 + 0.5) * 255);
          nd[idx + 1] = Math.round((-dy * inv * 0.5 + 0.5) * 255);
          nd[idx + 2] = Math.round(( 1.0 * inv * 0.5 + 0.5) * 255);
          nd[idx + 3] = 255;
        }
      }
      nCtx.putImageData(nImg, 0, 0);
      const tex = new THREE.CanvasTexture(nv);
      if (wrapS) tex.wrapS = THREE.RepeatWrapping;
      tex.anisotropy = maxAniso;
      return tex;
    }

    const scaleDetailCache = {};
    function getScaleNormalRough(isGold) {
      const k = isGold ? 'g' : 's';
      if (scaleDetailCache[k]) return scaleDetailCache[k];
      const s = 512;
      const hv = document.createElement('canvas'); hv.width = s; hv.height = s;
      const b = hv.getContext('2d');
      const rv = document.createElement('canvas'); rv.width = s; rv.height = s;
      const rc = rv.getContext('2d');
      b.fillStyle = '#707070'; b.fillRect(0, 0, s, s);
      rc.fillStyle = isGold ? '#161616' : '#242424'; rc.fillRect(0, 0, s, s);

      const cols = 28, rows = 36, cw = s / cols, ch = (s * 0.76) / rows, sy = s * 0.215;
      for (let row = 0; row < rows; row++) {
        const y = sy + row * ch, stag = (row % 2) * cw * 0.5;
        for (let col = -1; col <= cols; col++) {
          const x = col * cw + stag;
          const bg = b.createRadialGradient(x, y + ch * 0.1, 1, x, y + ch * 0.2, cw * 0.54);
          bg.addColorStop(0, isGold ? '#f5f5f5' : '#e6e6e6');
          bg.addColorStop(0.7, '#989898');
          bg.addColorStop(1, '#202020');
          b.fillStyle = bg;
          b.beginPath(); b.arc(x, y, cw * 0.51, 0.1 * Math.PI, 0.9 * Math.PI); b.fill();

          rc.strokeStyle = isGold ? '#444444' : '#646464';
          rc.lineWidth = 1.6;
          rc.beginPath(); rc.arc(x, y + 0.5, cw * 0.51, 0.14 * Math.PI, 0.86 * Math.PI); rc.stroke();
        }
      }
      const normalMap = heightToNormal(hv, isGold ? 2.9 : 2.4, true);
      const roughnessMap = new THREE.CanvasTexture(rv);
      roughnessMap.wrapS = THREE.RepeatWrapping;
      scaleDetailCache[k] = { normalMap, roughnessMap };
      return scaleDetailCache[k];
    }

    const skinCache = {};
    function getKoiSkinMat(variant) {
      if (skinCache[variant]) return skinCache[variant];
      const isGold = variant === 'gold';
      const isTancho = variant === 'tancho';
      const isShowa = variant === 'showa';
      const size = 1024;
      const cv = document.createElement('canvas'); cv.width = size; cv.height = size;
      const c = cv.getContext('2d');

      if (isGold) {
        const g = c.createLinearGradient(0, 0, size, 0);
        g.addColorStop(0.0, '#f6e4aa'); g.addColorStop(0.20, '#f8cc4c'); g.addColorStop(0.40, '#f0a616');
        g.addColorStop(0.5, '#ffd852'); g.addColorStop(0.60, '#f0a616'); g.addColorStop(0.80, '#f8cc4c'); g.addColorStop(1.0, '#f6e4aa');
        c.fillStyle = g; c.fillRect(0, 0, size, size);
      } else {
        const g = c.createLinearGradient(0, 0, size, 0);
        g.addColorStop(0.0, '#dce6ec'); g.addColorStop(0.22, '#f4f7f9'); g.addColorStop(0.5, '#ffffff');
        g.addColorStop(0.78, '#f4f7f9'); g.addColorStop(1.0, '#dce6ec');
        c.fillStyle = g; c.fillRect(0, 0, size, size);
      }

      function spot(u, v, ru, rv, cIn, cOut, tilt = 0) {
        for (const off of [-1, 0, 1]) {
          const cx = (u + off) * size, cy = v * size, rx = ru * size, ry = rv * size;
          if (cx + rx < -40 || cx - rx > size + 40) continue;
          c.save(); c.translate(cx, cy); c.rotate(tilt);
          const g = c.createRadialGradient(-rx * 0.12, -ry * 0.12, rx * 0.08, 0, 0, Math.max(rx, ry));
          g.addColorStop(0, cIn); g.addColorStop(0.8, cOut); g.addColorStop(1, cOut);
          c.fillStyle = g; c.beginPath();
          for (let i = 0; i <= 32; i++) {
            const a = (i / 32) * Math.PI * 2;
            const wb = 1 + 0.08 * Math.sin(a * 3 + u * 11) + 0.04 * Math.cos(a * 5 + v * 8);
            const px = Math.cos(a) * rx * wb, py = Math.sin(a) * ry * wb;
            if (i === 0) c.moveTo(px, py); else c.lineTo(px, py);
          }
          c.closePath(); c.fill(); c.restore();
        }
      }

      if (isTancho) {
        spot(0.50, 0.105, 0.095, 0.058, '#ff3a28', '#c6120e', 0);
        spot(0.36, 0.58,  0.052, 0.036, '#20242c', '#07080b', -0.2);
        spot(0.62, 0.78,  0.045, 0.030, '#20242c', '#07080b',  0.2);
      } else if (isShowa) {
        spot(0.48, 0.10, 0.13, 0.075, '#f53826', '#b81410', -0.1);
        spot(0.54, 0.42, 0.25, 0.150, '#f53826', '#b81410', 0.14);
        spot(0.46, 0.76, 0.19, 0.095, '#f53826', '#b81410', -0.1);
        spot(0.50, 0.22, 0.22, 0.075, '#22252c', '#07080b', 0.18);
        spot(0.30, 0.36, 0.12, 0.080, '#22252c', '#07080b', -0.2);
        spot(0.70, 0.52, 0.14, 0.085, '#22252c', '#07080b', 0.2);
        spot(0.46, 0.64, 0.15, 0.070, '#22252c', '#07080b', -0.1);
      } else if (!isGold) {
        // Taisho Sanke
        spot(0.50, 0.11, 0.16, 0.085, '#f53826', '#b81410', 0.05);
        spot(0.36, 0.34, 0.20, 0.135, '#f53826', '#b81410', -0.25);
        spot(0.62, 0.37, 0.17, 0.120, '#f53826', '#b81410', 0.22);
        spot(0.50, 0.62, 0.24, 0.145, '#f53826', '#b81410', 0.08);
        spot(0.44, 0.85, 0.15, 0.075, '#f53826', '#b81410', -0.1);
        for (const [u, v, ru, rv, t] of [
          [0.30, 0.23, 0.075, 0.055, -0.3], [0.70, 0.24, 0.070, 0.052, 0.3],
          [0.26, 0.48, 0.090, 0.060,  0.2], [0.74, 0.47, 0.085, 0.055, -0.2],
          [0.46, 0.53, 0.080, 0.052, -0.1], [0.64, 0.68, 0.085, 0.055, 0.2],
          [0.34, 0.74, 0.072, 0.048, -0.2],
        ]) spot(u, v, ru, rv, '#22252c', '#07080b', t);
      }

      // Vẽ vảy Ginrin / Kin Matsuba xếp lớp 3D
      const cols = 28, rows = 36, cw = size / cols, ch = (size * 0.76) / rows, sy = size * 0.215;
      for (let row = 0; row < rows; row++) {
        const y = sy + row * ch, stag = (row % 2) * cw * 0.5;
        for (let col = -1; col <= cols; col++) {
          const x = col * cw + stag;
          c.strokeStyle = isGold ? 'rgba(136, 72, 4, 0.36)' : 'rgba(12, 20, 26, 0.18)';
          c.lineWidth = isGold ? 2.4 : 1.8;
          c.beginPath(); c.arc(x, y + 1, cw * 0.51, 0.14 * Math.PI, 0.86 * Math.PI); c.stroke();

          c.strokeStyle = isGold ? 'rgba(255, 250, 214, 0.60)' : 'rgba(255, 255, 255, 0.34)';
          c.lineWidth = 1.2;
          c.beginPath(); c.arc(x, y - 1, cw * 0.45, 0.22 * Math.PI, 0.78 * Math.PI); c.stroke();
        }
      }

      const map = new THREE.CanvasTexture(cv);
      map.encoding = THREE.sRGBEncoding;
      map.wrapS = THREE.RepeatWrapping;
      map.anisotropy = maxAniso;
      const { normalMap, roughnessMap } = getScaleNormalRough(isGold);

      skinCache[variant] = new THREE.MeshPhysicalMaterial({
        map,
        normalMap,
        normalScale: new THREE.Vector2(isGold ? 0.90 : 0.72, isGold ? 0.90 : 0.72),
        roughnessMap,
        roughness: isGold ? 0.38 : 0.62,
        metalness: isGold ? 0.62 : 0.06,
        emissive: isGold ? 0x422800 : 0x000000,
        emissiveIntensity: isGold ? 0.22 : 0.0,
        clearcoat: 1.0,
        clearcoatRoughness: isGold ? 0.04 : 0.06,
        envMap: sharedEnvMap,
        envMapIntensity: isGold ? 1.85 : 1.25,
      });
      return skinCache[variant];
    }

    const finMatCache = {};
    function getFinMat(style, palette) {
      const key = `${style}-${palette}`;
      if (finMatCache[key]) return finMatCache[key];
      const w = 512, h = 512;
      const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
      const g = cv.getContext('2d');
      const isGold = palette === 'gold';
      const isTancho = palette === 'tancho';

      const grd = style === 'dorsal' ? g.createLinearGradient(0, h, 0, 0) : g.createLinearGradient(0, 0, w, 0);
      if (isGold) {
        grd.addColorStop(0.0, 'rgba(244,178,24,0.96)');
        grd.addColorStop(0.45, 'rgba(255,216,84,0.88)');
        grd.addColorStop(0.84, 'rgba(255,244,186,0.52)');
        grd.addColorStop(1.0, 'rgba(255,252,232,0)');
      } else if (isTancho) {
        grd.addColorStop(0.0, 'rgba(252,254,255,0.95)');
        grd.addColorStop(0.55, 'rgba(244,250,255,0.78)');
        grd.addColorStop(1.0, 'rgba(255,255,255,0)');
      } else {
        grd.addColorStop(0.0, 'rgba(252,254,253,0.96)');
        grd.addColorStop(0.38, 'rgba(226,40,32,0.86)');
        grd.addColorStop(0.76, 'rgba(18,20,26,0.82)');
        grd.addColorStop(0.92, 'rgba(250,252,250,0.44)');
        grd.addColorStop(1.0, 'rgba(255,255,255,0)');
      }
      g.fillStyle = grd; g.fillRect(0, 0, w, h);

      for (let i = 0; i < 32; i++) {
        const f = i / 31;
        g.strokeStyle = isGold ? 'rgba(255,250,210,0.55)' : 'rgba(255,255,255,0.38)';
        g.lineWidth = i % 2 === 0 ? 1.8 : 1.0;
        g.beginPath();
        if (style === 'dorsal') {
          g.moveTo(f * w, h); g.quadraticCurveTo(f * w - 20, h * 0.5, f * w - 40, 0);
        } else {
          g.moveTo(0, h * (0.34 + f * 0.32)); g.quadraticCurveTo(w * 0.52, h * (0.14 + f * 0.72), w, h * f);
        }
        g.stroke();
      }
      const tex = new THREE.CanvasTexture(cv);
      tex.encoding = THREE.sRGBEncoding;
      finMatCache[key] = new THREE.MeshPhysicalMaterial({
        map: tex,
        transparent: true,
        opacity: 0.94,
        side: THREE.DoubleSide,
        roughness: isGold ? 0.18 : 0.24,
        metalness: isGold ? 0.34 : 0.02,
        clearcoat: 0.8,
        envMap: sharedEnvMap,
        depthWrite: false,
      });
      return finMatCache[key];
    }

    // ------------------------------------------------------------------
    // 3. ĐIÊU KHẮC HÌNH KHỐI 3D CÁ KOI CHUẨN NHƯ SẢNH ĐĂNG NHẬP
    // ------------------------------------------------------------------
    const NOSE_Z = 1.9, TAIL_Z = -2.2, KOI_LEN = NOSE_Z - TAIL_Z;

    function koiCrossSection(t) {
      const s = Math.max(0, Math.min(1, t));
      const snout = Math.pow(Math.sin(Math.min(1, s * 1.03) * Math.PI), 0.66);
      const taper = 1.0 - 0.42 * Math.pow(s, 1.35);
      const halfW = snout * taper * 0.62 + (s > 0.78 ? ((s - 0.78) / 0.22) * 0.075 : 0);
      const topH  = Math.pow(Math.sin(Math.min(1, s * 1.02) * Math.PI), 0.70) * (0.70 - 0.24 * s) + (s > 0.8 ? ((s - 0.8) / 0.2) * 0.14 : 0);
      const botH  = Math.pow(Math.sin(Math.min(1, s * 1.01) * Math.PI), 0.74) * (0.56 - 0.22 * s) + (s > 0.8 ? ((s - 0.8) / 0.2) * 0.12 : 0);
      const gill  = Math.exp(-Math.pow((s - 0.21) / 0.055, 2)) * 0.035;
      const centerY = Math.sin(s * Math.PI) * 0.06 - (s < 0.2 ? (0.2 - s) * 0.22 : 0);
      return { halfW: halfW + gill, topH, botH, centerY };
    }

    function buildBodyGeo() {
      const rings = 34, radial = 20;
      const pos = [], uvs = [], idx = [];
      for (let i = 0; i <= rings; i++) {
        const t = i / rings, z = NOSE_Z - t * KOI_LEN, cs = koiCrossSection(t);
        for (let j = 0; j <= radial; j++) {
          const u = j / radial, th = (u - 0.5) * Math.PI * 2;
          const sinT = Math.sin(th), cosT = Math.cos(th);
          const rx = cs.halfW * sinT * (cosT > 0 ? (1 - 0.06 * cosT) : (1 - 0.14 * (-cosT)));
          const ry = (cosT >= 0 ? cs.topH * cosT : cs.botH * cosT) + cs.centerY;
          pos.push(rx, ry, z); uvs.push(u, t);
        }
      }
      const st = radial + 1;
      for (let i = 0; i < rings; i++) for (let j = 0; j < radial; j++) {
        const a = i * st + j, b = (i + 1) * st + j, c = (i + 1) * st + j + 1, d = i * st + j + 1;
        idx.push(a, d, b, b, d, c);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
      geo.setIndex(idx);
      geo.computeVertexNormals();
      geo.userData.basePos = new Float32Array(pos);
      return geo;
    }

    function buildTailGeo() {
      const segZ = 10, segY = 8, pos = [], uvs = [], idx = [];
      for (let i = 0; i <= segZ; i++) {
        const f = i / segZ;
        for (let j = 0; j <= segY; j++) {
          const v = j / segY, ny = (v - 0.5) * 2;
          const indent = Math.exp(-Math.pow(ny / 0.36, 2)) * 0.28 * f * f;
          pos.push(0, ny * (0.15 + Math.pow(f, 0.72) * 0.92), TAIL_Z + 0.12 - f * (1.42 - indent));
          uvs.push(f, v);
        }
      }
      const st = segY + 1;
      for (let i = 0; i < segZ; i++) for (let j = 0; j < segY; j++) {
        const a = i * st + j, b = (i + 1) * st + j, c = (i + 1) * st + j + 1, d = i * st + j + 1;
        idx.push(a, b, d, b, c, d);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
      geo.setIndex(idx); geo.computeVertexNormals();
      geo.userData.basePos = new Float32Array(pos);
      return geo;
    }

    function buildDorsalGeo() {
      const segZ = 12, segY = 4, pos = [], uvs = [], idx = [];
      for (let i = 0; i <= segZ; i++) {
        const f = i / segZ, z = 0.58 - 1.80 * f, cs = koiCrossSection((NOSE_Z - z) / KOI_LEN);
        const by = cs.topH + cs.centerY - 0.06, fh = Math.sin(Math.pow(f, 0.8) * Math.PI) * 0.62 + 0.06;
        for (let j = 0; j <= segY; j++) {
          const h = j / segY;
          pos.push(0, by + h * fh, z - h * 0.24 * (0.4 + 0.6 * f));
          uvs.push(f, h);
        }
      }
      const st = segY + 1;
      for (let i = 0; i < segZ; i++) for (let j = 0; j < segY; j++) {
        const a = i * st + j, b = (i + 1) * st + j, c = (i + 1) * st + j + 1, d = i * st + j + 1;
        idx.push(a, b, d, b, c, d);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
      geo.setIndex(idx); geo.computeVertexNormals();
      geo.userData.basePos = new Float32Array(pos);
      return geo;
    }

    function buildPecGeo(side) {
      const segR = 8, segC = 6, pos = [], uvs = [], idx = [];
      for (let i = 0; i <= segR; i++) {
        const r = i / segR;
        for (let j = 0; j <= segC; j++) {
          const c = j / segC, fa = (c - 0.35) * 1.15, reach = r * (1.12 - Math.abs(c - 0.45) * 0.36);
          pos.push(side * Math.cos(fa * 0.5) * reach * 0.92, -r * 0.34 - Math.sin(r * Math.PI) * 0.08 + (0.5 - c) * 0.14 * r, -Math.sin(fa) * reach * 0.85 - r * 0.42);
          uvs.push(r, c);
        }
      }
      const st = segC + 1;
      for (let i = 0; i < segR; i++) for (let j = 0; j < segC; j++) {
        const a = i * st + j, b = (i + 1) * st + j, c = (i + 1) * st + j + 1, d = i * st + j + 1;
        idx.push(a, b, d, b, c, d);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
      geo.setIndex(idx); geo.computeVertexNormals();
      geo.userData.basePos = new Float32Array(pos);
      return geo;
    }

    const eyeGeo = new THREE.SphereGeometry(0.11, 12, 12);
    const pupilGeo = new THREE.SphereGeometry(0.082, 10, 10);
    const pupilMat = new THREE.MeshPhysicalMaterial({ color: 0x030407, roughness: 0.04, clearcoat: 1.0, envMap: sharedEnvMap });
    const irisStdMat = new THREE.MeshPhysicalMaterial({ color: 0xe6dec2, roughness: 0.18, metalness: 0.35, clearcoat: 0.9, envMap: sharedEnvMap });
    const irisGoldMat = new THREE.MeshPhysicalMaterial({ color: 0xffd75e, roughness: 0.14, metalness: 0.68, clearcoat: 0.9, envMap: sharedEnvMap });
    const barbelStdMat = new THREE.MeshStandardMaterial({ color: 0xf6f4f0, roughness: 0.3 });
    const barbelGoldMat = new THREE.MeshStandardMaterial({ color: 0xf7cf5c, roughness: 0.2, metalness: 0.45 });

    function createBannerKoi3D(variant, scale) {
      const isGold = variant === 'gold';
      const finPalette = isGold ? 'gold' : (variant === 'tancho' ? 'tancho' : 'sanke');
      const group = new THREE.Group();
      group.scale.setScalar(scale);

      const bodyMesh = new THREE.Mesh(buildBodyGeo(), getKoiSkinMat(variant));
      bodyMesh.castShadow = true;
      group.add(bodyMesh);

      const tailMesh = new THREE.Mesh(buildTailGeo(), getFinMat('tail', finPalette));
      tailMesh.castShadow = true;
      group.add(tailMesh);

      const dorsalMesh = new THREE.Mesh(buildDorsalGeo(), getFinMat('dorsal', finPalette));
      group.add(dorsalMesh);

      const pecMat = getFinMat('pectoral', finPalette);
      const pecLeft = new THREE.Mesh(buildPecGeo(-1), pecMat);
      pecLeft.position.set(-0.44, -0.14, 0.72);
      pecLeft.castShadow = true;
      group.add(pecLeft);

      const pecRight = new THREE.Mesh(buildPecGeo(1), pecMat);
      pecRight.position.set(0.44, -0.14, 0.72);
      pecRight.castShadow = true;
      group.add(pecRight);

      const eyeGroup = new THREE.Group();
      for (const side of [-1, 1]) {
        const iris = new THREE.Mesh(eyeGeo, isGold ? irisGoldMat : irisStdMat);
        iris.position.set(side * 0.315, 0.08, 1.30); iris.scale.set(0.7, 1, 1.04);
        const pupil = new THREE.Mesh(pupilGeo, pupilMat);
        pupil.position.set(side * 0.348, 0.08, 1.318); pupil.scale.set(0.62, 0.92, 0.92);
        eyeGroup.add(iris, pupil);
      }
      group.add(eyeGroup);

      const barbels = [];
      for (const side of [-1, 1]) {
        const curve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(side * 0.14, -0.10, 1.72),
          new THREE.Vector3(side * 0.28, -0.18, 1.54),
          new THREE.Vector3(side * 0.36, -0.28, 1.32),
        ]);
        const bm = new THREE.Mesh(new THREE.TubeGeometry(curve, 8, 0.018, 5, false), isGold ? barbelGoldMat : barbelStdMat);
        group.add(bm);
        barbels.push({ mesh: bm, side });
      }

      return { group, bodyMesh, tailMesh, dorsalMesh, pecLeft, pecRight, eyeGroup, barbels };
    }

    function spineWaveX(z, phase, turnBend) {
      const u = Math.max(0, (NOSE_Z - z) / KOI_LEN);
      return Math.sin(phase - u * 4.7) * (0.02 + 0.36 * u * u) + turnBend * 0.65 * u * u;
    }

    function deformKoi3D(koi, phase, turnBend) {
      // Thân cá uốn sin 3D
      const bPos = koi.bodyMesh.geometry.attributes.position, bBase = koi.bodyMesh.geometry.userData.basePos;
      for (let i = 0; i < bPos.count; i++) {
        const bz = bBase[i * 3 + 2];
        bPos.setXYZ(i, bBase[i * 3] + spineWaveX(bz, phase, turnBend), bBase[i * 3 + 1], bz);
      }
      bPos.needsUpdate = true;
      koi.bodyMesh.geometry.computeVertexNormals();

      // Vây đuôi uốn sóng trễ pha
      const tPos = koi.tailMesh.geometry.attributes.position, tBase = koi.tailMesh.geometry.userData.basePos;
      for (let i = 0; i < tPos.count; i++) {
        const bz = tBase[i * 3 + 2];
        let dx = spineWaveX(bz, phase, turnBend);
        if (bz < TAIL_Z) {
          const tf = Math.min(1, (TAIL_Z - bz) / 1.45);
          dx += Math.sin(phase - 5.4 - tf * 2.4) * 0.35 * tf * tf;
        }
        tPos.setXYZ(i, tBase[i * 3] + dx, tBase[i * 3 + 1], bz);
      }
      tPos.needsUpdate = true;

      // Vây lưng
      const dPos = koi.dorsalMesh.geometry.attributes.position, dBase = koi.dorsalMesh.geometry.userData.basePos, dUv = koi.dorsalMesh.geometry.attributes.uv;
      for (let i = 0; i < dPos.count; i++) {
        const bz = dBase[i * 3 + 2], h = dUv.getY(i);
        dPos.setXYZ(i, dBase[i * 3] + spineWaveX(bz, phase, turnBend) + Math.sin(phase - 2.6 - h * 2.2) * 0.16 * h, dBase[i * 3 + 1], bz);
      }
      dPos.needsUpdate = true;

      // Cặp vây ngực ve vẩy
      for (const [mesh, side] of [[koi.pecLeft, -1], [koi.pecRight, 1]]) {
        const pPos = mesh.geometry.attributes.position, pBase = mesh.geometry.userData.basePos, pUv = mesh.geometry.attributes.uv;
        const lp = phase + (side > 0 ? 0 : 0.85);
        for (let i = 0; i < pPos.count; i++) {
          const r = pUv.getX(i), c = pUv.getY(i);
          pPos.setXYZ(i, pBase[i * 3], pBase[i * 3 + 1] + Math.sin(lp - r * 2.1 - c * 0.6) * 0.24 * r, pBase[i * 3 + 2] + Math.cos(lp - r * 1.6) * 0.18 * r);
        }
        pPos.needsUpdate = true;
        mesh.position.x = side * 0.44 + spineWaveX(0.72, phase, turnBend);
      }

      koi.eyeGroup.position.x = spineWaveX(1.30, phase, turnBend);
      const sDx = spineWaveX(1.70, phase, turnBend);
      for (const b of koi.barbels) {
        b.mesh.position.x = sDx;
        b.mesh.rotation.z = b.side * Math.sin(phase * 0.85 - 0.5) * 0.10 - turnBend * 0.12;
      }
    }

    // ------------------------------------------------------------------
    // 4. QUẢN LÝ CÁC BANNER 3D ĐANG HIỂN THỊ TRÊN TRANG
    // ------------------------------------------------------------------
    const bannerInstances = [];

    function isValidBannerTarget(el) {
      if (!el || el.nodeType !== 1) return false;
      if (el.dataset.koiAmbientMounted === '1') return false;
      if (el.closest('#koi-3d-wrap') || el.closest('.auth-card')) return false;
      if (el.tagName === 'BUTTON' || el.tagName === 'A' || el.tagName === 'SPAN' || el.tagName === 'IMG') return false;
      const rect = el.getBoundingClientRect();
      if (rect.width < 150 || rect.height < 26) return false;
      const parentMounted = el.parentElement && el.parentElement.closest('[data-koi-ambient-mounted="1"]');
      if (parentMounted && !el.classList.contains('side-banner') && !el.classList.contains('flash-sale-header')) return false;
      return true;
    }

    function mountKoiBanner3D(el) {
      if (!isValidBannerTarget(el)) return;
      el.dataset.koiAmbientMounted = '1';

      const cs = window.getComputedStyle(el);
      if (cs.position === 'static') el.style.position = 'relative';
      if (cs.overflow === 'visible') el.style.overflow = 'hidden';

      const isSlide = el.classList.contains('slide');
      Array.from(el.children).forEach((child) => {
        if (child.classList && child.classList.contains('koi-banner-canvas')) return;
        const ccs = window.getComputedStyle(child);
        if (ccs.position === 'static') child.style.position = 'relative';
        const minZ = isSlide ? 4 : 3;
        if (!child.style.zIndex || ccs.zIndex === 'auto' || Number(ccs.zIndex) < minZ) {
          child.style.zIndex = String(minZ);
        }
      });

      const canvas = document.createElement('canvas');
      canvas.className = 'koi-banner-canvas';
      canvas.setAttribute('aria-hidden', 'true');
      canvas.style.cssText = `position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:${isSlide ? 2 : 1};display:block;`;
      el.insertBefore(canvas, el.firstChild);

      const ctx = canvas.getContext('2d');
      const scene = new THREE.Scene();
      scene.environment = sharedEnvMap;

      // Ánh sáng 3D chuyên biệt để cá Koi nổi khối thật & đổ bóng mềm ngay lên nền màu banner
      scene.add(new THREE.HemisphereLight(0xf6f9ee, 0x3b4024, 1.22));
      const sun = new THREE.DirectionalLight(0xfff7e2, 1.60);
      sun.position.set(-4.5, 11.5, 6.5);
      sun.castShadow = false;
      scene.add(sun);

      const rim = new THREE.DirectionalLight(0xfff2cf, 0.68);
      rim.position.set(6, 4.0, -7);
      scene.add(rim);

      const shadowPlane = { position: { y: -1.15 } };

      // OrthographicCamera:
      // - Trên banner lớn/vừa (Hero, Side Banner, Flash Sale...): góc nhìn hồ từ trên chếch xuống cực nghệ thuật & hài hòa
      // - Trên thanh mảnh (.topbar / .top-bar): góc nhìn ngang 3/4 khoe trọn thân cá 3D bơi qua lại
      const camera = new THREE.OrthographicCamera(-6, 6, 3, -3, 0.1, 60);

      const inst = {
        el, canvas, ctx, scene, camera, shadowPlane,
        w: 0, h: 0, dpr: 1, halfW: 6, halfH: 3, isSlim: false,
        actors: [], ripples: [],
        mouse: { x: -999, y: -999, wx: 0, wy: 0, wz: 0, active: false, lastRipple: 0 },
        visible: true,
      };

      function syncSize() {
        const rect = el.getBoundingClientRect();
        if (rect.width < 20 || rect.height < 16) return;
        inst.w = Math.round(rect.width);
        inst.h = Math.round(rect.height);
        inst.dpr = 1;
        canvas.width = inst.w;
        canvas.height = inst.h;
        ctx.setTransform(1, 0, 0, 1, 0, 0);

        inst.isSlim = inst.h < 68;
        if (inst.isSlim) {
          camera.position.set(0, 1.5, 14.5);
          camera.lookAt(0, 0, 0);
          const pxPerUnit = Math.max(10.5, inst.h / 3.2);
          inst.halfW = (inst.w / pxPerUnit) * 0.5;
          inst.halfH = (inst.h / pxPerUnit) * 0.5;
          shadowPlane.position.y = -inst.halfH + 0.12;
        } else {
          camera.position.set(0, 14.0, 2.6);
          camera.lookAt(0, -0.1, 0);
          const pxPerUnit = Math.max(22, Math.min(44, inst.h / 7.6));
          inst.halfW = (inst.w / pxPerUnit) * 0.5;
          inst.halfH = (inst.h / pxPerUnit) * 0.5;
          shadowPlane.position.y = -1.15;
        }

        camera.left = -inst.halfW;
        camera.right = inst.halfW;
        camera.top = inst.halfH;
        camera.bottom = -inst.halfH;
        camera.updateProjectionMatrix();

        if (!inst.actors.length) {
          const isLarge = inst.h >= 210 && inst.w >= 420;
          const count = inst.isSlim ? 2 : (isLarge ? 2 : 1);
          const breeds = ['sanke', 'gold', 'tancho', 'showa'];
          const baseScale = inst.isSlim ? 0.62 : (isLarge ? 0.60 : 0.50);
          for (let i = 0; i < count; i++) {
            const sc = baseScale * (i === 0 ? 1.06 : (i === 1 ? 0.96 : 0.84));
            const koi = createBannerKoi3D(breeds[i % breeds.length], sc);
            scene.add(koi.group);
            if (inst.isSlim) {
              const dir = i % 2 === 0 ? 1 : -1;
              const startX = -inst.halfW * 0.72 + (i / Math.max(1, count - 1)) * inst.halfW * 1.44;
              const startY = i % 2 === 0 ? 0.12 : -0.18;
              const startZ = i % 2 === 0 ? 0.4 : -0.4;
              const startYaw = dir > 0 ? Math.PI * 0.5 : -Math.PI * 0.5;
              koi.group.position.set(startX, startY, startZ);
              inst.actors.push({
                koi, scale: sc,
                x: startX, y: startY, baseY: startY, targetY: startY, z: startZ,
                yaw: startYaw, targetYaw: startYaw, yawRate: 0, pitch: 0, smoothTurn: 0,
                cruiseSpeed: 3.2 + (i % 2) * 0.65,
                swimPhase: Math.random() * Math.PI * 2,
                turnTimer: 1.8 + Math.random() * 2.8,
                yPhase: Math.random() * Math.PI * 2,
              });
            } else {
              // Banner vừa/lớn: ưu tiên rải cá thoáng lệch nhẹ về phía phải/trống để tôn chữ bên trái
              const startX = inst.halfW * (0.1 + (Math.random() - 0.35) * 1.15);
              const startZ = (Math.random() - 0.5) * inst.halfH * 1.25;
              const startY = 0.08 - i * 0.14;
              const startYaw = Math.random() * Math.PI * 2;
              koi.group.position.set(startX, startY, startZ);
              inst.actors.push({
                koi, scale: sc,
                x: startX, y: startY, baseY: startY, targetY: startY, z: startZ,
                yaw: startYaw, targetYaw: startYaw, yawRate: 0, pitch: 0, smoothTurn: 0,
                cruiseSpeed: 1.55 + Math.random() * 0.45,
                swimPhase: Math.random() * Math.PI * 2,
                turnTimer: 1.6 + Math.random() * 2.8,
                yPhase: Math.random() * Math.PI * 2,
              });
            }
          }
        }
      }

      syncSize();
      if (window.ResizeObserver) new ResizeObserver(syncSize).observe(el);

      el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const mx = e.clientX - rect.left, my = e.clientY - rect.top;
        inst.mouse.x = mx; inst.mouse.y = my;
        inst.mouse.wx = ((mx / Math.max(1, inst.w)) * 2 - 1) * inst.halfW;
        inst.mouse.wy = -((my / Math.max(1, inst.h)) * 2 - 1) * inst.halfH;
        inst.mouse.wz = ((my / Math.max(1, inst.h)) * 2 - 1) * inst.halfH;
        inst.mouse.active = true;
        const now = performance.now();
        if (now - inst.mouse.lastRipple > 160 && inst.ripples.length < 10) {
          inst.mouse.lastRipple = now;
          inst.ripples.push({ x: mx, y: my, r: 2, maxR: 22, alpha: 0.28 });
        }
      });
      el.addEventListener('mouseleave', () => { inst.mouse.active = false; });

      if (window.IntersectionObserver) {
        new IntersectionObserver((entries) => {
          inst.visible = entries[0].isIntersecting;
        }, { threshold: 0.02 }).observe(el);
      }

      bannerInstances.push(inst);
    }

    function updateBannerActors(inst, dt, elapsed) {
      const spMul = REDUCED_MOTION ? 0.3 : 1.0;
      const effDt = dt * spMul;
      const hw = inst.halfW, hh = inst.halfH;

      for (let i = 0; i < inst.actors.length; i++) {
        const a = inst.actors[i];
        a.turnTimer -= dt;

        if (inst.isSlim) {
          // Thanh ngang mỏng (.topbar / .top-bar): cá 3D bơi góc ngang khoe trọn thân bên, vây lưng & đuôi quạt
          const dir = Math.sin(a.yaw) >= 0 ? 1 : -1;
          a.targetYaw = (dir > 0 ? Math.PI * 0.5 : -Math.PI * 0.5) + Math.sin(elapsed * 0.8 + i * 2.1) * 0.14;
          a.targetY = Math.sin(elapsed * 1.15 + a.yPhase) * Math.min(0.45, hh * 0.30);
          if (a.x > hw + 3.6) { a.x = -hw - 3.2; a.z = (Math.random() - 0.5) * 1.1; }
          else if (a.x < -hw - 3.6) { a.x = hw + 3.2; a.z = (Math.random() - 0.5) * 1.1; }

          let angDiff = a.targetYaw - a.yaw;
          while (angDiff > Math.PI) angDiff -= Math.PI * 2;
          while (angDiff < -Math.PI) angDiff += Math.PI * 2;
          const desiredRate = THREE.MathUtils.clamp(angDiff * 2.4, -1.9, 1.9);
          a.yawRate += (desiredRate - a.yawRate) * (1 - Math.exp(-6.5 * effDt));
          a.yaw += a.yawRate * effDt;

          const step = a.cruiseSpeed * effDt;
          const prevY = a.y;
          a.x += Math.sin(a.yaw) * step;
          a.z = THREE.MathUtils.clamp(a.z + Math.cos(a.yaw) * step, -1.8, 1.8);
          a.y += (THREE.MathUtils.clamp(a.targetY, -hh * 0.65, hh * 0.65) - a.y) * (1 - Math.exp(-2.4 * effDt));
          const targetPitch = THREE.MathUtils.clamp(-Math.atan2(a.y - prevY, Math.max(0.001, step)), -0.28, 0.28);
          a.pitch += (targetPitch - a.pitch) * (1 - Math.exp(-6.0 * effDt));
          a.smoothTurn += (THREE.MathUtils.clamp(a.yawRate * 0.45, -1, 1) - a.smoothTurn) * (1 - Math.exp(-7 * effDt));

          a.koi.group.position.set(a.x, a.y, a.z);
          a.koi.group.rotation.order = 'YXZ';
          a.koi.group.rotation.y = a.yaw;
          a.koi.group.rotation.x = a.pitch;
          a.koi.group.rotation.z = -a.smoothTurn * 0.28;
          a.swimPhase += (0.10 + step * 1.65) * (dt * 60) * spMul;
          deformKoi3D(a.koi, a.swimPhase, a.smoothTurn);
        } else {
          // Banner vừa & lớn (Hero, Side Banner, Flash Sale...): góc nhìn hồ trên xuống sang trọng, tự do uốn lượn 360° & đổ bóng 3D mềm!
          if (a.turnTimer <= 0) {
            a.turnTimer = 2.0 + Math.random() * 3.0;
            a.targetYaw += (Math.random() - 0.5) * 1.45;
          }

          if (inst.mouse.active) {
            const mdx = a.x - inst.mouse.wx, mdz = a.z - inst.mouse.wz;
            const md = Math.hypot(mdx, mdz);
            if (md > 0.2 && md < 3.4) {
              a.targetYaw = Math.atan2(mdx, mdz) + 0.35;
            }
          }

          for (let j = 0; j < inst.actors.length; j++) {
            if (i === j) continue;
            const b = inst.actors[j];
            const dx = a.x - b.x, dz = a.z - b.z;
            const d = Math.hypot(dx, dz);
            if (d > 0.01 && d < 2.2) {
              const away = Math.atan2(dx, dz);
              let da = away - a.targetYaw;
              while (da > Math.PI) da -= Math.PI * 2;
              while (da < -Math.PI) da += Math.PI * 2;
              a.targetYaw += da * Math.min(1, dt * 2.8);
            }
          }

          const mx = hw * 0.88, mz = hh * 0.78;
          if (Math.abs(a.x) > mx || Math.abs(a.z) > mz) {
            const toCenter = Math.atan2(-a.x * 0.7, -a.z * 0.7);
            let dc = toCenter - a.targetYaw;
            while (dc > Math.PI) dc -= Math.PI * 2;
            while (dc < -Math.PI) dc += Math.PI * 2;
            a.targetYaw += dc * Math.min(1, dt * 2.6);
          }

          let angDiff = a.targetYaw - a.yaw;
          while (angDiff > Math.PI) angDiff -= Math.PI * 2;
          while (angDiff < -Math.PI) angDiff += Math.PI * 2;
          const desiredRate = THREE.MathUtils.clamp(angDiff * 2.5, -2.0, 2.0);
          a.yawRate += (desiredRate - a.yawRate) * (1 - Math.exp(-7.0 * effDt));
          a.yaw += a.yawRate * effDt;

          const step = a.cruiseSpeed * effDt;
          a.x += Math.sin(a.yaw) * step;
          a.z += Math.cos(a.yaw) * step;
          a.y = a.baseY + Math.sin(elapsed * 1.1 + i * 1.9) * 0.14;

          a.smoothTurn += (THREE.MathUtils.clamp(a.yawRate * 0.45, -1, 1) - a.smoothTurn) * (1 - Math.exp(-7 * effDt));
          a.koi.group.position.set(a.x, a.y, a.z);
          a.koi.group.rotation.order = 'YXZ';
          a.koi.group.rotation.y = a.yaw;
          a.koi.group.rotation.x = 0;
          a.koi.group.rotation.z = -a.smoothTurn * 0.28;

          a.swimPhase += (0.10 + step * 1.65) * (dt * 60) * spMul;
          deformKoi3D(a.koi, a.swimPhase, a.smoothTurn);
        }
      }
    }

    // ------------------------------------------------------------------
    // 5. VÒNG LẶP RENDER TỐI ƯU (KHÔNG REALLOCATE WEBGL BUFFER, TẠM DỪNG KHI CUỘN)
    // ------------------------------------------------------------------
    let lastNow = performance.now();
    let isScrolling = false;
    let scrollResumeTimer = null;
    window.addEventListener('scroll', () => {
      isScrolling = true;
      clearTimeout(scrollResumeTimer);
      scrollResumeTimer = setTimeout(() => { isScrolling = false; }, 120);
    }, { passive: true });

    const FRAME_INTERVAL = 1000 / 30; // 30fps mượt và nhẹ GPU

    function tick(now) {
      requestAnimationFrame(tick);
      if (document.hidden || isScrolling) {
        lastNow = now;
        return;
      }
      const deltaMs = now - lastNow;
      if (deltaMs < FRAME_INTERVAL) return;
      const dt = Math.min(deltaMs / 1000, 0.05);
      lastNow = now;
      const elapsed = now * 0.001;

      for (let i = 0; i < bannerInstances.length; i++) {
        const inst = bannerInstances[i];
        if (!inst.visible || !inst.w || !inst.h || !document.body.contains(inst.el)) continue;
        if (inst.el.classList.contains('slide') && !inst.el.classList.contains('active')) continue;

        updateBannerActors(inst, dt, elapsed);

        const pw = inst.w;
        const ph = inst.h;
        if (pw > curBufW || ph > curBufH) {
          curBufW = Math.max(curBufW, pw, 1280);
          curBufH = Math.max(curBufH, ph, 420);
          sharedRenderer.setSize(curBufW, curBufH, false);
        }

        const vy = curBufH - ph;
        sharedRenderer.setViewport(0, vy, pw, ph);
        sharedRenderer.setScissor(0, vy, pw, ph);
        sharedRenderer.setScissorTest(true);
        sharedRenderer.clear();
        sharedRenderer.render(inst.scene, inst.camera);

        // Vẽ gợn sóng mảnh & blit vùng (0, 0, pw, ph) từ WebGL sang canvas 2D của banner
        const ctx = inst.ctx;
        ctx.clearRect(0, 0, pw, ph);

        for (let r = inst.ripples.length - 1; r >= 0; r--) {
          const rp = inst.ripples[r];
          rp.r += dt * 24;
          const life = 1 - rp.r / rp.maxR;
          if (life <= 0) { inst.ripples.splice(r, 1); continue; }
          ctx.strokeStyle = `rgba(255, 252, 238, ${(rp.alpha * life * life).toFixed(3)})`;
          ctx.lineWidth = 1.1;
          ctx.beginPath(); ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2); ctx.stroke();
        }

        ctx.globalAlpha = inst.isSlim ? 0.80 : 0.74;
        ctx.drawImage(sharedRenderer.domElement, 0, 0, pw, ph, 0, 0, pw, ph);
      }
    }

    function scanAndMount() {
      document.querySelectorAll(BANNER_SELECTOR).forEach(mountKoiBanner3D);
    }

    scanAndMount();
    setTimeout(scanAndMount, 650);
    setTimeout(scanAndMount, 1800);
    requestAnimationFrame(tick);
  }

  function boot() {
    ensureThree(start3DBannerEngine);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
