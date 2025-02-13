import aiohttp
import asyncio
import logging
import base64
import os
from logger import setup_logger
from utils import clean_unicode_escapes

logger = setup_logger()

class NeuralAPI:
    def __init__(self, tokens):
        self.text_api_key = tokens.get("QWEN_TEXT_API_KEY")
        self.vl_api_key = tokens.get("QWEN_VL_API_KEY")
        self.text_url = "https://chat.qwenlm.ai/api/chat/completions"
        self.image_url = "https://openrouter.ai/api/v1/chat/completions"

    async def send_request(self, messages, model="qwen-max-latest", stream=False):
        """
        Асинхронно отправляет POST-запрос к API и возвращает ответ.
        
        :param messages: История сообщений для отправки.
        :param model: Модель для генерации ответа.
        :param stream: Флаг для потоковой передачи.
        :return: JSON-ответ от API или None в случае ошибки.
        """
        headers = {
            "Authorization": f"Bearer {self.text_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36"
        }
        payload = {
            "chat_type": "t2t",
            "messages": messages,
            "model": model,
            "stream": stream
        }
        logger.info(f"Отправка запроса к API: {payload}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.text_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Получен ответ от API: {result}")
                        return result
                    else:
                        error_message = await response.text()
                        logger.error(f"Ошибка при отправке запроса: {response.status}, текст ошибки: {error_message}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            return None

    def process_response(self, response):
        """
        Обрабатывает ответ от API и возвращает текст ответа.
        
        :param response: JSON-ответ от API.
        :return: Текст ответа или None в случае ошибки.
        """
        if response and "choices" in response and len(response["choices"]) > 0:
            assistant_response = response["choices"][0]["message"]["content"]
            # Очищаем текст от Unicode escape-последовательностей
            cleaned_text = clean_unicode_escapes(assistant_response)
            logger.info(f"Обработан ответ от нейросети: {assistant_response}")
            return cleaned_text
        else:
            logger.error("Некорректный ответ от API.")
            return None