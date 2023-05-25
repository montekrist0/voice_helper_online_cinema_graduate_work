import os
from pathlib import Path

from pydantic import BaseSettings, Field


class BaseConfig(BaseSettings):
    mongo_host: str = Field('localhost', env='MONGO_HOST')
    mongo_port: int = Field(27017, env='MONGO_PORT')
    mongo_db: str = Field('ugc2_movies', env='MONGO_DB')

    class Config:
        env_file = os.path.join(Path(__file__).parent.absolute(), '.env')
        env_file_encoding = 'utf-8'


settings = BaseConfig()
