# Notion Database Transfer Tool / Инструмент переноса баз данных Notion

[English](#english) | [Русский](#russian)

## English

A tool for transferring data between Notion databases. Supports transfer between different workspaces and accounts.

### Features

- Transfer all records from one Notion database to another
- Preserve data structure and properties
- Handle API limitations
- Process logging
- Recovery capability after failures

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd notion-transfer-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create .env file based on .env.example:
```bash
cp .env.example .env
```

4. Fill .env with your data:
- ORIGIN_NOTION_TOKEN: Source account API token
- DEST_NOTION_TOKEN: Target account API token
- ORIGIN_DATABASE_ID: Source database ID
- DEST_DATABASE_ID: Target database ID

### Usage

1. Configure settings in .env file
2. Run the script:
```bash
python main.py
```

### Project Structure

```
notion-transfer-tool/
├── main.py                 # Entry point
├── config/
│   └── settings.py         # Project settings
├── notion/
│   ├── api.py             # API client
│   └── models.py          # Data models
├── utils/
│   ├── logger.py          # Logging settings
│   └── helpers.py         # Helper functions
├── requirements.txt        # Dependencies
└── .env                   # Configuration
```

### Logging

Logs are saved in the `logs/` directory and contain information about:
- Transfer start and completion
- Successfully transferred pages
- Errors and retry attempts
- Progress status

### Error Handling

- Automatic recovery after failures
- API error retries
- Progress saving
- Request rate limit handling

### License

MIT

---

## Russian

Инструмент для переноса данных между базами данных Notion. Поддерживает перенос между разными рабочими пространствами и аккаунтами.

### Возможности

- Перенос всех записей из одной базы данных Notion в другую
- Сохранение структуры данных и свойств
- Обработка ограничений API
- Логирование процесса переноса
- Возможность восстановления после сбоев

### Установка

1. Клонируйте репозиторий:
```bash
git clone [url-репозитория]
cd notion-transfer-tool
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

4. Заполните .env своими данными:
- ORIGIN_NOTION_TOKEN: API токен исходного аккаунта
- DEST_NOTION_TOKEN: API токен целевого аккаунта
- ORIGIN_DATABASE_ID: ID исходной базы данных
- DEST_DATABASE_ID: ID целевой базы данных

### Использование

1. Настройте конфигурацию в файле .env
2. Запустите скрипт:
```bash
python main.py
```

### Структура проекта

```
notion-transfer-tool/
├── main.py                 # Точка входа
├── config/
│   └── settings.py         # Настройки проекта
├── notion/
│   ├── api.py             # API клиент
│   └── models.py          # Модели данных
├── utils/
│   ├── logger.py          # Настройки логирования
│   └── helpers.py         # Вспомогательные функции
├── requirements.txt        # Зависимости
└── .env                   # Конфигурация
```

### Логирование

Логи сохраняются в директории `logs/` и содержат информацию о:
- Начале и завершении переноса
- Успешно перенесенных страницах
- Ошибках и повторных попытках
- Прогрессе выполнения

### Обработка ошибок

- Автоматическое восстановление после сбоев
- Повторные попытки при ошибках API
- Сохранение прогресса
- Обработка ограничений скорости запросов

### Лицензия

MIT
