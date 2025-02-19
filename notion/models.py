from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class NotionPage(BaseModel):
    """Модель страницы Notion"""
    id: str
    properties: Dict[str, Any]
    children: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class TransferProgress(BaseModel):
    """Модель для отслеживания прогресса переноса"""
    total_pages: int = 0
    transferred_pages: List[str] = Field(default_factory=list)
    failed_pages: Dict[str, str] = Field(default_factory=dict)
    current_cursor: Optional[str] = None

    def add_transferred_page(self, page_id: str) -> None:
        """Добавление успешно перенесенной страницы"""
        if page_id not in self.transferred_pages:
            self.transferred_pages.append(page_id)

    def add_failed_page(self, page_id: str, error: str) -> None:
        """Добавление страницы с ошибкой"""
        self.failed_pages[page_id] = error

    @property
    def progress_percentage(self) -> float:
        """Процент выполнения"""
        if self.total_pages == 0:
            return 0.0
        return (len(self.transferred_pages) / self.total_pages) * 100 