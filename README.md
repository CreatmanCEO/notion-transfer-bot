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
   - Copy the generated tokens

2. **Database IDs:**
   - Open your Notion database in browser
   - Copy the ID from the URL: `https://notion.so/workspace/{DATABASE_ID}?v=...`

### Development Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd notion-transfer-bot
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
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
WEBHOOK_URL=your_webhook_url  # Only for production
```

5. Run the bot:
```bash
python main.py
```

### Deployment to Render.com

1. Create a new account on [Render.com](https://render.com) if you don't have one
2. Fork this repository to your GitHub account
3. In Render dashboard:
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - Name: `notion-transfer-bot`
     - Environment: `Docker`
     - Region: Select nearest to your users
     - Branch: `main`
     - Plan: `Free`
   - Add environment variables:
     - `TELEGRAM_BOT_TOKEN`: Your bot token
     - `WEBHOOK_URL`: `https://your-service-name.onrender.com/webhook`
4. Click "Create Web Service"

The bot will automatically start when someone sends a message and stop after 15 minutes of inactivity to stay within the free tier limits.

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
   - Скопируйте сгенерированные токены

2. **ID баз данных:**
   - Откройте вашу базу данных Notion в браузере
   - Скопируйте ID из URL: `https://notion.so/workspace/{DATABASE_ID}?v=...`

### Настройка для разработки

1. Клонируйте репозиторий:
```bash
git clone [url-репозитория]
cd notion-transfer-bot
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
```
TELEGRAM_BOT_TOKEN=ваш_токен_telegram_бота
WEBHOOK_URL=ваш_webhook_url  # Только для продакшена
```

5. Запустите бота:
```bash
python main.py
```

### Деплой на Render.com

1. Создайте аккаунт на [Render.com](https://render.com), если у вас его нет
2. Сделайте форк этого репозитория в свой GitHub аккаунт
3. В панели управления Render:
   - Нажмите "New +"
   - Выберите "Web Service"
   - Подключите ваш GitHub репозиторий
   - Настройте сервис:
     - Имя: `notion-transfer-bot`
     - Окружение: `Docker`
     - Регион: Выберите ближайший к вашим пользователям
     - Ветка: `main`
     - План: `Free`
   - Добавьте переменные окружения:
     - `TELEGRAM_BOT_TOKEN`: Ваш токен бота
     - `WEBHOOK_URL`: `https://your-service-name.onrender.com/webhook`
4. Нажмите "Create Web Service"

Бот будет автоматически запускаться при получении сообщения и останавливаться после 15 минут неактивности, чтобы оставаться в пределах бесплатного тарифа.

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

### Лицензия

MIT
