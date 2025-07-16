import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

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

# Глобальный экземпляр репозитория
_repository = FileBookRepository("books.json")

def get_book_repository() -> FileBookRepository:
    return _repository