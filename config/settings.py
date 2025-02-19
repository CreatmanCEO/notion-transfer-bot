import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Загрузка переменных окружения
load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Создание директории для логов, если она не существует
LOGS_DIR.mkdir(exist_ok=True)

# Проверка наличия .env в .gitignore
gitignore_path = BASE_DIR / ".gitignore"
if gitignore_path.exists():
    with open(gitignore_path, 'r') as f:
        if '.env' not in f.read():
            logging.warning(
                "ВНИМАНИЕ: .env файл не добавлен в .gitignore! "
                "Это может привести к утечке конфиденциальных данных."
            )

# Настройки API Notion
NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

# Токены и ID баз данных с проверкой формата
ORIGIN_NOTION_TOKEN = os.getenv("ORIGIN_NOTION_TOKEN")
DEST_NOTION_TOKEN = os.getenv("DEST_NOTION_TOKEN")
ORIGIN_DATABASE_ID = os.getenv("ORIGIN_DATABASE_ID")
DEST_DATABASE_ID = os.getenv("DEST_DATABASE_ID")

# Проверка формата токенов (базовая валидация)
def validate_token(token: str) -> bool:
    if not token:
        return False
    if token.startswith("secret_"):
        return len(token) > 50  # Примерная длина токена Notion
    return False

# Проверка формата ID базы данных
def validate_database_id(db_id: str) -> bool:
    if not db_id:
        return False
    return len(db_id) > 30  # Примерная длина ID базы данных Notion

# Валидация конфиденциальных данных
if not all(validate_token(token) for token in [ORIGIN_NOTION_TOKEN, DEST_NOTION_TOKEN]):
    logging.warning(
        "ВНИМАНИЕ: Формат токенов не соответствует ожидаемому! "
        "Убедитесь, что вы используете правильные токены Notion."
    )

if not all(validate_database_id(db_id) for db_id in [ORIGIN_DATABASE_ID, DEST_DATABASE_ID]):
    logging.warning(
        "ВНИМАНИЕ: Формат ID баз данных не соответствует ожидаемому! "
        "Убедитесь, что вы используете правильные ID."
    )

# Настройки повторных попыток
MAX_RETRIES = 3
RETRY_DELAY = 1  # в секундах
RATE_LIMIT_DELAY = 5  # в секундах

# Настройки логирования
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "notion_transfer.log"
LOG_LEVEL = "INFO" 