import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
# Імпортуємо всі наші три роутери
from app.routers import auth_router, product_router, order_router

# Автоматичне створення таблиць ORM
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Online Shop REST API",
    description="Повноцінний Бекенд Інтернет-магазину на FastAPI (Варіант 9)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Реєструємо всі маршрути
app.include_router(auth_router.router)
app.include_router(product_router.router)
app.include_router(order_router.router)  # Підключили замовлення та адмінку

@app.get("/")
def root():
    return {
        "status": "active",
        "message": "Всі модулі REST API (Авторизація, Товари, Замовлення, Чорний список) успішно активовані!",
        "docs_url": "http://127.0.0.1:8000/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)