import pytest
import pytest_asyncio
import motor.motor_asyncio
import asyncio

from tests.unit.app.services.cmd_handler import CommandHandler

from tests.unit.settings import settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def mongo_db(event_loop):
    client = motor.motor_asyncio.AsyncIOMotorClient(host=settings.mongo_host, port=settings.mongo_port, maxPoolSize=10)
    yield client[settings.mongo_db]


@pytest.fixture(scope='function')
def command_handler(mongo_db):
    return CommandHandler(commands_db=mongo_db)
