"""Модуль, описывающий класс с методами для поиска в БД контента онлайн-кинотеатра."""
from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch, NotFoundError
from typing import List
from pprint import pprint


class DBSeeker(ABC):
    """Базовый для поиска объектов онлайн-кинотеатра."""
    @abstractmethod
    async def get_film_author(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_actor_films(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_director_films_count(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_film_length(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_top_films(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_top_n_films_in_genre(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_actor_top_n_films(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_film_genre(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_top_actor(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_film_description(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_film_year(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_film_rating(self, *args, **kwargs):
        pass


class ElasticSeeker(DBSeeker):
    """Класс для поиска объектов онлайн-кинотеатра в базе ElasticSearch."""
    def __init__(self, es_client: AsyncElasticsearch):
        self.client = es_client
        self.movies_index = 'movies'
        self.person_index = 'persons'
        self.genre_index = 'genres'

    async def get_film_author(self, movie_title: str) -> str:
        """Функция возвращает создателей (режиссеров и сценаристов) фильма по названию."""
        max_director_count = 2
        max_writer_count = 5

        query = {'query': {'multi_match': {'query': movie_title, 'fields': ['title_*']}}, 'size': 1}
        query_result: List[dict] | None = await self.get_by_query(index=self.movies_index, query=query)
        response = 'Авторы фильма мне неизвестны.'

        if query_result:
            film_directors: List[dict] | None = query_result[-1].get('directors')
            film_writers: List[dict] | None = query_result[-1].get('writers')

            if film_directors:
                response = 'Режиссеры фильма: '
                response += ', '.join(
                    [
                        director.get('full_name_ru') or director.get('full_name_en')
                        for director in film_directors[:max_director_count]
                    ]
                )

            if film_writers:
                response += '. Сценаристы фильма: '
                response += ', '.join(
                    [
                        writer.get('full_name_ru') or writer.get('full_name_en')
                        for writer in film_writers[:max_writer_count]
                    ]
                )

            pprint(response)
        return response

    async def get_person_info(self, actor: str) -> tuple:
        """Функция ищет в ES совпадения по переданному имени человека и возвращает кортеж (id, name)."""
        query = {
            "query": {
                "multi_match": {
                    "query": actor,
                    "fields": ["full_name_*"],
                    "fuzziness": "AUTO",
                    "prefix_length": 1
                }
            },
            "size": 1
        }
        pprint(actor)
        query_result: List[dict] | None = await self.get_by_query(index=self.person_index, query=query)
        pprint(query_result)

        person_id = query_result[-1].get('id')
        person_name = query_result[-1].get("full_name_ru") or query_result[-1].get("full_name_en")

        if query_result:
            return person_id, person_name

    async def get_actor_films(self, actor: str) -> str:
        """Функция возвращает фильмы с указанным актером."""
        max_film_count = 5
        actor_id, actor_name = await self.get_person_info(actor)

        if not actor_id:
            return f"Не удалось найти актера {actor}"

        query = {
            "query": {
                "nested": {
                    "path": "actors",
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "term": {
                                        "actors.id": actor_id
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "size": 5,
            "sort": [
                {
                    "rating_imdb": {
                        "order": "desc"
                    }
                }
            ]
        }

        query_result: List[dict] | None = await self.get_by_query(index=self.movies_index, query=query)

        if query_result:
            response = f"Топ фильмы с актером {actor_name}: "
            response += ', '.join([
                film.get('title_ru') for film in query_result[:max_film_count]
            ])
            return response

        return f"Мне не удалось найти фильмов с участием {actor_name}"

    async def get_director_films_count(self, director: str) -> str:
        """Функция возвращает количество фильмов с указанным человеком (сценаристом, режиссером, актером)"""

        director_id, director_name = await self.get_person_info(director)
        if not director_id:
            return f"Не удалось найти режиссера {director}"

        query = {
            "query": {
                "nested": {
                    "path": "actors",
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "term": {
                                        "directors.id": director_id
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "size": 1000
        }

        query_result: List[dict] | None = await self.get_by_query(index=self.movies_index, query=query)
        if query_result:
            return f"Фильмография {director} насчитывает около {len(query_result)} картин"

        return f"Мне не удалось найти фильмов, созданных {director}"

    async def get_film_length(self, movie_title: str) -> str:
        """Функция возвращает продолжительность фильма в минутах."""
        pass

    async def get_top_films(self, *args, **kwargs) -> str:
        """Функция возвращает топ-N фильмом по рейтингу."""
        pass

    async def get_top_n_films_in_genre(self, *args, **kwargs) -> str:
        """Функция возвращает топ-N фильмов в переданном жанре."""
        pass

    async def get_actor_top_n_films(self, *args, **kwargs) -> str:
        """Функция возвращает топ-N фильмов с переданным актером (сценаристом, режиссером)."""
        pass

    async def get_film_genre(self, *args, **kwargs) -> str:
        """Функция возвращает жанры, в котором снят фильм."""
        pass

    async def get_top_actor(self, *args, **kwargs) -> str:
        """Функция возвращает актера с самым большим числом фильмов."""
        pass

    async def get_film_description(self, *args, **kwargs) -> str:
        """Функция возвращает описание фильма."""
        pass

    async def get_film_year(self, *args, **kwargs) -> str:
        """Функция возвращает год создания фильма или сериала."""
        pass

    async def get_film_rating(self, *args, **kwargs) -> str:
        """Функция возвращает рейтинг фильма или сериала."""
        pass

    async def get_by_query(self, index: str, query: dict) -> List[dict] | None:
        """Функция для выполнения переданного в нее запроса ElasticSearch."""
        try:
            data = await self.client.search(index=index, body=query)
            return [item['_source'] for item in data['hits']['hits']]

        except NotFoundError:
            return None

    # TODO:
    #  - список фильмов, написанных таким-то сценаристом;
