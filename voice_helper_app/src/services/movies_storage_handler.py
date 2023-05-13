from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch, NotFoundError
from typing import List


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


class ElasticSeeker(DBSeeker):
    def __init__(self, es_client: AsyncElasticsearch):
        self.client = es_client
        self.movies_index = 'movies'
        self.person_index = 'persons'
        self.genre_index = 'genres'

    async def get_film_author(self, movie_title: str) -> str:
        query = {
            "query": {
                "multi_match": {
                  "query": movie_title,
                  "fields": ["title_*"]
                }
              },
            "size": 1
        }
        query_result = self.get_by_query(index=self.movies_index, query=query)
        if query_result:
            print(query_result)

        return "Some author"

    async def get_actor_films(self, *args, **kwargs):
        pass

    async def get_actor_films_count(self, *args, **kwargs):
        pass

    async def get_film_length(self, *args, **kwargs):
        pass

    async def get_top_n_films_in_genre(self, *args, **kwargs):
        pass

    async def get_actor_top_n_films(self, *args, **kwargs):
        pass

    async def get_film_genre(self, *args, **kwargs):
        pass

    async def get_top_actor(self, *args, **kwargs):
        pass

    async def get_by_query(self, index: str, query: dict) -> List[dict] | None:
        try:
            data = await self.client.search(index=index, body=query)
            return [item['_source'] for item in data['hits']['hits']]

        except NotFoundError:
            return None

