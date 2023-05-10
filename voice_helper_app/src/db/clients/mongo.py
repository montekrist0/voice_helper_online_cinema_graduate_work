import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from core.configs import settings

host = settings.mongo_host
port = settings.mongo_port

client: AsyncIOMotorClient | None = None


def create_mongo_client():
    return motor.motor_asyncio.AsyncIOMotorClient(host=host, port=port, maxPoolSize=10)


def get_mongo_client():
    return client
