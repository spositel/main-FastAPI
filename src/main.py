import requests
import logging
from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException 
from models import BookShort, BookFull, BookUpdate
from typing import List, Optional
import json

from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_FILE = "books.json"
app = FastAPI()

# Абстрактный базовый класс для API-клиентов
class BaseApiClient(ABC):
    @abstractmethod
    def request(self, method: str, url: str, **kwargs) -> Optional[dict]:
        pass

class OpenLibraryClient(BaseApiClient):
    def request(self, method: str, url: str, **kwargs) -> Optional[dict]:
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Request to {url} failed: {str(e)}")
            return None

    def fetch_book_details(self, title: str, author: str) -> dict:
        """Возвращает дополнительные данные о книге из Open Library API"""
        
        search_data = self.request(
            "GET", 
            "https://openlibrary.org/search.json",
            params={"title": title, "author": author, "limit": 1}
        )
        
        if not search_data or not search_data.get("docs"):
            return {}

        work_key = search_data["docs"][0].get("key")
        if not work_key:
            return {}

        work_data = self.request("GET", f"https://openlibrary.org{work_key}.json")
        if not work_data:
            return {}

        cover_id = search_data["docs"][0].get("cover_i")
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
        
        description = None
        if "description" in work_data:
            if isinstance(work_data["description"], str):
                description = work_data["description"]
            elif isinstance(work_data["description"], dict):
                description = work_data["description"].get("value")
        
        rating = work_data.get("ratings_average")
        
        return {
            "cover": cover_url,
            "description": description,
            "rating": rating
        }
class BookRepository(ABC):
    @abstractmethod
    def init_db(self):
        pass
    
    @abstractmethod
    def read_books(self) -> List[dict]:
        pass
    
    @abstractmethod
    def write_books(self, books: List[dict]):
        pass

class FileBookRepository(BookRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.init_db()
    
    def init_db(self):
        try:
            with open(self.file_path, "r") as f:
                pass
        except FileNotFoundError:
            with open(self.file_path, "w") as f:
                json.dump([], f)
            logger.info("Created new books database")
    
    def read_books(self) -> List[dict]:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading books: {e}")
            return []
    
    def write_books(self, books: List[dict]):
        try:
            with open(self.file_path, "w") as f:
                json.dump(books, f, indent=2)
        except IOError as e:
            logger.error(f"Error writing books: {e}")

ol_client = OpenLibraryClient()
book_repo = FileBookRepository(DB_FILE)



@app.get("/books", response_model=List[BookShort])
def get_books(author: Optional[str] = None, 
              year: Optional[int] = None,
              genre: Optional[str] = None):
    books = book_repo.read_books()
    if author:
        books = [b for b in books if author.lower() in b["author"].lower()]
    if year:
        books = [b for b in books if b["year"] == year]
    if genre:
        books = [b for b in books if genre.lower() in b["genre"].lower()]

    return [BookShort(**{
        "id": b["id"],
        "title": b["title"],
        "author": b["author"],
        "year": b["year"]
    }) for b in books]



@app.get("/books/{book_id}")
def get_book(book_id: int):
    books = book_repo.read_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookFull(**book)



@app.post("/books")
def add_book(book: BookFull):
    books = book_repo.read_books()
    new_id = max(b["id"] for b in books) + 1 if books else 1
    new_book = book.dict()
    new_book["id"] = new_id

    extra_data = ol_client.fetch_book_details(book.title, book.author)
    new_book["extra_data"] = extra_data

    books.append(new_book)
    book_repo.write_books(books)
    
    response = {
        "message": "Книга добавлена",
        "id": new_id,
        "title": book.title,
        "author": book.author
    }
    if extra_data:
        response["extra_data"] = extra_data
        response["message"] += " (с дополнительными данными)"
    return response



@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookUpdate):
    books = book_repo.read_books()
    book_to_update = next((b for b in books if b["id"] == book_id), None)
    if not book_to_update:
        raise HTTPException(status_code=404, detail="Book not found")
    
    updated_fields = []
    update_data = book.dict(exclude_unset=True)
    skip_value = "Введите значение"
    
    for field, value in update_data.items():
        if value is None:
            continue
        if field in ["title", "author", "genre"] and value == skip_value:
            continue
        if field in ["year", "pages"] and value == 0:
            continue
        
        book_to_update[field] = value
        updated_fields.append(field)
    
    book_repo.write_books(books)
    return {
        "message": "Книга обновлена",
        "updated_fields": updated_fields
    }


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    books = book_repo.read_books()
    new_books = [b for b in books if b["id"] != book_id]
    if len(new_books) == len(books):
        raise HTTPException(status_code=404, detail="Book not found")
    book_repo.write_books(new_books)
    return {"message": "Книга удалена"}