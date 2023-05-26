from dataclasses import dataclass
from typing import Callable

from pydantic import BaseSettings, Field

from core.indices import genre_index, movies_index, person_index
from core.queries import new_film_query, query_genres, query_persons
from models.models import Film, Genre, Person


class Dsl(BaseSettings):
    dbname: str = Field(default='movies_database', env='DB_NAME')
    user: str = Field(default='app', env='DB_USER')
    password: str = Field(default='123qwe', env='DB_PASSWORD')
    host: str = Field(default='localhost', env='DB_HOST')
    port: int = Field(default=5432, env='DB_PORT')
    options: str = '-c search_path=content'


class Config(BaseSettings):
    elastic_host: str = Field(default='http://localhost')
    elastic_port: int = Field(default=9200)
    redis_host: str = Field(default='localhost')
    redis_port: int = Field(default=6379)
    sleep_time_seconds: int = Field(default=60)
    db_film_limit: int = 50000
    db_genre_limit: int = 100
    db_person_limit: int = 200000


dsl = Dsl()
config = Config()


@dataclass
class ETLConfig:
    """Класс описывающий параметры ETL для отдельной сущности."""

    query: str
    index_schema: dict
    state_key: str
    elastic_index_name: str
    related_model: Callable
    batch_size: int = 10000
    limit_size: int = 50000


ETL_CONFIGS = [
    ETLConfig(new_film_query, movies_index, 'film_last_modified_date', 'movies', Film, limit_size=config.db_film_limit),
    ETLConfig(query_genres, genre_index, 'genre_last_modified_date', 'genres', Genre, limit_size=config.db_genre_limit),
    ETLConfig(query_persons, person_index, 'person_last_modified_date', 'persons', Person, limit_size=config.db_person_limit),
]
