from datetime import datetime, timedelta
from functools import lru_cache

from fuzzywuzzy import fuzz
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.configs import settings
from db.clients.mongo import get_mongo_client
from db.clients.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from services.movies_storage_handler import ElasticSeeker
from fastapi import Depends


# TODO: провести рефакторинг класса CommandHandler
# TODO: добавить тайп-хинтинги и докстринги


class CommandHandler:
    def __init__(self, commands_db: AsyncIOMotorDatabase, es_client: AsyncElasticsearch):
        self.db = commands_db
        self.last_update_cmd_tbr: datetime | None = None
        self.commands: dict | None = None
        self.to_be_removed: list | None = None
        self.movies_db = ElasticSeeker(es_client)

    async def handle_user_query(self, user_txt):
        parse_object = {
            'before_cleaning_user_txt': user_txt,
            'after_cleaning_user_txt': '',
            'discovered_cmd': '',
            'final_cmd': '',
            'original_txt': '',
            'key_word': '',
            'answer': '',
            'percent': 0,
        }
        print(user_txt)
        await self.update_cmd_tbr()
        parse_object['after_cleaning_user_txt'] = self.cleaning_user_txt(user_txt)
        parse_object = self.recognize_cmd(parse_object)
        parse_object = self.recognize_key_word(parse_object)
        parse_object = await self.execute_cmd(parse_object)
        print(parse_object['answer'])
        return parse_object['answer']

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
        return ' '.join([word.lower() for word in user_txt.split() if word not in self.to_be_removed]).strip()

    def recognize_cmd(self, parse_object: dict) -> dict:
        for command_name, texts_comparisons in self.commands.items():
            for original_text in texts_comparisons:
                percent = fuzz.ratio(parse_object['after_cleaning_user_txt'], original_text)
                if percent > parse_object['percent']:
                    parse_object['discovered_cmd'] = command_name
                    parse_object['final_cmd'] = command_name
                    parse_object['original_txt'] = original_text
                    parse_object['percent'] = percent
        if parse_object['percent'] <= 49:
            parse_object['final_cmd'] = 'unknown'
        if 50 <= parse_object['percent'] < 60:
            parse_object['final_cmd'] = 'ask_again'
        return parse_object

    async def execute_cmd(self, parse_object: dict):
        command_matrix = {
            'author': self.movies_db.get_film_author,
            'actor': self.movies_db.get_actor_films,
            'how_many_films': self.movies_db.get_director_films_count,
            'time_film': self.movies_db.get_film_length,
            'top_films': self.movies_db.get_top_films,
            'top_films_genre': self.movies_db.get_top_n_films_in_genre,
            'top_films_person': self.movies_db.get_actor_top_n_films,
            'film_genre': self.movies_db.get_film_genre,
            'top_actor': self.movies_db.get_top_actor,
            'film_about': self.movies_db.get_film_description,
        }

        command = parse_object.get('final_cmd')
        keyword = parse_object.get('key_word')
        answer = 'К сожалению, команда не распознана... пожалуйста, повторите запрос'

        if command in command_matrix:
            method = command_matrix.get(command)
            answer = await method(keyword)

        parse_object['answer'] = answer
        return parse_object

    @staticmethod
    def recognize_key_word(parse_object: dict) -> dict:
        parse_object['key_word'] = ' '.join(
            [
                user_word
                for user_word in parse_object['after_cleaning_user_txt'].split()
                if user_word not in parse_object['original_txt']
            ]
        ).strip()
        return parse_object


@lru_cache(maxsize=None)
def get_command_handler(
    mongo_client=Depends(get_mongo_client), elastic_client: AsyncElasticsearch = Depends(get_elastic)
):
    mongo_db = mongo_client[settings.mongo_db]
    return CommandHandler(mongo_db, elastic_client)
