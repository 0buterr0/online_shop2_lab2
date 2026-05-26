from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="client")  # "client" або "admin"
    is_blocked = Column(Boolean, default=False)  # Чорний список для неплатників (Вимога варіанту!)

    # Організовуємо зв'язок: один користувач може мати список замовлень
    orders = relationship("Order", back_populates="owner")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=10)  # Кількість товару на складі


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)  # Статус оплати замовлення (Вимога варіанту!)

    # Зв'язки для швидкого доступу через ORM
    owner = relationship("User", back_populates="orders")
    product = relationship("Product")