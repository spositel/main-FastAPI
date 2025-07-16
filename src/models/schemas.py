from pydantic import BaseModel
from typing import Optional

class BookShort(BaseModel):
    id: int 
    title: str 
    author: str 
    year: int 


class BookFull(BookShort):
    genre: str 
    pages: int 
    available: bool = True# 

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    pages: Optional[int] = None
    available: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Введите значение",
                "author": "Введите значение",
                "year": 0,  
                "genre": "Введите значение",
                "pages": 0,  
                "available": True  
            }
        }