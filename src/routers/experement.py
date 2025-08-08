from fastapi import APIRouter, HTTPException
from typing import List, Optional
from src.models.schemas import BookShort, BookFull, BookUpdate
from src.services.repository import get_book_repository

router = APIRouter()

@router.get("/experement")
async def experement():
    """Корневой маршрут, возвращающий приветственное сообщение."""
    #logger.info("Запрос к корневому маршруту")
    return {"message": "Здесь пока ничего нет"}