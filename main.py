import sys
from pathlib import Path
from typing import Optional

from config.settings import (
    ORIGIN_NOTION_TOKEN,
    DEST_NOTION_TOKEN,
    ORIGIN_DATABASE_ID,
    DEST_DATABASE_ID,
    BASE_DIR
)
from notion.api import NotionAPI
from notion.models import NotionPage, TransferProgress
from utils.logger import setup_logger
from utils.helpers import save_progress, load_progress

logger = setup_logger(__name__)

class NotionTransfer:
    """Класс для управления процессом переноса данных"""
    
    def __init__(self):
        self.origin_api = NotionAPI(ORIGIN_NOTION_TOKEN)
        self.dest_api = NotionAPI(DEST_NOTION_TOKEN)
        self.progress_file = BASE_DIR / "transfer_progress.json"
        self.progress = TransferProgress()
        
    def load_saved_progress(self) -> None:
        """Загрузка сохраненного прогресса"""
        saved_data = load_progress(self.progress_file)
        if saved_data:
            self.progress = TransferProgress(**saved_data)
            logger.info(f"Загружен сохраненный прогресс: {self.progress.progress_percentage:.1f}%")
    
    def transfer_page(self, page: NotionPage) -> Optional[str]:
        """
        Перенос одной страницы
        
        Args:
            page: Страница для переноса
            
        Returns:
            Optional[str]: ID созданной страницы или None в случае ошибки
        """
        try:
            page_data = {
                "parent": {"database_id": DEST_DATABASE_ID},
                "properties": page.properties
            }
            
            response = self.dest_api.create_page(page_data)
            return response["id"]
            
        except Exception as e:
            logger.error(f"Ошибка при переносе страницы {page.id}: {str(e)}")
            return None
    
    def run(self) -> None:
        """Запуск процесса переноса"""
        try:
            self.load_saved_progress()
            
            # Получение всех страниц из исходной базы данных
            response = self.origin_api.query_database(
                ORIGIN_DATABASE_ID,
                start_cursor=self.progress.current_cursor
            )
            
            if not response.get("results"):
                logger.warning(f"Нет данных в базе {ORIGIN_DATABASE_ID}")
                return
            
            # Обновление общего количества страниц
            self.progress.total_pages = len(response["results"])
            logger.info(f"Найдено {self.progress.total_pages} страниц для переноса")
            
            # Перенос каждой страницы
            for result in response["results"]:
                page = NotionPage(
                    id=result["id"],
                    properties=result["properties"],
                    children=result.get("children", [])
                )
                
                if page.id in self.progress.transferred_pages:
                    logger.info(f"Страница {page.id} уже перенесена, пропускаем")
                    continue
                
                if new_page_id := self.transfer_page(page):
                    self.progress.add_transferred_page(page.id)
                    logger.info(
                        f"Страница {page.id} успешно перенесена как {new_page_id}. "
                        f"Прогресс: {self.progress.progress_percentage:.1f}%"
                    )
                else:
                    self.progress.add_failed_page(page.id, "Ошибка при создании страницы")
                
                # Сохранение прогресса после каждой страницы
                save_progress(self.progress_file, self.progress.dict())
            
            logger.info("Перенос завершен!")
            
            if self.progress.failed_pages:
                logger.warning(
                    f"Не удалось перенести {len(self.progress.failed_pages)} страниц. "
                    "Проверьте лог для деталей."
                )
                
        except Exception as e:
            logger.error(f"Критическая ошибка: {str(e)}")
            sys.exit(1)

def main():
    """Точка входа в программу"""
    # Проверка наличия необходимых переменных окружения
    required_vars = {
        "ORIGIN_NOTION_TOKEN": ORIGIN_NOTION_TOKEN,
        "DEST_NOTION_TOKEN": DEST_NOTION_TOKEN,
        "ORIGIN_DATABASE_ID": ORIGIN_DATABASE_ID,
        "DEST_DATABASE_ID": DEST_DATABASE_ID
    }
    
    missing_vars = [name for name, value in required_vars.items() if not value]
    
    if missing_vars:
        logger.error(
            f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}\n"
            "Пожалуйста, создайте файл .env на основе .env.example"
        )
        sys.exit(1)
    
    transfer = NotionTransfer()
    transfer.run()

if __name__ == "__main__":
    main() 