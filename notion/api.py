import time
from typing import Dict, Any, Optional
import requests
from config.settings import (
    NOTION_API_VERSION,
    NOTION_BASE_URL,
    MAX_RETRIES,
    RETRY_DELAY,
    RATE_LIMIT_DELAY
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

class NotionAPI:
    """Класс для работы с API Notion"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Выполнение запроса к API с обработкой ошибок и повторными попытками
        
        Args:
            method: HTTP метод
            endpoint: Endpoint API
            data: Данные для отправки
            params: Параметры запроса
            
        Returns:
            Dict[str, Any]: Ответ от API
        """
        url = f"{NOTION_BASE_URL}/{endpoint}"
        retries = 0
        
        while retries < MAX_RETRIES:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )
                
                if response.status_code == 429:  # Rate limit
                    wait_time = int(response.headers.get("Retry-After", RATE_LIMIT_DELAY))
                    logger.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {str(e)}")
                if retries < MAX_RETRIES - 1:
                    retries += 1
                    time.sleep(RETRY_DELAY)
                    continue
                raise
    
    def query_database(
        self,
        database_id: str,
        start_cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получение данных из базы данных
        
        Args:
            database_id: ID базы данных
            start_cursor: Курсор для пагинации
            
        Returns:
            Dict[str, Any]: Результаты запроса
        """
        endpoint = f"databases/{database_id}/query"
        data = {"start_cursor": start_cursor} if start_cursor else {}
        return self._make_request("POST", endpoint, data=data)
    
    def create_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание новой страницы
        
        Args:
            page_data: Данные страницы
            
        Returns:
            Dict[str, Any]: Созданная страница
        """
        return self._make_request("POST", "pages", data=page_data) 