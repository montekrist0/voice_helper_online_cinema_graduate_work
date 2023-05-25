from datetime import datetime, timedelta

from fuzzywuzzy import fuzz
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from ..core.configs import settings
from ..core.log_config import logger
from ..services.models.models import UserQueryObject


class CommandHandler:
    """Класс для распознавания команды пользователя."""

    def __init__(self, commands_db: AsyncIOMotorDatabase):
        self.db = commands_db
        self.last_update_cmd_tbr: datetime | None = None
        self.commands: dict | None = None
        self.to_be_removed: list | None = None

    async def handle_user_query(self, user_txt: str) -> UserQueryObject | None:
        """Входная функция. Создается рабочий объект(словарь). С основной информацией для парсинга данных"""
        user_query_object = UserQueryObject()
        await self.update_cmd_tbr()
        if not await self.is_cmd_tbr():
            return None
        user_query_object.after_cleaning_user_txt = self.cleaning_user_txt(user_txt)
        self.recognize_cmd(user_query_object)
        self.recognize_key_word(user_query_object)
        logger.info(f'Объект запроса:\n{user_query_object}')
        return user_query_object

    async def update_cmd_tbr(self):
        """Вызов получения данных(cmd, tbr) через дельту времени"""
        delta_update = timedelta(hours=settings.delta_update_cmd_tbr)
        if self.last_update_cmd_tbr is None or self.last_update_cmd_tbr + delta_update < datetime.utcnow():
            await self.get_actual_commands()
            await self.get_actual_tbr()
            self.last_update_cmd_tbr = datetime.utcnow()

    async def get_actual_commands(self):
        """Получение словаря со списком команд и фраз тригеров cmd:trigger"""
        try:
            collection = self.db[settings.mongo_collection_cmd]
            commands = await collection.find_one()
            commands.pop('_id')
            self.commands = commands
        except PyMongoError:
            logger.debug('Не удалось получить актуальные команды')
            self.commands = None

    async def get_actual_tbr(self):
        """Получение списка слов для первичной чистки запроса пользователя"""
        try:
            collection = self.db[settings.mongo_collection_tbr]
            tbr = await collection.find_one()
            tbr.pop('_id')
            self.to_be_removed = tbr['text']
        except PyMongoError:
            logger.debug('Не удалось получить список слов для первичной очистки')
            self.to_be_removed = None

    async def is_cmd_tbr(self):
        if self.commands and self.to_be_removed:
            return True
        return False

    def cleaning_user_txt(self, user_txt: str) -> str:
        """Первичная очистка запроса пользователя от фонового шума"""
        return ' '.join([word for word in user_txt.lower().split() if word not in self.to_be_removed]).strip()

    def recognize_cmd(self, user_query_object: UserQueryObject) -> UserQueryObject:
        """Обнаружение команды используя расстояние Левенштейна"""
        for command_name, texts_comparisons in self.commands.items():
            for original_text in texts_comparisons:

                percent = fuzz.ratio(user_query_object.after_cleaning_user_txt, original_text)
                if percent > user_query_object.percent:
                    user_query_object.discovered_cmd = command_name
                    user_query_object.final_cmd = command_name
                    user_query_object.original_txt = original_text
                    user_query_object.percent = percent

        if user_query_object.percent <= 49:
            user_query_object.final_cmd = 'unknown'

        if 50 <= user_query_object.percent < 60:
            user_query_object.final_cmd = 'ask_again'

        return user_query_object

    @staticmethod
    def recognize_key_word(user_query_object: UserQueryObject) -> UserQueryObject:
        """Сбор ключевого слова соблюдая пробел"""
        user_query_object.key_word = ' '.join(
            [
                user_word
                for user_word in user_query_object.after_cleaning_user_txt.split()
                if user_word not in user_query_object.original_txt
            ]
        ).strip()
        return user_query_object
