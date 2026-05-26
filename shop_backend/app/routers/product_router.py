from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/products", tags=["Каталог Товарів"])

@router.get("/", response_model=List[schemas.ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Публічний ендпоінт: доступний усім (навіть неавторизованим), щоб бачити товари"""
    products = db.query(models.Product).all()
    return products

@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) # Захист токеном
):
    """Приватний ендпоінт: додавати товари може тільки Адміністратор"""
    # БІЗНЕС-ЛОГІКА ВАРІАНТУ №9: Перевірка ролі користувача
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено: Ця дія доступна лише для Адміністратора!"
        )
    
    # Якщо це адмін — створюємо товар
    new_product = models.Product(
        title=product_data.title,
        price=product_data.price,
        stock=product_data.stock
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product