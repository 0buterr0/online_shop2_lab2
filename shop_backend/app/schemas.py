from pydantic import BaseModel, EmailStr
from typing import Optional, List

# ==========================================
# СХЕМИ ДЛЯ КОРИСТУВАЧІВ (USERS)
# ==========================================

# Базова схема з загальними полями
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Дані, які ми очікуємо від клієнта при реєстрації
class UserCreate(UserBase):
    password: str

# Дані, які сервер повертає у відповідь (пароль тут ніколи не віддається!)
class UserResponse(UserBase):
    id: int
    role: str
    is_blocked: bool

    class Config:
        from_attributes = True  # Дозволяє Pydantic читати дані прямо з ORM-моделей SQLAlchemy

# ==========================================
# СХЕМИ ДЛЯ АВТЕНТИФІКАЦІЇ (JWT)
# ==========================================

# Схема для входу (Login)
class UserLogin(BaseModel):
    username: str
    password: str

# Схема токена, який ми віддамо фронтенду після успішного входу
class Token(BaseModel):
    access_token: str
    token_type: str

# Дані, які зашифровані всередині JWT-токена
class TokenData(BaseModel):
    username: Optional[str] = None

# ==========================================
# СХЕМИ ДЛЯ ТОВАРІВ (PRODUCTS)
# ==========================================

# Схема для створення/оновлення товару (для Адміна)
class ProductCreate(BaseModel):
    title: str
    price: float
    stock: int

# Схема для віддачі товару клієнту
class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# СХЕМИ ДЛЯ ЗАМОВЛЕНЬ (ORDERS)
# ==========================================

# Дані, які клієнт надсилає, коли натискає "Купити"
class OrderCreate(BaseModel):
    product_id: int
    quantity: int

# Повна інформація про замовлення, яку повертає сервер
class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    is_paid: bool
    product: ProductResponse  # Вкладаємо схему товару, щоб фронтенд бачив, ЩО саме купили

    class Config:
        from_attributes = True