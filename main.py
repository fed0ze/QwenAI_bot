import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot import TelegramBot
from database_logic import DatabaseManager
from utils import load_tokens
from logger import setup_logger

# Инициализируем логгер
logger = setup_logger()

async def start_bot():
    """
    Запускает бота.
    """
    try:
        logger.info("Начало инициализации бота...")
        
        # Загрузка токенов
        tokens = load_tokens()
        
        # Инициализация базы данных
        db_manager = DatabaseManager()
        await db_manager.init_db()
        logger.info("База данных успешно инициализирована.")
        
        # Запуск бота
        bot = TelegramBot(tokens)  # Токены загружаются внутри класса
        await bot.run()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

async def main():
    logger.info("Начало работы программы...")
    
    # Создаем планировщик
    scheduler = AsyncIOScheduler()
    
    # Добавляем задачу для перезапуска бота каждые 2 часа
    scheduler.add_job(start_bot, 'interval', hours=2)
    
    # Запускаем планировщик
    scheduler.start()
    
    # Первый запуск бота
    await start_bot()
    
    # Бесконечный цикл для поддержания работы планировщика
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка планировщика...")
        scheduler.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")