import json
from pathlib import Path
from typing import Dict, Any

def save_progress(file_path: Path, data: Dict[str, Any]) -> None:
    """
    Сохранение прогресса переноса в JSON файл
    
    Args:
        file_path: Путь к файлу для сохранения
        data: Данные для сохранения
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_progress(file_path: Path) -> Dict[str, Any]:
    """
    Загрузка сохраненного прогресса из JSON файла
    
    Args:
        file_path: Путь к файлу с сохраненным прогрессом
        
    Returns:
        Dict[str, Any]: Загруженные данные или пустой словарь
    """
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} 