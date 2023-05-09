from functools import lru_cache

from fuzzywuzzy import fuzz
from motor.motor_asyncio import AsyncIOMotorDatabase
import orjson

from core.configs import settings
from db.clients.mongo import get_mongo_client


class CommandHandler:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.commands: dict | None = None
        self.to_be_removed: list | None = None

    async def handle(self, user_txt):
        await self.get_actual_commands()
        await self.get_actual_tbr()
        user_txt = await self.cleaning_user_txt(user_txt)
        parse_object = await self.recognize_cmd(user_txt)
        print(parse_object)

    async def get_actual_commands(self):
        collection = self.db[settings.mongo_collection_cmd]
        commands = await collection.find_one()
        commands.pop('_id')
        self.commands = commands

    async def get_actual_tbr(self):
        collection = self.db[settings.mongo_collection_tbr]
        tbr = await collection.find_one()
        tbr.pop('_id')
        self.to_be_removed = tbr['text']

    async def cleaning_user_txt(self, user_txt):
        for word in user_txt:
            user_txt = user_txt.replace(word, word.lower()).strip()
        for word in self.to_be_removed:
            user_txt = user_txt.replace(word, "").strip()
        return user_txt

    async def recognize_cmd(self, user_txt):
        parse_object = {'user_txt': user_txt,
                        'discovered_cmd': '',
                        'original_txt': '',
                        'key_word': '',
                        'percent': 0}
        for command_name, texts_comparisons in self.commands.items():
            for original_text in texts_comparisons:
                percent = fuzz.ratio(user_txt, original_text)
                if percent > parse_object['percent']:
                    parse_object['discovered_cmd'] = command_name
                    parse_object['original_txt'] = original_text
                    parse_object['percent'] = percent
        parse_object = await self.recognize_key_word(parse_object)
        return parse_object

    @staticmethod
    async def recognize_key_word(parse_object: dict):
        parse_object['key_word'] = parse_object['user_txt'].replace(parse_object['original_txt'], "").strip()
        return parse_object


@lru_cache(maxsize=None)
def get_command_handler():
    client = get_mongo_client()
    db = client[settings.mongo_db]
    # collection_cmd = db[settings.mongo_collection_cmd]
    # collection_tbr = db[settings.mongo_collection_tbr]
    return CommandHandler(db)
