/**
 * Salamtea — Shared Frontend Module
 * ====================================
 * Handles:
 *  - Product price catalogue
 *  - Cart state (localStorage)
 *  - Cart drawer UI
 *  - Checkout modal
 *  - API communication (Orders + Contact)
 *  - WhatsApp link generation
 */

'use strict';

// ── Config ────────────────────────────────────────────────────────────────────
const ST = {
  API_BASE: 'http://127.0.0.1:8000/api',   // ← change to your deployed URL in prod
  WA_PHONE: '923009002321',

  PRICES: {
    'Black Tea':               { '250g': 450,  '500g': 850,  '1kg': 1600, '2kg': 3100 },
    'Green Tea':               { '250g': 500,  '500g': 950,  '1kg': 1800, '2kg': 3500 },
    'Ilaichi (Cardamom) Tea':  { '250g': 550,  '500g': 1050, '1kg': 2000, '2kg': 3900 },
  },

  PACK_LABELS: {
    '250g': 'Everyday Pack',
    '500g': 'Family Pack',
    '1kg':  'Household Pack',
    '2kg':  'Bulk Pack',
  },
};

// ── Cart (localStorage) ───────────────────────────────────────────────────────
const Cart = (() => {
  const KEY = 'st_cart_v1';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; }
    catch { return []; }
  }

  function save(items) {
    localStorage.setItem(KEY, JSON.stringify(items));
    _updateBadges();
  }

  function all() { return load(); }

  function add(teaVariety, packSize, qty = 1) {
    const items  = load();
    const exists = items.find(i => i.tea_variety === teaVariety && i.pack_size === packSize);
    if (exists) {
      exists.quantity += qty;
    } else {
      items.push({ tea_variety: teaVariety, pack_size: packSize, quantity: qty });
    }
    save(items);
    return items;
  }

  function remove(teaVariety, packSize) {
    save(load().filter(i => !(i.tea_variety === teaVariety && i.pack_size === packSize)));
  }

  function updateQty(teaVariety, packSize, qty) {
    const items = load();
    const item  = items.find(i => i.tea_variety === teaVariety && i.pack_size === packSize);
    if (item) { item.quantity = Math.max(1, qty); }
    save(items);
    return items;
  }

  function clear() { save([]); }

  function total() {
    return load().reduce((sum, i) => {
      return sum + (ST.PRICES[i.tea_variety]?.[i.pack_size] || 0) * i.quantity;
    }, 0);
  }

  function count() {
    return load().reduce((n, i) => n + i.quantity, 0);
  }

  return { all, add, remove, updateQty, clear, total, count };
})();


// ── Badge updates ─────────────────────────────────────────────────────────────
function _updateBadges() {
  const n = Cart.count();
  document.querySelectorAll('.badge, .cart-count').forEach(el => {
    el.textContent = n;
    el.style.display = n > 0 ? '' : 'none';
  });
}


// ── Cart Drawer ───────────────────────────────────────────────────────────────
function _ensureDrawer() {
  if (document.getElementById('st-drawer')) return;

  const drawer = document.createElement('div');
  drawer.id = 'st-drawer';
  drawer.innerHTML = `
    <div id="st-overlay"></div>
    <aside id="st-panel">
      <div id="st-panel-head">
        <span>Your Cart</span>
        <button id="st-close" aria-label="Close cart">✕</button>
      </div>
      <div id="st-items"></div>
      <div id="st-panel-foot">
        <div id="st-total-row">
          <span>Grand Total</span>
          <span id="st-total">Rs 0</span>
        </div>
        <button id="st-checkout-btn" class="st-cta-btn">Proceed to Checkout</button>
        <button id="st-wa-cart-btn" class="st-wa-btn">
          <span>◉</span> Order via WhatsApp
        </button>
      </div>
    </aside>`;

  document.body.appendChild(drawer);
  _injectDrawerStyles();

  document.getElementById('st-overlay').addEventListener('click', closeDrawer);
  document.getElementById('st-close').addEventListener('click', closeDrawer);
  document.getElementById('st-checkout-btn').addEventListener('click', openCheckout);
  document.getElementById('st-wa-cart-btn').addEventListener('click', _whatsappCartQuick);
}

function openDrawer() {
  _ensureDrawer();
  _renderDrawer();
  document.getElementById('st-drawer').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeDrawer() {
  document.getElementById('st-drawer')?.classList.remove('open');
  document.body.style.overflow = '';
}

function _renderDrawer() {
  const items     = Cart.all();
  const container = document.getElementById('st-items');
  const foot      = document.getElementById('st-panel-foot');

  if (!items.length) {
    container.innerHTML = `
      <div class="st-empty">
        <p>Your cart is empty.</p>
        <a href="our-tea.html">Browse Our Tea →</a>
      </div>`;
    foot.style.display = 'none';
    return;
  }

  foot.style.display = '';
  container.innerHTML = items.map(item => {
    const price = ST.PRICES[item.tea_variety]?.[item.pack_size] || 0;
    const line  = price * item.quantity;
    return `
      <div class="st-item" data-variety="${esc(item.tea_variety)}" data-size="${esc(item.pack_size)}">
        <div class="st-item-info">
          <p class="st-item-name">${esc(item.tea_variety)}</p>
          <p class="st-item-sub">${esc(item.pack_size)} · ${esc(ST.PACK_LABELS[item.pack_size] || '')}</p>
        </div>
        <div class="st-item-ctrl">
          <button class="st-qty-btn st-qty-dec" aria-label="Decrease">−</button>
          <span class="st-qty-val">${item.quantity}</span>
          <button class="st-qty-btn st-qty-inc" aria-label="Increase">+</button>
        </div>
        <div class="st-item-price">
          <p>Rs ${fmt(line)}</p>
          <button class="st-remove" aria-label="Remove">Remove</button>
        </div>
      </div>`;
  }).join('');

  document.getElementById('st-total').textContent = `Rs ${fmt(Cart.total())}`;

  // Wire qty controls
  container.querySelectorAll('.st-item').forEach(row => {
    const variety = row.dataset.variety;
    const size    = row.dataset.size;
    row.querySelector('.st-qty-inc').addEventListener('click', () => {
      const item = Cart.all().find(i => i.tea_variety === variety && i.pack_size === size);
      if (item) { Cart.updateQty(variety, size, item.quantity + 1); _renderDrawer(); }
    });
    row.querySelector('.st-qty-dec').addEventListener('click', () => {
      const item = Cart.all().find(i => i.tea_variety === variety && i.pack_size === size);
      if (item) {
        if (item.quantity <= 1) { Cart.remove(variety, size); }
        else { Cart.updateQty(variety, size, item.quantity - 1); }
        _renderDrawer();
      }
    });
    row.querySelector('.st-remove').addEventListener('click', () => {
      Cart.remove(variety, size);
      _renderDrawer();
    });
  });
}


// ── Checkout Modal ────────────────────────────────────────────────────────────
function _ensureModal() {
  if (document.getElementById('st-modal')) return;

  const m = document.createElement('div');
  m.id = 'st-modal';
  m.innerHTML = `
    <div id="st-modal-overlay"></div>
    <div id="st-modal-box" role="dialog" aria-modal="true" aria-labelledby="st-modal-title">
      <div id="st-modal-head">
        <h2 id="st-modal-title">Checkout</h2>
        <button id="st-modal-close" aria-label="Close">✕</button>
      </div>

      <div id="st-modal-body">

        <!-- Order summary -->
        <div class="st-section-label">Order Summary</div>
        <div id="st-summary"></div>

        <!-- Customer form -->
        <div class="st-section-label" style="margin-top:18px;">Delivery Details</div>
        <form id="st-checkout-form" novalidate>
          <div class="st-field">
            <label for="st-name">Full Name *</label>
            <input id="st-name" name="customer_name" type="text" placeholder="e.g. Ahmed Khan" required>
          </div>
          <div class="st-field">
            <label for="st-phone">Phone / WhatsApp *</label>
            <input id="st-phone" name="customer_phone" type="tel" placeholder="e.g. 03009002321" required>
          </div>
          <div class="st-field">
            <label for="st-email">Email (optional)</label>
            <input id="st-email" name="customer_email" type="email" placeholder="you@example.com">
          </div>
          <div class="st-field">
            <label for="st-addr">Delivery Address *</label>
            <textarea id="st-addr" name="delivery_address" rows="3"
              placeholder="House / Flat No., Street, City" required></textarea>
          </div>
          <div class="st-field">
            <label for="st-notes">Order Notes (optional)</label>
            <textarea id="st-notes" name="notes" rows="2"
              placeholder="Any special instructions…"></textarea>
          </div>

          <div id="st-form-error" class="st-msg st-error" style="display:none;"></div>
          <div id="st-form-success" class="st-msg st-success" style="display:none;"></div>

          <div style="display:flex;gap:10px;margin-top:14px;">
            <button type="submit" id="st-place-order" class="st-cta-btn" style="flex:1;">
              ✓ Place Order
            </button>
            <button type="button" id="st-wa-modal-btn" class="st-wa-btn" style="flex:1;">
              ◉ Order via WhatsApp
            </button>
          </div>
        </form>
      </div>
    </div>`;

  document.body.appendChild(m);
  _injectModalStyles();

  document.getElementById('st-modal-overlay').addEventListener('click', closeModal);
  document.getElementById('st-modal-close').addEventListener('click', closeModal);
  document.getElementById('st-checkout-form').addEventListener('submit', _handleCheckout);
  document.getElementById('st-wa-modal-btn').addEventListener('click', _whatsappFromModal);
}

function openCheckout() {
  closeDrawer();
  _ensureModal();

  const items = Cart.all();
  if (!items.length) { alert('Your cart is empty.'); return; }

  // Populate summary
  const summary = document.getElementById('st-summary');
  summary.innerHTML = items.map(item => {
    const price = ST.PRICES[item.tea_variety]?.[item.pack_size] || 0;
    return `
      <div class="st-sum-row">
        <span>${esc(item.tea_variety)} (${esc(item.pack_size)}) × ${item.quantity}</span>
        <span>Rs ${fmt(price * item.quantity)}</span>
      </div>`;
  }).join('') + `
    <div class="st-sum-total">
      <span>Grand Total</span>
      <span>Rs ${fmt(Cart.total())}</span>
    </div>`;

  // Reset form state
  const formEl = document.getElementById('st-checkout-form');
  const summaryEl = document.getElementById('st-summary');
  if (formEl) formEl.style.display = 'block';
  if (summaryEl) summaryEl.style.display = 'block';
  formEl.reset();
  document.getElementById('st-form-error').style.display   = 'none';
  document.getElementById('st-form-success').style.display = 'none';
  document.getElementById('st-place-order').disabled       = false;
  document.getElementById('st-place-order').textContent    = '✓ Place Order';

  document.getElementById('st-modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('st-modal')?.classList.remove('open');
  document.body.style.overflow = '';
}

async function _handleCheckout(e) {
  e.preventDefault();
  const form    = e.target;
  const errBox  = document.getElementById('st-form-error');
  const okBox   = document.getElementById('st-form-success');
  const btn     = document.getElementById('st-place-order');

  errBox.style.display = okBox.style.display = 'none';

  const name  = form.customer_name.value.trim();
  const phone = form.customer_phone.value.trim();
  const addr  = form.delivery_address.value.trim();

  if (!name || !phone || !addr) {
    errBox.textContent    = 'Please fill in Name, Phone and Delivery Address.';
    errBox.style.display  = 'block';
    return;
  }

  btn.disabled    = true;
  btn.textContent = 'Placing Order…';

  const payload = {
    customer_name:    name,
    customer_phone:   phone,
    customer_email:   form.customer_email.value.trim() || null,
    delivery_address: addr,
    notes:            form.notes.value.trim() || null,
    cart: Cart.all().map(i => ({
      tea_variety: i.tea_variety,
      pack_size:   i.pack_size,
      quantity:    i.quantity,
    })),
  };

  try {
    const res  = await fetch(`${ST.API_BASE}/orders/checkout`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      let errMsg = 'Something went wrong. Please try again.';
      if (typeof data.detail === 'string') {
        errMsg = data.detail;
      } else if (Array.isArray(data.detail)) {
        errMsg = data.detail.map(d => d.msg || JSON.stringify(d)).join('. ');
      } else if (data.detail && typeof data.detail === 'object') {
        errMsg = JSON.stringify(data.detail);
      }
      throw new Error(errMsg);
    }

    // Success
    Cart.clear();
    _updateBadges();
    okBox.innerHTML  = `
      <strong>Order Placed!</strong> Order ID: <code>${esc(data.order_id)}</code><br>
      ${esc(data.message)}`;
    okBox.style.display  = 'block';
    form.style.display   = 'none';
    document.getElementById('st-summary').style.display = 'none';

  } catch (err) {
    errBox.textContent   = err.message;
    errBox.style.display = 'block';
    btn.disabled         = false;
    btn.textContent      = '✓ Place Order';
  }
}

async function _whatsappFromModal() {
  const form = document.getElementById('st-checkout-form');
  const name = form.customer_name.value.trim() || 'Customer';
  const addr = form.delivery_address.value.trim() || 'To be confirmed';
  await _sendToWhatsApp(name, addr, Cart.all());
}

async function _whatsappCartQuick() {
  await _sendToWhatsApp('Customer', 'To be confirmed', Cart.all());
}

async function _sendToWhatsApp(name, address, cartItems) {
  if (!cartItems.length) { alert('Your cart is empty.'); return; }
  try {
    const res  = await fetch(`${ST.API_BASE}/orders/whatsapp-link`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ customer_name: name, delivery_address: address, cart: cartItems }),
    });
    if (!res.ok) throw new Error('Could not generate WhatsApp link.');
    const data = await res.json();
    window.open(data.whatsapp_url, '_blank');
  } catch {
    // Fallback: build URL client-side
    const lines = cartItems.map(i => {
      const p = ST.PRICES[i.tea_variety]?.[i.pack_size] || 0;
      return `  - ${i.tea_variety} (${i.pack_size}) × ${i.quantity} = Rs ${fmt(p * i.quantity)}`;
    }).join('\n');
    const total = Cart.total();
    const msg = encodeURIComponent(
      `Hello Salamtea, I would like to place an order:\n\n${lines}\n\n` +
      `💰 Total Price: Rs ${fmt(total)}\n\n` +
      `👤 My Name: ${name}\n📍 Delivery Address: ${address}`
    );
    window.open(`https://wa.me/${ST.WA_PHONE}?text=${msg}`, '_blank');
  }
}


// ── Public API: called from product buttons ────────────────────────────────────
window.stAddToCart = function(teaVariety, packSize, qty) {
  // If packSize not provided, show a size picker mini-modal
  if (!packSize) {
    _showSizePicker(teaVariety);
    return;
  }
  Cart.add(teaVariety, packSize, qty || 1);
  _showToast(`${teaVariety} (${packSize}) added to cart!`);
  openDrawer();
};

window.stOrderWhatsApp = function(teaVariety, packSize) {
  if (!packSize) { _showSizePicker(teaVariety, true); return; }
  const price = ST.PRICES[teaVariety]?.[packSize] || 0;
  const msg   = encodeURIComponent(
    `Hello Salamtea, I would like to place an order:\n\n` +
    `  - ${teaVariety} (${packSize}) = Rs ${fmt(price)}\n\n` +
    `💰 Total Price: Rs ${fmt(price)}\n\n` +
    `👤 My Name: (please enter)\n📍 Delivery Address: (please enter)`
  );
  window.open(`https://wa.me/${ST.WA_PHONE}?text=${msg}`, '_blank');
};

window.stOpenCart = openDrawer;
window.stOpenCheckout = openCheckout;


// ── Size picker (mini modal when no size selected) ────────────────────────────
function _showSizePicker(teaVariety, isWhatsApp = false) {
  const existing = document.getElementById('st-size-picker');
  if (existing) existing.remove();

  const prices  = ST.PRICES[teaVariety] || {};
  const sizes   = Object.keys(prices);

  const picker = document.createElement('div');
  picker.id = 'st-size-picker';
  picker.innerHTML = `
    <div id="st-sp-overlay"></div>
    <div id="st-sp-box">
      <div id="st-sp-head">
        <span>Select Pack Size</span>
        <button id="st-sp-close">✕</button>
      </div>
      <p style="font-size:12px;color:#6d685f;margin-bottom:14px;">${esc(teaVariety)}</p>
      <div id="st-sp-sizes">
        ${sizes.map(sz => `
          <button class="st-sp-size" data-size="${esc(sz)}">
            <span class="st-sp-weight">${esc(sz)}</span>
            <span class="st-sp-label">${esc(ST.PACK_LABELS[sz] || '')}</span>
            <span class="st-sp-price">Rs ${fmt(prices[sz])}</span>
          </button>`).join('')}
      </div>
    </div>`;

  document.body.appendChild(picker);
  _injectPickerStyles();

  document.getElementById('st-sp-overlay').addEventListener('click', () => picker.remove());
  document.getElementById('st-sp-close').addEventListener('click', () => picker.remove());

  picker.querySelectorAll('.st-sp-size').forEach(btn => {
    btn.addEventListener('click', () => {
      const sz = btn.dataset.size;
      picker.remove();
      if (isWhatsApp) { window.stOrderWhatsApp(teaVariety, sz); }
      else            { window.stAddToCart(teaVariety, sz, 1); }
    });
  });

  setTimeout(() => picker.classList.add('open'), 10);
}


// ── Toast ─────────────────────────────────────────────────────────────────────
function _showToast(msg) {
  const t = document.createElement('div');
  t.className  = 'st-toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.classList.add('show'), 10);
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, 3000);
  _injectToastStyles();
}


// ── Helpers ───────────────────────────────────────────────────────────────────
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
                  .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function fmt(n) {
  return Number(n).toLocaleString('en-PK');
}


// ── Style injectors ───────────────────────────────────────────────────────────
let _stylesInjected = {};

function _inject(id, css) {
  if (_stylesInjected[id]) return;
  const s = document.createElement('style');
  s.id = id;
  s.textContent = css;
  document.head.appendChild(s);
  _stylesInjected[id] = true;
}

function _injectDrawerStyles() {
  _inject('st-drawer-css', `
    #st-drawer { position:fixed;inset:0;z-index:9000;pointer-events:none; }
    #st-overlay { position:absolute;inset:0;background:rgba(0,0,0,.45);opacity:0;transition:opacity .3s; }
    #st-panel {
      position:absolute;right:0;top:0;bottom:0;width:380px;max-width:100vw;
      background:#f6f1e8;border-left:1px solid #d9d1c3;
      display:flex;flex-direction:column;transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1);
    }
    #st-drawer.open { pointer-events:all; }
    #st-drawer.open #st-overlay { opacity:1; }
    #st-drawer.open #st-panel   { transform:translateX(0); }
    #st-panel-head {
      display:flex;justify-content:space-between;align-items:center;
      padding:20px 22px;border-bottom:1px solid #d9d1c3;
      font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;font-weight:600;color:#25251f;
    }
    #st-close {
      background:none;border:none;cursor:pointer;font-size:18px;color:#6d685f;line-height:1;
      padding:4px 6px;border-radius:3px;transition:color .2s;
    }
    #st-close:hover { color:#3f5d16; }
    #st-items { flex:1;overflow-y:auto;padding:16px 22px; }
    .st-empty  { text-align:center;padding:40px 0;font-size:14px;color:#6d685f; }
    .st-empty a { color:#3f5d16;text-decoration:none;font-weight:600; }
    .st-item {
      display:flex;align-items:flex-start;gap:10px;
      padding:12px 0;border-bottom:1px solid #e8e2d8;
    }
    .st-item-info { flex:1; }
    .st-item-name { font-size:13px;font-weight:600;color:#25251f;margin:0 0 3px; }
    .st-item-sub  { font-size:11px;color:#6d685f;margin:0; }
    .st-item-ctrl { display:flex;align-items:center;gap:8px; }
    .st-qty-btn {
      width:26px;height:26px;border:1px solid #c9c3b8;background:#fff;
      border-radius:3px;cursor:pointer;font-size:16px;line-height:1;color:#3f5d16;
      transition:background .2s;
    }
    .st-qty-btn:hover { background:#e8f0d8; }
    .st-qty-val { font-size:13px;font-weight:600;min-width:22px;text-align:center;color:#25251f; }
    .st-item-price { text-align:right;min-width:80px; }
    .st-item-price p { font-size:13px;font-weight:600;color:#3f5d16;margin:0 0 5px; }
    .st-remove {
      font-size:10px;color:#9a948c;background:none;border:none;cursor:pointer;
      text-decoration:underline;padding:0;
    }
    .st-remove:hover { color:#c0392b; }
    #st-panel-foot { padding:18px 22px;border-top:1px solid #d9d1c3;background:#eee8dc; }
    #st-total-row {
      display:flex;justify-content:space-between;align-items:center;
      font-size:15px;font-weight:700;color:#25251f;margin-bottom:14px;
    }
    #st-total { color:#3f5d16;font-family:'Cormorant Garamond',Georgia,serif;font-size:20px; }
    .st-cta-btn {
      width:100%;height:42px;background:#3f5d16;color:#fff;border:none;
      border-radius:4px;cursor:pointer;font-size:12px;letter-spacing:.5px;
      font-family:Montserrat,Arial,sans-serif;font-weight:600;margin-bottom:8px;
      transition:background .2s,transform .2s;
    }
    .st-cta-btn:hover:not(:disabled) { background:#2e4510;transform:translateY(-1px); }
    .st-cta-btn:disabled { opacity:.6;cursor:not-allowed; }
    .st-wa-btn {
      width:100%;height:42px;background:#fff;color:#3f5d16;
      border:1px solid #3f5d16;border-radius:4px;cursor:pointer;
      font-size:12px;letter-spacing:.5px;font-family:Montserrat,Arial,sans-serif;font-weight:600;
      display:flex;align-items:center;justify-content:center;gap:6px;
      transition:background .2s,transform .2s;
    }
    .st-wa-btn:hover { background:#e8f0d8;transform:translateY(-1px); }
    @media(max-width:480px){#st-panel{width:100vw;}}
  `);
}

function _injectModalStyles() {
  _inject('st-modal-css', `
    #st-modal { position:fixed;inset:0;z-index:9100;pointer-events:none; }
    #st-modal-overlay { position:absolute;inset:0;background:rgba(0,0,0,.55);opacity:0;transition:opacity .3s; }
    #st-modal-box {
      position:absolute;top:50%;left:50%;width:520px;max-width:calc(100vw - 32px);
      transform:translate(-50%,-48%);opacity:0;transition:transform .3s,opacity .3s;
      background:#f6f1e8;border:1px solid #d9d1c3;border-radius:7px;
      max-height:90vh;display:flex;flex-direction:column;overflow:hidden;
    }
    #st-modal.open { pointer-events:all; }
    #st-modal.open #st-modal-overlay { opacity:1; }
    #st-modal.open #st-modal-box     { transform:translate(-50%,-50%);opacity:1; }
    #st-modal-head {
      display:flex;justify-content:space-between;align-items:center;
      padding:18px 24px;border-bottom:1px solid #d9d1c3;flex:none;
    }
    #st-modal-title { margin:0;font-family:'Cormorant Garamond',Georgia,serif;font-size:22px;color:#25251f; }
    #st-modal-close {
      background:none;border:none;cursor:pointer;font-size:18px;color:#6d685f;
      padding:4px 6px;border-radius:3px;transition:color .2s;
    }
    #st-modal-close:hover { color:#3f5d16; }
    #st-modal-body { overflow-y:auto;padding:20px 24px; }
    .st-section-label {
      font-size:10px;letter-spacing:1.2px;color:#8a8480;font-family:Montserrat,Arial,sans-serif;
      font-weight:600;margin-bottom:8px;
    }
    .st-sum-row {
      display:flex;justify-content:space-between;font-size:13px;color:#25251f;
      padding:5px 0;border-bottom:1px solid #e8e2d8;
    }
    .st-sum-total {
      display:flex;justify-content:space-between;
      font-size:15px;font-weight:700;color:#3f5d16;padding:10px 0 0;
    }
    .st-field { margin-bottom:10px; }
    .st-field label { display:block;font-size:11px;color:#6d685f;margin-bottom:4px;letter-spacing:.3px; }
    .st-field input, .st-field textarea {
      width:100%;border:1px solid #d9d1c3;border-radius:3px;background:#f8f4ec;
      color:#25251f;padding:9px 12px;font-size:13px;font-family:Montserrat,Arial,sans-serif;
      outline:none;transition:border-color .2s,box-shadow .2s;
    }
    .st-field input:focus, .st-field textarea:focus {
      border-color:#3f5d16;box-shadow:0 0 0 3px rgba(63,93,22,.1);
    }
    .st-field textarea { resize:vertical; }
    .st-msg { padding:10px 14px;border-radius:4px;font-size:13px;margin-bottom:8px; }
    .st-error   { background:#fdf0f0;border:1px solid #e0b0b0;color:#8b2020; }
    .st-success { background:#f0f6ec;border:1px solid #a0c080;color:#2a5020; }
    code { background:#e8e2d8;padding:2px 6px;border-radius:3px;font-size:12px; }
  `);
}

function _injectPickerStyles() {
  _inject('st-picker-css', `
    #st-size-picker { position:fixed;inset:0;z-index:9200;pointer-events:none; }
    #st-sp-overlay  { position:absolute;inset:0;background:rgba(0,0,0,.55);opacity:0;transition:opacity .25s; }
    #st-sp-box {
      position:absolute;top:50%;left:50%;width:360px;max-width:calc(100vw - 32px);
      transform:translate(-50%,-47%);opacity:0;transition:transform .25s,opacity .25s;
      background:#f6f1e8;border:1px solid #d9d1c3;border-radius:7px;padding:24px;
    }
    #st-size-picker.open { pointer-events:all; }
    #st-size-picker.open #st-sp-overlay { opacity:1; }
    #st-size-picker.open #st-sp-box     { transform:translate(-50%,-50%);opacity:1; }
    #st-sp-head {
      display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;
      font-family:'Cormorant Garamond',Georgia,serif;font-size:18px;font-weight:600;color:#25251f;
    }
    #st-sp-close { background:none;border:none;cursor:pointer;font-size:16px;color:#6d685f; }
    #st-sp-sizes { display:flex;flex-direction:column;gap:8px; }
    .st-sp-size {
      display:flex;align-items:center;gap:12px;padding:12px 14px;
      border:1px solid #d9d1c3;background:#fff;border-radius:4px;cursor:pointer;
      transition:border-color .2s,background .2s;text-align:left;
    }
    .st-sp-size:hover { border-color:#3f5d16;background:#eef4e6; }
    .st-sp-weight { font-family:'Cormorant Garamond',Georgia,serif;font-size:16px;font-weight:700;color:#3f5d16;width:36px; }
    .st-sp-label  { flex:1;font-size:12px;color:#6d685f; }
    .st-sp-price  { font-size:14px;font-weight:700;color:#25251f; }
  `);
}

function _injectToastStyles() {
  _inject('st-toast-css', `
    .st-toast {
      position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(20px);
      background:#3f5d16;color:#fff;padding:12px 22px;border-radius:24px;
      font-size:13px;font-family:Montserrat,Arial,sans-serif;
      opacity:0;transition:opacity .3s,transform .3s;z-index:9999;white-space:nowrap;
      box-shadow:0 4px 18px rgba(0,0,0,.25);pointer-events:none;
    }
    .st-toast.show { opacity:1;transform:translateX(-50%) translateY(0); }
  `);
}


// ── Initialise on DOMContentLoaded ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  _updateBadges();

  // Wire cart icons
  document.querySelectorAll('.icon.cart, .action[aria-label="Cart"], a[aria-label="Cart"]')
    .forEach(el => {
      el.style.cursor = 'pointer';
      el.addEventListener('click', e => { e.preventDefault(); openDrawer(); });
    });
});
