import hashlib
from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

# Секретний ключ для шифрування токенів та алгоритм (згідно з концептом JWT)
SECRET_KEY = "SUPER_SECRET_KEY_FOR_LAB2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Шлях, куди FastAPI буде звертатися за токеном
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# --- Хешування паролів ---
def hash_password(password: str) -> str:
    """Хешує пароль за допомогою SHA-256 (без сторонніх важких ліб)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє, чи збігається введений пароль з хешем у базі"""
    return hash_password(plain_password) == hashed_password

# --- Робота з JWT токенами ---
def create_access_token(data: dict) -> str:
    """Генерує тимчасовий JWT токен для фронтенду"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Перевірка авторизації (Dependency) ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Захисна функція: перевіряє токен, дістає користувача та перевіряє Чорний список"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося перевірити облікові дані або токен застарів",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
        
    # БІЗНЕС-ЛОГІКА ВАРІАНТУ №9: Якщо користувач у чорному списку - блокуємо доступ до API
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ваш акаунт заблоковано адміністратором за несплату!"
        )
        
    return user