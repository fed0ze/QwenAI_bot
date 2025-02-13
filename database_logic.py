import sqlite3
import json
import aiosqlite
import logging

from logger import setup_logger

from utils import clean_unicode_escapes

logger = setup_logger()

class DatabaseManager:
    def __init__(self, db_name='dialogs.db'):
        self.db_name = db_name

    async def init_db(self):
        """
        Асинхронно инициализирует базу данных и создает таблицу для хранения диалогов.
        """
        logger.info("Инициализация базы данных...")
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("PRAGMA encoding = 'UTF-8';")
            await db.execute('''
                CREATE TABLE IF NOT EXISTS dialogs (
                    user_id INTEGER PRIMARY KEY,
                    messages TEXT
                )
            ''')
            await db.commit()
        logger.info("База данных успешно инициализирована.")

    async def get_user_messages(self, user_id):
        """
        Асинхронно получает историю диалога пользователя из базы данных.
        
        :param user_id: ID пользователя Telegram.
        :return: Список сообщений или пустой список, если история отсутствует.
        """
        logger.info(f"Получение истории диалога для user_id: {user_id}")
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT messages FROM dialogs WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()

        if result:
            messages = json.loads(result[0])
            logger.info(f"История диалога для user_id {user_id} загружена: {messages}")
            return messages
        else:
            logger.warning(f"История диалога для user_id {user_id} не найдена.")
            return []

    async def save_user_messages(self, user_id, messages):
        """
        Асинхронно сохраняет историю диалога пользователя в базу данных.
        
        :param user_id: ID пользователя Telegram.
        :param messages: Список сообщений для сохранения.
        """
        cleaned_messages = [
            {"role": msg["role"], "content": clean_unicode_escapes(msg["content"]), "extra": msg["extra"], "chat_type": msg["chat_type"]}
            for msg in messages
        ]

        logger.info(f"Сохранение истории диалога для user_id: {user_id}")
        messages_json = json.dumps(cleaned_messages, ensure_ascii=False)

        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT OR REPLACE INTO dialogs (user_id, messages)
                VALUES (?, ?)
            ''', (user_id, messages_json))
            await db.commit()
        logger.info(f"История диалога для user_id {user_id} успешно сохранена.")