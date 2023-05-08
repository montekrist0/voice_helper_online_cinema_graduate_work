from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorCollection
import orjson

from core.configs import settings
from db.clients.mongo import get_mongo_client


class CommandHandler:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        self.commands: dict | None = None

    async def handle(self):
        await self.get_actual_commands()

    async def get_actual_commands(self):
        commands = await self.collection.find_one()
        self.commands = orjson.loads(commands)

    async def recognize_cmd(self, user_cmd):
        result = {'user_cmd': user_cmd,
                  'discovered_cmd': '',
                  'percent': 0}
        for command, texts_comparisons in self.commands.items():
            for original_text in texts_comparisons:
                pass
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
