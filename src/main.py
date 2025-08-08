import uvicorn
import logging
from fastapi import FastAPI
from .routers import books
from .routers import experement
from fastapi.middleware.cors import CORSMiddleware
from .utils.logger import setup_logger

logger = setup_logger("app.main")

app = FastAPI(
    title="Библиотечный каталог",
    description="API для управления библиотечным каталогом",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(books.router)
app.include_router(experement.router)

logger.info("Приложение успешно настроено") 

@app.on_event("startup")
async def startup_event():
    logger.info("Приложение запущено")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Приложение остановлено")
    
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)




