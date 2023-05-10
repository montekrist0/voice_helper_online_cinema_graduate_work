from datetime import (datetime,
                      timedelta)
from functools import lru_cache

from fuzzywuzzy import fuzz
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.configs import settings
from db.clients.mongo import get_mongo_client


class CommandHandler:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.last_update_cmd_tbr: datetime | None = None
        self.commands: dict | None = None
        self.to_be_removed: list | None = None

    async def handle(self, user_txt):
        parse_object = {'before_cleaning_user_txt': user_txt,
                        'after_cleaning_user_txt': '',
                        'discovered_cmd': '',
                        'final_cmd': '',
                        'original_txt': '',
                        'key_word': '',
                        'percent': 0}
        await self.update_cmd_tbr()
        parse_object['after_cleaning_user_txt'] = self.cleaning_user_txt(user_txt)
        parse_object = self.recognize_cmd(parse_object)
        parse_object = self.recognize_key_word(parse_object)
        print(parse_object)
        result = self.execute_cmd(parse_object)
        return result

    async def update_cmd_tbr(self):
        delta_update = timedelta(hours=settings.delta_update_cmd_tbr)
        if self.last_update_cmd_tbr is None or self.last_update_cmd_tbr + delta_update < datetime.utcnow():
            await self.get_actual_commands()
            await self.get_actual_tbr()
            self.last_update_cmd_tbr = datetime.utcnow()

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

    def cleaning_user_txt(self, user_txt: str) -> str:
        for word in user_txt.split():
            user_txt = user_txt.replace(word, word.lower()).strip()
        for word in self.to_be_removed:
            user_txt = user_txt.replace(word, "").strip()
        return user_txt

    def recognize_cmd(self, parse_object: dict) -> dict:
        for command_name, texts_comparisons in self.commands.items():
            for original_text in texts_comparisons:
                percent = fuzz.ratio(parse_object['after_cleaning_user_txt'], original_text)
                if percent > parse_object['percent']:
                    parse_object['discovered_cmd'] = command_name
                    parse_object['final_cmd'] = command_name
                    parse_object['original_txt'] = original_text
                    parse_object['percent'] = percent
        if 40 <= parse_object['percent'] < 50:
            parse_object['final_cmd'] = 'unknown'
        if 50 <= parse_object['percent'] < 60:
            parse_object['final_cmd'] = 'ask_again'
        return parse_object

    def execute_cmd(self, parse_object: dict) -> str:
        cmd = parse_object['final_cmd']
        match cmd:
            case 'author':
                film = parse_object['key_word']
                return f'Тут мы узнаем какой автор создал {film}'
            case 'actor':
                actor = parse_object['key_word']
                return f'Тут мы узнаем в каком фильме играл актер {actor}'
            case 'how_many_films':
                author = parse_object['key_word']
                return f'Тут мы узнаем сколько фильмов у {author}'
            case 'time_film':
                film = parse_object['key_word']
                return f'Тут му узнаем сколько длится фильм {film}'
            case 'top_films':
                return f'Тут будет перечисление 10 топ фильмов'
            case 'top_films_genre':
                genre = parse_object['key_word']
                return f'Тут будет перечисление 10 топ фильмов в жанре {genre}'
            case 'top_films_person':
                actor = parse_object['key_word']
                return f'Тут будет перечисление 10 топ фильмов с актером {actor}'
            case 'film_genre':
                film = parse_object['key_word']
                return f'Тут будет в каком жанре снят фильм {film}'
            case 'top_actor':
                return f'Тут будет ответ какой актер самый популярный'
            case 'unknown':
                return 'Мне неизвестная команда'
            case 'ask_again':
                return 'Тут будет задан уточняющий вопрос.'

    @staticmethod
    def recognize_key_word(parse_object: dict) -> dict:
        for user_word in parse_object['after_cleaning_user_txt'].split():
            if user_word not in parse_object['original_txt']:
                parse_object['key_word'] += user_word if len(
                    parse_object['key_word']) < 0 else f' {user_word}'
        parse_object['key_word'] = parse_object['key_word'].strip()
        return parse_object


@lru_cache(maxsize=None)
def get_command_handler():
    client = get_mongo_client()
    db = client[settings.mongo_db]
    return CommandHandler(db)
