import requests
import logging
from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException 
from src.routers import books

from typing import List, Optional
import json

from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_FILE = "books.json"
app = FastAPI(
    title="Библиотечный каталог",
    description="API для управления библиотечным каталогом",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.include_router(books.router)

    

@app.on_event("startup")
async def startup_event():
    logger.info("Application started")







