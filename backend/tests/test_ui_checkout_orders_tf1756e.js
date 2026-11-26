/**
 * KIỂM THỬ TỰ ĐỘNG GIAO DIỆN CHECKOUT & LỊCH SỬ ĐƠN HÀNG (TASK TF1756E)
 * Người thực hiện: Trần Gia Huy (B25DTCN180)
 * Phạm vi: frontend/user/checkout.html & frontend/user/orders.html
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const checkoutPath = path.join(__dirname, '../../frontend/user/checkout.html');
const ordersPath = path.join(__dirname, '../../frontend/user/orders.html');

console.log('='.repeat(60));
console.log('KIEM THU GIAO DIEN CHECKOUT & LICH SU DON HANG (TF1756E)');
console.log('Nguoi thuc hien: Tran Gia Huy (B25DTCN180)');
console.log('='.repeat(60));

const checkoutHtml = fs.readFileSync(checkoutPath, 'utf8');
const ordersHtml = fs.readFileSync(ordersPath, 'utf8');

let totalTests = 0;
let passedTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    passedTests++;
    console.log(`[PASS] ${name}`);
  } catch (err) {
    console.error(`[FAIL] ${name}: ${err.message}`);
  }
}

// 1. Kiểm tra Viewport & Title
runTest('TC-CK-01: Viewport meta tag checkout.html hop le', () => {
  assert.ok(checkoutHtml.includes('name="viewport"'), 'Thieu the viewport trong checkout.html');
  assert.ok(checkoutHtml.includes('width=device-width, initial-scale=1.0'), 'Sai thiet lap viewport checkout.html');
  assert.ok(checkoutHtml.includes('<title>Thanh Toán Đơn Hàng | JML Store</title>'), 'Sai tieu de checkout.html');
});

// 2. Desktop Grid Layout Checkout
runTest('TC-CK-02: Desktop Grid layout checkout.html (grid-template-columns: 1fr 420px)', () => {
  assert.ok(checkoutHtml.includes('.checkout-layout {'), 'Thieu selector .checkout-layout');
  assert.ok(checkoutHtml.includes('grid-template-columns: 1fr 420px;'), 'Sai grid layout desktop checkout');
  assert.ok(checkoutHtml.includes('position: sticky;'), 'Thieu sticky cho tom tat thanh toan desktop');
});

// 3. Responsive 960px Checkout
runTest('TC-CK-03: Responsive breakpoint 960px (chuyen layout 1 cot & an checkout steps)', () => {
  assert.ok(checkoutHtml.includes('@media (max-width: 960px)'), 'Thieu @media 960px checkout');
  assert.ok(checkoutHtml.includes('.checkout-steps { display: none; }'), 'Chua an checkout steps tren <= 960px');
});

// 4. Responsive 600px Checkout
runTest('TC-CK-04: Responsive breakpoint 600px (1 cot form & saved addresses)', () => {
  assert.ok(checkoutHtml.includes('@media (max-width: 600px)'), 'Thieu @media 600px checkout');
  assert.ok(checkoutHtml.includes('.saved-addresses, .form-grid { grid-template-columns: 1fr; }'), 'Chua chuyen form va dia chi sang 1 cot');
});

// 5. Toast Checkout Responsive (BUG-03)
runTest('TC-CK-05: Sửa BUG-03: Toast message checkout can deu 16px tren mobile', () => {
  assert.ok(checkoutHtml.includes('.toast-msg { left: 16px; right: 16px; bottom: 16px; max-width: none; justify-content: center; }'), 'Chua responsive toast tren checkout mobile');
});

// 6. Font size input mobile <= 480px chong auto-zoom (BUG-04)
runTest('TC-CK-06: Sửa BUG-04: Input font size 16px tren mobile <= 480px chong iOS auto zoom', () => {
  assert.ok(checkoutHtml.includes('.form-control, .form-select, .form-textarea { font-size: 16px; }'), 'Chua set font-size 16px chong zoom tren mobile');
});

// 7. Viewport & Title Orders
runTest('TC-OD-01: Viewport meta tag orders.html hop le', () => {
  assert.ok(ordersHtml.includes('name="viewport"'), 'Thieu the viewport trong orders.html');
  assert.ok(ordersHtml.includes('width=device-width, initial-scale=1.0'), 'Sai thiet lap viewport orders.html');
  assert.ok(ordersHtml.includes('<title>Lịch Sử Đơn Hàng | JML Store</title>'), 'Sai tieu de orders.html');
});

// 8. Filter tabs touch scroll (BUG-05)
runTest('TC-OD-02: Sửa BUG-05: Filter tabs ho tro vuot ngang tren mobile <= 768px', () => {
  assert.ok(ordersHtml.includes('.filter-tabs { overflow-x: auto; flex-wrap: nowrap;'), 'Chua set overflow-x: auto cho filter tabs');
  assert.ok(ordersHtml.includes('-webkit-overflow-scrolling: touch;'), 'Chua co ho tro vuot cham cam ung touch scrolling');
});

// 9. Card & Action buttons mobile orders
runTest('TC-OD-03: Responsive card & action buttons orders.html tren mobile <= 768px', () => {
  assert.ok(ordersHtml.includes('.order-card-head { flex-direction: column; align-items: flex-start; gap: 8px; }'), 'Card head chua flex-direction column');
  assert.ok(ordersHtml.includes('.btn-detail, .btn-cancel, .btn-received { flex: 1; min-width: 120px; justify-content: center; }'), 'Nut bam chua dan deu tren mobile');
});

// 10. Modal box responsive 95% (BUG-06)
runTest('TC-OD-04: Sửa BUG-06: Modal box responsive 95% va footer nut bam dan deu tren mobile', () => {
  assert.ok(ordersHtml.includes('.modal-box { max-height: 95vh; width: 95%; margin: 10px; }'), 'Modal box chua co width 95% tren mobile');
  assert.ok(ordersHtml.includes('.btn-modal-cancel, .btn-modal-received, .btn-modal-close { flex: 1; min-width: 120px; justify-content: center; }'), 'Footer nut bam modal chua dan deu flex: 1');
});

// 11. Chong tran ngang ca 2 trang (BUG-01)
runTest('TC-ALL-01: Sửa BUG-01: Chong tran ngang toan dien (overflow-x: hidden) cho ca 2 trang', () => {
  assert.ok(checkoutHtml.includes('overflow-x: hidden;'), 'checkout.html chua co overflow-x: hidden');
  assert.ok(ordersHtml.includes('overflow-x: hidden;'), 'orders.html chua co overflow-x: hidden');
});

console.log('-'.repeat(60));
console.log(`KET QUA: ${passedTests}/${totalTests} TEST CASES PASSED (${Math.round((passedTests / totalTests) * 100)}%) - HOAN THANH TASK TF1756E!`);
console.log('='.repeat(60));

if (passedTests !== totalTests) {
  process.exit(1);
}
