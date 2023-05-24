import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

from core.configs import settings
from core.log_config import logger

host = settings.mongo_host
port = settings.mongo_port

client: AsyncIOMotorClient | None = None


def create_mongo_client():
    return motor.motor_asyncio.AsyncIOMotorClient(host=host, port=port, maxPoolSize=10)


async def check_mongo():
    try:
        await client.admin.command('ismaster')
        logger.info('Соединение с MongoDB успешно установлено!')
    except ConnectionFailure:
        logger.debug('Не удалось установить соединение с MongoDB.')


def get_mongo_client():
    return client
