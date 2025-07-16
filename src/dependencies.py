from app.services.api_client import get_api_client
from app.services.repository import get_book_repository

def get_dependencies():
    return {
        "api_client": get_api_client(),
        "book_repo": get_book_repository()
    }