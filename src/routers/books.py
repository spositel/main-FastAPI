from fastapi import APIRouter, HTTPException
from typing import List, Optional
from src.models.schemas import BookShort, BookFull, BookUpdate
from src.services.repository import get_book_repository
from src.services.api_client import get_api_client

router = APIRouter()

@router.get("/books", response_model=List[BookShort])
async def get_books(
    author: Optional[str] = None, 
    year: Optional[int] = None,
    genre: Optional[str] = None
):
    book_repo = get_book_repository()
    books = book_repo.read_books()
    
    if author:
        books = [b for b in books if author.lower() in b["author"].lower()]
    if year:
        books = [b for b in books if b["year"] == year]
    if genre:
        books = [b for b in books if genre.lower() in b["genre"].lower()]

    return [BookShort(**b) for b in books]

@router.get("/books/{book_id}", response_model=BookFull)
async def get_book(book_id: int):
    book_repo = get_book_repository()
    books = book_repo.read_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookFull(**book)

@router.post("/books", status_code=201)
async def add_book(book: BookFull):
    book_repo = get_book_repository()
    ol_client = get_api_client()
    
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

@router.put("/books/{book_id}")
async def update_book(book_id: int, book: BookUpdate):
    book_repo = get_book_repository()
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

@router.delete("/books/{book_id}")
async def delete_book(book_id: int):
    book_repo = get_book_repository()
    books = book_repo.read_books()
    
    new_books = [b for b in books if b["id"] != book_id]
    if len(new_books) == len(books):
        raise HTTPException(status_code=404, detail="Book not found")
    
    book_repo.write_books(new_books)
    return {"message": "Книга удалена"}