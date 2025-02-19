import sys
import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
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
ORIGIN_TOKEN, DEST_TOKEN, ORIGIN_DB, DEST_DB, CONFIRMATION = range(5)

# Данные пользователей
user_data: Dict[int, dict] = {}

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
    reply_keyboard = [["Начать перенос", "Отмена"]]
    await update.message.reply_text(
        "👋 Привет! Я помогу перенести данные между базами Notion.\n"
        "Для начала мне понадобится несколько параметров.\n"
        "Вы можете отменить процесс в любой момент, отправив /cancel",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ORIGIN_TOKEN

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена операции"""
    user = update.message.from_user
    logger.info(f"Пользователь {user.id} отменил операцию")
    await update.message.reply_text(
        "👋 Операция отменена. Для начала нового переноса отправьте /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def get_origin_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение токена исходного аккаунта"""
    if update.message.text == "Отмена":
        return await cancel(update, context)
    
    await update.message.reply_text(
        "🔑 Пожалуйста, отправьте токен исходного аккаунта Notion (ORIGIN_NOTION_TOKEN)"
    )
    return DEST_TOKEN

async def get_dest_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение токена целевого аккаунта"""
    user_data[update.effective_user.id] = {"origin_token": update.message.text}
    
    await update.message.reply_text(
        "🔑 Теперь отправьте токен целевого аккаунта Notion (DEST_NOTION_TOKEN)"
    )
    return ORIGIN_DB

async def get_origin_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение ID исходной базы данных"""
    user_data[update.effective_user.id]["dest_token"] = update.message.text
    
    await update.message.reply_text(
        "📁 Отправьте ID исходной базы данных (ORIGIN_DATABASE_ID)"
    )
    return DEST_DB

async def get_dest_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение ID целевой базы данных"""
    user_data[update.effective_user.id]["origin_db"] = update.message.text
    
    await update.message.reply_text(
        "📁 Отправьте ID целевой базы данных (DEST_DATABASE_ID)"
    )
    return CONFIRMATION

async def confirm_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждение и начало переноса"""
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
    
    port = int(os.environ.get("PORT", "8080"))
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
    
    # Добавление обработчика диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ORIGIN_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_origin_token)],
            DEST_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dest_token)],
            ORIGIN_DB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_origin_db)],
            DEST_DB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dest_db)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_transfer)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    
    # Запуск веб-сервера и настройка вебхука
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        asyncio.get_event_loop().run_until_complete(setup_webhook(app, webhook_url))
        asyncio.get_event_loop().run_until_complete(run_web_server())
        asyncio.get_event_loop().run_forever()
    else:
        # Fallback на polling режим для локальной разработки
        app.run_polling()

if __name__ == "__main__":
    main() 