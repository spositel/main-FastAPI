#from pydantic import BaseModel
#from typing import Optional

from pydantic import BaseModel, HttpUrl
from typing import Optional
from enum import Enum

class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"

class StorageType(str, Enum):
    FILE = "file"
    JSONBIN = "jsonbin"
    DB = "db"

class BookFilter(BaseModel):
    author: Optional[str] = None
    genre: Optional[str] = None
    availability: Optional[AvailabilityStatus] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "author": "Достоевский",
                "genre": "Роман",
                "availability": "available",
                "limit": 10,
                "offset": 0
            }
        }




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