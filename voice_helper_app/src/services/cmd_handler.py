from datetime import datetime, timedelta
from functools import lru_cache

from fuzzywuzzy import fuzz
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.configs import settings
from db.clients.mongo import get_mongo_client

from fastapi import Depends
from services.models.models import UserQueryObject


class CommandHandler:
    def __init__(self, commands_db: AsyncIOMotorDatabase):
        self.db = commands_db
        self.last_update_cmd_tbr: datetime | None = None
        self.commands: dict | None = None
        self.to_be_removed: list | None = None
        # self.movies_db = ElasticSeeker(es_client)

    async def handle_user_query(self, user_txt: str) -> UserQueryObject:
        """Входная функция. Создается рабочий объект(словарь). С основной информацией для парсинга данных"""
        user_query_object = UserQueryObject()
        await self.update_cmd_tbr()
        user_query_object.after_cleaning_user_txt = self.cleaning_user_txt(user_txt)
        self.recognize_cmd(user_query_object)
        self.recognize_key_word(user_query_object)
        # TODO: везде в проекте заменить print на DEBUG логирование
        print(user_query_object)
        return user_query_object
        # user_query_object = await self.execute_cmd(user_query_object)
        # return user_query_object.answer

    async def update_cmd_tbr(self):
        # TODO: выяснить нужна ли эта функция и можно ли как-то
        #       оптимизировать этот функционал?
        """Вызов получения данных(cmd, tbr) через дельту времени"""
        delta_update = timedelta(hours=settings.delta_update_cmd_tbr)
        if self.last_update_cmd_tbr is None or self.last_update_cmd_tbr + delta_update < datetime.utcnow():
            await self.get_actual_commands()
            await self.get_actual_tbr()
            self.last_update_cmd_tbr = datetime.utcnow()

    async def get_actual_commands(self):
        """Получение словаря со списком команд и фраз тригеров cmd:trigger"""
        collection = self.db[settings.mongo_collection_cmd]
        commands = await collection.find_one()
        commands.pop('_id')
        self.commands = commands

    async def get_actual_tbr(self):
        # TODO: что такое tbr? совсем непонятно. надо изменить название
        """Получение списка слов для первичной чистки запроса пользователя"""
        collection = self.db[settings.mongo_collection_tbr]
        tbr = await collection.find_one()
        tbr.pop('_id')
        self.to_be_removed = tbr['text']

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


@lru_cache(maxsize=None)
def get_command_handler(mongo_client=Depends(get_mongo_client)) -> CommandHandler:
    mongo_db: AsyncIOMotorDatabase = mongo_client[settings.mongo_db]
    return CommandHandler(mongo_db)
