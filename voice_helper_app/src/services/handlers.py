from functools import lru_cache

from fuzzywuzzy import fuzz
from motor.motor_asyncio import AsyncIOMotorCollection
import orjson

from core.configs import settings
from db.clients.mongo import get_mongo_client


class CommandHandler:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        self.commands: dict | None = None

    async def handle(self, user_txt):
        await self.get_actual_commands()
        await self.recognize_cmd(user_txt)

    async def get_actual_commands(self):
        commands = await self.collection.find_one()
        commands.pop('_id')
        self.commands = commands

    async def recognize_cmd(self, user_txt):
        result = {'user_txt': user_txt,
                  'discovered_cmd': '',
                  'percent': 0}
        for command_name, texts_comparisons in self.commands.items():
            for original_text in texts_comparisons:
                percent = fuzz.ratio(user_txt, original_text)
                if percent > result['percent']:
                    result['discovered_cmd'] = command_name
                    result['percent'] = percent
        print(result)
            # for x in v:
            #     vrt = fuzz.ratio(cmd, x)
            #     if vrt > RC['percent']:
            #         RC['cmd'] = c
            #         RC['percent'] = vrt


@lru_cache(maxsize=None)
def get_command_handler():
    client = get_mongo_client()
    db = client[settings.mongo_db]
    collection = db[settings.mongo_collection_commands]
    return CommandHandler(collection)
