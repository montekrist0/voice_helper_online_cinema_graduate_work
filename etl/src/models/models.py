from datetime import date
from typing import List, Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Base(BaseModel):
    id: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonBase(Base):
    full_name_en: str = None
    full_name_ru: str = None


class Person(PersonBase):
    role: List[str] = []
    film_ids: List[str] = []


class Genre(Base):
    name: str


class Film(Base):
    title_en: str = None
    title_ru: str = None
    description: str = None
    rating_imdb: float = None
    type: str
    age_limit: int = None
    film_length: int = None
    year: int = None
    genres: List[Genre] = []
    actors: List[PersonBase] = []
    directors: List[PersonBase] = []
    writers: List[PersonBase] = []
