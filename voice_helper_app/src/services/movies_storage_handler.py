"""Модуль, описывающий класс с методами для поиска в БД контента онлайн-кинотеатра."""
from abc import ABC, abstractmethod
from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.clients.elastic import get_elastic
from core.log_config import logger


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

    async def execute_user_command(self, command: str, keyword: str) -> str:
        """Выполнение команды, запрос в еластик"""
        command_matrix = {
            'author': self.get_film_author,
            'actor': self.get_actor_films,
            'how_many_films': self.get_director_films_count,
            'time_film': self.get_film_length,
            'top_films': self.get_top_films,
            'top_films_genre': self.get_top_n_films_in_genre,
            'film_genre': self.get_film_genre,
            'top_actor': self.get_top_actor,
            'film_about': self.get_film_description,
            'film_year': self.get_film_year,
            'film_rating': self.get_film_rating,
        }

        answer = 'К сожалению, команда не распознана... пожалуйста, повторите запрос'

        if command in command_matrix:
            method = command_matrix.get(command)
            answer = await method(keyword)

        return answer

    async def get_film_author(self, movie_title: str) -> str:
        """Функция возвращает создателей (режиссеров и сценаристов) фильма по названию."""
        max_director_count = 2
        max_writer_count = 5

        query = {'query': {'multi_match': {'query': movie_title, 'fields': ['title_*']}}, 'size': 1}
        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = 'Авторы фильма мне неизвестны.'

        if query_result:
            film_directors = query_result[-1].get('directors')
            film_writers = query_result[-1].get('writers')

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
        return response

    async def get_person_info(self, actor: str) -> tuple:
        """Функция ищет в ES совпадения по переданному имени человека и возвращает кортеж (id, name)."""
        query = {
            'query': {
                'multi_match': {'query': actor, 'fields': ['full_name_*'], 'fuzziness': 'AUTO', 'prefix_length': 1}
            },
            'size': 1,
        }

        query_result = await self.get_by_query(index=self.person_index, query=query)
        person_id = query_result[-1].get('id')
        person_name = query_result[-1].get('full_name_ru') or query_result[-1].get('full_name_en')

        if query_result:
            return person_id, person_name

    async def get_actor_films(self, actor: str) -> str:
        """Функция возвращает ТОП-фильмы с указанным актером."""
        max_film_count = 5
        actor_id, actor_name = await self.get_person_info(actor)

        if not actor_id:
            return f'Не удалось найти актера {actor}'

        query = {
            'query': {'nested': {'path': 'actors', 'query': {'bool': {'must': [{'term': {'actors.id': actor_id}}]}}}},
            'size': 5,
            'sort': [{'rating_imdb': {'order': 'desc'}}],
        }

        query_result = await self.get_by_query(index=self.movies_index, query=query)

        if query_result:
            response = f'Топ фильмы с актером {actor_name}: '
            response += ', '.join([film.get('title_ru') for film in query_result[:max_film_count]])
            return response

        return f'Мне не удалось найти фильмов с участием {actor_name}'

    async def get_director_films_count(self, director: str) -> str:
        """Функция возвращает количество фильмов с указанным режиссером"""
        max_size = 1000
        director_id, director_name = await self.get_person_info(director)

        if not director_id:
            return f'Не удалось найти режиссера {director}'

        query = {
            'query': {
                'nested': {'path': 'actors', 'query': {'bool': {'must': [{'term': {'directors.id': director_id}}]}}}
            },
            'size': max_size,
        }

        query_result = await self.get_by_query(index=self.movies_index, query=query)
        if query_result:
            return f'Фильмография {director} насчитывает около {len(query_result)} картин'

        return f'Мне не удалось найти фильмов, созданных {director}'

    async def get_film_length(self, movie_title: str) -> str:
        """Функция возвращает продолжительность фильма в минутах."""
        query = {
            'query': {'multi_match': {'query': movie_title, 'fields': ['title_*'], 'fuzziness': 'AUTO'}},
            'size': 1,
        }
        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = f'Длительность фильма {movie_title} мне неизвестна'

        if query_result:
            film_length: int = query_result[-1].get('film_length')
            film_name: str = query_result[-1].get('title_ru')
            movie_title: str = film_name if film_name else movie_title

            if film_length:
                response = f'Длительность фильма {movie_title} составляет {film_length} минут'

        return response

    async def get_top_films(self, *args, **kwargs) -> str:
        """Функция возвращает топ-N фильмом по рейтингу."""
        size = 10
        query = {'query': {'match_all': {}}, 'size': size, 'sort': [{'rating_imdb': {'order': 'desc'}}]}
        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = f'Топ {size} фильмов мне неизвестны'

        if query_result:
            films_names: str = ', '.join([film.get('title_ru') for film in query_result])
            if films_names:
                response = f'Топ фильмы: {films_names}'

        return response

    async def get_top_n_films_in_genre(self, genre_name: str) -> str:
        """Функция возвращает топ-N фильмов в переданном жанре."""
        size = 10
        query = {
            'query': {
                'nested': {'path': 'genres', 'query': {'bool': {'must': [{'match': {'genres.name': genre_name}}]}}}
            },
            'size': size,
            'sort': [{'rating_imdb': {'order': 'desc'}}],
        }

        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = f'Топ {size} фильмов в жанре {genre_name} мне неизвестны'

        if query_result:
            films_names: str = ', '.join([film.get('title_ru') for film in query_result])
            if films_names:
                response = f'Топ фильмы в жанре {genre_name}: {films_names}'

        return response

    async def get_film_genre(self, movie_title: str) -> str:
        """Функция возвращает жанры, в котором снят фильм."""
        query = {
            'query': {'multi_match': {'query': movie_title, 'fields': ['title_*'], 'fuzziness': 'AUTO'}},
            'size': 1,
        }
        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = 'Мне неизвестно в каком жанре снят фильм'

        if query_result:
            films_genres: list = query_result[-1].get('genres')
            film_name: str = query_result[-1].get('title_ru')
            response = f'Мне неизвестно в каком жанре снят фильм {film_name}'

            if films_genres:
                films_genres: str = ''.join([genre.get('name') for genre in films_genres])
                response = f'Фильм {film_name} снят в жанре: {films_genres}'

        return response

    async def get_top_actor(self, *args, **kwargs) -> str:
        """Функция возвращает актера с самым большим числом фильмов."""
        query = {
            'query': {'bool': {'must': [{'term': {'role': 'actor'}}]}},
            'size': 1,
            'sort': [{'film_ids': {'order': 'desc'}}],
        }
        query_result = await self.get_by_query(index=self.person_index, query=query)
        response = 'Мне неизвестно какой самый популярный актёр'

        if query_result:
            actor_name: str = query_result[-1].get('full_name_ru')
            if actor_name:
                response = f'Самый популярный актер {actor_name}'

        return response

    async def get_film_description(self, movie_title) -> str:
        """Функция возвращает описание фильма."""
        query = {
            'query': {'multi_match': {'query': movie_title, 'fields': ['title_*'], 'fuzziness': 'AUTO'}},
            'size': 1,
        }
        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = 'Мне неизвестно про что фильм'

        if query_result:
            description: str = query_result[-1].get('description')
            movie_title: str = query_result[-1].get('title_ru')
            response = f'Мне неизвестно про что фильм {movie_title}'
            if description:
                response = f'Описание фильма {movie_title}:...{description}'

        return response

    async def get_film_year(self, movie_title) -> str:
        """Функция возвращает год создания фильма или сериала."""
        query = {
            'query': {'multi_match': {'query': movie_title, 'fields': ['title_*'], 'fuzziness': 'AUTO'}},
            'size': 1,
        }
        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = 'Мне неизвестен год создания фильма'

        if query_result:
            year: str = query_result[-1].get('year')
            movie_title: str = query_result[-1].get('title_ru')
            response = f'Мне неизвестен год создания фильма {movie_title}'
            if year:
                response = f'Год создания фильма {movie_title}:...{year}'

        return response

    async def get_film_rating(self, movie_title) -> str:
        """Функция возвращает рейтинг фильма или сериала."""
        query = {
            'query': {'multi_match': {'query': movie_title, 'fields': ['title_*'], 'fuzziness': 'AUTO'}},
            'size': 1,
        }
        query_result = await self.get_by_query(index=self.movies_index, query=query)
        response = 'Мне неизвестен рейтинг'

        if query_result:
            rating: str = query_result[-1].get('rating_imdb')
            movie_title: str = query_result[-1].get('title_ru')
            response = f'Мне неизвестен рейтинг {movie_title}'
            if rating:
                response = f'Рейтинг {movie_title}:...{rating}'

        return response

    async def get_by_query(self, index: str, query: dict) -> list[dict] | None:
        """Функция для выполнения переданного в нее запроса ElasticSearch."""
        try:
            data = await self.client.search(index=index, body=query)
            return [item['_source'] for item in data['hits']['hits']]
        except NotFoundError:
            logger.debug('Не удалось получить данные из ES')
            return None

    # TODO:
    #  - список фильмов, написанных таким-то сценаристом;


@lru_cache(maxsize=None)
def get_response_maker(elastic_client: AsyncElasticsearch = Depends(get_elastic)) -> ElasticSeeker:
    return ElasticSeeker(elastic_client)
