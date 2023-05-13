import os

from pydantic import (BaseSettings,
                      Field)


class Settings(BaseSettings):
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mongo_host: str = Field(default='localhost')
    mongo_port: int = Field(default='27017')
    mongo_db: str = Field(default='voice_helper')
    delta_update_cmd_tbr: int = Field(default=3)
    redis_message_host: str = Field(default='localhost')
    redis_message_port: int = Field(default=6379)
    mongo_collection_cmd = 'commands'
    mongo_collection_tbr = 'to_be_removed'
    elastic_host: str
    elastic_port: int


settings = Settings()
