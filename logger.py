import logging
import sys

def setup_logger():
    """
    Настраивает логирование для проекта.
    """
    logger = logging.getLogger()
    if not logger.handlers:  # Проверяем, что логгер еще не настроен
        logger.setLevel(logging.DEBUG)  # Устанавливаем глобальный уровень логирования
        
        # Создаем обработчик для вывода в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Создаем обработчик для записи в файл
        file_handler = logging.FileHandler("bot.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        
        # Формат логов
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Добавляем обработчики к логгеру
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger