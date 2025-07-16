import requests
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict

logger = logging.getLogger(__name__)

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
        
        description = work_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")
        
        rating = work_data.get("ratings_average")
        
        return {
            "cover": cover_url,
            "description": description,
            "rating": rating
        }

# Глобальный экземпляр клиента
_api_client = OpenLibraryClient()

def get_api_client() -> OpenLibraryClient:
    return _api_client