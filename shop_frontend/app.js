const API_URL = "http://127.0.0.1:8000/api";

// ==========================================
// 1. АВТЕНТИФІКАЦІЯ ТА ВХІД
// ==========================================

// Реєстрація нового користувача
async function registerUser(username, email, password) {
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        if (!response.ok) {
            alert(`Помилка реєстрації: ${data.detail || "щось пішло не так"}`);
            return false;
        }
        return true;
    } catch (err) {
        console.error(err);
        alert("Не вдалося з'єднатися з сервером.");
        return false;
    }
}

// Вхід (Логін) та збереження токена (Сумісно з OAuth2 Form на бекенді)
async function loginUser(username, password) {
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/x-www-form-urlencoded" 
            },
            body: formData
        });
        
        const data = await response.json();
        if (!response.ok) {
            const errDiv = document.getElementById('auth-error');
            if (errDiv) {
                errDiv.innerText = data.detail || "Неправильний логін або пароль";
                errDiv.style.display = "block";
            }
            return false;
        }
        
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", username);
        return true;
    } catch (err) {
        console.error(err);
        alert("Помилка авторизації. Перевірте, чи запущено бекенд!");
        return false;
    }
}

// Вихід з системи
function logoutUser() {
    localStorage.clear();
    window.location.href = "login.html";
}

// ==========================================
// 2. РОБОТА З ТОВАРАМИ ТА ЗАМОВЛЕННЯМИ
// ==========================================

// Отримання всіх товарів з бекенду
async function fetchProducts() {
    try {
        const response = await fetch(`${API_URL}/products/`);
        return await response.json();
    } catch (err) {
        console.error(err);
        return [];
    }
}

// Створення замовлення клієнтом (Купівля)
async function createOrder(productId, quantity = 1) {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Будь ласка, спочатку увійдіть у свій акаунт!");
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/orders/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        });

        const data = await response.json();
        if (!response.ok) {
            alert(`Помилка замовлення: ${data.detail}`);
        } else {
            alert("Товар успішно замовлено! Оплатіть його в кошику.");
            if (typeof loadDashboard === "function") loadDashboard();
        }
    } catch (err) {
        console.error(err);
    }
}

// Оплата замовлення (Вимога варіанту 9)
async function payOrder(orderId) {
    const token = localStorage.getItem("token");
    try {
        const response = await fetch(`${API_URL}/orders/${orderId}/pay`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.ok) {
            alert("Замовлення успішно оплачено!");
            if (typeof loadDashboard === "function") loadDashboard();
        } else {
            const data = await response.json();
            alert(`Помилка оплати: ${data.detail}`);
        }
    } catch (err) {
        console.error(err);
    }
}
async function loadAllOrdersForAdmin() {
    const token = localStorage.getItem('token');
    // Робимо запит до нового ендпоінту, який ми додали в order_router.py
    const response = await fetch('http://127.0.0.1:8000/api/orders/all', {
        headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });

    if (response.ok) {
        const orders = await response.json();
        const container = document.getElementById('admin-orders-container');
        if (!container) return; // Якщо блоку немає на сторінці, просто виходимо
        
        container.innerHTML = '<h3>Усі замовлення клієнтів (Адмін-панель):</h3>';
        
        orders.forEach(order => {
            container.innerHTML += `
                <div class="order-card" style="border: 1px solid #ccc; padding: 10px; margin: 5px;">
                    <p>Замовлення №${order.id}</p>
                    <p>Клієнт (ID): ${order.user_id}</p>
                    <p>Товар (ID): ${order.product_id}</p>
                    <p>Сума: ${order.total_price} грн</p>
                    <p>Статус оплати: ${order.is_paid ? '✅ Оплачено' : '⏳ В очікуванні'}</p>
                </div>
            `;
        });
    }
}
// Викликаємо функцію тільки якщо ми на сторінці адмінки
if (window.location.pathname.includes('admin.html')) {
    loadAllOrdersForAdmin();
}
// Отримання списку замовлень поточного користувача
async function fetchMyOrders() {
    const token = localStorage.getItem("token");
    if (!token) return [];
    
    try {
        const response = await fetch(`${API_URL}/orders/my`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        return await response.json();
    } catch (err) {
        console.error(err);
        return [];
    }
}