from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ContentType
from aiogram.filters import Command
from ai_logic import NeuralAPI
from database_logic import DatabaseManager
import logging
import os
from utils import split_message, clean_unicode_escapes, load_tokens
from logger import setup_logger
logger = setup_logger()

class TelegramBot:
    def __init__(self, tokens):
        self.bot = Bot(token=tokens.get("TELEGRAM_BOT_TOKEN"))
        self.dp = Dispatcher()
        self.neural_api = NeuralAPI(tokens)  # Передаем токены в NeuralAPI
        self.db_manager = DatabaseManager()
        self.user_locks = {}
        self.register_handlers()

    def register_handlers(self):
        @self.dp.message(Command("start"))
        async def start(message: Message):
            await message.answer("Привет! Я ваш персональный помощник. Как могу помочь?")

        @self.dp.message(Command("clear"))
        async def clear_history(message: Message):
            user_id = message.from_user.id
            await self.db_manager.save_user_messages(user_id, [])
            await message.answer("История диалога очищена.")

        @self.dp.message(Command("donate"))
        async def donate(message: Message):
            user_id = message.from_user.id
            await message.answer("Вы хотите сделать добровольное пожертвование?\n\nВы можете отправить USDT по адресу: UQD0RAA75gioFEADjmGkH8h0LUXMCQXbFog0V2PwhPrnVjdx\n\nИли написать в личные сообщения админу: @abobafed и задонатить как-нибудь еще :)\n\nТак мы будем знать, что не зря платим за хостинг :)")
        @self.dp.message(F.photo)
        async def handle_photo(message: Message):
            user_id = message.from_user.id
            if self.user_locks.get(user_id, False):
                await message.answer("Пожалуйста, дождитесь ответа на предыдущий запрос.")
                return
            self.user_locks[user_id] = True
            logger.info(f"Получено изображение от пользователя {user_id}")
            await message.answer("Пока что, я не умею анализировать изображения :с\n\nВы можете ускорить прогресс моего развития, совершив добровольное пожертвование - /donate")
            self.user_locks[user_id] = False

        @self.dp.message(F.text)
        async def handle_message(message: Message):
            user_id = message.from_user.id
            if self.user_locks.get(user_id, False):
                await message.answer("Пожалуйста, дождитесь ответа на предыдущий запрос.")
                return
            self.user_locks[user_id] = True
            try:
                logger.info(f"Получено сообщение от пользователя {user_id}: {message.text}")
                
                # Получаем историю диалога пользователя из базы данных
                messages = await self.db_manager.get_user_messages(user_id)
                
                # Добавляем сообщение пользователя в историю
                messages.append({"role": "user", "content": message.text, "extra": {}, "chat_type": "t2t"})
                
                # Отправляем запрос к API
                response = await self.neural_api.send_request(messages)
                if response:
                    assistant_response = self.neural_api.process_response(response)
                    if assistant_response:
                        # Разбиваем ответ на части, если он слишком длинный
                        parts = split_message(assistant_response)
                        for part in parts:
                            await message.answer(part)
                        
                        # Добавляем ответ нейросети в историю
                        messages.append({"role": "assistant", "content": assistant_response, "extra": {}, "chat_type": "t2t"})
                        await self.db_manager.save_user_messages(user_id, messages)
                    else:
                        await message.answer("Извините, произошла ошибка при обработке вашего запроса.")
                else:
                    await message.answer("Не удалось получить ответ от нейросети.")
            finally:
                self.user_locks[user_id] = False

    async def run(self):
        logger.info("Запуск бота...")
        await self.dp.start_polling(self.bot)