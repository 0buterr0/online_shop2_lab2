from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/auth", tags=["Автентифікація"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Реєстрація нового користувача (Клієнта)"""
    # Перевіряємо, чи існує вже користувач з таким логіном
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким ім'ям вже існує"
        )

    # Автоматично визначаємо роль: перший юзер 'admin' стає адміном, інші — client
    user_role = "admin" if user_data.username.lower() == "admin" else "client"

    # Хешуємо пароль та створюємо запис в базі
    hashed_pwd = auth.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        role=user_role,
        is_blocked=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Повертаємо чистий словник, щоб уникнути помилок сумісності зі схемами
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }

@router.post("/login", response_model=schemas.Token)
def login(
    user_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """Вхід у систему: перевірка пароля та видача токена (Сумісно зі Swagger та Frontend)"""
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    
    if not user or not auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильне ім'я користувача або пароль"
        )
        
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вхід неможливий: вас занесено до чорного списку!"
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}