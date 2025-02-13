import requests
from dotenv import load_dotenv
import os
from logger import setup_logger
logger = setup_logger()

def split_message(text, max_length=4096):
    """
    Разбивает текст на части, каждая из которых не превышает max_length символов.
    
    :param text: Исходный текст.
    :param max_length: Максимальная длина одной части (по умолчанию 4096).
    :return: Список частей текста.
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

def clean_unicode_escapes(text):
    """
    Очищает текст от Unicode escape-последовательностей.
    
    :param text: Исходный текст с escape-последовательностями.
    :return: Очищенный текст.
    """
    try:
        # Декодируем escape-последовательности Unicode
        cleaned_text = bytes(text, 'utf-8').decode('unicode_escape')
        
        # Если текст все еще содержит "кракозябры", пробуем перекодировать его
        if not cleaned_text.isprintable():
            cleaned_text = cleaned_text.encode('latin1').decode('utf-8', errors='replace')
        
        # Удаляем лишние пробелы и ненужные символы
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    except Exception as e:
        print(f"Ошибка при очистке текста: {e}")
        return text  # Возвращаем исходный текст, если возникла ошибка

def load_tokens():
    """
    Загружает API-ключи из файла .env.
    
    :return: Словарь с API-ключами.
    """
    # Загружаем переменные окружения из файла .env
    load_dotenv()

    required_keys = {"TELEGRAM_BOT_TOKEN", "QWEN_TEXT_API_KEY"}
    tokens = {}

    for key in required_keys:
        value = os.getenv(key)
        if not value:
            logger.error(f"Отсутствует токен: {key}")
            raise ValueError(f"Отсутствует токен: {key}")
        tokens[key] = value
        logger.info(f"Загружен токен: {key}={value[:5]}...")  # Логируем первые символы токена

    return tokens