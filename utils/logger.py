import logging
from rich.logging import RichHandler
from config.settings import LOG_FORMAT, LOG_FILE, LOG_LEVEL

def setup_logger(name: str) -> logging.Logger:
    """
    Настройка логгера с выводом в файл и консоль
    
    Args:
        name: Имя логгера
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Форматтер для логов
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Обработчик для файла
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Обработчик для консоли с rich форматированием
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console_handler)
    
    return logger 