from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# База даних буде зберігатися в автоматичному файлі shop_v2.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./shop_v2.db"

# Створюємо рушій (engine) для зв'язку з SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Створюємо фабрику сесій для виконання запитів (створення, читання, видалення)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас, від якого будуть успадковуватися всі наші таблиці (класи-моделі)
Base = declarative_base()

# Функція-генератор для керування сесіями (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()