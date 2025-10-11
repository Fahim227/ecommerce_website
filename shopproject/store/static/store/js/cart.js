// cart.js - vanilla JS cart manager using localStorage

(() => {
  const CART_KEY = 'picksymart_cart';

  // DOM refs
  const openCartBtn = document.getElementById('openCartBtn');
  const closeCartBtn = document.getElementById('closeCartBtn');
  const cartSlider = document.getElementById('cartSlider');
  const cartOverlay = document.getElementById('cartOverlay');
  const cartItemsEl = document.getElementById('cartItems');
  const cartCountBadge = document.getElementById('cartCountBadge');
  const cartTotalEl = document.getElementById('cartTotal');
  const clearCartBtn = document.getElementById('clearCartBtn');
  const checkoutBtn = document.getElementById('checkoutBtn');

  // Toast
  let toastEl = document.getElementById('cartToast');
  let toastBody = document.getElementById('cartToastBody');
  let bsToast = toastEl ? new bootstrap.Toast(toastEl, { delay: 1800 }) : null;

  // Utilities
  function getCart() {
    try {
      return JSON.parse(localStorage.getItem(CART_KEY) || '{}');
    } catch (e) {
      console.error('cart parse error', e);
      return {};
    }
  }

  function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    updateBadge();
  }

  function updateBadge() {
    const cart = getCart();
    const count = Object.values(cart).reduce((s, item) => s + (item.quantity || 0), 0);
    cartCountBadge.textContent = count;
    if (count > 0) {
      cartCountBadge.classList.remove('d-none');
    } else {
      cartCountBadge.classList.add('d-none');
    }
  }

  // Formatting price
  function formatPrice(n) {
    if (isNaN(n)) return '৳0.00';
    return '৳' + Number(n).toFixed(2);
  }

  // Render cart items into slider
  function renderCart() {
    const cart = getCart();
    const keys = Object.keys(cart);
    if (!keys.length) {
      cartItemsEl.innerHTML = '<div class="text-center text-muted">Your cart is empty.</div>';
      cartTotalEl.textContent = formatPrice(0);
      return;
    }
    let html = '';
    let total = 0;
    keys.forEach(key => {
      const item = cart[key];
      const subtotal = Number(item.price) * Number(item.quantity);
      total += subtotal;
      html += `
      <div class="cart-item" data-key="${key}">
        <img src="${item.image || '/static/store/img/placeholder.png'}" alt="${escapeHtml(item.title)}">
        <div style="flex:1;">
          <div class="title">${escapeHtml(item.title)}</div>
          <div class="small text-muted">${formatPrice(item.price)} each</div>
          <div class="d-flex justify-content-between align-items-center mt-2">
            <div class="quantity-controls   d-flex align-items-center gap-1">
              <button type="button" class="btn btn-outline-secondary btn-sm btn-decrease" data-key="${key}">−</button>
              <div >
              <input type="text" class="form-control form-control-sm text-center" style="width:40px;"
                   id="qty-{{ slug }}" value=${item.quantity} readonly>
              </div>
              <button type="button" class="btn btn-outline-secondary btn-sm btn-increase"   data-key="${key}">+</button>
            </div>
            <div class="text-end">
              <div><strong>${formatPrice(subtotal)}</strong></div>
              <div><a href="#" class="text-danger small remove-item" data-key="${key}">Remove</a></div>
            </div>
          </div>
        </div>
      </div>`;
    });

    cartItemsEl.innerHTML = html;
    cartTotalEl.textContent = formatPrice(total);

    // attach event listeners for controls
    attachCartItemListeners();
  }

  function escapeHtml(unsafe) {
    return ('' + unsafe)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function attachCartItemListeners() {
    cartItemsEl.querySelectorAll('.btn-increase').forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        const k = btn.dataset.key;
        changeQty(k, 1);
      };
    });
    cartItemsEl.querySelectorAll('.btn-decrease').forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        const k = btn.dataset.key;
        changeQty(k, -1);
      };
    });
    cartItemsEl.querySelectorAll('.remove-item').forEach(link => {
      link.onclick = (e) => {
        e.preventDefault();
        const k = link.dataset.key;
        removeItem(k);
      };
    });
  }

  function changeQty(key, delta) {
    const cart = getCart();
    if (!cart[key]) return;
    cart[key].quantity = Math.max(1, Number(cart[key].quantity) + delta);
    saveCart(cart);
    renderCart();
  }

  function removeItem(key) {
    const cart = getCart();
    if (!cart[key]) return;
    delete cart[key];
    saveCart(cart);
    renderCart();
    showToast('Removed from cart');
  }

  function clearCart() {
    localStorage.removeItem(CART_KEY);
    updateBadge();
    renderCart();
  }

  // Add item to cart — accepts object param {id, title, price, image, quantity}
  function addToCart(item) {
    const cart = getCart();
    const key = String(item.id);
    if (!cart[key]) {
      cart[key] = { ...item, quantity: Number(item.quantity || 1) };
    } else {
      cart[key].quantity = Number(cart[key].quantity || 0) + Number(item.quantity || 1);
    }
    saveCart(cart);
    renderCart();
    showToast('Added to cart');
  }

  function showToast(msg) {
    if (!bsToast) return;
    toastBody.textContent = msg;
    bsToast.show();
  }

  // open/close slider
  function openCart() {
    cartSlider.classList.add('open');
    cartOverlay.style.display = 'block';
    renderCart();
  }
  function closeCart() {
    cartSlider.classList.remove('open');
    cartOverlay.style.display = 'none';
  }

  // attach global events
  function attachGlobalEvents() {
    if (openCartBtn) openCartBtn.onclick = (e) => { 
      e.preventDefault(); openCart(); };
    if (closeCartBtn) closeCartBtn.onclick = closeCart;
    if (cartOverlay) cartOverlay.onclick = closeCart;
    if (clearCartBtn) clearCartBtn.onclick = () => { clearCart(); };
    if (checkoutBtn) checkoutBtn.onclick = (e) => {
    // window.location.href = "{% url 'store:order_create' %}";



      e.preventDefault();
      // example: redirect to checkout page and pass cart (the server can parse posted JSON)
      // We'll redirect to /cart/checkout/ and let JS POST cart there.
      postCartToCheckout();
    };
    // Add-to-cart buttons: elements with class 'add-to-cart' expected to have data attributes:
    document.querySelectorAll('.add-to-cart').forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        const data = {
          id: btn.dataset.id,
          title: btn.dataset.title,
          price: Number(btn.dataset.price),
          image: btn.dataset.image,
          quantity: Number(btn.dataset.quantity || 1)
        };
        addToCart(data);
      };
    });
  }

  // POST cart JSON to server checkout endpoint (optional)
  function postCartToCheckout() {
    const cart = getCart();
    if (!Object.keys(cart).length) {
      showToast('Cart is empty');
      return;
    }
    // Create form and submit POST with cart JSON
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = '/cart/checkout/';  // adjust url if different
    // CSRF token: attempt to read from cookie (Django default) and add hidden field
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      const inputCsrf = document.createElement('input');
      inputCsrf.type = 'hidden';
      inputCsrf.name = 'csrfmiddlewaretoken';
      inputCsrf.value = csrfToken;
      form.appendChild(inputCsrf);
    }
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'cart_json';
    input.value = JSON.stringify(cart);
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
  }

  // helper to read cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i=0; i<cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Boot
  function init() {
    updateBadge();
    attachGlobalEvents();
  }

  // Wait for DOM ready
  document.addEventListener('DOMContentLoaded', init);
})();
