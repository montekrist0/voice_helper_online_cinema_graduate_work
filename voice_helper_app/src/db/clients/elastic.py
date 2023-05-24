from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError as ConnectionErrorES

from core.configs import settings
from core.log_config import logger

es: AsyncElasticsearch | None = None


def create_es_client():
    return AsyncElasticsearch(hosts=[f'{settings.elastic_host}:{settings.elastic_port}'])


def get_elastic() -> AsyncElasticsearch:
    return es


async def check_es():
    try:
        if await es.ping():
            logger.info('Соединение с Elasticsearch успешно установлено!')
        else:
            logger.warning('Не удалось установить соединение с Elasticsearch.')
    except ConnectionErrorES:
        logger.debug('Не удалось установить соединение с Elasticsearch.')
