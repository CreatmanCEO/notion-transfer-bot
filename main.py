import sys
import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, filters
from aiohttp import web
import asyncio

from config.settings import BASE_DIR
from notion.api import NotionAPI
from notion.models import NotionPage, TransferProgress
from utils.logger import setup_logger
from utils.helpers import save_progress, load_progress

# Загрузка переменных окружения
load_dotenv()

logger = setup_logger(__name__)

# Состояния диалога
(LANGUAGE_SELECT, MAIN_MENU, TRANSFER_START, ORIGIN_TOKEN, DEST_TOKEN, 
 ORIGIN_DB, DEST_DB, CONFIRMATION, FAQ, HELP) = range(10)

# Данные пользователей
user_data: Dict[int, dict] = {}

# Тексты на разных языках
TEXTS = {
    'ru': {
        'welcome': (
            "👋 Привет! Я бот для переноса данных между базами Notion.\n\n"
            "Я помогу вам:\n"
            "📋 Перенести все записи из одной базы в другую\n"
            "🔄 Сохранить структуру и свойства данных\n"
            "📊 Отслеживать прогресс в реальном времени\n\n"
            "Выберите язык интерфейса:"
        ),
        'main_menu': "🏠 Главное меню",
        'select_action': "Выберите действие:",
        'start_transfer': "🚀 Начать перенос",
        'how_to_get_tokens': "🔑 Как получить токены",
        'how_to_get_db_ids': "📝 Как получить ID базы",
        'faq': "❓ FAQ",
        'about': "ℹ️ О боте",
        'help': "🆘 Помощь",
        'cancel': "❌ Отмена",
        'back': "⬅️ Назад",
        'origin_token_prompt': (
            "🔑 Отправьте токен исходного аккаунта Notion\n\n"
            "Как получить токен:\n"
            "1. Перейдите на https://www.notion.so/my-integrations\n"
            "2. Нажмите 'New integration'\n"
            "3. Заполните форму и получите токен"
        ),
        'dest_token_prompt': "🔑 Теперь отправьте токен целевого аккаунта Notion",
        'origin_db_prompt': (
            "📁 Отправьте ID исходной базы данных\n\n"
            "ID базы можно найти в её URL:\n"
            "notion.so/workspace/[ID-БАЗЫ]?v=..."
        ),
        'dest_db_prompt': "📁 Отправьте ID целевой базы данных",
        'faq_text': (
            "*Часто задаваемые вопросы:*\n\n"
            "*В: Как получить токен Notion?*\n"
            "О: Перейдите в [Notion Integrations](https://www.notion.so/my-integrations), "
            "создайте новую интеграцию и скопируйте токен.\n\n"
            "*В: Где найти ID базы данных?*\n"
            "О: Откройте базу данных в браузере и скопируйте ID из URL:\n"
            "`notion.so/workspace/{ID-БАЗЫ}?v=...`\n\n"
            "*В: Какие данные переносятся?*\n"
            "О: Все записи базы данных с сохранением структуры и свойств.\n\n"
            "*В: Можно ли отменить перенос?*\n"
            "О: Да, используйте команду /cancel в любой момент."
        ),
        'about_text': (
            "*О боте:*\n\n"
            "Notion Transfer Bot помогает переносить данные между базами Notion. "
            "Бот использует официальный API Notion и поддерживает:\n\n"
            "✅ Перенос всех записей\n"
            "✅ Сохранение структуры\n"
            "✅ Отслеживание прогресса\n"
            "✅ Восстановление после ошибок\n\n"
            "Версия: 1.0.0\n"
            "Разработчик: @your_username"
        ),
        'help_text': (
            "*Помощь:*\n\n"
            "🔹 */start* - Начать работу\n"
            "🔹 */cancel* - Отменить текущую операцию\n"
            "🔹 */help* - Показать это сообщение\n\n"
            "При возникновении проблем:\n"
            "1. Проверьте правильность токенов\n"
            "2. Убедитесь, что ID баз указаны верно\n"
            "3. Проверьте права доступа интеграций\n\n"
            "Нужна помощь? Напишите @your_username"
        )
    },
    'en': {
        'welcome': (
            "👋 Hi! I'm a bot for transferring data between Notion databases.\n\n"
            "I'll help you:\n"
            "📋 Transfer all records from one database to another\n"
            "🔄 Preserve data structure and properties\n"
            "📊 Track progress in real-time\n\n"
            "Choose interface language:"
        ),
        'main_menu': "🏠 Main Menu",
        'select_action': "Select an action:",
        'start_transfer': "🚀 Start Transfer",
        'how_to_get_tokens': "🔑 How to Get Tokens",
        'how_to_get_db_ids': "📝 How to Get DB IDs",
        'faq': "❓ FAQ",
        'about': "ℹ️ About",
        'help': "🆘 Help",
        'cancel': "❌ Cancel",
        'back': "⬅️ Back",
        'origin_token_prompt': (
            "🔑 Send the source Notion account token\n\n"
            "How to get the token:\n"
            "1. Go to https://www.notion.so/my-integrations\n"
            "2. Click 'New integration'\n"
            "3. Fill the form and get the token"
        ),
        'dest_token_prompt': "🔑 Now send the target account token",
        'origin_db_prompt': (
            "📁 Send the source database ID\n\n"
            "You can find the ID in its URL:\n"
            "notion.so/workspace/[DATABASE-ID]?v=..."
        ),
        'dest_db_prompt': "📁 Send the target database ID",
        'faq_text': (
            "*Frequently Asked Questions:*\n\n"
            "*Q: How to get a Notion token?*\n"
            "A: Go to [Notion Integrations](https://www.notion.so/my-integrations), "
            "create a new integration and copy the token.\n\n"
            "*Q: Where to find database ID?*\n"
            "A: Open the database in browser and copy ID from URL:\n"
            "`notion.so/workspace/{DATABASE-ID}?v=...`\n\n"
            "*Q: What data is transferred?*\n"
            "A: All database records with preserved structure and properties.\n\n"
            "*Q: Can I cancel the transfer?*\n"
            "A: Yes, use /cancel command at any time."
        ),
        'about_text': (
            "*About:*\n\n"
            "Notion Transfer Bot helps transfer data between Notion databases. "
            "The bot uses official Notion API and supports:\n\n"
            "✅ All records transfer\n"
            "✅ Structure preservation\n"
            "✅ Progress tracking\n"
            "✅ Error recovery\n\n"
            "Version: 1.0.0\n"
            "Developer: @your_username"
        ),
        'help_text': (
            "*Help:*\n\n"
            "🔹 */start* - Start working\n"
            "🔹 */cancel* - Cancel current operation\n"
            "🔹 */help* - Show this message\n\n"
            "If you encounter problems:\n"
            "1. Check if tokens are correct\n"
            "2. Make sure database IDs are valid\n"
            "3. Verify integration permissions\n\n"
            "Need help? Contact @your_username"
        )
    }
}

# Глобальная переменная для хранения объекта приложения
app = None

class NotionTransfer:
    """Класс для управления процессом переноса данных"""
    
    def __init__(self, origin_token: str, dest_token: str, origin_db: str, dest_db: str):
        self.origin_api = NotionAPI(origin_token)
        self.dest_api = NotionAPI(dest_token)
        self.origin_db = origin_db
        self.dest_db = dest_db
        self.progress_file = BASE_DIR / f"transfer_progress_{origin_db}.json"
        self.progress = TransferProgress()
        
    def load_saved_progress(self) -> None:
        """Загрузка сохраненного прогресса"""
        saved_data = load_progress(self.progress_file)
        if saved_data:
            self.progress = TransferProgress(**saved_data)
            logger.info(f"Загружен сохраненный прогресс: {self.progress.progress_percentage:.1f}%")
    
    async def transfer_page(self, page: NotionPage) -> Optional[str]:
        """Перенос одной страницы"""
        try:
            page_data = {
                "parent": {"database_id": self.dest_db},
                "properties": page.properties
            }
            
            response = await self.dest_api.create_page(page_data)
            return response["id"]
            
        except Exception as e:
            logger.error(f"Ошибка при переносе страницы {page.id}: {str(e)}")
            return None
    
    async def run(self, update: Update) -> None:
        """Запуск процесса переноса"""
        try:
            self.load_saved_progress()
            
            # Получение всех страниц из исходной базы данных
            response = await self.origin_api.query_database(
                self.origin_db,
                start_cursor=self.progress.current_cursor
            )
            
            if not response.get("results"):
                await update.message.reply_text("❌ Нет данных в исходной базе данных")
                return
            
            # Обновление общего количества страниц
            self.progress.total_pages = len(response["results"])
            await update.message.reply_text(f"📊 Найдено {self.progress.total_pages} страниц для переноса")
            
            # Перенос каждой страницы
            for i, result in enumerate(response["results"], 1):
                page = NotionPage(
                    id=result["id"],
                    properties=result["properties"],
                    children=result.get("children", [])
                )
                
                if page.id in self.progress.transferred_pages:
                    continue
                
                if new_page_id := await self.transfer_page(page):
                    self.progress.add_transferred_page(page.id)
                    if i % 5 == 0:  # Обновляем статус каждые 5 страниц
                        await update.message.reply_text(
                            f"✅ Прогресс: {self.progress.progress_percentage:.1f}% "
                            f"({i}/{self.progress.total_pages})"
                        )
                else:
                    self.progress.add_failed_page(page.id, "Ошибка при создании страницы")
                
                # Сохранение прогресса после каждой страницы
                save_progress(self.progress_file, self.progress.dict())
            
            # Финальное сообщение
            if self.progress.failed_pages:
                await update.message.reply_text(
                    f"⚠️ Перенос завершен с ошибками\n"
                    f"Успешно перенесено: {len(self.progress.transferred_pages)} страниц\n"
                    f"Ошибок: {len(self.progress.failed_pages)} страниц"
                )
            else:
                await update.message.reply_text("✅ Перенос успешно завершен!")
                
        except Exception as e:
            logger.error(f"Критическая ошибка: {str(e)}")
            await update.message.reply_text(f"❌ Произошла ошибка: {str(e)}")

def get_language_keyboard():
    """Создание клавиатуры выбора языка"""
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard(lang: str):
    """Создание клавиатуры главного меню"""
    texts = TEXTS[lang]
    keyboard = [
        [InlineKeyboardButton(texts['start_transfer'], callback_data="transfer")],
        [
            InlineKeyboardButton(texts['how_to_get_tokens'], callback_data="tokens_help"),
            InlineKeyboardButton(texts['how_to_get_db_ids'], callback_data="db_help")
        ],
        [
            InlineKeyboardButton(texts['faq'], callback_data="faq"),
            InlineKeyboardButton(texts['about'], callback_data="about")
        ],
        [InlineKeyboardButton(texts['help'], callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Веб-хендлеры
async def health_check(request):
    """Эндпоинт проверки здоровья сервиса"""
    return web.Response(text="OK", status=200)

async def webhook_handler(request):
    """Обработчик вебхуков от Telegram"""
    if app:
        update = Update.de_json(await request.json(), app.bot)
        await app.process_update(update)
    return web.Response(status=200)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога"""
    await update.message.reply_text(
        TEXTS['ru']['welcome'],  # Начинаем с русского
        reply_markup=get_language_keyboard()
    )
    return LANGUAGE_SELECT

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора языка"""
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split('_')[1]
    context.user_data['language'] = lang
    
    await query.edit_message_text(
        text=TEXTS[lang]['select_action'],
        reply_markup=get_main_menu_keyboard(lang)
    )
    return MAIN_MENU

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка действий из главного меню"""
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'ru')
    texts = TEXTS[lang]
    
    action = query.data
    if action == "transfer":
        await query.edit_message_text(texts['origin_token_prompt'])
        return ORIGIN_TOKEN
    elif action in ["tokens_help", "db_help", "faq", "about", "help"]:
        text = texts[f'{action}_text']
        keyboard = [[InlineKeyboardButton(texts['back'], callback_data="back_to_menu")]]
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return MAIN_MENU
    elif action == "back_to_menu":
        await query.edit_message_text(
            text=texts['select_action'],
            reply_markup=get_main_menu_keyboard(lang)
        )
        return MAIN_MENU
    
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена операции"""
    user = update.message.from_user
    lang = context.user_data.get('language', 'ru')
    logger.info(f"Пользователь {user.id} отменил операцию")
    
    await update.message.reply_text(
        TEXTS[lang]['cancel'],
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def get_origin_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение токена исходного аккаунта"""
    lang = context.user_data.get('language', 'ru')
    user_data[update.effective_user.id] = {"origin_token": update.message.text}
    
    await update.message.reply_text(TEXTS[lang]['dest_token_prompt'])
    return DEST_TOKEN

async def get_dest_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение токена целевого аккаунта"""
    lang = context.user_data.get('language', 'ru')
    user_data[update.effective_user.id]["dest_token"] = update.message.text
    
    await update.message.reply_text(TEXTS[lang]['origin_db_prompt'])
    return ORIGIN_DB

async def get_origin_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение ID исходной базы данных"""
    lang = context.user_data.get('language', 'ru')
    user_data[update.effective_user.id]["origin_db"] = update.message.text
    
    await update.message.reply_text(TEXTS[lang]['dest_db_prompt'])
    return DEST_DB

async def get_dest_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение ID целевой базы данных"""
    user_id = update.effective_user.id
    user_data[user_id]["dest_db"] = update.message.text
    
    # Создание экземпляра класса переноса
    transfer = NotionTransfer(
        origin_token=user_data[user_id]["origin_token"],
        dest_token=user_data[user_id]["dest_token"],
        origin_db=user_data[user_id]["origin_db"],
        dest_db=user_data[user_id]["dest_db"]
    )
    
    await update.message.reply_text("🚀 Начинаю процесс переноса...")
    await transfer.run(update)
    
    # Очистка данных пользователя
    del user_data[user_id]
    
    return ConversationHandler.END

async def setup_webhook(app: Application, webhook_url: str):
    """Настройка вебхука"""
    await app.bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен на {webhook_url}")

async def run_web_server():
    """Запуск веб-сервера"""
    web_app = web.Application()
    web_app.router.add_get("/health", health_check)
    web_app.router.add_post("/webhook", webhook_handler)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Веб-сервер запущен на порту {port}")

def main() -> None:
    """Запуск бота"""
    global app
    
    # Проверка наличия токена бота
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "7343545514:AAFUY4a9arc5dR2wHQU5uma3AC58HJ03vJM")
    if not bot_token:
        logger.error("Отсутствует токен бота (TELEGRAM_BOT_TOKEN)")
        sys.exit(1)
    
    # Создание и настройка бота
    app = Application.builder().token(bot_token).build()
    
    # Добавление обработчиков
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE_SELECT: [CallbackQueryHandler(language_callback, pattern=r"^lang_")],
            MAIN_MENU: [CallbackQueryHandler(menu_callback)],
            ORIGIN_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_origin_token)],
            DEST_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dest_token)],
            ORIGIN_DB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_origin_db)],
            DEST_DB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dest_db)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    
    # Запуск веб-сервера и настройка вебхука
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        # Создаем и запускаем асинхронный цикл событий
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Инициализируем приложение
        loop.run_until_complete(app.initialize())
        
        # Настраиваем вебхук и запускаем сервер
        loop.run_until_complete(setup_webhook(app, webhook_url))
        loop.run_until_complete(run_web_server())
        
        # Запускаем приложение
        loop.run_until_complete(app.start())
        
        # Запускаем цикл событий
        loop.run_forever()
    else:
        # Fallback на polling режим для локальной разработки
        app.run_polling()

if __name__ == "__main__":
    main() 