# Notion Database Transfer Bot / Бот для переноса баз данных Notion

[English](#english) | [Русский](#russian)

## English

A Telegram bot for transferring data between Notion databases. The bot helps users migrate data between different workspaces and accounts through a simple chat interface.

### Features

- Transfer all records from one Notion database to another
- Preserve data structure and properties
- Handle API limitations
- Real-time progress updates
- Support for multiple users
- Interactive dialog interface
- Error handling and recovery
- Automatic scaling on Render.com (starts on request)
- Multilingual interface (English and Russian)
- Comprehensive help system and FAQ
- Strict token format validation
- Language switching at any point without losing progress

### Usage

1. Start a chat with [@NotionTransferBot](https://t.me/NotionExportBot)
2. Choose your preferred language (English or Russian)
3. Use the interactive menu to:
   - Start data transfer
   - Learn how to get Notion tokens
   - Find database IDs
   - Read FAQ
   - Get help
4. Follow the bot's instructions to provide:
   - Source Notion API token
   - Target Notion API token
   - Source database ID
   - Target database ID
5. Monitor the transfer progress in real-time

### Bot Commands

- `/start` - Start the bot and choose language
- `/cancel` - Cancel current operation
- `/help` - Show help information

### How to Get Notion API Tokens and Database IDs

1. **API Tokens:**
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Create a new integration for both source and target workspaces
   - Copy the generated tokens (format: secret_xxxxx...)

2. **Database IDs:**
   - Open your Notion database in browser
   - Copy the ID from the URL: `https://notion.so/workspace/{DATABASE_ID}?v=...`


### Project Structure

```
notion-transfer-bot/
├── main.py                 # Bot implementation and entry point
├── config/
│   └── settings.py         # Project settings
├── notion/
│   ├── api.py             # Notion API client
│   └── models.py          # Data models
├── utils/
│   ├── logger.py          # Logging settings
│   └── helpers.py         # Helper functions
├── Dockerfile             # Docker configuration
├── render.yaml            # Render.com configuration
├── requirements.txt       # Dependencies
└── .env                   # Configuration
```

### Potential Improvements

1. **Data Transfer Enhancements:**
   - Support for nested pages and subpages
   - Handling of file attachments
   - Selective property transfer
   - Database schema comparison before transfer

2. **User Experience:**
   - Progress visualization with charts
   - Transfer scheduling
   - Batch operations
   - Transfer templates
   - Database preview before transfer

3. **Security:**
   - Token encryption in storage
   - Rate limiting
   - Access control lists
   - Audit logging

4. **Performance:**
   - Parallel transfers
   - Batch processing
   - Caching of frequently accessed data
   - Optimized database queries

5. **Monitoring and Maintenance:**
   - Health check dashboard
   - Usage statistics
   - Error rate monitoring
   - Automated backups

6. **Integration:**
   - Support for other Notion features
   - Export to different formats
   - Integration with other platforms
   - API for external access

### Support

Need help? Contact [@Creatman_it](https://t.me/Creatman_it)

### License

MIT

---

## Russian

Telegram бот для переноса данных между базами данных Notion. Бот помогает пользователям мигрировать данные между различными рабочими пространствами и аккаунтами через простой чат-интерфейс.

### Возможности

- Перенос всех записей из одной базы данных Notion в другую
- Сохранение структуры данных и свойств
- Обработка ограничений API
- Обновления прогресса в реальном времени
- Поддержка множества пользователей
- Интерактивный диалоговый интерфейс
- Обработка ошибок и восстановление
- Автоматическое масштабирование на Render.com (запуск по запросу)
- Многоязычный интерфейс (русский и английский)
- Система помощи и FAQ
- Строгая валидация формата токенов
- Переключение языка в любой момент без потери прогресса

### Использование

1. Начните чат с [@NotionTransferBot](https://t.me/NotionExportBot)
2. Выберите предпочитаемый язык (русский или английский)
3. Используйте интерактивное меню для:
   - Начала переноса данных
   - Получения информации о токенах Notion
   - Поиска ID баз данных
   - Чтения FAQ
   - Получения помощи
4. Следуйте инструкциям бота для предоставления:
   - API токена исходного аккаунта Notion
   - API токена целевого аккаунта Notion
   - ID исходной базы данных
   - ID целевой базы данных
5. Отслеживайте прогресс переноса в реальном времени

### Команды бота

- `/start` - Запустить бота и выбрать язык
- `/cancel` - Отменить текущую операцию
- `/help` - Показать справку

### Как получить API токены и ID баз данных Notion

1. **API токены:**
   - Перейдите в [Notion Integrations](https://www.notion.so/my-integrations)
   - Создайте новую интеграцию для исходного и целевого рабочих пространств
   - Скопируйте сгенерированные токены (формат: secret_xxxxx...)

2. **ID баз данных:**
   - Откройте вашу базу данных Notion в браузере
   - Скопируйте ID из URL: `https://notion.so/workspace/{DATABASE_ID}?v=...`


### Структура проекта

```
notion-transfer-bot/
├── main.py                 # Реализация бота и точка входа
├── config/
│   └── settings.py         # Настройки проекта
├── notion/
│   ├── api.py             # API клиент Notion
│   └── models.py          # Модели данных
├── utils/
│   ├── logger.py          # Настройки логирования
│   └── helpers.py         # Вспомогательные функции
├── Dockerfile             # Конфигурация Docker
├── render.yaml            # Конфигурация Render.com
├── requirements.txt       # Зависимости
└── .env                   # Конфигурация
```

### Потенциальные улучшения

1. **Улучшения переноса данных:**
   - Поддержка вложенных страниц и подстраниц
   - Обработка файловых вложений
   - Выборочный перенос свойств
   - Сравнение схем баз данных перед переносом

2. **Пользовательский опыт:**
   - Визуализация прогресса с графиками
   - Планирование переносов
   - Пакетные операции
   - Шаблоны переноса
   - Предварительный просмотр базы данных

3. **Безопасность:**
   - Шифрование токенов при хранении
   - Ограничение частоты запросов
   - Списки контроля доступа
   - Аудит действий

4. **Производительность:**
   - Параллельные переносы
   - Пакетная обработка
   - Кэширование часто используемых данных
   - Оптимизация запросов к базе данных

5. **Мониторинг и обслуживание:**
   - Панель проверки состояния
   - Статистика использования
   - Мониторинг частоты ошибок
   - Автоматическое резервное копирование

6. **Интеграция:**
   - Поддержка других функций Notion
   - Экспорт в различные форматы
   - Интеграция с другими платформами
   - API для внешнего доступа

### Поддержка

Нужна помощь? Напишите [@Creatman_it](https://t.me/Creatman_it)

### Лицензия

MIT
