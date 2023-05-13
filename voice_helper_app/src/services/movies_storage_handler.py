from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch, NotFoundError
from typing import List
from pprint import pprint


class DBSeeker(ABC):
    @abstractmethod
    async def get_film_author(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_actor_films(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_actor_films_count(self, *args, **kwargs):
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

    async def get_actor_films(self, actor: str):
        """Функция возвращает фильмы с указанным актером"""
        pass

    # TODO: добавить докстринги и тайпхинтинги в методы

    async def get_actor_films_count(self, actor: str):
        pass

    async def get_film_length(self, movie_title: str):
        pass

    async def get_top_films(self, *args, **kwargs):
        pass

    async def get_top_n_films_in_genre(self, *args, **kwargs):
        pass

    async def get_actor_top_n_films(self, *args, **kwargs):
        pass

    async def get_film_genre(self, *args, **kwargs):
        pass

    async def get_top_actor(self, *args, **kwargs):
        pass

    async def get_film_description(self, *args, **kwargs):
        pass

    async def get_film_year(self, *args, **kwargs):
        pass

    async def get_film_rating(self, *args, **kwargs):
        pass

    async def get_by_query(self, index: str, query: dict) -> List[dict] | None:
        try:
            data = await self.client.search(index=index, body=query)
            return [item['_source'] for item in data['hits']['hits']]

        except NotFoundError:
            return None

    # TODO:
    #  - список фильмов, созданных таким-то сценаристом;
    #  - год создания фильма/сериала
    #  - какой рейтинг у фильма
