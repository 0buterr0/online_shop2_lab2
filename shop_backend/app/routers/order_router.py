from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/orders", tags=["Замовлення та Адміністрування"])

# ==========================================
# ЛОГІКА ДЛЯ КЛІЄНТІВ (ORDERS)
# ==========================================

@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: schemas.OrderCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не знайдено")
        
    if product.stock < order_data.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Недостатньо товару на складі. Доступно: {product.stock}"
        )
        
    product.stock -= order_data.quantity
    total_price = product.price * order_data.quantity
    
    new_order = models.Order(
        user_id=current_user.id,
        product_id=product.id,
        quantity=order_data.quantity,
        total_price=total_price,
        is_paid=False 
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/all", response_model=List[schemas.OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Адмінський ендпоінт: отримує список УСІХ замовлень"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    return db.query(models.Order).all()
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")
        
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Ви можете оплачувати лише власні замовлення")
        
    if order.is_paid:
        raise HTTPException(status_code=400, detail="Замовлення вже оплачено")
        
    order.is_paid = True
    db.commit()
    db.refresh(order)
    return order


@router.get("/my", response_model=List[schemas.OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    return orders

# ==========================================
# ЛОГІКА ДЛЯ АДМІНІСТРАТОРА
# ==========================================

@router.get("/all", response_model=List[schemas.OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Адмін може бачити всі замовлення всіх користувачів"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    return db.query(models.Order).all()

@router.post("/users/{user_id}/block")
def toggle_user_block(
    user_id: int, 
    block: bool, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор має доступ")
        
    user_to_mod = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_mod:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
        
    if user_to_mod.role == "admin":
        raise HTTPException(status_code=400, detail="Неможливо заблокувати іншого адміністратора")
        
    user_to_mod.is_blocked = block
    db.commit()
    
    status_str = "заблоковано" if block else "розблоковано"
    return {"message": f"Користувача {user_to_mod.username} успішно {status_str}."}